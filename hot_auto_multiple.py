import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import threading
import os
import psutil
import datetime

users_keys = {
    'ates2' : 'ed25519:3mrC4SM9TaJjjbsH21cGDYH6s6xqQxWj5hLZN2QH8QKNBdW5ZD45VnwgKu3jugUEGfyrm13MKFR4s1qc3f857P1w'
}

class WalletAutomation:
    def __init__(self, private_key_owner, private_key, operation):
        self.private_key_owner = private_key_owner
        self.private_key = private_key
        self.operation = operation
        self.remaining_time = None
        self.initialize_and_run()

    def initialize_and_run(self):
        # Setup driver options
        options = uc.ChromeOptions()
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
        driver = uc.Chrome(options=options)

        # Attempt to automate the process with retries for exception
        step = None
        print(
            f"-> Automation started for ~{self.private_key_owner}~ as {self.operation}")
        try:
            # Open web page
            step = 'Web page opening...'
            driver.get('https://tgapp.herewallet.app/auth/import')

            # Fill private key field
            step = 'Private key field founding and filling up...'
            private_key_field_xpath = '//*[@id="root"]/div/div[1]/label/textarea'
            private_key_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, private_key_field_xpath)))
            private_key_field.send_keys(self.private_key)
            time.sleep(1)

            # Click continue button
            step = 'Continue button clicking...'
            continue_button_xpath = '//*[@id="root"]/div/div[2]/button'
            continue_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, continue_button_xpath)))
            continue_button.click()
            time.sleep(1)

            # Click account button
            step = 'Account button clicking...'
            account_button_xpath = '//*[@id="root"]/div/button'
            account_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, account_button_xpath)))
            account_button.click()
            time.sleep(1)

            # Click hot button
            step = 'Hot button clicking...'
            hot_button_xpath = '//*[@id="root"]/div/div/div/div[4]/div[1]/div'
            hot_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, hot_button_xpath)))
            hot_button.click()
            time.sleep(1)

            # Remaining time
            step = 'Remaining time taking...'
            time_xpath = '//*[@id="root"]/div/div[2]/div/div[3]/div/div[2]/div[1]/p[2]'
            self.remaining_time = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, time_xpath))
            ).text
            time.sleep(1)

            if self.operation == 'claim':
                # Current Hot balance
                step = 'Current Hot balance taking...'
                hot_balance_xpath = '//*[@id="root"]/div/div[2]/div/div[2]/div[3]/p[2]'
                current_hot_balance = float(WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, hot_balance_xpath))
                ).text)
                time.sleep(1)

                # In storage
                step = 'In storage taking...'
                storage_xpath = '//*[@id="root"]/div/div[2]/div/div[2]/div[2]/h1'
                storage = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, storage_xpath))
                ).text
                time.sleep(1)

                # Click claim button
                claim_button_xpath = '//*[@id="root"]/div/div[2]/div/div[3]/div/div[2]/div[2]/button'
                claim_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, claim_button_xpath)))
                time.sleep(1)

                if claim_button and not claim_button.get_attribute("disabled"):
                    step = 'Claim button clicking...'
                    claim_button.click()
                    time.sleep(1)

                    def has_value_changed(driver):
                        global new_hot_balance
                        new_hot_balance = float(WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, hot_balance_xpath))
                        ).text)
                        return current_hot_balance != new_hot_balance

                    WebDriverWait(driver, 120).until(has_value_changed)

                    # In storage
                    storage_xpath = '//*[@id="root"]/div/div[2]/div/div[2]/div[2]/h1'
                    storage = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, storage_xpath))
                    ).text
                    time.sleep(1)

                    print(
                        f'--> In storage: {storage} for ~{self.private_key_owner}~')
                    print(
                        f'--> Current Hot Balance: {current_hot_balance} --> {new_hot_balance} for ~{self.private_key_owner}~')
                    print(
                        f'--> Mined {format(new_hot_balance - current_hot_balance, ".6f")} Hot :) for ~{self.private_key_owner}~')
                    print(f"Automation succeeded for ~{self.private_key_owner}~")

        except Exception:
            print(f'Error while {step} for ~{self.private_key_owner}~')
            time.sleep(1)
        
        time.sleep(1)
        kill_process_by_pid(driver.browser_pid)
        driver.quit()


def kill_process_by_pid(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=30)
    except psutil.NoSuchProcess:
        print(f"PID {pid} doesn't found.")
    except Exception as e:
        print(f"Error kill_process_by_pid: {e}")


def parse_time_to_minutes(private_key_owner, time_str):
    try:
        total_minutes = 0
        if time_str != 'Filled':
            parts = time_str.split(' ')
            for part in parts:
                if 'h' in part:
                    total_minutes += int(part.replace('h', '')) * 60
                elif 'm' in part:
                    total_minutes += int(part.replace('m', ''))
            return total_minutes
        else:
            print(f'Storage full, hopefully for ~{private_key_owner}~')
            return 0
    except Exception as e:
        print(f"{e}")
        return 0


def handle_user_claim(private_key_owner, private_key):
    while True:
        wallet_automation = WalletAutomation(
            private_key_owner=private_key_owner, private_key=private_key, operation='time')

        if wallet_automation.remaining_time is not None:
            remaining_time_in_minutes = parse_time_to_minutes(private_key_owner=private_key_owner,
                                                              time_str=wallet_automation.remaining_time)

            if remaining_time_in_minutes == 0:
                print(f"Initiating claim process for {private_key_owner}...")
                WalletAutomation(private_key_owner=private_key_owner,
                                 private_key=private_key, operation='claim')
            else:
                now  = datetime.datetime.now().strftime("%H:%M")
                new_time = (datetime.datetime.now() + datetime.timedelta(minutes=remaining_time_in_minutes+1)).strftime("%H:%M")
                print(
                    f" -Started at {now} -> Waiting {remaining_time_in_minutes} minutes for ~{private_key_owner}~. ETC: {new_time}")
                time.sleep((remaining_time_in_minutes * 60)+70)
                print(
                    f"Waiting period over for ~{private_key_owner}~, initiating claim process...")
                WalletAutomation(private_key_owner=private_key_owner,
                                 private_key=private_key, operation='claim')
                time.sleep(10)
        else:
            continue


if __name__ == '__main__':
    for private_key_owner, private_key in users_keys.items():
        thread = threading.Thread(
            target=handle_user_claim, args=(private_key_owner, private_key))
        thread.start()


# def get_remaining_times():
#     remaining_times = {}
#     for private_key_owner, private_key in users_keys.items():
#         remaining_time_in_minutes = parse_time_to_minutes(time_str=WalletAutomation(
#             private_key_owner=private_key_owner, private_key=private_key, operation='time').remaining_time)
#         remaining_times[private_key_owner] = remaining_time_in_minutes
#     return remaining_times

# def wait_for_max_time():
#     remaining_times = get_remaining_times()
#     max_remaining_time_owner = max(remaining_times, key=remaining_times.get)
#     max_remaining_time = remaining_times[max_remaining_time_owner]
#     print(max_remaining_time)
