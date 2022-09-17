import undetected_chromedriver as uc
import order
import concurrent.futures
import threading
import json
import csv
import telegram
from concurrent.futures import ThreadPoolExecutor

def get_data_path():
    return r"C:\Users\Gama\Downloads\GamaTradingSystem\auto_order\data.json"

def get_analysis_report():
    return r"C:\Users\Gama\Downloads\GamaTradingSystem\WINAReport.csv"

def get_user_data():
    f = open(get_data_path())
    users = json.load(f)
    f.close()
    return users

# Check csv content
def is_empty_csv(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for i, _ in enumerate(reader):
            if i:  # Found the second row
                return False
    return True

# Define data order params
class data_order():
    def __init__(self, emiten, buy_price, take_profit, cut_loss):
        self.emiten = emiten
        self.buy_price = buy_price
        self.take_profit = take_profit
        self.cut_loss = cut_loss

# Get web driver
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
    print(driver)
    order.login(user, driver)   

    for obj in list_order:
        order.create_buy_order(user, driver, obj.emiten, obj.buy_price)

    order.logout(user, driver)
    order.delete_cache(user, driver)

def sell(user, list_order):
    driver = get_driver()
    print(driver)
    order.login(user, driver)   

    for obj in list_order:
        order.create_sell_order(user, driver, obj.emiten, obj.take_profit, obj.cut_loss)

    order.logout(user, driver)
    order.delete_cache(user, driver)

def async_buy(list_order):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(buy, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (user["email"], exc))

def async_sell(list_order):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(sell, user, list_order): user for user in get_user_data()}
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (user["email"], exc))

def send_signal(chat_ids, msg, bot):
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)