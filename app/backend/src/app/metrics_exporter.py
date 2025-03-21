from prometheus_client import Gauge

BASE_ASSET_LAST_PRICE_GAUGE = Gauge('base_asset_last_price', 'Last price of base asset', ['base_asset_ticker', 'short_name', 'base_asset_code', 'strike'])
OPTION_VOLATILITY_GAUGE = Gauge('option_volatility', 'Option volatility', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_ASK_GAUGE = Gauge('option_ask', 'Option ask', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_ASK_IV_GAUGE = Gauge('option_ask_iv', 'Option ask implied volatility', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_BID_GAUGE = Gauge('option_bid', 'Option bid', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_BID_IV_GAUGE = Gauge('option_bid_iv', 'Option bid implied volatility', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_LAST_PRICE_GAUGE = Gauge('option_last_price', 'Option last price', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
OPTION_LAST_PRICE_IV_GAUGE = Gauge('option_last_price_iv', 'Option last price implied volatility', ['ticker', 'strike', 'type', 'base_asset_ticker', 'expiration_datetime'])
CENTRAL_STRIKE_GAUGE = Gauge('central_strike', 'Central strike', ['base_asset_ticker'])


def set_base_asset_metrics(base_asset):
    if base_asset.last_price:
        BASE_ASSET_LAST_PRICE_GAUGE.labels(base_asset_ticker=base_asset.ticker, short_name=base_asset.short_name,
                                           base_asset_code=base_asset.base_asset_code, strike=_format_strike_string(base_asset.strike)).set(
            base_asset.last_price)


def set_option_metrics(option):
    formatted_strike = _format_strike_string(option.strike)
    expiration_date = option.expiration_datetime.strftime("%d.%m.%y")
    if option.volatility:
        OPTION_VOLATILITY_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                       base_asset_ticker=option.base_asset_ticker,
                                       expiration_datetime=expiration_date).set(
            option.volatility)

    if option.ask:
        OPTION_ASK_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                base_asset_ticker=option.base_asset_ticker,
                                expiration_datetime=expiration_date).set(option.ask)

    if option.ask_iv:
        OPTION_ASK_IV_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                   base_asset_ticker=option.base_asset_ticker,
                                   expiration_datetime=expiration_date).set(option.ask_iv)

    if option.bid:
        OPTION_BID_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                base_asset_ticker=option.base_asset_ticker,
                                expiration_datetime=expiration_date).set(option.bid)

    if option.bid_iv:
        OPTION_BID_IV_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                   base_asset_ticker=option.base_asset_ticker,
                                   expiration_datetime=expiration_date).set(option.bid_iv)

    if option.last_price:
        OPTION_LAST_PRICE_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                       base_asset_ticker=option.base_asset_ticker,
                                       expiration_datetime=expiration_date).set(
            option.last_price)

    if option.last_price_iv:
        OPTION_LAST_PRICE_IV_GAUGE.labels(ticker=option.ticker, strike=formatted_strike, type=option.type,
                                          base_asset_ticker=option.base_asset_ticker,
                                          expiration_datetime=expiration_date).set(
            option.last_price_iv)


def _format_strike_string(strike):
    if strike == int(strike):
        return str(int(strike))
    else:
        return str(strike).rstrip('0').rstrip('.')