#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import argparse
import pandas as pd
import os
import time

# Initialize DataFrame for results
columns = ["Company Name", "Industry", "Company Size"]
scraped_data = pd.DataFrame(columns=columns)

# Set up argument parsing for input and output file paths
parser = argparse.ArgumentParser(description='Process input and output file paths.')
parser.add_argument('-i', '--input', type=str, required=True, help='name of the input file (without extension)')
parser.add_argument('-o', '--output', type=str, required=True, help='name of the output file (without extension)')
args = parser.parse_args()

# Set up Chrome WebDriver with incognito mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)

# Ensure output directory exists
os.makedirs('./Output_file/', exist_ok=True)

# Function to extract text safely
def extract_text_or_none(tag):
    try:
        if tag and tag.find('dd'):
            return tag.find('dd').get_text(strip=True)
    except Exception as e:
        print(f"Error extracting text: {e}")
    return None

# Function to extract industry and size details
def extract_data(soup, company_name):
    try:
        industry = extract_text_or_none(soup.find('div', {'data-test-id': 'about-us__industry'}))
        size = extract_text_or_none(soup.find('div', {'data-test-id': 'about-us__size'}))
        scraped_data.loc[len(scraped_data)] = [company_name, industry, size]
    except Exception as e:
        print(f"Error extracting data for {company_name}: {e}")

# Function to automate scraping for a single company
def scrape_company(company_name):
    try:
        # Google search for LinkedIn page
        driver.get('https://www.google.com')
        search_box = driver.find_element(By.NAME, 'q')
        search_query = f"{company_name.strip()} linkedin"
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Click on the first result
        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h3'))
        )
        first_result.click()

        # Wait for the LinkedIn page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Scroll to load dynamic content
        for _ in range(5):  # Scroll 5 times
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        extract_data(soup, company_name)
    except Exception as e:
        print(f"Error scraping company {company_name}: {e}")

# Function to perform data crawling
def data_crawl(input_file, output_file):
    try:
        input_path = f'./Input_file/{input_file}.xlsx'
        df = pd.read_excel(input_path)
        if 'Company_name' not in df.columns:
            print("Error: 'Company_name' column not found in input file.")
            return
        
        company_list = df['Company_name'].dropna().unique()
        for company in company_list:
            scrape_company(company)

        # Save results to Excel
        output_path = f'./Output_file/{output_file}.xlsx'
        scraped_data.to_excel(output_path, index=False)
        print(f"Scraping completed. Results saved to {output_path}")
    except Exception as e:
        print(f"Error in data crawling: {e}")

# Main execution
data_crawl(args.input, args.output)
driver.quit()

