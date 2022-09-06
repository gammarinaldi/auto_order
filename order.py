import os
import time
import math
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from datetime import date, timedelta
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = os.getenv('LOGIN_URL')
LOGOUT_URL = os.getenv('LOGOUT_URL')
HOMEPAGE_URL = os.getenv('HOMEPAGE_URL')

# TODO: login data encryption

DELAY = 10 # seconds

def login(user, driver):
    user_email = user["email"]
    user_pass = user["password"]
    user_pin = user["pin"]

    # Input login
    driver.get(LOGIN_URL + '/login')

    email = driver.find_element(By.XPATH, '//input[@name="email"]')
    email.send_keys(user_email)

    password = driver.find_element(By.XPATH, '//input[@name="password"]')
    password.send_keys(user_pass)
    password.send_keys(Keys.RETURN)

    print(user_email + ": input login")

    # Input PIN
    pins = []
    for pin in user_pin:
        pins.append(pin)

    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//input[@class="pincode-input-text"]')))
        print(user_email + ": input PIN")

        pin1 = driver.find_element(By.XPATH, '//input[@class="pincode-input-text"]')
        pin1.send_keys(pins[0])

        pin2 = driver.find_element(By.XPATH, '//input[@class="pincode-input-text"]/following::input')
        pin2.send_keys(pins[1])

        pin3 = driver.find_element(By.XPATH, '//input[@class="pincode-input-text"]/following::input/following::input')
        pin3.send_keys(pins[2])

        pin4 = driver.find_element(By.XPATH, '//input[@class="pincode-input-text"]/following::input/following::input/following::input')
        pin4.send_keys(pins[3])
    except TimeoutException:
        print(user_email + ": input PIN failed!")

    time.sleep(3)

def logout(user, driver):
    print(user["email"] + ": logout")
    driver.get(LOGOUT_URL)

def open_emiten_page(user_email, driver, emiten):
    time.sleep(3)
    print(user_email + ": open emiten page => " + emiten)
    driver.get(HOMEPAGE_URL + emiten)
    time.sleep(3)

def filter_non_digits(string: str) -> str:
    result = ''
    for char in string:
        if char in '1234567890':
            result += char
    return int(result) 

def get_buying_power(driver):
    # Get buying power
    # buy_power_str = driver.find_element(By.XPATH, '//span[text()="Regular Buying Power"]/following::span').text
    # buy_power_num = filter_non_digits(buy_power_str)
    buy_power_num = 20_000_000
    return math.floor(buy_power_num / 4)

def create_buy_order(user, driver, emiten, buy_price):
    user_email = user["email"]

    # Open emiten page
    open_emiten_page(user_email, driver, emiten)

    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="btnBuy"]')))
        print(user_email + ": button beli")

        time.sleep(3)

        # Click Beli button
        driver.find_element(By.XPATH, '//button[@data-testid="btnBuy"]').click()
        
        # Input price
        try:
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="btnBuy"]')))
            print(user_email + ": input harga")
            input_price = driver.find_element(By.XPATH, '//input[@id="INPUT_BUY_PRICE"]')
            input_price.send_keys(Keys.CONTROL + "A")
            input_price.send_keys(Keys.DELETE)
            input_price.send_keys(buy_price)

            # Calculate position size (Lot)
            buy_power = get_buying_power(driver)
            buy_lot = buy_power / (int(buy_price) * 100)
            input_lot = driver.find_element(By.XPATH, '//*[@id="INPUT_BUY_LOT"]')
            input_lot.send_keys(Keys.CONTROL + "A")
            input_lot.send_keys(Keys.DELETE)
            input_lot.send_keys(math.floor(buy_lot))

            print(user_email + ": buying power => " + str(buy_power))
            print(user_email + ": buy lot => " + str(buy_lot))

            buy_btn = driver.find_element(By.XPATH, '//button[@data-testid="btnPopupBuy"]').is_enabled()
            if buy_btn:
                # Click button Beli
                driver.find_element(By.XPATH, '//button[@data-testid="btnPopupBuy"]').click()

                # Click button Konfirmasi Beli
                try:
                    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="btnConfirmBuy"]')))
                    print(user_email + ": konfirmasi beli")

                    time.sleep(3)

                    driver.find_element(By.XPATH, '//button[@data-testid="btnConfirmBuy"]').click()
                    print(user_email + ": buying " + emiten + " SUCCESS!")
                except TimeoutException:
                    print(user_email + ": button konfirmasi beli does not exist!")
        except TimeoutException:
            print(user_email + ": input harga does not exist!")
            create_buy_order(user, driver, emiten, buy_price)
    except TimeoutException:
        print(user_email + ": button beli does not exist!")
        create_buy_order(user, driver, emiten, buy_price)

    time.sleep(3)

