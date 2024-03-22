from datetime import datetime, time

_DAILY_SESSION_START_TIME = time(9, 0)
_EVENING_SESSION_START_TIME = time(19, 5)
_EVENING_SESSION_END_TIME = time(23, 50)


def is_trading_session_active_now() -> bool:
    now = datetime.now()
    return _is_datetime_in_today_daily_session(now) or _is_datetime_in_today_evening_session(now)


def is_datetime_in_current_trading_session(datetime_to_check: datetime) -> bool:
    now = datetime.now()
    is_in_daily_session = _is_datetime_in_today_daily_session(now) and _is_datetime_in_today_daily_session(datetime_to_check)
    is_in_evening_session = _is_datetime_in_today_evening_session(now) and _is_datetime_in_today_evening_session(datetime_to_check)
    return is_in_daily_session or is_in_evening_session


def _get_today_datetime(time_position: time) -> datetime:
    current_date = datetime.today().date()
    return datetime.combine(current_date, time_position)


def _get_today_daily_session_start_datetime() -> datetime:
    return _get_today_datetime(_DAILY_SESSION_START_TIME)


def _get_today_evening_session_start_datetime() -> datetime:
    return _get_today_datetime(_EVENING_SESSION_START_TIME)


def _get_today_evening_session_end_datetime() -> datetime:
    return _get_today_datetime(_EVENING_SESSION_END_TIME)


def _is_datetime_in_today_daily_session(dtime: datetime) -> bool:
    daily_session_start_datetime = _get_today_daily_session_start_datetime()
    evening_session_start_datetime = _get_today_evening_session_start_datetime()
    return daily_session_start_datetime < dtime < evening_session_start_datetime


def _is_datetime_in_today_evening_session(dtime: datetime) -> bool:
    evening_session_start_datetime = _get_today_evening_session_start_datetime()
    evening_session_end_datetime = _get_today_evening_session_end_datetime()
    return evening_session_start_datetime < dtime < evening_session_end_datetime


