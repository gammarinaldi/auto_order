import concurrent.futures
from math import floor
import login
import logout
import order
import portfolio
import json
import csv
import telegram
import logging
import traceback
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

def users_path():
    return r"C:\Users\Gama\Downloads\GamaTradingSystem\auto_order\data.json"

def analysis_path():
    return r"C:\Users\Gama\Downloads\GamaTradingSystem\WINAReport.csv"

def get_user_data():
    f = open(users_path())
    users = json.load(f)
    f.close()
    return users

def get_tele_data():
    load_dotenv()
    tele_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tele_chat_ids = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
    tele_log_id = os.getenv('TELEGRAM_LOGGER_ID')

    return tele_bot_token, tele_chat_ids, tele_log_id

def is_empty_csv(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for i, _ in enumerate(reader):
            if i:  # Found the second row
                return False
    return True

class data_order():
    def __init__(self, emiten, buy_price, take_profit, cut_loss):
        self.emiten = emiten
        self.buy_price = buy_price
        self.take_profit = take_profit
        self.cut_loss = cut_loss

def buy(user, list_order):
    res = login.call(user)
    data = res.json()
    print(user["email"] + ": login")
    print(data)
    access_token = "jwt " + data["access_token"]
    # porto = portfolio.call(access_token)
    # data_porto = porto.json()
    # trading_limit = data_porto["result"]["trading_limit"]
    trading_limit = 4_000_000

    for obj in list_order:
        allocated_amount = trading_limit / 4
        lot = floor(( allocated_amount / float(obj.buy_price)) / 100)
        res = order.create_buy(access_token, obj.emiten, obj.buy_price, lot)
        print(user["email"] + ":buy " + obj.emiten)
        print(res.json())
    
    res = logout.call(access_token)
    print(user["email"] + ": logout")
    print(res.json())

def sell(user, list_order):
    res = login.call(user)
    data = res.json()
    access_token = "jwt " + data["access_token"]
    porto = portfolio.call(access_token)
    porto_data = porto.json()
    porto_dicts = porto_data["result"]["portfolio"]
    
    for obj in list_order:
        emiten = obj.emiten
        tp = int(obj.take_profit)
        cl = int(obj.cut_loss)

        for dict in porto_dicts:
            if dict["stock"] == emiten:
                order.create_sell(access_token, emiten, tp, cl, dict["beglot"], "GTE")
                time.sleep(3)
                order.create_sell(access_token, emiten, tp, cl, dict["beglot"], "LTE")
    
    logout.call(access_token)

def async_buy(list_order, chat_ids, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(buy, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                if future.done():
                    print(user["email"] + ": process async buy order completed!")
                    if future.result() == None:
                        print("RESULT OK")
                    else:
                        print("FAILED RESULT")
                        print(future.result())
                else:
                    print(user["email"] + ": process async buy order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)

def async_sell(list_order, chat_ids, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(sell, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            # future.result()
            user = future_to_user[future]
            try:
                if future.done():
                    print(user["email"] + ": process async sell order completed!")
                    if future.result() == None:
                        print("RESULT OK")
                    else:
                        print("FAILED RESULT")
                        print(future.result())
                else:
                    print(user["email"] + ": process async sell order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)

def send_msg(bot, chat_ids, msg):
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=msg)

def send_msg_v2(bot, chat_ids, msg):
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)

def error_log(bot, chat_id):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    error_msg = traceback.format_exc()
    logger.debug(error_msg)
    send_log(bot, chat_id, error_msg)

def send_log(bot, chat_id, msg):
    bot.send_message(chat_id=chat_id, text=msg)
