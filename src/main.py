from flask import Flask, jsonify, request, render_template
import requests
import asyncio
import websockets
import sys
import os
import json
import uuid
import threading
import random
from implied_volatility import implied_vol, option_price, OPTION_TYPE_CALL, OPTION_TYPE_PUT
from datetime import datetime


app = Flask(__name__)
app.json_provider_class.compact = False

BASE_ASSET_CODE = 'SiH4'
STRIKES_COUNT = 11
STRIKE_STEP = 1000
MOEX_OPTIONS_LIST_URL = 'https://iss.moex.com/iss/statistics/engines/futures/markets/options/series/Si-3.24M210324XA/securities.json'
# TODO: secret config client token must be taken from env
ALOR_REFRESH_TOKEN_URL = 'https://oauth.alor.ru/refresh'
ALOR_WS_URL = 'wss://api.alor.ru/ws'

g_alor_auth = {
    'token': ''
}
g_model = {
    'base_asset': {
        'quotes': {}
    },
    'options': {}
}
g_guid_links = {}
g_async_queue = asyncio.Queue()


def get_guid_dict():
    guid = str(uuid.uuid4())
    g_guid_links[guid] = {'guid': guid, 'data': {}}
    return guid, g_guid_links[guid]


@app.route('/model', methods=['GET'])
def get_model():
    return jsonify(g_model)


@app.route('/chart.json', methods=['GET'])
def get_diagram_data():
    return jsonify(prepare_data_for_diagram())


# TODO: serve static files via nginx
@app.route('/chart.html', methods=['GET'])
def get_chart():
    return render_template('chart.html')


# TODO: serve static files via nginx
@app.route('/volatility_chart.js', methods=['GET'])
def get_chart_js():
    return render_template('volatility_chart.js')


def get_time_to_option_maturity():
    # TODO: учитывать точность до минут, когда даты экспирации опционов будут зависеть от серии
    options_expiration_date = datetime(2024, 3, 21, 18, 50)

    difference = options_expiration_date - datetime.now()
    seconds_in_year = 365 * 24 * 60 * 60
    return difference.total_seconds() / seconds_in_year


def get_iv_for_option_price(asset_price, strike_price, opt_price, option_type):
    # parameters
    S = asset_price
    K = strike_price
    T = get_time_to_option_maturity()
    r = 0  # risk-free interest rate
    C = opt_price

    tol = 10 ** -8
    iv = implied_vol(C, S, K, r, T, tol, option_type)
    if not iv:
        return None
    return iv * 100


def prepare_data_for_diagram():
    # TODO: Пересчитывать данные по волатильностям, как только пришли новые данные с биржи, а не когда они запрашиваются
    #   для отображения
    strikes_data = []
    last_price = g_model['base_asset']['quotes']['data']['last_price']
    for strike in g_model['list_of_strikes']:
        call_option_data = g_model['options'][strike]['C']
        put_option_data = g_model['options'][strike]['P']
        volatility = call_option_data['instrument']['data']['volatility']
        call_ask = call_option_data['quotes']['data']['ask']
        call_bid = call_option_data['quotes']['data']['bid']
        call_last_price = call_option_data['quotes']['data']['last_price']
        put_ask = put_option_data['quotes']['data']['ask']
        put_bid = put_option_data['quotes']['data']['bid']

        call_ask_volatility = get_iv_for_option_price(last_price, strike, call_ask, OPTION_TYPE_CALL)
        call_bid_volatility = get_iv_for_option_price(last_price, strike, call_bid, OPTION_TYPE_CALL)

        if 'processed_last_price' in call_option_data and call_option_data['processed_last_price'] == call_last_price:
            call_last_price_volatility = call_option_data['computed_last_price_volatility']
        else:
            call_last_price_volatility = get_iv_for_option_price(last_price, strike, call_last_price, OPTION_TYPE_CALL)
            call_option_data['processed_last_price'] = call_last_price
            call_option_data['computed_last_price_volatility'] = call_last_price_volatility

        put_ask_volatility = get_iv_for_option_price(last_price, strike, put_ask, OPTION_TYPE_PUT)
        put_bid_volatility = get_iv_for_option_price(last_price, strike, put_bid, OPTION_TYPE_PUT)
        strikes_data.append({
            'strike': strike,
            'volatility': volatility,
            'call_ask_volatility': call_ask_volatility,
            'call_bid_volatility': call_bid_volatility,
            'call_last_price_volatility': call_last_price_volatility,
            'put_ask_volatility': put_ask_volatility,
            'put_bid_volatility': put_bid_volatility,
            'call_last_price': call_last_price,  # for debug
            'call_ask': call_ask,  # for debug
            'put_bid': put_bid,  # for debug
            'put_ask': put_ask,  # for debug
        })


    return {
        'strikes': strikes_data,
        'last_price': last_price,
    }


