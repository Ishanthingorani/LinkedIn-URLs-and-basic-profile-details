import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="LinkedIn Company Scraper", layout="wide")
st.title("LinkedIn Company Scraper (Live Website)")

# --- Function to scrape LinkedIn company info using requests ---
def get_linkedin_info(company_name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        # Google search for LinkedIn company page
        search_url = f"https://www.google.com/search?q={company_name}+site:linkedin.com/company/"
        r = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        link_tag = soup.select_one("div.yuRUbf > a")  # first search result
        if not link_tag:
            return {"Company Name": company_name, "Industry": None, "Company Size": None}

        linkedin_url = link_tag['href']
        r2 = requests.get(linkedin_url, headers=headers)
        soup2 = BeautifulSoup(r2.text, "html.parser")

        industry, size = None, None
        for dt in soup2.find_all("dt"):
            if "Industry" in dt.text:
                industry = dt.find_next("dd").text.strip() if dt.find_next("dd") else None
            elif "Company size" in dt.text:
                size = dt.find_next("dd").text.strip() if dt.find_next("dd") else None

        return {"Company Name": company_name, "Industry": industry, "Company Size": size}

    except Exception as e:
        return {"Company Name": company_name, "Industry": None, "Company Size": None}

# --- File upload ---
uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if "Company_name" not in df.columns:
        st.error("Excel must contain a 'Company_name' column")
    else:
        st.success(f"{df.shape[0]} companies loaded!")

        if st.button("Start Scraping"):
            results_list = []
            with st.spinner("Scraping in progress..."):
                for idx, company in enumerate(df['Company_name'], start=1):
                    results_list.append(get_linkedin_info(company))
                    st.progress(idx / len(df))
                    time.sleep(1)  # polite delay to avoid Google blocking
            results = pd.DataFrame(results_list)
            st.success("Scraping completed!")
            st.dataframe(results)

            # --- Download button ---
            results.to_excel("LinkedIn_Output.xlsx", index=False)
            st.download_button(
                label="Download Excel",
                data=open("LinkedIn_Output.xlsx", "rb"),
                file_name="LinkedIn_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
