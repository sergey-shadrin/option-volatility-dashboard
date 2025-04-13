from datetime import datetime
from model.option import Option

# время жизни последней цены last_price_iv для расчетов (15 минут в секундах)
LAST_PRICE_LIFETIME = 60 * 15

def get_real_volatility(option: Option) -> float:

    real_vol = None
    if option.last_price_timestamp is not None and is_last_price_timestamp_actual(option.last_price_timestamp):
        # если есть LastPrice и время жизни его не истекло
        real_vol = option.last_price_iv
    else:
        if option.ask_iv is None or option.bid_iv is None:  # нет бида или нет аска
            real_vol = option.volatility
        else:
            if option.ask_iv is not None and option.bid_iv is not None and option.ask_iv > option.volatility > option.bid_iv:  # в пределах спреда bid-ask
                real_vol = option.volatility
            else:
                if (option.ask_iv < option.volatility and option.bid_iv < option.volatility and
                        option.ask_iv < option.volatility or option.volatility < option.bid_iv):  # вне пределов спреда bid-ask
                    real_vol = (option.ask_iv + option.bid_iv) / 2
    return real_vol

def is_last_price_timestamp_actual(last_price_timestamp) -> bool:
    current_timestamp = datetime.utcnow()  # текущее время в секундах UTC
    return current_timestamp - last_price_timestamp < LAST_PRICE_LIFETIME