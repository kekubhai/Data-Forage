import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def scrape_website(website):
    print("Launching Chrome...")  # Fixed typo
    
    chrome_driver_path = "./chromedriver.exe"  # Removed trailing space
    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    
    try:
        driver.get(website)
        print("Website opened successfully.")
        
        html = driver.page_source
        time.sleep(10)
        
        return html
    
    finally:
        driver.quit()
        print("Chrome closed.")
