import sys
import os
from app.implied_volatility import implied_vol
from infrastructure.alor_api import AlorApi
from model import option_series_type, option_type
from model.base_asset import BaseAsset
from model.option import Option
from model.option_model import OptionModel
from model.watched_instruments_filter import WatchedInstrumentsFilter
from view.flask_app import get_flask_app
from datetime import datetime
from infrastructure import moex_api
from view.option_data_request_params import OptionDataRequestParams

STRIKES_COUNT = 11
STRIKE_STEP = 1000
RISK_FREE_INTEREST_RATE = 0  # risk-free interest rate


def get_iv_for_option_price(asset_price: int, option: Option, opt_price: int):
    strike_price = option.strike
    for param in (asset_price, strike_price, opt_price, option.option_type):
        if param is None:
            return None

    # parameters
    time_to_maturity = option.get_time_to_maturity()

    tolerance = 10 ** -8
    iv = implied_vol(opt_price, asset_price, strike_price, RISK_FREE_INTEREST_RATE, time_to_maturity, tolerance, option.option_type)
    if not iv:
        return None
    return iv * 100


def get_env_or_exit(var_name):
    value = os.environ.get(var_name)

    if value is None:
        print_error_message_and_exit(f'{var_name} environment variable is not set.')

    return value


def print_error_message_and_exit(error_message):
    sys.stderr.write(error_message + '\n')
    sys.exit(1)


# Центральный страйк - наиболее близкий к цене базового актива с учётом заданного шага цены страйков
def calculate_central_strike(base_asset_price):
    return round(base_asset_price / STRIKE_STEP) * STRIKE_STEP


# Формируем список страйков с учетом заданного количества страйков, шага цены страйка и центрального страйка
# TODO: проверять, что все страйки больше нуля
def get_list_of_strikes(central_strike):
    strikes_before_count = STRIKES_COUNT // 2
    first_strike = central_strike - strikes_before_count * STRIKE_STEP
    strikes = []
    for i in range(STRIKES_COUNT):
        strikes.append(first_strike + i * STRIKE_STEP)

    return strikes


def get_option_strike(option: Option):
    return option.strike


