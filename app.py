import streamlit as st
import pandas as pd
from scraping_functions import scrape_company_list

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")
st.title("LinkedIn Company Scraper")

uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if "Company_name" not in df.columns:
        st.error("Excel must contain a 'Company_name' column")
    else:
        st.success(f"{df.shape[0]} companies loaded!")
        if st.button("Start Scraping"):
            with st.spinner("Scraping in progress..."):
                results = scrape_company_list(df['Company_name'].tolist())
            st.success("Scraping completed!")
            st.dataframe(results)
            results.to_excel("Output.xlsx", index=False)
            st.download_button(
                label="Download Excel",
                data=open("Output.xlsx","rb"),
                file_name="LinkedIn_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
