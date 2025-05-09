import streamlit as st
import requests
from bs4 import BeautifulSoup

import base64
import io
import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np
from collections import defaultdict
import random
from urllib.parse import urlparse, urljoin

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page config
st.set_page_config(
    page_title="DataForage Web Scraper",
    page_icon="🔍",
    layout="wide"
)

# Header with styling
st.markdown("""
<style>
    /* Global Styles and Variables */
    :root {
        --primary-color: #10b981;
        --primary-dark: #047857;
        --primary-light: #d1fae5;
        --secondary-color: #3b82f6;
        --accent-color: #8b5cf6;
        --text-color: #1f2937;
        --text-light: #6b7280;
        --bg-light: #f9fafb;
        --bg-dark: #111827;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --rounded-sm: 0.375rem;
        --rounded-md: 0.5rem;
        --rounded-lg: 1rem;
    }

    /* Page Layout Improvements */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Brand Header */
    .main-header {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
        line-height: 1.1;
    }
    
    .sub-header {
        font-size: 1.25rem;
        color: var(--text-light);
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    /* Input Elements Styling */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid #e5e7eb;
        border-radius: var(--rounded-md);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.625rem 1.5rem;
        border-radius: var(--rounded-md);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }
    
    .stButton button:active {
        transform: translateY(1px);
        box-shadow: var(--shadow-sm);
    }
    
    /* Tag container */
    .tag-container {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #e5e7eb;
        border-radius: var(--rounded-lg);
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* Results container */
    .results-container {
        margin-top: 2.5rem;
        border-top: 1px solid #e5e7eb;
        padding-top: 2rem;
    }
    
    /* Insight container */
    .insight-container {
        background: linear-gradient(to right, #f0fdf4, white);
        border-left: 6px solid var(--primary-color);
        border-radius: var(--rounded-md);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-md);
    }
    
    /* Format options */
    .format-options {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: var(--rounded-md);
        padding: 1.25rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    /* Select box styling */
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: var(--rounded-md);
        border-color: #e5e7eb;
        transition: all 0.2s;
    }
    
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: var(--primary-color);
    }
    
    /* Checkbox styling */
    .stCheckbox label span[aria-hidden="true"] div::after {
        border-color: var(--primary-color) !important;
    }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: var(--primary-color) !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--text-color);
        background-color: #f9fafb;
        border-radius: var(--rounded-md);
        padding: 0.5rem 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        color: var(--primary-color);
    }
    
    /* Table/DataFrame Styling */
    [data-testid="stDataFrame"] table {
        border-collapse: collapse;
        width: 100%;
    }
    
    [data-testid="stDataFrame"] th {
        background: linear-gradient(to right, var(--primary-color), var(--primary-dark));
        color: white !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        text-align: center;
        padding: 0.75rem 1rem;
    }
    
    [data-testid="stDataFrame"] td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e7eb;
        font-size: 0.95rem;
    }
    
    [data-testid="stDataFrame"] tr:nth-child(even) td {
        background-color: #f9fafb;
    }
    
    [data-testid="stDataFrame"] tr:hover td {
        background-color: #f0fdf4;
    }
    
    /* Footer styling */
    footer {
        margin-top: 3rem;
        padding-top: 1.25rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: var(--text-light);
        font-size: 0.9rem;
    }
    
    footer a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }
    
    footer a:hover {
        text-decoration: underline;
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .format-options, .streamlit-expanderHeader {
            background-color: #1f2937;
        }
        
        [data-testid="stDataFrame"] tr:nth-child(even) td {
            background-color: #1f2937;
        }
        
        [data-testid="stDataFrame"] tr:hover td {
            background-color: #374151;
        }
        
        .insight-container {
            background: linear-gradient(to right, #065f46, #1f2937);
            color: #d1fae5;
        }
    }
</style>
""", unsafe_allow_html=True)

# Create app header with improved styling
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; margin-bottom: 2rem;">
    <h1 class="main-header">DataForage Web Scraper</h1>
    <p class="sub-header">Turn any website into structured data in seconds</p>
