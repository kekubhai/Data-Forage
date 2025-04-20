import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random
from urllib.parse import urljoin, urlparse

# Configuration options
MAX_PAGES = 3  # Maximum number of pages to scrape
PROXY_ENABLED = False  # Whether to use proxies
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
]

# Step 1: Get URL and scraping options from user
url = input("Enter the URL to scrape: ")

# Ask if pagination should be enabled
enable_pagination = input("Do you want to scrape multiple pages? (y/n, default: n): ").lower().strip() == 'y'
if enable_pagination:
    max_pages = input(f"Maximum pages to scrape (default: {MAX_PAGES}): ")
    max_pages = int(max_pages) if max_pages.isdigit() else MAX_PAGES
    print(f"Will scrape up to {max_pages} pages")

# Ask if proxies should be used
use_proxy = input("Do you want to use proxy servers to avoid detection? (y/n, default: n): ").lower().strip() == 'y'
if use_proxy:
    proxies = input("Enter proxies separated by comma (format: http://ip:port,http://ip:port) or press Enter to use default: ")
    if proxies:
        proxies = [p.strip() for p in proxies.split(",")]
        print(f"Using {len(proxies)} custom proxies")
    else:
        # Sample proxy list - in a real app, you'd use a proxy service or your own list
        proxies = ["http://103.152.112.162:80", "http://193.239.86.249:3128", "http://159.65.77.168:8585"]
        print("Using default proxy servers")

# Function to get a random user agent and proxy
def get_request_config():
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    if use_proxy:
        proxy = random.choice(proxies)
        return {"headers": headers, "proxies": {"http": proxy, "https": proxy}}
    else:
        return {"headers": headers}

# Function to scrape a single page and return results
def scrape_page(page_url, data_type_keywords):
    print(f"Scraping: {page_url}")
    
    # Get request configuration with headers and optional proxies
    req_config = get_request_config()
    
    try:
        if use_proxy:
            response = requests.get(page_url, headers=req_config["headers"], proxies=req_config["proxies"], timeout=10)
        else:
            response = requests.get(page_url, headers=req_config["headers"], timeout=10)
            
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_url}. Status code: {response.status_code}")
            return [], None
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find next pagination link if available
        next_page_url = find_next_page_link(soup, page_url)
        
        # Process data based on keywords
        page_results = process_data_by_type(soup, data_type_keywords)
        
        return page_results, next_page_url
    
    except Exception as e:
        print(f"Error scraping {page_url}: {str(e)}")
        return [], None

