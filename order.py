import os
import time
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

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
PIN1 = os.getenv('PIN1')
PIN2 = os.getenv('PIN2')
PIN3 = os.getenv('PIN3')
PIN4 = os.getenv('PIN4')
LOGIN_URL = os.getenv('LOGIN_URL')
HOMEPAGE_URL = os.getenv('HOMEPAGE_URL')

# TODO: login data encryption

DELAY = 10 # seconds

def login(driver):
    # Input login
    driver.get(LOGIN_URL + '/login')

    email = driver.find_element(By.XPATH, '//*[@id="root"]/section/div[1]/div/div[2]/form/div[1]/input')
    email.send_keys(EMAIL)

    password = driver.find_element(By.XPATH, '//*[@id="root"]/section/div[1]/div/div[2]/form/div[2]/input')
    password.send_keys(PASSWORD)
    password.send_keys(Keys.RETURN)

    print('Input login OK')

    # Input PIN
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/span')))
        print("Input PIN OK")

        pin1 = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div/input[1]')
        pin1.send_keys(PIN1)

        pin2 = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div/input[2]')
        pin2.send_keys(PIN2)

        pin3 = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div/input[3]')
        pin3.send_keys(PIN3)

        pin4 = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div/input[4]')
        pin4.send_keys(PIN4)
    except TimeoutException:
        print("Loading took too much time!")

    # Wait for homepage
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/p')))
        print("Homepage OK")            
    except TimeoutException:
        print("Loading took too much time!")

def open_emiten_page(driver, emiten):
    driver.get(HOMEPAGE_URL + emiten)

def create_buy_order(driver, emiten, buy_price):
    # Open emiten page
    open_emiten_page(driver, emiten)

    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Beli"]')))
        print("Buy button OK")

        time.sleep(1)

        # Click Beli button
        driver.find_element(By.XPATH, '//button[text()="Beli"]').click()
    except TimeoutException:
        print("Loading took too much time!")

    # Input price
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="INPUT_BUY_PRICE"]')))
        print("Input buy price OK")
        time.sleep(1)
        input_price = driver.find_element(By.XPATH, '//*[@id="INPUT_BUY_PRICE"]')
        input_price.send_keys(Keys.CONTROL + "A")
        input_price.send_keys(Keys.DELETE)
        input_price.send_keys(buy_price)
    except TimeoutException:
        print("Element does not exist!")

    # Lot size
    driver.find_element(By.XPATH, '//*[@id="btn"]').click()

    buy_btn = driver.find_element(By.XPATH, '//button[@data-testid="btnPopupBuy"]').is_enabled()
    if buy_btn:
        # Click Beli
        driver.find_element(By.XPATH, '//button[@data-testid="btnPopupBuy"]').click()

        # Konfirmasi Beli
        try:
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="btnConfirmBuy"]')))
            print("Konfirmasi beli OK")
            driver.find_element(By.XPATH, '//button[@data-testid="btnConfirmBuy"]').click()
        except TimeoutException:
            print("Element does not exist!")

def create_auto_order(driver, emiten, take_profit, cut_loss):
    create_take_profit(driver, emiten, take_profit)
    time.sleep(5)
    create_cut_loss(driver, emiten, cut_loss)

def create_take_profit(driver, emiten, take_profit):
    print('Start create take profit')

    # Open emiten page
    open_emiten_page(driver, emiten)

    # Check Jual button
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnSell"]')))
        print("Button Jual OK")

        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@data-testid="btnSell"]').click()

        # Select auto order type
        select_auto_order_type(driver)

        # Input expiry date
        calculate_expiry_date(driver)

        # Click take profit
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[11]/div[2]/div/div[2]/div').click()

        # Input trigger price
        take_profit_field = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[11]/div[2]/div/div[3]/input')
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
        
        send_auto_order(driver)
    except TimeoutException:
        print("Button Jual does not exist!")

def create_cut_loss(driver, emiten, cut_loss):
    print('Start create cut loss')

    # Open emiten page
    open_emiten_page(driver, emiten)

    # Check Jual button
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnSell"]')))
        print("Button Jual OK")

        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@data-testid="btnSell"]').click()

        # Select auto order type
        select_auto_order_type(driver)

        # Input expiry date
        calculate_expiry_date(driver)

        # Click cut loss
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[11]/div[2]/div/div[1]/div').click()

        # Input trigger price
        cut_loss_field = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[11]/div[2]/div/div[3]/input')
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

        send_auto_order(driver)
    except TimeoutException:
        print("Button Jual does not exist!")

def select_auto_order_type(driver):
    # Pick order type
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="periodType"]')))
        print("Pilih Tipe Order OK")
        driver.find_element(By.XPATH, '//*[@id="periodType"]').click()
        driver.find_element(By.XPATH, '//*[@data-testid="opt-periodType-1"]').click()
    except TimeoutException:
        print("Element does not exist!")

def calculate_expiry_date(driver):
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
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[9]/div[2]/div/div[1]/div/input')))
        print("Start date picker OK")

        # Click start date picker 
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[9]/div[2]/div/div[1]/div/input').click()

        # Select start month
        select_start_month = Select(driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[9]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]/select'))
        select_start_month.select_by_value(start_m)

        # Select start year
        select_start_year = Select(driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[9]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/select'))
        select_start_year.select_by_value(start_y)

        # Click start date
        driver.find_element(By.XPATH, "//div[text()='" + start_d + "'][@aria-disabled='false']").click()
    except TimeoutException:
        print("Element does not exist!")

    # Input expiry end date
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[10]/div[2]/div/div[1]/div/input')))
        print("End date picker OK")

        # Click end date picker 
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[10]/div[2]/div/div[1]/div/input').click()

        # Select end month
        select_end_month = Select(driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[10]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]/select'))
        select_end_month.select_by_value(end_m)

        # Select end year
        select_end_year = Select(driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[2]/div[3]/div/div/div[3]/div[5]/div[1]/div/div[1]/div[10]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/select'))
        select_end_year.select_by_value(end_y)

        # Click end date
        driver.find_element(By.XPATH, "//div[text()='" + end_d + "'][@aria-disabled='false']").click()
    except TimeoutException:
        print("Element does not exist!")

def send_auto_order(driver):
    # Click aktifkan auto order
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnPopupSell"]')))
        print("Aktifkan auto order take profit OK")

        time.sleep(3)

        driver.find_element(By.XPATH, '//*[@data-testid="btnPopupSell"]').click()
    except TimeoutException:
        print("Element does not exist!")

    # Click konfirmasi auto order
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="btnConfirmSell"]')))
        print("Konfirmasi auto order take profit OK")

        time.sleep(3)
        
        driver.find_element(By.XPATH, '//*[@data-testid="btnConfirmSell"]').click()
    except TimeoutException:
        print("Konfirmasi auto order take profit does not exist!")

# Delete chrome cache
def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.

    perform_actions(driver, Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 5 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

def perform_actions(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)

    time.sleep(2)

    print('Performing delete cache!')
    actions.perform()

# For testing
# if __name__ == '__main__':
#     import undetected_chromedriver as uc
#     options = uc.ChromeOptions()
#     options.headless=False
#     # options.add_argument('--headless')
#     driver = uc.Chrome(options=options)

#     emiten = 'MRAT'
#     buy_price = '290'
#     take_profit = '316'
#     cut_loss = '264'

#     print('START')
#     delete_cache(driver)

#     login(driver)
#     create_buy_order(driver, emiten, buy_price)
#     create_auto_order(driver, emiten, take_profit, cut_loss)

#     driver.quit()
#     print('FINISH')