import requests
import pandas as pd
import re

# Function to remove illegal Excel characters
def clean_text(value):
    if isinstance(value, str):
        # Remove non-printable control characters Excel doesn't support
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    return value

# Function to fetch all records from paginated endpoint
def fetch_all_records(base_url, key_name):
    all_records = []
    page = 1

    while True:
        url = f"{base_url}?page={page}&per_page=100"
        response = requests.get(url, headers={"accept": "application/json"})
        if response.status_code != 200:
            print(f"⚠️ Failed on page {page}. Status: {response.status_code}")
            break

        result = response.json().get("result", {})
        data = result.get(key_name, [])
        if not data:
            break

        all_records.extend(data)
        print(f"✅ Fetched page {page} with {len(data)} records")
        page += 1

    return all_records

# Base URLs
contracts_url = "https://api.doge.gov/savings/contracts"
grants_url = "https://api.doge.gov/savings/grants"

# Fetch data
contracts = fetch_all_records(contracts_url, "contracts")
grants = fetch_all_records(grants_url, "grants")

# Convert to DataFrames and clean
contracts_df = pd.DataFrame(contracts).applymap(clean_text)
grants_df = pd.DataFrame(grants).applymap(clean_text)

# Save to Excel with tabs
with pd.ExcelWriter("doge_full_download.xlsx", engine="openpyxl") as writer:
    contracts_df.to_excel(writer, sheet_name="Contracts", index=False)
    grants_df.to_excel(writer, sheet_name="Grants", index=False)

print("\n🎉 All data downloaded and saved to 'doge_full_download.xlsx'")
