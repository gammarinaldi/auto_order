if __name__ == '__main__':
    import undetected_chromedriver as uc
    import csv
    import telegram
    import time
    import os
    import order
    import math
    from dotenv import load_dotenv
    from selenium.webdriver.common.by import By

    print("Performing WINA...")

    try:
        def is_empty_csv(path):
            with open(path) as csvfile:
                reader = csv.reader(csvfile)
                for i, _ in enumerate(reader):
                    if i:  # Found the second row
                        return False
            return True

        def filter_non_digits(string: str) -> str:
            result = ''
            for char in string:
                if char in '1234567890':
                    result += char
            return int(result) 

        # Define object
        class data():
            def __init__(self, emiten, buy_price, take_profit, cut_loss):
                self.emiten = emiten
                self.buy_price = buy_price
                self.take_profit = take_profit
                self.cut_loss = cut_loss

        load_dotenv()
    
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        TELEGRAM_CHAT_IDS = [os.getenv('TELEGRAM_CHAT_ID_WINA'), os.getenv('TELEGRAM_CHAT_ID_SINYALA')]
        TELEGRAM_LOGGER_ID = os.getenv('TELEGRAM_LOGGER_ID')
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

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
                    list.append(data(emiten, buy_price, take_profit, cut_loss))

                # Length of list
                list_len = len(list)

                # Get buying power
                buy_power_str = driver.find_element(By.XPATH, '//span[text()="Regular Buying Power"]/following::span').text
                buy_power_num = filter_non_digits(buy_power_str)
                buy_power = buy_power_num / len(list)

                # Send buy order to sekuritas
                for obj in list:
                    order.create_buy_order(driver, obj.emiten, obj.buy_price, math.floor(buy_power))

                print('Wait 1 hour to create auto order')
                time.sleep(3600)

                # Send auto sell order to sekuritas
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

