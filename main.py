import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64
import io
import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np
from collections import defaultdict

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
    .main-header {
        font-size: 2.5rem;
        color: #10b981;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .stButton button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #047857;
    }
    .tag-container {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #d1d5db;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .results-container {
        margin-top: 2rem;
        border-top: 1px solid #d1d5db;
        padding-top: 2rem;
    }
    .insight-container {
        background-color: #f8fafc;
        border-left: 4px solid #10b981;
        padding: 16px;
        border-radius: 4px;
        margin: 20px 0;
    }
    .dark-mode .insight-container {
        background-color: #1e293b;
        border-left: 4px solid #10b981;
    }
    .format-options {
        background-color: #f0fdf4;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }
    .dark-mode .format-options {
        background-color: #0f3123;
    }
</style>
""", unsafe_allow_html=True)

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

# URL input section
with st.container():
    url = st.text_input("Enter the URL to scrape:", value=st.session_state.url)
    analyze_button = st.button("Analyze Page")

    if analyze_button and url:
        st.session_state.url = url
        with st.spinner("Analyzing website..."):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    st.error(f"Failed to retrieve page. Status code: {response.status_code}")
                else:
                    soup = BeautifulSoup(response.content, "html.parser")
                    st.session_state.soup = soup
                    
                    # Extract all unique tags
                    all_tags = set([tag.name for tag in soup.find_all() if tag.name is not None])
                    st.session_state.tags = sorted(all_tags)
                    
                    st.success("Website successfully analyzed!")
            except Exception as e:
                st.error(f"Error occurred: {e}")

# Tag selection section
if st.session_state.tags:
    with st.container():
        st.subheader("Available Tags")
        st.markdown('<div class="tag-container">', unsafe_allow_html=True)
        
        # Create columns for the tags to display in multiple columns
        cols = st.columns(3)
        selected_tags = []
        
        # Distribute tags among columns
        for i, tag in enumerate(st.session_state.tags):
            col_index = i % 3
            with cols[col_index]:
                if st.checkbox(f"<{tag}>", key=f"tag_{tag}"):
                    selected_tags.append(tag)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scrape button
        if st.button("Scrape Selected Tags"):
            if not selected_tags:
                st.warning("Please select at least one tag to scrape.")
            else:
                with st.spinner("Scraping data..."):
                    results = []
                    
                    for tag in selected_tags:
                        for el in st.session_state.soup.find_all(tag):
                            text = el.get_text(strip=True)
                            if text:
                                results.append({"Tag": tag, "Text": text})
                    
                    if not results:
                        st.warning("No data found for the selected tags.")
                    else:
                        df = pd.DataFrame(results)
                        st.session_state.df = df
                        
                        # Create reformatted version with tags as columns
                        original_df, reformatted_df = reformat_for_excel(df)
                        st.session_state.df_reformatted = reformatted_df
                        
                        st.success(f"Successfully scraped {len(results)} items!")

# Results display section
if st.session_state.df is not None and not st.session_state.df.empty:
    with st.container():
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