import concurrent.futures
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

LOG = []

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
    if res.status_code == 200:
        data = res.json()
        access_token = "jwt " + data["access_token"]

        msg = user["email"] + ": login OK"
        print(msg)
        LOG.append(msg)

        # porto = portfolio.call(access_token)
        # data_porto = porto.json()
        # trading_limit = data_porto["result"]["trading_limit"]
        trading_limit = 4_000_000
        amount = trading_limit / 4

        for obj in list_order:
            res = order.create_buy(access_token, obj.emiten, amount)
            if res.status_code == 200:
                msg = user["email"] + ": order buy Rp " + amount + " " + obj.emiten + " sent"
                print(msg)
                LOG.append(msg)
                print(res.json())
            else:
                msg = user["email"] + ": create order buy error: " + res.text
                LOG.append(msg)
        
        res = logout.call(access_token)
        if res.status_code == 200:
            msg = user["email"] + ": logout OK"
            LOG.append(msg)
        else:
            msg = user["email"] + ": logout error: " + res.text
            LOG.append(msg)
    else:
        msg = user["email"] + ": login error: " + res.text
        LOG.append(msg)


def sell(user, list_order):
    res = login.call(user)
    if res.status_code == 200:
        data = res.json()
        access_token = "jwt " + data["access_token"]

        msg = user["email"] + ": login OK"
        print(msg)
        LOG.append(msg)

        porto_res = portfolio.call(access_token)
        if porto_res.status_code == 200:
            porto_data = porto_res.json()
            porto_dicts = porto_data["result"]["portfolio"]
            
            for obj in list_order:
                emiten = obj.emiten
                tp = int(obj.take_profit)
                cl = int(obj.cut_loss)

                for dict in porto_dicts:
                    if dict["stock"] == emiten:
                        lot = dict["beglot"]
                        res = order.create_sell(access_token, emiten, tp, lot, "GTE")
                        if res.status_code == 200:
                            print(user["email"] + ": set TP" + emiten + " OK")
                            print(res.json())
                            LOG.append(user["email"] + ": buy " + lot + " lot " + emiten + " success!")

                            time.sleep(3)

                            res = order.create_sell(access_token, emiten, cl, lot, "LTE")
                            if res.status_code == 200:
                                print(user["email"] + ": set CL" + emiten + " OK")
                                print(res.json())
                            else:
                                msg = user["email"] + ": set CL error: " + res.text
                                LOG.append(msg)
                        else:
                            msg = user["email"] + ": set TP error: " + res.text
                            LOG.append(msg)
                    else:
                        LOG.append(user["email"] + ": buy " + lot + " lot " + emiten + " failed!")
            
            res = logout.call(access_token)
            if res.status_code == 200:
                msg = user["email"] + ": logout OK"
                LOG.append(msg)
            else:
                msg = user["email"] + ": logout error: " + res.text
                LOG.append(msg)
        else:
            msg = user["email"] + ": get portfolio error: " + res.text
            LOG.append(msg)
    else:
        msg = user["email"] + ": login error: " + res.text
        LOG.append(msg)

def async_buy(list_order, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(buy, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                if future.done():
                    if future.result() == None:
                        print(user["email"] + ": RESULT OK")
                    else:
                        print(user["email"] + ": RESULT ERROR")
                        print(future.result())
                else:
                    print(user["email"] + ": process async buy order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)

def async_sell(list_order, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(sell, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                if future.done():
                    print(user["email"] + ": process async sell order completed!")
                    if future.result() == None:
                        print("RESULT: OK")
                    else:
                        print("RESULT: FAILED")
                        print(future.result())
                else:
                    print(user["email"] + ": process async sell order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)

def send_log(bot, chat_id, log):
    bot.send_message(chat_id=chat_id, text=join_msg(log))

def join_msg(list):
    if list:
        return '\n'.join(list)
    else:
        return "Message is empty"

def send_msg_v2(bot, chat_ids, msg):
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)

def error_log(bot, chat_id):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    error_msg = traceback.format_exc()
    logger.debug(error_msg)
    # bot.send_message(chat_id=chat_id, text=error_msg)