def create_sell_order(user, driver, emiten, take_profit, cut_loss):
    user_email = user["email"]
    create_take_profit(user_email, driver, emiten, take_profit)
    time.sleep(5)
    create_cut_loss(user_email, driver, emiten, cut_loss)

def create_take_profit(user_email, driver, emiten, take_profit):
    print(user_email + ": start create take profit")

    # Open emiten page
    open_emiten_page(user_email, driver, emiten)

    # Check jual button
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="btnSell"]')))
        print(user_email + ": button jual")

        time.sleep(3)

        driver.find_element(By.XPATH, '//*[@data-testid="btnSell"]').click()

        # Select order type
        select_auto_order_type(user_email, driver)

        # Input expiry date
        calculate_expiry_date(user_email, driver)

        # Click take profit
        driver.find_element(By.XPATH, '//div[@class="pl-4 pr-4 col-md-3"]').click()

        # Input trigger price
        take_profit_field = driver.find_element(By.XPATH, '//div[@class="pl-4 col-md-6"]//input')
        take_profit_field.send_keys(Keys.CONTROL + "a")
        take_profit_field.send_keys(Keys.DELETE)
        take_profit_field.send_keys(take_profit)

        # Input sell price (TP)
        sell_price = driver.find_element(By.XPATH, '//*[@id="INPUT_SELL_PRICE"]')
        sell_price.send_keys(Keys.CONTROL + "a")
        sell_price.send_keys(Keys.DELETE)
        sell_price.send_keys(take_profit)

        # Get available lot
        lot = driver.find_element(By.XPATH, '//span[text()="Lot Yang Dimiliki"]/following::span').text

        # Input lot to order
        sell_lot = driver.find_element(By.XPATH, '//*[@id="INPUT_SELL_LOT"]')
        sell_lot.send_keys(Keys.CONTROL + "a")
        sell_lot.send_keys(Keys.DELETE)
        sell_lot.send_keys(lot)
        
        send_auto_order(user_email, driver)
    except TimeoutException:
        print(user_email + ": retrying button jual...")
        create_take_profit(user_email, driver, emiten, take_profit)

def create_cut_loss(user_email, driver, emiten, cut_loss):
    print(user_email + ": start create cut loss")

    # Open emiten page
    open_emiten_page(user_email, driver, emiten)

    # Check jual button
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnSell"]')))
        print(user_email + ": button jual")

        time.sleep(3)

        driver.find_element(By.XPATH, '//*[@data-testid="btnSell"]').click()

        # Select auto order type
        select_auto_order_type(user_email, driver)

        # Input expiry date
        calculate_expiry_date(user_email, driver)

        # Click cut loss
        driver.find_element(By.XPATH, '//div[@class="pl-0 pr-8 col-md-3"]').click()

        # Input trigger price
        cut_loss_field = driver.find_element(By.XPATH, '//div[@class="pl-4 col-md-6"]//input')
        cut_loss_field.send_keys(Keys.CONTROL + "a")
        cut_loss_field.send_keys(Keys.DELETE)
        cut_loss_field.send_keys(cut_loss)

        # Input sell price (CL)
        sell_price = driver.find_element(By.XPATH, '//*[@id="INPUT_SELL_PRICE"]')
        sell_price.send_keys(Keys.CONTROL + "a")
        sell_price.send_keys(Keys.DELETE)
        sell_price.send_keys(cut_loss)

        # Get available lot
        lot = driver.find_element(By.XPATH, '//span[text()="Lot Yang Dimiliki"]/following::span').text

        # Input lot to order
        sell_lot = driver.find_element(By.XPATH, '//*[@id="INPUT_SELL_LOT"]')
        sell_lot.send_keys(Keys.CONTROL + "a")
        sell_lot.send_keys(Keys.DELETE)
        sell_lot.send_keys(lot)

        send_auto_order(user_email, driver)
    except TimeoutException:
        print(user_email + ": retrying button jual...")
        create_cut_loss(user_email, driver, emiten, cut_loss)

