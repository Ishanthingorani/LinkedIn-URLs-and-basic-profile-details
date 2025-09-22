import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

st.set_page_config(page_title="LinkedIn Company Scraper", layout="wide")
st.title("🔎 LinkedIn Company Scraper (Cloud-Friendly)")

uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type=["xlsx"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file)
    
    if 'Company_name' not in df_input.columns:
        st.error("Input Excel must have a 'Company_name' column.")
    else:
        st.write("Preview of uploaded data:")
        st.dataframe(df_input.head(10))

        if st.button("Run Scraper"):
            scraped_data = pd.DataFrame(columns=["Company Name", "LinkedIn URL", "Industry", "Company Size"])
            
            company_list = df_input['Company_name'].dropna().unique()
            progress_bar = st.progress(0)
            
            headers = {"User-Agent": "Mozilla/5.0"}
            
            for idx, company_name in enumerate(company_list):
                try:
                    # Google search for LinkedIn
                    query = urllib.parse.quote(f"{company_name} linkedin")
                    google_url = f"https://www.google.com/search?q={query}"
                    response = requests.get(google_url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract first LinkedIn URL
                    link_tag = soup.find('a', href=True)
                    linkedin_url = ""
                    if link_tag and "linkedin.com/company" in link_tag['href']:
                        linkedin_url = link_tag['href']
                    
                    industry = None
                    size = None
                    
                    # If LinkedIn URL found, scrape Industry & Company Size
                    if linkedin_url:
                        r = requests.get(linkedin_url, headers=headers)
                        soup2 = BeautifulSoup(r.text, 'html.parser')
                        industry_tag = soup2.find('div', {'data-test-id': 'about-us__industry'})
                        size_tag = soup2.find('div', {'data-test-id': 'about-us__size'})
                        industry = industry_tag.get_text(strip=True) if industry_tag else None
                        size = size_tag.get_text(strip=True) if size_tag else None
                    
                    scraped_data.loc[len(scraped_data)] = [company_name, linkedin_url, industry, size]
                except Exception as e:
                    st.warning(f"Error scraping {company_name}: {e}")
                
                progress_bar.progress((idx+1)/len(company_list))
                time.sleep(1)  # polite delay
            
            st.success("✅ Scraping completed!")
            st.subheader("Preview of scraped results")
            st.dataframe(scraped_data.head(20))

            output_path = "scraped_results.xlsx"
            scraped_data.to_excel(output_path, index=False)
            with open(output_path, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="scraped_results.xlsx")