class OptionApp:

    _SUPPORTED_BASE_ASSET_TICKERS = ['SiM4']

    def __init__(self):
        self._model = OptionModel()
        self._watchedInstrumentsFilter = WatchedInstrumentsFilter()
        alor_client_token = get_env_or_exit('ALOR_CLIENT_TOKEN')
        self._alorApi = AlorApi(alor_client_token)

    def start(self):
        self._prepare_model()
        self._start_flask_app()
        self._subscribe_to_base_asset_events()
        self._alorApi.run_async_connection()

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
        central_strike = calculate_central_strike(base_asset.last_price)
        list_of_strikes = get_list_of_strikes(central_strike)
        options_by_strikes = self._model.option_repository.get_by_strikes(base_asset.ticker, list_of_strikes)
        for option in options_by_strikes:
            option_ticker = option.ticker
            if not self._watchedInstrumentsFilter.has_option_ticker(option):
                self._alorApi.subscribe_to_quotes(option_ticker, self._handle_option_quotes_event)
                self._alorApi.subscribe_to_instrument(option_ticker, self._handle_option_instrument_event)
                self._watchedInstrumentsFilter.add_option_ticker(option_ticker)

    def _handle_option_quotes_event(self, ticker, data):
        option = self._model.option_repository.get_by_ticker(ticker)
        base_asset = self._model.base_asset_repository.get_by_ticker(option.base_asset_ticker)
        base_asset_last_price = base_asset.last_price
        prev_last_price_of_option = option.last_price
        option.last_price = data['last_price']
        option.ask = data['ask']
        option.bid = data['bid']
        if option.last_price is not None and (
                prev_last_price_of_option is None or prev_last_price_of_option != option.last_price):
            # Волатильность по цене последней сделки опциона вычисляется только по факту изменения,
            # так как это уже свершившиеся событие, и волатильность по нему не нужно пересчитывать постоянно
            option.last_price_iv = get_iv_for_option_price(base_asset_last_price, option,
                                                           option.last_price)

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
        # TODO: оценить трудоёмкость выполнения
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

        option_series_data = moex_api.get_option_series(base_asset.base_asset_code)
        for option_series in option_series_data:
            series_name = str(option_series['name'])
            if series_name.startswith(base_asset.short_name):
                self._populate_options_for_series(base_asset, option_series)

    def _get_option_expiration_datetime(self, base_asset_code: str, series_type: str, expiration_date: str):
        expiration_datetime = expiration_date + 'T18:50:00'
        currency_base_asset_codes = ('Si', 'Eu', 'Cn')
        if base_asset_code in currency_base_asset_codes and series_type == option_series_type.QUARTER:
            expiration_datetime = expiration_date + 'T14:00:00'
        return datetime.fromisoformat(expiration_datetime)

    def _populate_options_for_series(self, base_asset: BaseAsset, series_data: dict):
        series_name = series_data['name']
        series_type = series_data['series_type']
        expiration_date = series_data['expiration_date']

        expiration_datetime = self._get_option_expiration_datetime(base_asset.base_asset_code, series_type,
                                                                   expiration_date)
        base_asset.add_expiration_datetime(expiration_datetime)
        option_list_data = moex_api.get_option_list_by_series(series_name)
        for option_data in option_list_data:
            self._populate_option_from_option_data(option_data, base_asset.ticker, expiration_datetime)

    def _populate_option_from_option_data(self, option_data, base_asset_ticker, expiration_datetime):
        is_traded = option_data['is_traded']
        if is_traded:
            ticker = option_data['secid']
            strike = option_data['strike']
            type = option_data['option_type']
            option = Option(ticker, base_asset_ticker, expiration_datetime, strike, type)
            self._model.option_repository.insert_option(option)

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
        # TODO: добавить поддержку нескольких серий
        expiration_date = request_params.expiration_dates[0]
        watched_option_tickers = self._watchedInstrumentsFilter.option_tickers

        expiration_datetime = datetime.fromisoformat(expiration_date)
        options = self._model.option_repository.get_by_tickers_and_expiration_date_for_base_asset(base_asset.ticker,
                                                                                                  watched_option_tickers,
                                                                                                  expiration_datetime)

        options_sorted_by_strike = sorted(options, key=get_option_strike)

        strikes_dictionary = {}
        for option in options_sorted_by_strike:
            if option.strike not in strikes_dictionary:
                strikes_dictionary[option.strike] = {}

            strikes_dictionary[option.strike][option.option_type] = option

        strikes = []
        for strike, options in strikes_dictionary.items():
            call_option = options[option_type.CALL]
            put_option = options[option_type.PUT]
            strikes.append({
                'strike': strike,
                'volatility': call_option.volatility,
                'call': {
                    'ask_volatility': call_option.ask_iv,
                    'bid_volatility': call_option.bid_iv,
                    'last_price_volatility': call_option.last_price_iv,
                },
                'put': {
                    'ask_volatility': put_option.ask_iv,
                    'bid_volatility': put_option.bid_iv,
                    'last_price_volatility': put_option.last_price_iv,
                },
            })

        return {
            'last_price': base_asset.last_price,
            'strikes': strikes
        }

    def dump_model(self):
        return self._model.dump()

    def dump_watched_instruments(self):
        watched_option_tickers = self._watchedInstrumentsFilter.option_tickers
        watched_options = self._model.option_repository.get_by_tickers(watched_option_tickers)

        return [vars(option) for option in watched_options]

    def get_option_diagram_data(self, request_params: OptionDataRequestParams):
        return self._retrieve_data_for_diagram(request_params)


def main():
    option_app = OptionApp()
    option_app.start()


if __name__ == '__main__':
    main()
