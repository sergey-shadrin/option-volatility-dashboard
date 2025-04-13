from datetime import datetime, timedelta, timezone

from model.option import Option

# время жизни последней цены last_price_iv для расчетов (15 минут в секундах)
LAST_PRICE_LIFETIME_MINUTES = 15

def get_real_volatility(option: Option) -> float:
    real_vol = None
    if option.last_price_timestamp is not None and is_last_price_timestamp_actual(option.last_price_timestamp):
        # если есть LastPrice и время жизни его не истекло
        real_vol = option.last_price_iv
    else:
        if option.ask_iv is None or option.bid_iv is None:  # нет бида или нет аска
            real_vol = option.volatility
        elif option.ask_iv is not None and option.bid_iv is not None and option.volatility is not None:
            if option.ask_iv > option.volatility > option.bid_iv:  # в пределах спреда bid-ask
                real_vol = option.volatility
            elif (option.ask_iv < option.volatility and option.bid_iv < option.volatility and
                  option.ask_iv < option.volatility or option.volatility < option.bid_iv):  # вне пределов спреда bid-ask
                real_vol = (option.ask_iv + option.bid_iv) / 2
    return real_vol

def is_last_price_timestamp_actual(last_price_timestamp) -> bool:
    now = datetime.now(timezone.utc)
    time_ago = now - timedelta(minutes=LAST_PRICE_LIFETIME_MINUTES)

    last_price_datetime = datetime.fromtimestamp(last_price_timestamp, tz=timezone.utc)
    return time_ago <= last_price_datetime <= now