def populate_options_dict(response_data):
    securities_columns = response_data['securities']['columns']
    securities_data = response_data['securities']['data']
    options_dict = {}
    for security_data in securities_data:
        security_dict = {}

        for i in range(len(securities_columns)):
            key = securities_columns[i]
            value = security_data[i]
            security_dict[key] = value

        is_traded = security_dict['is_traded']
        if is_traded:
            strike = security_dict['strike']
            option_type = security_dict['option_type']
            if strike not in options_dict:
                options_dict[strike] = {}

            options_dict[strike][option_type] = {'moex_data': security_dict}
    return options_dict


def get_options_from_moex():
    response_object = get_object_from_json_endpoint(MOEX_OPTIONS_LIST_URL)
    if not response_object:
        return None

    return populate_options_dict(response_object)


def get_env_or_exit(var_name):
    value = os.environ.get(var_name)

    if value is None:
        print_error_message_and_exit(f'{var_name} environment variable is not set.')

    return value


def get_alor_authorization_token():

    # alor_client_token = '5059ee3f-882c-4e50-a848-6b748ff0f89c'
    alor_client_token = get_env_or_exit('ALOR_CLIENT_TOKEN')
    params = {'token': alor_client_token}

    response = get_object_from_json_endpoint(ALOR_REFRESH_TOKEN_URL, 'POST', params)
    alor_authorization_token = ''
    if response:
        alor_authorization_token = response['AccessToken']
    return alor_authorization_token


def get_object_from_json_endpoint(url, method='GET', params={}):
    response = requests.request(method, url, params=params)

    response_data = None
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content (JSON data)
        response_data = response.json()
    else:
        # Print an error message if the request was not successful
        print_error_message_and_exit(f"Error: {response.status_code}")
    return response_data


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


def subscribe_to_option_instrument(option_from_model):
    guid, dict = get_guid_dict()
    option_from_model['instrument'] = dict
    asset_code = option_from_model['moex_data']['secid']
    instrument_subscribe_json = get_json_to_instrument_subscribe(asset_code, guid)
    g_async_queue.put_nowait(instrument_subscribe_json)


def subscribe_to_option_quotes(option_from_model):
    guid, dict = get_guid_dict()
    option_from_model['quotes'] = dict
    asset_code = option_from_model['moex_data']['secid']
    quotes_subscribe_json = get_json_to_quotes_subscribe(asset_code, guid)
    g_async_queue.put_nowait(quotes_subscribe_json)


def subscribe_to_option_data(option_from_model):
    if 'quotes' not in option_from_model:
        subscribe_to_option_quotes(option_from_model)
    if 'instrument' not in option_from_model:
        subscribe_to_option_instrument(option_from_model)


def subscribe_to_options_data(list_of_strikes):
    for strike in list_of_strikes:
        call_option = g_model['options'][strike]['C']
        put_option = g_model['options'][strike]['P']
        subscribe_to_option_data(call_option)
        subscribe_to_option_data(put_option)


def handle_base_asset_data(data):
    last_price = data['last_price']
    central_strike = calculate_central_strike(last_price)
    list_of_strikes = get_list_of_strikes(central_strike)
    g_model['list_of_strikes'] = list_of_strikes
    subscribe_to_options_data(list_of_strikes)


def handle_alor_data(guid, data):
    g_guid_links[guid]['data'] = data
    base_asset_quotes_guid = g_model['base_asset']['quotes']['guid']
    if guid == base_asset_quotes_guid:
        handle_base_asset_data(data)


async def consumer(message):
    message_dict = json.loads(message)
    if 'data' in message_dict and 'guid' in message_dict:
        guid = message_dict['guid']
        data = message_dict['data']
        handle_alor_data(guid, data)


async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)


async def producer_handler(websocket):
    while True:
        message = await g_async_queue.get()
        await websocket.send(message)


async def handler(websocket):
    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


async def connect_to_alor_websocket():
    async with websockets.connect(ALOR_WS_URL) as websocket:
        await handler(websocket)


def get_json_to_quotes_subscribe(asset_code, guid):
    request_data = {
        "opcode": "QuotesSubscribe",
        "code": asset_code,
        "exchange": "MOEX",
        "guid": guid,
        "token": g_alor_auth['token']
    }
    return json.dumps(request_data)


def get_json_to_instrument_subscribe(asset_code, guid):
    request_data = {
        "opcode": "InstrumentsGetAndSubscribeV2",
        "code": asset_code,
        "exchange": "MOEX",
        "guid": guid,
        "token": g_alor_auth['token']
    }
    return json.dumps(request_data)


def main():
    g_model['options'] = get_options_from_moex()
    g_alor_auth['token'] = get_alor_authorization_token()

    base_asset_quotes_guid, base_asset_quotes_dict = get_guid_dict()
    g_model['base_asset']['quotes'] = base_asset_quotes_dict
    quotes_subscribe_to_base_asset_json = get_json_to_quotes_subscribe(BASE_ASSET_CODE, base_asset_quotes_guid)
    g_async_queue.put_nowait(quotes_subscribe_to_base_asset_json)

    asyncio.run(connect_to_alor_websocket(), debug=True)


def run_flask_app():
    # Enable pretty-printing for JSON responses
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    main()
