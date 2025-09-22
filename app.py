import streamlit as st
import pandas as pd
from scraper import run_scraper

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")

st.title("🔎 LinkedIn Scraper App")

uploaded_file = st.file_uploader("Upload Excel file with company data", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head(10))

    if st.button("Run Scraper"):
        with st.spinner("Scraping in progress... Please wait."):
            updated_df = run_scraper(df.copy())
        st.success("✅ Scraping completed!")

        st.subheader("Preview of Results")
        st.dataframe(updated_df.head(20))

        # Save result to Excel
        output_path = "output_scraped.xlsx"
        updated_df.to_excel(output_path, index=False)
        with open(output_path, "rb") as f:
            st.download_button("📥 Download Results", f, file_name="scraped_results.xlsx")
