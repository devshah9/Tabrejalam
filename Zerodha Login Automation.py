from selenium import webdriver
#chrome options class is used to manipulate various properties of Chrome driver
from selenium.webdriver.chrome.options import Options
#waits till the content loads
from selenium.webdriver.support.ui import WebDriverWait
#finds that content
from selenium.webdriver.support import expected_conditions as EC
#find the above condition/conntent by the xpath, id etc.
from selenium.webdriver.common.by import By

#zerodha
from kiteconnect import KiteConnect

# python
from time import sleep
import urllib.parse as urlparse
from fake_useragent import UserAgent
import configparser 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# config configration 
config = configparser.ConfigParser()
config.read('config.ini')

#credentials
api_key = config['DEFAULT']["api_key"]
api_secret = config['DEFAULT']["api_secret"]
account_username = config['DEFAULT']["account_username"]
account_password = config['DEFAULT']["account_password"]
account_two_fa = int(config['DEFAULT']["account_two_fa"])

kite = KiteConnect(api_key=api_key)

ua = UserAgent()
userAgent = ua.random


options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
options.add_argument(f'user-agent={userAgent}')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(kite.login_url())

# #identify login section
form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]')))

# #enter the ID
driver.find_element(By.XPATH, "//input[@type='text']").send_keys(account_username)


#enter the password
driver.find_element(By.XPATH, "//input[@type='password']").send_keys(account_password)

#submit
driver.find_element(By.XPATH, "//button[@type='submit']").click()

#sleep for a second so that the page can submit and proceed to upcoming question (2fa)
sleep(1)
form = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="login-form"]//form')))

#identify login section for 2fa
#enter the 2fa code
driver.find_element(By.XPATH, "//input[@type='password']").send_keys(account_two_fa)

#submit
driver.find_element(By.XPATH, "//button[@type='submit']").click()

sleep(1)
current_url = driver.current_url

driver.close()

parsed = urlparse.urlparse(current_url)
request_token = urlparse.parse_qs(parsed.query)['request_token'][0]

access_token = kite.generate_session(request_token=request_token,api_secret=api_secret)['access_token']

kite.set_access_token(access_token)
# kite.L
a = kite.ltp("NSE:RELIANCE")
print(a)