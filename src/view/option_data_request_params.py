class OptionDataRequestParams:
    def __init__(self):
        self._base_asset_ticker = None
        self._expiration_dates = []
        self._strikes_count = None
        self._strikes_step = None

    @property
    def base_asset_ticker(self) -> str:
        return self._base_asset_ticker

    @base_asset_ticker.setter
    def base_asset_ticker(self, base_asset_ticker: str):
        self._base_asset_ticker = base_asset_ticker

    @property
    def expiration_dates(self) -> [str]:
        return self._expiration_dates

    @expiration_dates.setter
    def expiration_dates(self, expiration_dates: [str]):
        self._expiration_dates = expiration_dates

    @property
    def strikes_count(self) -> int:
        return self._strikes_count

    @strikes_count.setter
    def strikes_count(self, strikes_count: int):
        self._strikes_count = strikes_count

    @property
    def strikes_step(self) -> int:
        return self._strikes_step

    @strikes_step.setter
    def strikes_step(self, strikes_step: int):
        self._strikes_step = strikes_step

