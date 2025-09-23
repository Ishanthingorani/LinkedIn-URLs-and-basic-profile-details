from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# === CONFIGURE YOUR LOCAL CHROMEDRIVER PATH ===
chrome_driver_path = r"C:\Users\HP\Downloads\chromedriver-win32 (2)\chromedriver-win32\chromedriver.exe"
service = Service(chrome_driver_path)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless=new")  # Optional: remove if you want to see the browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize DataFrame for results
columns = ["Company Name", "Industry", "Company Size"]
scraped_data = pd.DataFrame(columns=columns)

# === FUNCTION TO EXTRACT DATA FROM LINKEDIN PAGE ===
def extract_data(soup, company_name):
    industry, size = None, None
    try:
        for dt in soup.find_all("dt"):
            if "Industry" in dt.text:
                industry = dt.find_next("dd").text.strip() if dt.find_next("dd") else None
            elif "Company size" in dt.text:
                size = dt.find_next("dd").text.strip() if dt.find_next("dd") else None
    except Exception as e:
        print(f"Error extracting data for {company_name}: {e}")
    return {"Company Name": company_name, "Industry": industry, "Company Size": size}

# === FUNCTION TO SCRAPE SINGLE COMPANY ===
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

        # Scroll to load dynamic content
        for _ in range(5):
            driver.execute_script("window.scrollBy(0,1000);")
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        return extract_data(soup, company_name)
    except Exception as e:
        print(f"Error scraping {company_name}: {e}")
        return {"Company Name": company_name, "Industry": None, "Company Size": None}

# === FUNCTION TO PROCESS COMPANY LIST ===
def scrape_company_list(company_list):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    results = []
    for company in company_list:
        print(f"Scraping: {company}")
        results.append(scrape_company(driver, company))
    driver.quit()
    return pd.DataFrame(results)

# === MAIN EXECUTION ===
def main():
    input_file = input("Enter input Excel file name (with .xlsx): ").strip()
    if not os.path.exists(input_file):
        print(f"File '{input_file}' not found!")
        return

    df = pd.read_excel(input_file)
    if 'Company_name' not in df.columns:
        print("Error: 'Company_name' column not found in input file.")
        return

    company_list = df['Company_name'].dropna().unique()
    print(f"Total companies to scrape: {len(company_list)}")

    results = scrape_company_list(company_list)

    output_file = input("Enter output Excel file name (with .xlsx): ").strip()
    results.to_excel(output_file, index=False)
    print(f"Scraping completed! Results saved to {output_file}")

if __name__ == "__main__":
    main()
