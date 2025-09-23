import streamlit as st
import pandas as pd
from pyngrok import ngrok
from scraper_playwright import run_scraper

# ===============================
# Mapping dictionaries
# ===============================

industry_mapping = {
    "Information Technology & Services": "IT_ITES",
    "Computer Software": "IT_ITES",
    "Internet": "E-Commerce",
    "Banking": "BFSI",
    "Financial Services": "BFSI",
    "Insurance": "BFSI",
    "Hospital & Health Care": "Healthcare",
    "Pharmaceuticals": "Pharma",
    "Biotechnology": "Pharma",
    "Construction": "Real Estate & Construction",
    "Civil Engineering": "Infrastructure",
    "Education Management": "Education_Research",
    "E-Learning": "Education_Research",
    "Airlines/Aviation": "Aerospace & Defense",
    "Automotive": "Automobile",
    "Textiles": "Textile",
    "FMCG": "FMCG",
    "Consumer Goods": "FMCG",
    "Oil & Energy": "Energy & Utilities",
    "Utilities": "Energy & Utilities",
    "Telecommunications": "Telecom",
    "Logistics & Supply Chain": "Logistics & Transportation",
    "Management Consulting": "Consulting",
    "Marketing & Advertising": "Advt_Med_Ent",
    "Media Production": "Advt_Med_Ent",
    "Government Administration": "Govt_Psu",
    "Public Policy": "Govt_Psu",
    "Hospitality": "Hospitality",
    "Retail": "Retail",
    "Apparel & Fashion": "Retail",
    "Real Estate": "Real Estate & Construction",
    "Chemicals": "Chemical",
    "Machinery": "Manufacturing",
    "Electrical/Electronic Manufacturing": "Electric_Electronics",
    # Default catch-all
    "Others": "Others"
}

employee_mapping = {
    "1-10 employees": "01 to 50",
    "11-50 employees": "01 to 50",
    "51-200 employees": "51 to 100",
    "201-500 employees": "251 to 500",
    "501-1,000 employees": "501 to 1000",
    "1,001-5,000 employees": "1001 to 2500",
    "5,001-10,000 employees": "5001 & above",
    "10,001+ employees": "5001 & above"
}

# ===============================
# Streamlit + Ngrok
# ===============================

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")
st.title("🔎 LinkedIn Company Scraper (Industry + Employee Size)")

# Start ngrok tunnel
public_url = ngrok.connect(8501)
st.sidebar.success(f"🌍 Shareable Link: {public_url}")

uploaded_file = st.file_uploader("Upload Excel file with 'Company_name' column", type=["xlsx"])

if uploaded_file:
    df_input = pd.read_excel(uploaded_file)

    if "Company_name" not in df_input.columns:
        st.error("❌ Input Excel must contain a 'Company_name' column.")
    else:
        if st.button("Start Scraping"):
            results = []
            with st.spinner("Scraping LinkedIn... Please wait ⏳"):
                for company in df_input["Company_name"].dropna().unique():
                    details = run_scraper(company)  # returns dict with LinkedIn data

                    if details:
                        industry_raw = details.get("Industry", "Not Found")
                        size_raw = details.get("Company Size", "Not Found")

                        industry_mapped = industry_mapping.get(industry_raw, "Others")
                        size_mapped = employee_mapping.get(size_raw, "Not Found")

                        results.append({
                            "Company Name": company,
                            "LinkedIn URL": details.get("LinkedIn URL", "Not Found"),
                            "Industry (LinkedIn)": industry_raw,
                            "Industry (Mapped)": industry_mapped,
                            "Employee Size (LinkedIn)": size_raw,
                            "Employee Size (Mapped)": size_mapped
                        })
                    else:
                        results.append({
                            "Company Name": company,
                            "LinkedIn URL": "Not Found",
                            "Industry (LinkedIn)": "Not Found",
                            "Industry (Mapped)": "Not Found",
                            "Employee Size (LinkedIn)": "Not Found",
                            "Employee Size (Mapped)": "Not Found"
                        })

            df_results = pd.DataFrame(results)
            st.success("✅ Scraping completed")
            st.dataframe(df_results, use_container_width=True)

            st.download_button(
                "⬇️ Download Results as Excel",
                data=df_results.to_csv(index=False),
                file_name="linkedin_scraping_results.csv",
                mime="text/csv"
            )
else:
    st.info("📂 Please upload an Excel file to start.")
