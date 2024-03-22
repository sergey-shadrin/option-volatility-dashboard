from app import trading_session_time
from app.implied_volatility import get_iv_for_option_price
from infrastructure.alor_api import AlorApi
from model import option_series_type, option_type
from model.base_asset import BaseAsset
from model.option import Option
from model.option_model import OptionModel
from model.watched_instruments_filter import WatchedInstrumentsFilter
from view.flask_app import get_flask_app
from datetime import datetime
from infrastructure import moex_api, env_utils
from view.option_data_request_params import OptionDataRequestParams

_MAX_STRIKES_COUNT = 11
_DEFAULT_STRIKE_STEP = 1000


class OptionApp:

    _SUPPORTED_BASE_ASSET_TICKERS = ['SiM4']

    def __init__(self):
        print('Debug message to test github Actions')
        self._model = OptionModel()
        self._watchedInstrumentsFilter = WatchedInstrumentsFilter()
        alor_client_token = env_utils.get_env_or_exit('ALOR_CLIENT_TOKEN')
        self._alorApi = AlorApi(alor_client_token)

    def start(self):
        self._prepare_model()
        self._start_flask_app()
        self._subscribe_to_base_asset_events()
        self._alorApi.run_async_connection(env_utils.get_bool('DEBUG'))

    def _subscribe_to_base_asset_events(self):
        for base_asset in self._model.base_asset_repository.get_all():
            self._alorApi.subscribe_to_quotes(base_asset.ticker, self._handle_base_asset_quotes_event)

    def _handle_base_asset_quotes_event(self, ticker, data):
        prev_last_price = None
        base_asset = self._model.base_asset_repository.get_by_ticker(ticker)
        if base_asset.last_price is not None:
            prev_last_price = base_asset.last_price

        base_asset.last_price = data['last_price']

        if prev_last_price is None:
            self._update_watched_instruments_filter(base_asset)
        elif prev_last_price != base_asset.last_price:
            self._update_watched_instruments_filter(base_asset)
            self._recalculate_volatilities(base_asset)

    def _update_watched_instruments_filter(self, base_asset):
        list_of_strikes = _get_list_of_strikes(base_asset.last_price, _DEFAULT_STRIKE_STEP, _MAX_STRIKES_COUNT)
        options_by_strikes = self._model.option_repository.get_by_strikes(base_asset.ticker, list_of_strikes)
        for option in options_by_strikes:
            option_ticker = option.ticker
            if not self._watchedInstrumentsFilter.has_option_ticker(option_ticker):
                self._alorApi.subscribe_to_quotes(option_ticker, self._handle_option_quotes_event)
                self._alorApi.subscribe_to_instrument(option_ticker, self._handle_option_instrument_event)
                self._watchedInstrumentsFilter.add_option_ticker(option_ticker)

    def _handle_option_quotes_event(self, ticker, data):
        option = self._model.option_repository.get_by_ticker(ticker)
        base_asset = self._model.base_asset_repository.get_by_ticker(option.base_asset_ticker)
        base_asset_last_price = base_asset.last_price
        prev_last_price_timestamp_of_option = option.last_price_timestamp

        option.last_price = data['last_price']
        option.last_price_timestamp = data['last_price_timestamp']
        option.ask = data['ask']
        option.bid = data['bid']
        if option.last_price is not None and option.last_price_timestamp is not None:
            last_price_timestamp_datetime = datetime.fromtimestamp(option.last_price_timestamp)
            if trading_session_time.is_datetime_in_current_trading_session(last_price_timestamp_datetime):
                # Вычисляем новую волатильность по цене последней сделки,
                # если сделка совершалась в текущую торговую сессию
                if prev_last_price_timestamp_of_option is None or prev_last_price_timestamp_of_option != option.last_price_timestamp:
                    # Волатильность по цене последней сделки опциона вычисляется только по факту совершения сделки,
                    # так как это уже свершившиеся событие, и волатильность по нему не нужно пересчитывать постоянно.
                    # При этом возможны сделки по прежней цене, но с другим временем совершения
                    option.last_price_iv = get_iv_for_option_price(base_asset_last_price, option,
                                                                   option.last_price)
            elif trading_session_time.is_trading_session_active_now():
                # Если на данный момент идёт активная торговая сессия,
                # нужно убирать данные по вычисленной волатильности сделки,
                # имевшей место в прошлой торговой сессии
                option.last_price_iv = None

        if option.ask:
            option.ask_iv = get_iv_for_option_price(base_asset_last_price, option,
                                                    option.ask)
        if option.bid:
            option.bid_iv = get_iv_for_option_price(base_asset_last_price, option,
                                                    option.bid)

    def _handle_option_instrument_event(self, ticker, data):
        option = self._model.option_repository.get_by_ticker(ticker)
        option.volatility = data['volatility']

    def _recalculate_volatilities(self, base_asset):
        option_repository = self._model.option_repository
        watched_option_tickers = self._watchedInstrumentsFilter.option_tickers
        watched_options_of_base_asset = option_repository.get_by_tickers_for_base_asset(base_asset.ticker,
                                                                                        watched_option_tickers)
        for option in watched_options_of_base_asset:
            option.ask_iv = get_iv_for_option_price(base_asset.last_price, option,
                                                    option.ask)
            option.bid_iv = get_iv_for_option_price(base_asset.last_price, option,
                                                    option.bid)

    def _start_flask_app(self):
        flask_app = get_flask_app()
        flask_app.set_option_app(self)
        flask_app.start_app_in_thread()

    def _prepare_model(self):
        for base_asset_ticker in self._SUPPORTED_BASE_ASSET_TICKERS:
            self._populate_model_for_base_asset(base_asset_ticker)

    def _populate_model_for_base_asset(self, base_asset_ticker: str):
        base_asset = self._init_base_asset_from_moex_api(base_asset_ticker)
        self._model.base_asset_repository.insert_base_asset(base_asset)

        option_expirations = moex_api.get_option_expirations(base_asset_ticker)
        for option_expiration_data in option_expirations:
            series_type = option_expiration_data['series_type']
            expiration_date = option_expiration_data['expiration_date']
            self._populate_options_from_board(base_asset, series_type, expiration_date)

    def _populate_options_from_board(self, base_asset: BaseAsset, series_type: str, expiration_date: str):
        expiration_datetime = self._get_option_expiration_datetime(base_asset.base_asset_code, series_type,
                                                                   expiration_date)
        base_asset.add_expiration_datetime(expiration_datetime)

        option_board_data = moex_api.get_option_board(base_asset.ticker, expiration_date)
        for opt_type in option_board_data:
            for option_data in option_board_data[opt_type]:
                option_ticker = option_data['SECID']
                strike = option_data['STRIKE']
                option = Option(option_ticker, base_asset.ticker, expiration_datetime, strike, opt_type)
                self._model.option_repository.insert_option(option)

    def _get_option_expiration_datetime(self, base_asset_code: str, series_type: str, expiration_date: str):
        expiration_datetime = expiration_date + 'T18:50:00'
        currency_base_asset_codes = ('Si', 'Eu', 'Cn')
        if base_asset_code in currency_base_asset_codes and series_type == option_series_type.QUARTER:
            expiration_datetime = expiration_date + 'T14:00:00'
        return datetime.fromisoformat(expiration_datetime)

    def _init_base_asset_from_moex_api(self, base_asset_ticker):
        base_asset = BaseAsset(base_asset_ticker)
        asset_description_rows = moex_api.get_security_description(base_asset_ticker)
        for row in asset_description_rows:
            if row['name'] == 'SHORTNAME':
                base_asset.short_name = row['value']
            if row['name'] == 'ASSETCODE':
                base_asset.base_asset_code = row['value']
        return base_asset

    def _retrieve_data_for_diagram(self, request_params: OptionDataRequestParams):
        # TODO: концепт с динамическим обновлением списка "наблюдаемых" инструментов пока не реализован
        #  из-за трудностей передачи данных между потоками. Метод вызывается из обработчика Flask в другом потоке.
        #  если вызывать отсюда методы asyncio.Queue() - происходит падение с ошибкой
        #  "RuntimeError: Non-thread-safe operation invoked on an event loop other than the current one"

        # Извлекаем те данные, что уже есть
        base_asset_ticker = request_params.base_asset_ticker
        base_asset = self._model.base_asset_repository.get_by_ticker(base_asset_ticker)
        watched_option_tickers = self._watchedInstrumentsFilter.option_tickers

        expiration_datetimes = [datetime.fromisoformat(expiration_date) for expiration_date in request_params.expiration_dates]
        options = self._model.option_repository.get_by_tickers_and_expiration_dates_for_base_asset(base_asset.ticker,
                                                                                                   watched_option_tickers,
                                                                                                   expiration_datetimes)

        options_sorted_by_strike = sorted(options, key=_get_option_strike)

        strikes_dictionary = {}
        for option in options_sorted_by_strike:
            if option.strike not in strikes_dictionary:
                strikes_dictionary[option.strike] = {}

            expiration_date_iso_string = option.expiration_datetime.date().isoformat()
            if expiration_date_iso_string not in strikes_dictionary[option.strike]:
                strikes_dictionary[option.strike][expiration_date_iso_string] = {}

            strikes_dictionary[option.strike][expiration_date_iso_string][option.type] = option
        list_of_labels = []
        # TODO: сортировка по возрастанию даты экспирации

        strikes_to_labels_dict = {}
        for strike, strike_dataset in strikes_dictionary.items():
            strikes_to_labels_dict[strike] = {}
            for expiration_date, option_pair in strike_dataset.items():
                for opt_type, option in option_pair.items():
                    if opt_type == option_type.CALL:
                        label = f'{expiration_date} Volatility'
                        strikes_to_labels_dict[strike][label] = option.volatility
                        if label not in list_of_labels:
                            list_of_labels.append(label)
                    type_string = 'Call' if opt_type == option_type.CALL else 'Put'
                    label_prefix = f'{expiration_date} {type_string}'

                    label = f'{label_prefix} Ask'
                    strikes_to_labels_dict[strike][label] = option.ask_iv
                    if label not in list_of_labels:
                        list_of_labels.append(label)

                    label = f'{label_prefix} Bid'
                    strikes_to_labels_dict[strike][label] = option.bid_iv
                    if label not in list_of_labels:
                        list_of_labels.append(label)

                    label = f'{label_prefix} Last Price'
                    strikes_to_labels_dict[strike][label] = option.last_price_iv
                    if label not in list_of_labels:
                        list_of_labels.append(label)

        list_of_strikes = list(strikes_dictionary.keys())

        view_datasets = []
        for i in range(len(list_of_labels)):
            if i not in view_datasets:
                view_datasets.append([])
            for j in range(len(list_of_strikes)):
                label = list_of_labels[i]
                strike = list_of_strikes[j]
                value = strikes_to_labels_dict[strike][label]
                view_datasets[i].append(value)

        return {
            'last_price': base_asset.last_price,
            'labels': list_of_labels,
            'strikes': list_of_strikes,
            'view_datasets': view_datasets,
        }

    def dump_model(self):
        return self._model.dump()

    def dump_watched_instruments(self):
        watched_option_tickers = self._watchedInstrumentsFilter.option_tickers
        watched_options = self._model.option_repository.get_by_tickers(watched_option_tickers)

        return [vars(option) for option in watched_options]

    def get_option_diagram_data(self, request_params: OptionDataRequestParams):
        return self._retrieve_data_for_diagram(request_params)


# Центральный страйк - наиболее близкий к цене базового актива с учётом заданного шага цены страйков
def _calculate_central_strike(base_asset_price, strike_step):
    return round(base_asset_price / strike_step) * strike_step


# Формируем список страйков с учетом заданного количества страйков, шага цены страйка и центрального страйка
# TODO: проверять, что все страйки больше нуля
def _get_list_of_strikes(base_asset_price, strike_step, strikes_count):
    central_strike = _calculate_central_strike(base_asset_price, strike_step)
    strikes_before_count = strikes_count // 2
    first_strike = central_strike - strikes_before_count * strike_step
    strikes = []
    for i in range(strikes_count):
        strikes.append(first_strike + i * strike_step)

    return strikes


def _get_option_strike(option: Option):
    return option.strike
