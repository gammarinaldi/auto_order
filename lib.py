from types import NoneType
import undetected_chromedriver as uc
import concurrent.futures
import threading
import json
import csv
import telegram
import logging
import traceback
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

LIST = []

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

def get_driver():
    threadLocal = threading.local()
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        options = uc.ChromeOptions()
        options.headless=True
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        setattr(threadLocal, 'driver', driver)
    return driver

def buy(user, list_order):
    driver = get_driver()
    order.login(user, driver)
    
    for obj in list_order:
        res = order.create_buy_order(user, driver, obj.emiten, obj.buy_price)
        LIST.append(res)

    order.logout(user, driver)
    order.delete_cache(user, driver)

def sell(user, list_order):
    driver = get_driver()
    order.login(user, driver)   

    for obj in list_order:
        res = order.create_sell_order(user, driver, obj.emiten, obj.take_profit, obj.cut_loss)
        LIST.append(res)

    order.logout(user, driver)
    order.delete_cache(user, driver)

def async_buy(list_order, chat_ids, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(buy, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                if future.done():
                    print(user["email"] + ": process async buy order completed!")
                    
                    if future.result() == NoneType:
                        print("RESULT:")
                        print(future.result())
                    else:
                        print("FAILED RESULT")
                else:
                    print(user["email"] + ": process async buy order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)
    send_result(bot, chat_ids)

def async_sell(list_order, chat_ids, bot):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(sell, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            # future.result()
            user = future_to_user[future]
            try:
                if future.done():
                    print(user["email"] + ": process async sell order completed!")
                else:
                    print(user["email"] + ": process async sell order failed!")
            except Exception:
                _, _, tele_log_id = get_tele_data()
                error_log(bot, tele_log_id)
    send_result(bot, chat_ids)

def send_result(bot, chat_ids):
    send_msg(bot, chat_ids, join_msg(LIST))

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

def join_msg(list):
    return '\n'.join(list[0])