# scraper_playwright.py

import pandas as pd
import time
from playwright.sync_api import sync_playwright

def scrape_company(page, company_name):
    try:
        # Google search
        page.goto("https://www.google.com/")
        page.fill("input[name='q']", f"{company_name} linkedin")
        page.press("input[name='q']", "Enter")
        page.wait_for_timeout(3000)

        # Click first result
        page.click("h3", timeout=5000)

        # Wait for LinkedIn page
        page.wait_for_load_state("networkidle")

        # Scroll a bit to load dynamic content
        for _ in range(3):
            page.mouse.wheel(0, 2000)
            time.sleep(1)

        # Extract info
        industry = page.locator("div[data-test-id='about-us__industry'] dd").inner_text(timeout=2000) if page.locator("div[data-test-id='about-us__industry'] dd").count() > 0 else "Not Found"
        size = page.locator("div[data-test-id='about-us__size'] dd").inner_text(timeout=2000) if page.locator("div[data-test-id='about-us__size'] dd").count() > 0 else "Not Found"

        return {"Company Name": company_name, "Industry": industry, "Company Size": size}

    except Exception as e:
        print(f"Error scraping {company_name}: {e}")
        return {"Company Name": company_name, "Industry": "Error", "Company Size": "Error"}


def run_scraper(input_file, output_file):
    df = pd.read_excel(f"./Input_file/{input_file}.xlsx")

    if "Company_name" not in df.columns:
        print("❌ Input file must contain a 'Company_name' column")
        return

    company_list = df["Company_name"].dropna().unique()
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless mode
        page = browser.new_page()

        for company in company_list:
            results.append(scrape_company(page, company))

        browser.close()

    output_df = pd.DataFrame(results)
    output_df.to_excel(f"./Output_file/{output_file}.xlsx", index=False)
    print(f"✅ Scraping finished. File saved: ./Output_file/{output_file}.xlsx")
