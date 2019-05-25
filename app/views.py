from .app import app, render_template, jsonify, request
from .visualize import generate_plotly_url
from .predictions import minute_price_historical, conv_for_server


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_status/<string:algorithm>')
def get_status(algorithm):
    if algorithm == 'ema':
        with open('ema.txt', 'r+') as ema_f:
            status = ema_f.read()
    else:
        with open('rsi.txt', 'r+') as rsi_f:
            status = rsi_f.read()
    return jsonify({'state': status}), 200


@app.route('/get_data/<string:crypto>')
def get_data(crypto):
    if crypto == 'etc':
        lst = conv_for_server(minute_price_historical('ETH', 'USD', 10, 1, ['Coinbase']))
        return jsonify({"data": lst})
    lst = conv_for_server(minute_price_historical('BTC', 'USD', 30, 1, ['Coinbase']))
    return jsonify({"data": lst})


@app.route('/change_status', methods=['POST'])
def change_status():
    global state
    json = request.json
    if json:
        state = json['state']
    return 'OK'
