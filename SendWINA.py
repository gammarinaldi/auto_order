import csv
import telegram
import time
import lib
import os
from dotenv import load_dotenv

if __name__ == '__main__':
    # Define telegram bot
    tele_bot_token, tele_chat_ids, tele_log_id = lib.get_tele_data()
    bot = telegram.Bot(token=tele_bot_token)

    list_order = []
    path = lib.analysis_path()

    load_dotenv()
    enable_signal = os.getenv('ENABLE_SIGNAL')
    enable_buy = os.getenv('ENABLE_BUY')
    enable_sell = os.getenv('ENABLE_SELL')

    try:
        print("Performing WINA...\n")

        with open(path, "r") as file:
            csvreader = csv.reader(file)
            if lib.is_empty_csv(path) == False:
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
                    if enable_signal == "1":
                        lib.send_msg_v2(bot, tele_chat_ids, msg)

                    # Input order parameters for auto order
                    list_order.append(lib.data_order(emiten, buy_price, take_profit, cut_loss))

                # Perform auto order buy
                if enable_buy == "1":
                    t1 = time.time()

                    # Async buy
                    lib.async_order("buy", list_order, bot)

                    t2 = time.time()
                    diff = t2 -t1
                    print("Processing auto-buy order takes: " + str(round(diff, 2)) + " secs.")
                    lib.send_log(bot, tele_log_id, lib.LOG)
                    lib.LOG = []

                # Perform auto order sell
                if enable_sell == "1":
                    print('Wait 1 hour to create auto sell order')
                    time.sleep(3600)

                    t1 = time.time()

                    # Async sell
                    lib.async_order("sell", list_order, bot)

                    t2 = time.time()
                    diff = t2 -t1
                    print("Processing auto-sell order takes: " + str(round(diff, 2)) + " secs.")
                    lib.send_log(bot, tele_log_id, lib.LOG)
            else: 
                msg = "Sorry, no signal for today."
                lib.send_msg_v2(bot, tele_chat_ids, msg)
    except Exception as error:
        print(error)
        lib.error_log(bot, tele_log_id)

    print("Done.")

