import requests
import json

def create_buy(access_token, emiten, price, lot):
    url = "https://ht2.ajaib.co.id/api/v1/stock/buy/"

    payload = json.dumps({
        "ticker_code": emiten,
        "price": price,
        "lot": lot,
        "board": "0RG",
        "period": "day"
    })

    headers = {
        'authority': 'ht2.ajaib.co.id',
        'accept': '*/*',
        'accept-language': 'id',
        'authorization': access_token,
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://invest.ajaib.co.id',
        'referer': 'https://invest.ajaib.co.id/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'x-ht-ver-id': '0322b9396fc0f476309aeafbbbe4e72d210e5c8f5815abf1fde7503b9126086e3e6d000a5f255765e8db3489c563a8fa950870c8920099ba073a08590d3da722',
        'x-platform': 'WEB',
        'x-product': 'stock-mf'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response

def create_sell(access_token, emiten, take_profit, lot, comparator):
    url = "https://ht2.ajaib.co.id/api/v1/stock/auto-trading/?account_type=REG"

    payload = json.dumps({
        "code": emiten,
        "side": "SELL",
        "criterion": "PRICE",
        "comparator": comparator,
        "value": take_profit,
        "order_price": take_profit,
        "lot": lot,
        "start_date": "2022-10-21",
        "end_date": "2022-10-28",
        "expiry": "day"
    })

    headers = {
        'authority': 'ht2.ajaib.co.id',
        'accept': '*/*',
        'accept-language': 'id',
        'authorization': access_token,
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://invest.ajaib.co.id',
        'referer': 'https://invest.ajaib.co.id/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'x-ht-ver-id': '0322b9396fc0f476309aeafbbbe4e72d210e5c8f5815abf1fde7503b9126086e3e6d000a5f255765e8db3489c563a8fa950870c8920099ba073a08590d3da722',
        'x-platform': 'WEB',
        'x-product': 'stock-mf'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response
