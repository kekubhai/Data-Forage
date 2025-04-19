import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

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

# Show examples of available data on the page
print("\nExamples of data available on this page:")
# Sample some text from different common elements
examples = []
common_elements = ['h1', 'h2', 'p', 'a', 'div.title', '.header', 'li', 'td']
for selector in common_elements:
    try:
        elements = soup.select(selector)[:2]  # Get up to 2 examples
        for el in elements:
            text = el.get_text(strip=True)
            if text and len(text) > 5 and text not in examples:
                examples.append(text)
    except:
        pass

# Show a sample of the available data (up to 5 examples)
for i, example in enumerate(examples[:5], 1):
    if len(example) > 50:
        example = example[:50] + "..."
    print(f"{i}. {example}")

# Step 2: Ask user what kind of data they want
data_type = input("\nWhat kind of data do you need from this website? (e.g., 'product prices', 'article titles', 'contact information'): ")

# Step 3: Scrape based on user input
print(f"\nScraping for: {data_type}")
results = []

# Define common patterns based on the user's request
keywords = data_type.lower().split()

# Try different tag combinations based on the keywords
if any(word in ['price', 'prices', 'cost', 'costs', '$'] for word in keywords):
    # Look for price-related content
    price_patterns = [
        re.compile(r'\$\s*[\d,]+\.?\d*'),  # $XX.XX format
        re.compile(r'price', re.IGNORECASE),
        re.compile(r'cost', re.IGNORECASE)
    ]
    for element in soup.find_all(['span', 'div', 'p', 'h3']):
        text = element.get_text(strip=True)
        if text and (any(pattern.search(text) for pattern in price_patterns)):
            results.append({"Type": "Price", "Text": text})

elif any(word in ['title', 'titles', 'heading', 'headings', 'header', 'headers'] for word in keywords):
    # Look for titles and headings
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'title', '.title', '.heading']):
        text = element.get_text(strip=True)
        if text:
            results.append({"Type": "Title/Heading", "Text": text})

elif any(word in ['contact', 'email', 'phone', 'address'] for word in keywords):
    # Look for contact information
    contact_patterns = [
        re.compile(r'[\w\.-]+@[\w\.-]+'),  # Email
        re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),  # Phone
        re.compile(r'address', re.IGNORECASE)
    ]
    for element in soup.find_all(['p', 'div', 'span', 'address']):
        text = element.get_text(strip=True)
        if text and (any(pattern.search(text) for pattern in contact_patterns)):
            results.append({"Type": "Contact Info", "Text": text})

else:
    # Generic search - look for elements that might match the keywords
    for element in soup.find_all(['p', 'div', 'span', 'li', 'h1', 'h2', 'h3', 'a']):
        text = element.get_text(strip=True)
        if text and any(keyword in text.lower() for keyword in keywords):
            results.append({"Type": "Matched Content", "Text": text})

# If no specific matches were found, get a more general collection of page content
if not results:
    print("No specific matches found. Collecting general content...")
    for element in soup.find_all(['p', 'li', 'h1', 'h2', 'h3']):
        text = element.get_text(strip=True)
        if text and len(text) > 10:  # Filter out very short texts
            results.append({"Type": "General Content", "Text": text})

if not results:
    print("No data found that matches your request.")
    exit(1)

df = pd.DataFrame(results)
df.to_excel("scraped_data.xlsx", index=False)
print(f"✅ Found {len(results)} items. Data saved to 'scraped_data.xlsx'")