def select_auto_order_type(user_email, driver):
    # Pick order type
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="periodType"]')))
        print(user_email + ": pilih tipe order")
        driver.find_element(By.XPATH, '//*[@id="periodType"]').click()
        driver.find_element(By.XPATH, '//*[@data-testid="opt-periodType-1"]').click()
    except TimeoutException:
        print(user_email + ": pilih tipe order does not exist!")

def calculate_expiry_date(user_email, driver):
    # Calculate expiry date
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=30)

    start_m = str(int(start.strftime('%#m')) - 1)
    start_y = start.strftime('%Y')
    start_d = start.strftime('%#d')

    end_m = str(int(end.strftime('%#m')) - 1)
    end_y = end.strftime('%Y')
    end_d = end.strftime('%#d')

    # Input expiry start date
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//div[@class="react-datepicker__input-container"]//input')))
        print(user_email + ": start date picker")

        # Click start date picker 
        driver.find_element(By.XPATH, '//div[@class="react-datepicker__input-container"]//input').click()

        # Select start month
        select_start_month = Select(driver.find_element(By.XPATH, '//select[@class="react-datepicker__month-select"]'))
        select_start_month.select_by_value(start_m)

        # Select start year
        select_start_year = Select(driver.find_element(By.XPATH, '//select[@class="react-datepicker__year-select"]'))
        select_start_year.select_by_value(start_y)

        # Click start date
        driver.find_element(By.XPATH, "//div[text()='" + start_d + "'][@aria-disabled='false']").click()
    except TimeoutException:
        print(user_email + ": start date picker does not exist!")

    # Input expiry end date
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//div[@class="react-datepicker__input-container"]//following::div[@class="react-datepicker__input-container"]')))
        print(user_email + ": end date picker")

        # Click end date picker 
        driver.find_element(By.XPATH, '//div[@class="react-datepicker__input-container"]//following::div[@class="react-datepicker__input-container"]').click()

        # Select end month
        select_end_month = Select(driver.find_element(By.XPATH, '//select[@class="react-datepicker__month-select"]'))
        select_end_month.select_by_value(end_m)

        # Select end year
        select_end_year = Select(driver.find_element(By.XPATH, '//select[@class="react-datepicker__year-select"]'))
        select_end_year.select_by_value(end_y)

        # Click end date
        driver.find_element(By.XPATH, "//div[text()='" + end_d + "'][@aria-disabled='false']").click()
    except TimeoutException:
        print(user_email + ": end date picker does not exist!")

def send_auto_order(user_email, driver):
    # Click aktifkan auto order
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnPopupSell"]')))
        print(user_email + ": aktifkan auto order take profit")

        time.sleep(3)

        driver.find_element(By.XPATH, '//*[@data-testid="btnPopupSell"]').click()
    except TimeoutException:
        print(user_email + ": aktifkan auto order take profit does not exist!")

    # Click konfirmasi auto order
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnConfirmSell"]')))
        print(user_email + ": konfirmasi auto order take profit")

        time.sleep(3)
        
        driver.find_element(By.XPATH, '//*[@data-testid="btnConfirmSell"]').click()
    except TimeoutException:
        print(user_email + ": konfirmasi auto order take profit does not exist!")

# Delete chrome cache
def delete_cache(user, driver):
    print(user["email"] + ": delete cache!")

    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.

    perform_delete_cache(driver, Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 5 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

def perform_delete_cache(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)
    time.sleep(2)
    actions.perform()

def filter_non_digits(string: str) -> str:
    result = ''
    for char in string:
        if char in '1234567890':
            result += char
    return int(result) 

# For testing
# if __name__ == '__main__':
    # import undetected_chromedriver as uc
    # options = uc.ChromeOptions()
    # options.headless=True
    # options.add_argument('--headless')
    # driver = uc.Chrome(options=options)

    # emiten = 'GOTO'
    # buy_price = '300'
    # take_profit = '500'
    # cut_loss = '100'

    # print('START')
    # delete_cache(driver)

    # login(driver)
    # create_buy_order(driver, emiten, buy_price)
    # create_auto_order(driver, emiten, take_profit, cut_loss)

    # driver.quit()
    # print('FINISH')