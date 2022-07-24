if __name__ == '__main__':
    import undetected_chromedriver as uc
    import csv
    import telegram
    import time
    from order import *
    from dotenv import load_dotenv

    load_dotenv()

    print("Sending WINA to telegram...")

    try:
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        TELEGRAM_CHAT_IDS = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
        TELEGRAM_LOGGER_ID = os.getenv('TELEGRAM_LOGGER_ID')

        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

        # Define object
        class data():
            def __init__(self):
                self.emiten = emiten
                self.take_profit = take_profit
                self.cut_loss = cut_loss

        list = []

        # Init auto order
        driver = uc.Chrome()
        delete_cache(driver)
        login(driver)

        with open("WINAReport.csv", "r") as file:
            csvreader = csv.reader(file)
            next(csvreader, None)

            for row in csvreader:
                emiten = row[0]
                signal_date = row[1].split(" ")[0]
                close = row[2]
                change = row[3]
                trx = row[4]
                buy_price = row[5]
                take_profit = row[6]
                cut_loss = row[7]
                
                msg = "💌 Rekomendasi WINA \(" + signal_date + "\)\n\n*Buy $" + emiten + "\nBuy @" + buy_price + "\nTake Profit @" + take_profit + "\nCutloss @" + cut_loss + "*\n\n_Disclaimer ON\. DYOR\._"

                for chat_id in TELEGRAM_CHAT_IDS:
                    bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)

                # Input data for auto order
                list.append(data(emiten, take_profit, cut_loss))

                # Send buy order to sekuritas
                create_buy_order(driver, emiten, buy_price)

        # Wait 1 hour
        time.sleep(5)

        print('Wait 1 hour to create auto order')
        # Create auto order
        for obj in list:
            create_auto_order(driver, obj.emiten, obj.take_profit, obj.cut_loss)

    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=e)

    print("Done.")

