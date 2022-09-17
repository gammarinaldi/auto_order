import csv
import telegram
import time
import os
import logging
import traceback
import lib
from dotenv import load_dotenv

if __name__ == '__main__':
    # Load config env
    load_dotenv()

    # Define telegram bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_IDS = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
    TELEGRAM_LOGGER_ID = os.getenv('TELEGRAM_LOGGER_ID')
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

    list_order = []
    path = lib.get_analysis_report()

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
                    lib.send_signal(TELEGRAM_CHAT_IDS, msg, bot)

                    # Input order parameters for auto order
                    list_order.append(lib.data_order(emiten, buy_price, take_profit, cut_loss))

                t1 = time.time()

                # Send async buy order to sekuritas
                lib.async_buy(list_order)

                t2 = time.time()
                diff = t2 -t1
                print("Processing buy order takes: " + str(round(diff, 2)) + " secs.")

                print('Wait 1 hour to create auto sell order')
                time.sleep(3600)

                t1 = time.time()

                # Send async auto sell order to sekuritas
                lib.async_sell(list_order)

                t2 = time.time()
                diff = t2 -t1
                print("Processing buy order takes: " + str(round(diff, 2)) + " secs.")
            else: 
                msg = "Sorry, no signal for today."
                bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=msg)
                for chat_id in TELEGRAM_CHAT_IDS:
                    bot.send_message(chat_id=chat_id, text=msg)
    except Exception as error:
        # Define logger
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        error_msg = traceback.format_exc()
        logger.debug(error_msg)
        bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=error_msg)

    print("Done.")

