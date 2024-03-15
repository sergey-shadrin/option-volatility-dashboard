import json

from flask import Flask, jsonify, request
import threading

from view.option_data_request_params import OptionDataRequestParams


class FlaskApp:
    def __init__(self):
        self._option_app = None

    def set_option_app(self, option_app):
        self._option_app = option_app

    def start_app_in_thread(self):
        # Start Flask app in a separate thread
        flask_thread = threading.Thread(target=self._run_flask_app)
        flask_thread.daemon = True
        flask_thread.start()

    def dump_model(self):
        return jsonify(self._option_app.dump_model())

    def dump_watched_instruments(self):
        return jsonify(self._option_app.dump_watched_instruments())

    def get_diagram_data(self):
        request_params = OptionDataRequestParams()
        request_params.base_asset_ticker = 'SiM4'
        request_params.expiration_dates = ['2024-03-28', '2024-04-04']
        request_params.strikes_count = 11
        request_params.strikes_step = 1000
        result = self._option_app.get_option_diagram_data(request_params)

        return jsonify(result)

    def get_option_diagram_data(self):
        if request.method == 'POST':
            request_params_data = json.loads(request.form.get('request_params_json'))
            request_params = OptionDataRequestParams()
            request_params.base_asset_ticker = request_params_data['base_asset_ticker']
            request_params.expiration_dates = request_params_data['expiration_dates']
            request_params.strikes_count = request_params_data['strikes_count']
            request_params.strikes_step = request_params_data['strikes_step']

            result = self._option_app.get_option_diagram_data(request_params)
        else:
            result = {'error': 'Only POST requests are allowed.'}

        return jsonify(result)

    def _run_flask_app(self):
        app.run(host='0.0.0.0', port=5000)


app = Flask(__name__)
app.json_provider_class.compact = False

_flask_app = FlaskApp()


def get_flask_app():
    return _flask_app


@app.route('/dump_model', methods=['GET'])
def dump_model():
    return _flask_app.dump_model()


@app.route('/dump_watched_instruments', methods=['GET'])
def dump_watched_instruments():
    return _flask_app.dump_watched_instruments()


@app.route('/chart.json', methods=['GET'])
def get_diagram_data():
    return _flask_app.get_diagram_data()


@app.route('/option_diagram_data.json', methods=['POST'])
def option_diagram_data():
    return _flask_app.get_option_diagram_data()
