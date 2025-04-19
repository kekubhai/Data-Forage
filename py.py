import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Get URL from user
url = input("Enter the URL to scrape: ")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Failed to retrieve page.")
    exit(1)

soup = BeautifulSoup(response.content, "html.parser")

# Step 2: Find all unique tags
all_tags = set([tag.name for tag in soup.find_all()])
all_tags = sorted(all_tags)

print("\nAvailable tags on this page:")
for idx, tag in enumerate(all_tags, 1):
    print(f"{idx}. <{tag}>")

# Step 3: Ask user to select tags
selected = input("\nEnter the numbers of the tags you want to scrape (comma-separated, e.g. 1,3,5): ")
try:
    selected_indices = [int(x.strip())-1 for x in selected.split(',') if x.strip().isdigit()]
    selected_tags = [all_tags[i] for i in selected_indices if 0 <= i < len(all_tags)]
except Exception as e:
    print("Invalid input. Please enter valid numbers.")
    exit(1)

if not selected_tags:
    print("No valid tags selected.")
    exit(1)

print(f"\nScraping tags: {', '.join('<'+t+'>' for t in selected_tags)}")

# Step 4: Scrape and save
results = []
for tag in selected_tags:
    for el in soup.find_all(tag):
        text = el.get_text(strip=True)
        if text:
            results.append({"Tag": tag, "Text": text})

if not results:
    print("No data found for the selected tags.")
    exit(1)

df = pd.DataFrame(results)
df.to_excel("scraped_data.xlsx", index=False)
print("✅ Data saved to 'scraped_data.xlsx'")