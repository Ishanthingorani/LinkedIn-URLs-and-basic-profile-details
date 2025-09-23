# app.py
import streamlit as st
import pandas as pd
from scraper_playwright import run_scraper

st.title("🔎 LinkedIn Scraper with Playwright")

uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type=["xlsx"])

if uploaded_file:
    input_path = "./Input_file/input.xlsx"
    output_path = "./Output_file/output.xlsx"

    df = pd.read_excel(uploaded_file)
    df.to_excel(input_path, index=False)

    if st.button("Run Scraper"):
        run_scraper("input", "output")
        st.success("Scraping completed ✅")

        result_df = pd.read_excel(output_path)
        st.dataframe(result_df)
        st.download_button("Download Results", data=result_df.to_csv(index=False), file_name="results.csv", mime="text/csv")
