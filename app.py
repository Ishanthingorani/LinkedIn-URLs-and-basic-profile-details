import streamlit as st
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os

st.set_page_config(page_title="LinkedIn Company Scraper", layout="wide")
st.title("🔎 LinkedIn Company Scraper")

uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type=["xlsx"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file)
    
    if 'Company_name' not in df_input.columns:
        st.error("Input Excel must have a 'Company_name' column.")
    else:
        st.write("Preview of uploaded data:")
        st.dataframe(df_input.head(10))

        if st.button("Run Scraper"):
            scraped_data = pd.DataFrame(columns=["Company Name", "Industry", "Company Size"])
            
            # Setup Chrome WebDriver
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")
            driver = webdriver.Chrome(options=chrome_options)
            
            company_list = df_input['Company_name'].dropna().unique()
            progress_bar = st.progress(0)
            
            for idx, company_name in enumerate(company_list):
                try:
                    # Google search
                    driver.get('https://www.google.com')
                    search_box = driver.find_element(By.NAME, 'q')
                    search_box.send_keys(f"{company_name.strip()} linkedin")
                    search_box.send_keys(Keys.RETURN)

                    # Click first result
                    first_result = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'h3'))
                    )
                    first_result.click()

                    # Wait for page to load
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    for _ in range(5):
                        driver.execute_script("window.scrollBy(0, 1000);")
                        time.sleep(2)

                    # Parse page
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    def extract_text_or_none(tag):
                        try:
                            if tag and tag.find('dd'):
                                return tag.find('dd').get_text(strip=True)
                        except:
                            return None
                        return None
                    industry = extract_text_or_none(soup.find('div', {'data-test-id': 'about-us__industry'}))
                    size = extract_text_or_none(soup.find('div', {'data-test-id': 'about-us__size'}))
                    scraped_data.loc[len(scraped_data)] = [company_name, industry, size]
                except Exception as e:
                    st.warning(f"Error scraping {company_name}: {e}")
                
                progress_bar.progress((idx+1)/len(company_list))
            
            driver.quit()
            
            st.success("✅ Scraping completed!")
            st.subheader("Preview of scraped results")
            st.dataframe(scraped_data.head(20))

            # Download button
            output_path = "scraped_results.xlsx"
            scraped_data.to_excel(output_path, index=False)
            with open(output_path, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="scraped_results.xlsx")