# Function to find the next page link
def find_next_page_link(soup, current_url):
    # Common patterns for pagination links
    next_page_patterns = [
        # Text-based patterns
        {"element": "a", "text": ["next", "next page", "›", "»", ">", "次へ", "下一页", "siguiente"]},
        # Class-based patterns (common pagination classes)
        {"element": "a", "class": ["next", "pagination-next", "next-page", "page-next"]}
    ]
    
    base_url = current_url
    parsed_url = urlparse(current_url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Try to find next page link based on text patterns
    for pattern in next_page_patterns:
        if "text" in pattern:
            for text_pattern in pattern["text"]:
                for link in soup.find_all(pattern["element"]):
                    if link.get_text().lower().strip() == text_pattern.lower() and link.has_attr('href'):
                        return urljoin(base_url, link['href'])
        
        if "class" in pattern:
            for class_pattern in pattern["class"]:
                for link in soup.find_all(pattern["element"], class_=lambda c: c and class_pattern in c.lower()):
                    if link.has_attr('href'):
                        return urljoin(base_url, link['href'])
    
    # Look for common pagination patterns in URLs
    # For number-based pagination
    page_number = None
    
    # Check if the current URL contains a page parameter
    if "page=" in current_url:
        match = re.search(r'page=(\d+)', current_url)
        if match:
            page_number = int(match.group(1))
            next_page_url = re.sub(r'page=\d+', f'page={page_number+1}', current_url)
            return next_page_url
    
    # Try to find any pagination elements with incrementing numbers
    pagination_elements = soup.select('.pagination a, .pager a, .pages a')
    current_max = 0
    
    for el in pagination_elements:
        if el.get_text().isdigit():
            num = int(el.get_text())
            current_max = max(current_max, num)
    
    if current_max > 0:
        # Look for the current page number
        for el in pagination_elements:
            if el.get_text().isdigit() and int(el.get_text()) == current_max:
                if el.find_next_sibling() and el.find_next_sibling().name == 'a' and el.find_next_sibling().has_attr('href'):
                    return urljoin(base_url, el.find_next_sibling()['href'])
    
    return None

# Function to process data based on keywords
def process_data_by_type(soup, keywords):
    results = []
    
    # Try different content types based on the keywords
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
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4']):
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
    
    return results

# Main scraping process
def scrape_with_options(start_url, data_type):
    all_results = []
    current_url = start_url
    pages_scraped = 0
    
    # First page - do initial scrape and also show data examples
    try:
        req_config = get_request_config()
        
        if use_proxy:
            response = requests.get(current_url, headers=req_config["headers"], proxies=req_config["proxies"], timeout=10)
        else:
            response = requests.get(current_url, headers=req_config["headers"], timeout=10)
            
        if response.status_code != 200:
            print(f"Failed to retrieve page {current_url}. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Show examples of available data on the page without mentioning HTML tags
        print("\nExamples of data available on this page:")
        
        # Extract various types of content without showing the source tags
        examples = []
        
        # Get page title
        if soup.title:
            title = soup.title.get_text(strip=True)
            if title:
                examples.append({"category": "Page Title", "text": title})
        
        # Get main headings
        for heading in soup.find_all(['h1', 'h2'], limit=3):
            text = heading.get_text(strip=True)
            if text and len(text) > 5:
                examples.append({"category": "Heading", "text": text})
        
        # Get potential product info
        price_pattern = re.compile(r'\$\s*[\d,]+\.?\d*')
        for element in soup.find_all(['span', 'div', 'p'], limit=50):
            text = element.get_text(strip=True)
            if text and price_pattern.search(text):
                examples.append({"category": "Price Information", "text": text})
                break
        
        # Get paragraph text
        for para in soup.find_all('p', limit=5):
            text = para.get_text(strip=True)
            if text and len(text) > 20:  # Reasonable paragraph length
                examples.append({"category": "Paragraph Content", "text": text})
                break
        
        # Get link text
        link_texts = []
        for link in soup.find_all('a', limit=10):
            text = link.get_text(strip=True)
            if text and len(text) > 5 and text not in link_texts:
                link_texts.append(text)
        if link_texts:
            examples.append({"category": "Link Content", "text": link_texts[0]})
        
        # Show the examples without mentioning HTML structure
        shown = 0
        for example in examples:
            if shown >= 5:  # Limit to 5 examples
                break
            text = example["text"]
            if len(text) > 60:
                text = text[:60] + "..."
            print(f"{shown+1}. {example['category']}: {text}")
            shown += 1
        
        if not examples:
            print("Couldn't extract specific examples. The page may have unusual structure.")
        
        # Process first page
        keywords = data_type.lower().split()
        page_results = process_data_by_type(soup, keywords)
        all_results.extend(page_results)
        pages_scraped += 1
        
        # Find next page if pagination is enabled
        if enable_pagination:
            next_page_url = find_next_page_link(soup, current_url)
        else:
            next_page_url = None
        
        # Scrape additional pages if available and pagination is enabled
        while enable_pagination and next_page_url and pages_scraped < max_pages:
            # Add a delay between requests to be nice to the server
            time.sleep(random.uniform(1, 3))
            
            page_results, next_page_url = scrape_page(next_page_url, keywords)
            all_results.extend(page_results)
            pages_scraped += 1
            
            print(f"Scraped page {pages_scraped} of {max_pages} maximum")
        
        return all_results
    
    except Exception as e:
        print(f"Error in scraping process: {str(e)}")
        return all_results

# Step 2: Ask user what kind of data they want
data_type = input("\nWhat kind of data do you need from this website? (e.g., 'product prices', 'article titles', 'contact information'): ")

# Step 3: Start the scraping process
print(f"\nScraping for: {data_type}")
results = scrape_with_options(url, data_type)

# Handle results
if not results:
    print("No data found that matches your request.")
    exit(1)

df = pd.DataFrame(results)
df.to_excel("scraped_data.xlsx", index=False)
print(f"✅ Found {len(results)} items from {pages_scraped} pages. Data saved to 'scraped_data.xlsx'")

# Print proxy usage summary if enabled
if use_proxy:
    print(f"Proxy servers were used to avoid detection.")