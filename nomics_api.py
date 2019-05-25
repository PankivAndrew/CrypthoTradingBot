import requests
url = "https://api.nomics.com/v1/currencies?key=f4b956d31db28555b9d720edaaa78c12&exchange=binance&base=BTC,ETH,LTC,XMR&quote=BTC,ETH,BNB"
data = requests.get(url)

print(data.text)