</div>
""", unsafe_allow_html=True)

# Add navigation menu at the top
st.markdown("""
<div class="nav-container">
    <a href="main.py" class="nav-item nav-item-active">🔍 Web Scraper</a>
    <a href="chat.py" class="nav-item">💬 AI Chat</a>
</div>
""", unsafe_allow_html=True)

# Add navigation using Streamlit's built-in functionality
col1, col2 = st.columns([1, 5])
with col1:
    # This button is no longer needed with Streamlit's native page navigation
    # if st.button("Switch to AI Chat"):
    #     st.switch_page("chat.py")
    pass

st.markdown('<h1 class="main-header">DataForage Web Scraper</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Extract data from any website in seconds</p>', unsafe_allow_html=True)

# Function to reformat DataFrame for better Excel structure
def reformat_for_excel(df):
    """
    Restructures data so tags become column headers
    Returns original and restructured dataframe
    """
    # If we only have Tag and Text columns, we restructure
    if set(df.columns) == {"Tag", "Text"}:
        # Group by tag and collect text values
        tag_groups = defaultdict(list)
        
        for _, row in df.iterrows():
            tag_groups[row['Tag']].append(row['Text'])
        
        # Find the maximum count for any tag to determine number of rows
        max_rows = max([len(texts) for texts in tag_groups.values()])
        
        # Create a new dataframe with tags as column headers
        new_data = {}
        for tag, texts in tag_groups.items():
            # Pad the list with NaNs if needed
            padded_texts = texts + [np.nan] * (max_rows - len(texts))
            new_data[tag] = padded_texts
            
        reformatted_df = pd.DataFrame(new_data)
        return df, reformatted_df
    
    # If dataframe structure is different, return original
    return df, df

# Function to get insights from Gemini API
def get_gemini_insights(dataframe, original_df=None, user_prompt=""):
    """
    Use Google's Gemini API to analyze data and provide insights based on user prompt
    """
    if not GEMINI_API_KEY:
        return "Error: Gemini API key not found in environment variables. Please add GEMINI_API_KEY to your .env file."
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate comprehensive data context
        data_description = ""
        
        # Include information about the original structure
        if original_df is not None and not original_df.equals(dataframe):
            data_description += f"""
            Original data structure:
            - Columns: {', '.join(original_df.columns)}
            - Sample rows: 
            {original_df.head(3).to_string(index=False)}
            
            The data has been restructured for better Excel readability with HTML tags as column headers:
            """
        
        # Add reformatted data info
        sample_data = dataframe.head(5).to_string()
        column_info = str(dataframe.dtypes)
        data_shape = f"Rows: {dataframe.shape[0]}, Columns: {dataframe.shape[1]}"
        
        data_description += f"""
        Data shape: {data_shape}
        Column names: {', '.join(dataframe.columns)}
        Column types: {column_info}
        Sample data:
        {sample_data}
        """
        
        # Create prompt with context about the data
        if not user_prompt:
            system_prompt = f"""
            You are a data analysis expert reviewing website scraped content. 
            {data_description}
            
            This data was scraped from a website. Each column represents content from HTML tags of that name.
            
            Please provide insights on:
            1. What kind of content seems to be in each tag/column
            2. How this Excel data is structured and optimized for analysis
            3. The best ways to work with this data in spreadsheet tools
            4. Potential insights or patterns visible in the extracted content
            
            Focus on practical, actionable advice for working with this data.
            """
        else:
            system_prompt = f"""
            You are a data analysis expert reviewing website scraped content.
            {data_description}
            
            This data was scraped from a website. Each column represents content from HTML tags of that name.
            
            User question: {user_prompt}
            
            Please provide detailed, helpful insights based on the user's question, focusing on the actual content
            visible in the data. Base your answers on what you can see in the sample data provided.
            """
        
        # Generate response
        response = model.generate_content(system_prompt)
        return response.text
    
    except Exception as e:
        return f"Error getting insights: {str(e)}"

# Create session state to store data between reruns
if 'tags' not in st.session_state:
    st.session_state.tags = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_reformatted' not in st.session_state:
    st.session_state.df_reformatted = None
if 'url' not in st.session_state:
    st.session_state.url = ""
if 'soup' not in st.session_state:
    st.session_state.soup = None
if 'insights' not in st.session_state:
    st.session_state.insights = ""

# After URL input section, add pagination and proxy options
with st.container():
    url = st.text_input("Enter the URL to scrape:", value=st.session_state.url)
    
    # Advanced options in an expandable section
    with st.expander("Advanced Scraping Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            enable_pagination = st.checkbox("Enable pagination", value=False, 
                                          help="Scrape multiple pages by automatically detecting and following 'next page' links")
            if enable_pagination:
                max_pages = st.slider("Maximum pages to scrape", min_value=1, max_value=10, value=3,
                                     help="Limit the number of pages to prevent long-running scrapes")
        
        with col2:
            use_proxy = st.checkbox("Use proxy servers", value=False,
                                  help="Route requests through proxy servers to avoid detection or IP blocking")
            if use_proxy:
                proxy_option = st.radio("Proxy source:", ["Default proxies", "Custom proxies"])
                if proxy_option == "Custom proxies":
                    custom_proxies = st.text_area("Enter proxy servers (one per line, format: http://ip:port)",
                                                placeholder="http://103.152.112.162:80\nhttp://193.239.86.249:3128")
                    if custom_proxies:
                        proxies = [p.strip() for p in custom_proxies.split("\n") if p.strip()]
                    else:
                        proxies = []
                else:
                    proxies = ["http://103.152.112.162:80", "http://193.239.86.249:3128", "http://159.65.77.168:8585"]
        
        # Add user agent rotation option
        rotate_user_agents = st.checkbox("Rotate user agents", value=True,
                                      help="Cycle through different browser user-agents to avoid detection")
    
    analyze_button = st.button("Analyze Page")

    if analyze_button and url:
        st.session_state.url = url
        with st.spinner("Analyzing website..."):
            try:
                # Store options in session state
                st.session_state.pagination = {
                    "enabled": enable_pagination,
                    "max_pages": max_pages if enable_pagination else 1
                }
                
                st.session_state.proxy = {
                    "enabled": use_proxy,
                    "proxies": proxies if use_proxy else []
                }
                
                st.session_state.user_agents = {
                    "rotate": rotate_user_agents,
                    "agents": [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
                    ]
                }
                
                # Prepare request headers
                headers = {
                    'User-Agent': random.choice(st.session_state.user_agents["agents"]) if rotate_user_agents else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
                }
                
                # Make request with proxy if enabled
                if use_proxy and proxies:
                    proxy = random.choice(proxies)
                    response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=10)
                    st.session_state.used_proxy = proxy
                else:
                    response = requests.get(url, headers=headers)
                    st.session_state.used_proxy = None
                
                if response.status_code != 200:
                    st.error(f"Failed to retrieve page. Status code: {response.status_code}")
                else:
                    soup = BeautifulSoup(response.content, "html.parser")
                    st.session_state.soup = soup
                    
                    # Extract all unique tags
                    all_tags = set([tag.name for tag in soup.find_all() if tag.name is not None])
                    st.session_state.tags = sorted(all_tags)
                    
                    # Check for pagination if enabled
                    if enable_pagination:
                        # Store the current URL for pagination
                        st.session_state.current_url = url
                        
                        # Find potential next page link
                        next_page_patterns = [
                            # Text-based patterns
                            {"element": "a", "text": ["next", "next page", "›", "»", ">"]},
                            # Class-based patterns
                            {"element": "a", "class": ["next", "pagination-next", "next-page"]}
                        ]
                        
                        next_page_url = None
                        base_url = url
                        parsed_url = urlparse(url)
                        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        
                        # Try to find next page link
                        for pattern in next_page_patterns:
                            if "text" in pattern:
                                for text_pattern in pattern["text"]:
                                    for link in soup.find_all(pattern["element"]):
                                        if link.get_text().lower().strip() == text_pattern.lower() and link.has_attr('href'):
                                            next_page_url = urljoin(base_url, link['href'])
                                            break
                            
                            if "class" in pattern:
                                for class_pattern in pattern["class"]:
                                    for link in soup.find_all(pattern["element"], class_=lambda c: c and class_pattern in c.lower()):
                                        if link.has_attr('href'):
                                            next_page_url = urljoin(base_url, link['href'])
                                            break
                        
                        # Check if pagination is available
                        if next_page_url:
                            st.session_state.pagination["next_url"] = next_page_url
                            st.success(f"Website successfully analyzed! Pagination detected - up to {max_pages} pages can be scraped.")
                        else:
                            st.session_state.pagination["next_url"] = None
                            st.success("Website successfully analyzed! No pagination links detected.")
                    else:
                        st.success("Website successfully analyzed!")
            except Exception as e:
                st.error(f"Error occurred: {e}")

# Tag selection section
if st.session_state.tags:
    with st.container():
        st.subheader("What data would you like to extract?")
        
        # Instead of showing tags, ask user what kind of data they want
        data_categories = [
            "Page Titles and Headers",
            "Product Information",
            "Prices and Costs",
            "Contact Information",
            "Links and Navigation",
            "Article Content",
            "Custom Query"
        ]
        
        selected_category = st.selectbox(
            "Select the type of data you're interested in:",
            data_categories
        )
        
        # Custom query option
        if selected_category == "Custom Query":
            custom_query = st.text_input(
                "Describe what data you want to extract:",
                placeholder="E.g., 'product names with prices', 'author names', 'company addresses'"
            )
        
        # Scrape button
        if st.button("Extract Data"):
            with st.spinner("Extracting data..."):
                results = []
                
                # Map user-friendly categories to appropriate tags and extraction logic
                if selected_category == "Page Titles and Headers":
                    header_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']
                    for tag in header_tags:
                        if tag in st.session_state.tags:
                            for el in st.session_state.soup.find_all(tag):
                                text = el.get_text(strip=True)
                                if text:
                                    results.append({"Type": f"Header ({tag})", "Text": text})
                
                elif selected_category == "Product Information":
                    # Look for product-related elements
                    product_classes = ["product", "item", "goods"]
                    # Try various product patterns
                    for el in st.session_state.soup.find_all(class_=lambda c: c and any(p in str(c).lower() for p in product_classes)):
                        name = el.get_text(strip=True)
                        if name:
                            results.append({"Type": "Product", "Text": name})
                    
                    # Also check common product containers
                    for tag in ['div', 'li', 'article']:
                        if tag in st.session_state.tags:
                            for el in st.session_state.soup.find_all(tag):
                                if el.find('img') and (el.find('h3') or el.find('h2')):
                                    text = el.get_text(strip=True)
                                    results.append({"Type": "Product Item", "Text": text[:200]})
                
                elif selected_category == "Prices and Costs":
                    # Price extraction with regex patterns
                    import re
                    price_pattern = re.compile(r'(\$|€|£|\¥|USD|EUR)\s?[\d,.]+|\d+(\.\d{2})?(?=\s*(?:\$|€|£|\¥|USD|EUR))')
                    
                    for tag in ['span', 'div', 'p', 'strong']:
                        if tag in st.session_state.tags:
                            for el in st.session_state.soup.find_all(tag):
                                text = el.get_text(strip=True)
                                if price_pattern.search(text):
                                    results.append({"Type": "Price", "Text": text})
                
                elif selected_category == "Contact Information":
                    # Email regex pattern
                    import re
                    email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
                    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
                    
                    # Check contact info in various tags
                    for tag in ['p', 'div', 'span', 'a', 'address']:
                        if tag in st.session_state.tags:
                            for el in st.session_state.soup.find_all(tag):
                                text = el.get_text(strip=True)
                                if "contact" in text.lower() or email_pattern.search(text) or phone_pattern.search(text):
                                    results.append({"Type": "Contact", "Text": text})
                
                elif selected_category == "Links and Navigation":
                    # Get links
                    if 'a' in st.session_state.tags:
                        for el in st.session_state.soup.find_all('a'):
                            text = el.get_text(strip=True)
                            href = el.get('href', '')
                            if text and href:
                                results.append({"Type": "Link", "Text": text, "URL": href})
                
                elif selected_category == "Article Content":
                    # Article content typically in p tags, sometimes with article container
                    article_container = st.session_state.soup.find('article')
                    
                    if article_container:
                        for p in article_container.find_all('p'):
                            text = p.get_text(strip=True)
                            if text and len(text) > 15:  # Avoid very short paragraphs
                                results.append({"Type": "Article Paragraph", "Text": text})
                    else:
                        # No article container, look for content in p tags
                        for p in st.session_state.soup.find_all('p'):
                            text = p.get_text(strip=True)
                            if text and len(text) > 30:  # Longer threshold for general p tags
                                results.append({"Type": "Paragraph", "Text": text})
                
                elif selected_category == "Custom Query":
                    # Handle custom query with intelligent extraction
                    query_terms = custom_query.lower().split()
                    
                    for tag in st.session_state.tags:
                        for el in st.session_state.soup.find_all(tag):
                            text = el.get_text(strip=True)
                            if text and any(term in text.lower() for term in query_terms):
                                results.append({"Type": f"Custom Match ({tag})", "Text": text})
                
                if not results:
                    st.warning("No data found matching your selection. Try another category or custom query.")
                else:
                    # Create DataFrame with the results
                    if selected_category == "Links and Navigation":
                        df = pd.DataFrame(results)
                    else:
                        # For other categories, standardize to two columns
                        df = pd.DataFrame(results)
                        if "URL" in df.columns:
                            df = df[["Type", "Text", "URL"]]
                        else:
                            df = df[["Type", "Text"]]
                    
                    st.session_state.df = df
                    
                    # Create reformatted version with types as columns
                    original_df, reformatted_df = reformat_for_excel(df)
                    st.session_state.df_reformatted = reformatted_df
                    
                    st.success(f"Successfully extracted {len(results)} items!")

# Results display section
if st.session_state.df is not None and not st.session_state.df.empty:
    with st.container():
        # Above the data display, show scraping statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Items Scraped", len(st.session_state.df))
        
        with col2:
            if hasattr(st.session_state, 'pagination') and st.session_state.pagination.get("enabled"):
                st.metric("Pages Scraped", st.session_state.pagination.get("pages_scraped", 1))
        
        with col3:
            if hasattr(st.session_state, 'used_proxy') and st.session_state.used_proxy:
                st.info(f"Used proxy: {st.session_state.used_proxy}")
        
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.subheader("Scraped Data")
        
        # Display format selection
        st.markdown('<div class="format-options">', unsafe_allow_html=True)
        display_format = st.radio(
            "Select data format:",
            ["Original format", "Tags as columns"],
            help="Choose how to view and export your data"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show the selected data format
        if display_format == "Original format":
            display_df = st.session_state.df
            st.dataframe(display_df)
        else:
            display_df = st.session_state.df_reformatted
            st.dataframe(display_df)
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="scraped_data.csv",
                mime="text/csv",
                key="csv-download"
            )
            
        with col2:
            # Excel export with better formatting
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                display_df.to_excel(writer, index=False, sheet_name="Scraped Data")
                
                # Get the xlsxwriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets["Scraped Data"]
                
                # Add formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#10b981',
                    'color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                # Apply the header format
                for col_num, value in enumerate(display_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Auto-adjust column widths
                for i, col in enumerate(display_df.columns):
                    max_len = max(
                        display_df[col].astype(str).map(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.set_column(i, i, max_len)
            
            st.download_button(
                label="Download Excel",
                data=buffer.getvalue(),
                file_name="scraped_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="excel-download"
            )
        
        # AI Insights Section
        st.subheader("AI Data Insights")
        
        # User prompt for custom questions
        user_prompt = st.text_area("Ask a question about your data (optional):", 
                                  placeholder="E.g., How can I format this data for analysis? What patterns do you notice?")
        
        if st.button("Get AI Insights"):
            with st.spinner("Generating insights..."):
                # Use the currently displayed format for insights
                insights = get_gemini_insights(
                    display_df,
                    original_df=st.session_state.df if display_format == "Tags as columns" else None,
                    user_prompt=user_prompt
                )
                st.session_state.insights = insights
        
        # Display insights
        if st.session_state.insights:
            st.markdown('<div class="insight-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.insights)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
---
Made with ❤️ by DataForage | [GitHub](https://github.com/dataforage) | [Documentation](https://dataforage.ai/docs)
""")