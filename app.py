from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Headless Chrome
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_data(soup, company_name):
    industry, size = None, None
    try:
        for dt in soup.find_all("dt"):
            if "Industry" in dt.text:
                industry = dt.find_next("dd").text.strip() if dt.find_next("dd") else None
            elif "Company size" in dt.text:
                size = dt.find_next("dd").text.strip() if dt.find_next("dd") else None
    except:
        pass
    return {"Company Name": company_name, "Industry": industry, "Company Size": size}

def scrape_company(driver, company_name):
    try:
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(f"{company_name} site:linkedin.com/company/")
        search_box.send_keys(Keys.RETURN)

        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.yuRUbf > a"))
        )
        first_result.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        for _ in range(5):
            driver.execute_script("window.scrollBy(0,1000);")
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        return extract_data(soup, company_name)
    except:
        return {"Company Name": company_name, "Industry": None, "Company Size": None}

def scrape_company_list(company_list):
    driver = init_driver()
    results = []
    for company in company_list:
        results.append(scrape_company(driver, company))
    driver.quit()
    return pd.DataFrame(results)
