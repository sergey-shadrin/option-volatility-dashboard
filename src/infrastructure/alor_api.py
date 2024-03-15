import asyncio
import json
import queue
import uuid

import websockets

from infrastructure.alor_api_event import AlorApiEvent
from infrastructure.api_utils import get_object_from_json_endpoint

REFRESH_TOKEN_URL = 'https://oauth.alor.ru/refresh'
WEBSOCKET_URL = 'wss://api.alor.ru/ws'
EXCHANGE_MOEX = "MOEX"

API_METHOD_QUOTES_SUBSCRIBE = "QuotesSubscribe"
API_METHOD_INSTRUMENTS_GET_AND_SUBSCRIBE = "InstrumentsGetAndSubscribeV2"

_async_queue = asyncio.Queue()

def _get_guid():
    return str(uuid.uuid4())


def _get_authorization_token(client_token):
    params = {'token': client_token}

    response = get_object_from_json_endpoint(REFRESH_TOKEN_URL, 'POST', params)
    authorization_token = None
    if response and 'AccessToken' in response:
        authorization_token = response['AccessToken']
    return authorization_token


class AlorApi:
    def __init__(self, client_token):
        self._api_events = {}
        self._auth_token = _get_authorization_token(client_token)

    def run_async_connection(self):
        asyncio.run(self._connect_to_websocket(), debug=True)

    def subscribe_to_instrument(self, ticker, callback):
        self._subscribe_to_event(API_METHOD_INSTRUMENTS_GET_AND_SUBSCRIBE, ticker, callback)

    def subscribe_to_quotes(self, ticker: str, callback: callable):
        self._subscribe_to_event(API_METHOD_QUOTES_SUBSCRIBE, ticker, callback)

    def _handle_alor_data(self, guid, data):
        api_event = self._get_api_event(guid)
        ticker = api_event.ticker
        callback = api_event.callback
        callback(ticker, data)

    def _get_api_event(self, guid: str) -> AlorApiEvent:
        return self._api_events[guid]

    def _add_api_event(self, guid: str, api_event: AlorApiEvent):
        self._api_events[guid] = api_event

    async def _connect_to_websocket(self):
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            await self._handler(websocket)

    async def _consumer(self, message):
        message_dict = json.loads(message)
        if 'data' in message_dict and 'guid' in message_dict:
            guid = message_dict['guid']
            data = message_dict['data']
            self._handle_alor_data(guid, data)

    async def _consumer_handler(self, websocket):
        async for message in websocket:
            await self._consumer(message)

    async def _producer_handler(self, websocket):
        while True:
            message = await _async_queue.get()
            await websocket.send(message)

    async def _handler(self, websocket):
        consumer_task = asyncio.create_task(self._consumer_handler(websocket))
        producer_task = asyncio.create_task(self._producer_handler(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    def _subscribe_to_event(self, api_method: str, ticker: str, callback: callable):
        guid = _get_guid()
        event = AlorApiEvent(ticker, callback)
        self._add_api_event(guid, event)
        subscribe_json = self._get_json_to_subscribe(api_method, ticker, guid)
        _async_queue.put_nowait(subscribe_json)

    def _get_json_to_subscribe(self, api_method: str, ticker: str, guid: str):
        return json.dumps({
            "opcode": api_method,
            "code": ticker,
            "exchange": EXCHANGE_MOEX,
            "guid": guid,
            "token": self._auth_token
        })
