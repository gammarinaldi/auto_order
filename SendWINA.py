from pickle import FALSE
import undetected_chromedriver as uc
import csv
import telegram
import time
import os
import order
import concurrent.futures
import threading
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

if __name__ == '__main__':
    try:
        def get_user_data():
            f = open('auto_order\data.json')
            users = json.load(f)
            f.close()
            return users

        USERS = get_user_data()
        
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
                future_to_user = {executor.submit(buy, user, list_order): user for user in USERS}
                for future in concurrent.futures.as_completed(future_to_user):
                    user = future_to_user[future]
                    try:
                        future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (user["email"], exc))

        def async_sell(list_order):
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_user = {executor.submit(sell, user, list_order): user for user in USERS}
                for future in concurrent.futures.as_completed(future_to_user):
                    user = future_to_user[future]
                    try:
                        future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (user["email"], exc))

        def send_signal(chat_ids, msg):
            for chat_id in chat_ids:
                bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)
        
        print("Performing WINA...\n")

        # Load config env
        load_dotenv()

        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        TELEGRAM_CHAT_IDS = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
        TELEGRAM_LOGGER_ID = os.getenv('TELEGRAM_LOGGER_ID')
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

        list_order = []
        path = r"C:\Users\Gama\Downloads\GamaTradingSystem\WINAReport.csv"

        with open(path, "r") as file:
            csvreader = csv.reader(file)
            if is_empty_csv(path) == False:
                next(csvreader, None)

                for row in csvreader:
                    emiten = row[0]
                    if row[0].find(".JK") != -1:
                        emiten = emiten.replace(".JK", "")
                    signal_date = row[1].split(" ")[0]
                    # close = row[2]
                    # change = row[3]
                    # trx = row[4]
                    buy_price = row[5]
                    take_profit = row[6]
                    cut_loss = row[7]
                    
                    msg = "💌 Rekomendasi WINA \(" + signal_date + "\)\n\n*Buy $" + emiten + "\nBuy @" + buy_price + "\nTake Profit @" + take_profit + "\nCutloss @" + cut_loss + "*\n\n_Disclaimer ON\. DYOR\._"

                    # Send signal to telegram
                    # send_signal(TELEGRAM_CHAT_IDS, msg)

                    # Input order parameters for auto order
                    list_order.append(data_order(emiten, buy_price, take_profit, cut_loss))

                t1 = time.time()

                # Send async buy order to sekuritas
                async_buy(list_order)

                t2 = time.time()
                diff = t2 -t1
                print("Processing buy order takes: " + str(round(diff, 2)) + " secs.")

                print('Wait 1 hour to create auto sell order')
                time.sleep(5)

                t1 = time.time()

                # Send async auto sell order to sekuritas
                async_sell(list_order)

                t2 = time.time()
                diff = t2 -t1
                print("Processing buy order takes: " + str(round(diff, 2)) + " secs.")
            else: 
                msg = "Sorry, no signal for today."
                bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=msg)
                for chat_id in TELEGRAM_CHAT_IDS:
                        bot.send_message(chat_id=chat_id, text=msg)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=str(e))

    print("Done.")

