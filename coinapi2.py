import requests
from datetime import datetime, timedelta

def get_json(GET, endpoint='https://rest.coinapi.io', headers={'X-CoinAPI-Key': '<YOUR_API_KEY>'}):
	# Gets the json-formatted output of the passed 'GET' query (relative to the endpoint).
	url = endpoint + GET
	response = requests.get(url, headers=headers)
	json = response.json()
	return json

def get_exchanges(json):
	# Returns a list of all the exchanges that coinapi can collect data from.
	exchanges = []
	for i in json:
		if i['exchange_id'] not in exchanges:
			exchanges.append(i['exchange_id'])
			exchanges.sort()
	return exchanges

def exch_history(symbols, exchange, start, end, period='5MIN'):
	#returns a history of the exchange as a JSON object with attributes 'exchange' and 'data'. 'data' is a list of intervals.
	#'start' and 'end' are datetime objects.
	# period can equal '5MIN', '30SEC', '1HR', ... some values work and some don't. There's a complete list on coinapi.com
	start_str = start.replace(microsecond=0).isoformat()
	end_str = end.replace(microsecond=0).isoformat()
	exch_hist_obj = {}
	exch_hist_obj['exchange'] = exchange
	symbol_hist_objs = {}
	for i in symbols:
		if i['exchange_id'] == exchange:
			i_symbol_id = i['symbol_id']
			GET = '/v1/ohlcv/' + i_symbol_id +\
					'/history?period_id=' + period + '&' +\
					'time_start=' + start + '&' +\
					'time_end=' + end
			#The following line fetches the data for the symbol with oldest sample first.
			i_symbol_samples_list = get_json(GET) # This is a list of samples from i_symbol_id.
			i_symbol_hist_obj = dict(symbol_id=i_symbol_id, samples=i_symbol_samples_list)
			symbol_hist_objs[i_symbol_id] = i_symbol_hist_obj
	exch_hist_obj['data'] = exch_symbol_hist_objs
	return json.dumps(exch_hist_obj)

def week_history(exchange, period='5MIN'):
	# Merely a specification of exch_history with:
	symbols = get_json('/v1/symbols')
	start = datetime.now()
	end = datetime.now() - timedelta(days=7)
	return exch_history(symbols, exchange, start, end, period)

def full_week():
	# Returns a week's worth of intervals from all exchanges and all symbols.
	# This function uses WAY too many API calls for use on an unpaid access plan.
	exch_hist_objs = {}
	symbols = get_json('/v1/symbols')
	exchanges = get_exchanges(symbols)
	for exchange in exchanges:
		exch_hist_objs[exchange] = week_history(symbols, exchange)
	return json.dumps(exch__hist_objs)

def multigraph(symbol_id):
	# Returns a multigraph indexed by chronological order of the intervals in a symbol's week's history on exchange 'BINANCE'.
	# Each of the values associated with an interval should be a statistic of values from within the datset (at least to start).
	# A multigraph can be used to detect events within the data.
	# Events can be examined for variable-term correlation with the stock's price.
	# Successful events can be selected and emoloyed within strategies to make money against the market.
	mg = []
	symbol_samples = week_history('BINANCE')['data'][symbol_id]['samples']
	for sample in symbol_samples: # a symbol_history object:
		# Extract primitive statistics.
		price_open = sample['price_open']
		price_close = sample['price_close']
		price_high = sample['price_high']
		price_low = sample['price_low']
		volume_traded = sample['volume_traded']
		trades_count = sample['trades_count']
		# Develop new statistics.
		price_middle = (price_high + price_low) / 2
		trade_weight = volume_traded / trades_count
		mg.append([index, price_middle, trade_weight])
		index += 1
	mg = sorted(mg)
	return mg

binance_hist_obj = week_history(symbols, 'BINANCE')
