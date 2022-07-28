if __name__ == '__main__':
    import undetected_chromedriver as uc
    import csv
    import telegram
    import time
    import os
    import order
    from dotenv import load_dotenv

    def is_empty_csv(path):
        with open(path) as csvfile:
            reader = csv.reader(csvfile)
            for i, _ in enumerate(reader):
                if i:  # found the second row
                    return False
        return True

    try:
        load_dotenv()

        print("Performing WINA...")
    
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        TELEGRAM_CHAT_IDS = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
        TELEGRAM_LOGGER_ID = os.getenv('TELEGRAM_LOGGER_ID')

        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

        # Define object
        class data():
            def __init__(self, emiten, take_profit, cut_loss):
                self.emiten = emiten
                self.take_profit = take_profit
                self.cut_loss = cut_loss

        list = []
        path = r"C:\Users\Superadmin\Desktop\GamaTradingSystem\WINAReport.csv"

        with open(path, "r") as file:
            csvreader = csv.reader(file)
            if is_empty_csv(path) == False:
                next(csvreader, None)

                # Init auto order
                options = uc.ChromeOptions()
                options.headless=True
                options.add_argument('--headless')
                driver = uc.Chrome(options=options)

                order.delete_cache(driver)
                order.login(driver)

                for row in csvreader:
                    emiten = row[0].replace(".JK", "")
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

                    time.sleep(3)

                    # Send buy order to sekuritas
                    order.create_buy_order(driver, emiten, buy_price)

                print('Wait 1 hour to create auto order')

                time.sleep(3600)

                # Create auto order
                for obj in list:
                    order.create_auto_order(driver, obj.emiten, obj.take_profit, obj.cut_loss)
            else: 
                msg = "Sorry, no signal for today."
                bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=msg)
                for chat_id in TELEGRAM_CHAT_IDS:
                        bot.send_message(chat_id=chat_id, text=msg)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=TELEGRAM_LOGGER_ID, text=str(e))

    print("Done.")

