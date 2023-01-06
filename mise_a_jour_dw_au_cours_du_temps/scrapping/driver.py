from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc


def driver():

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = uc.Chrome(options=chrome_options)
    
    return driver
