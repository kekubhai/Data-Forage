import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
import requests
from bs4 import BeautifulSoup
import time

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="DataForage Chat",
    page_icon="💬",
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
    .chat-container {
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        background-color: #f9fafb;
    }
    .user-message {
        background-color: #e0f2fe;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin-bottom: 10px;
        display: inline-block;
        max-width: 80%;
    }
    .ai-message {
        background-color: #f0fdf4;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin-bottom: 10px;
        display: inline-block;
        max-width: 80%;
        border-left: 4px solid #10b981;
    }
    .feature-box {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 15px;
        color: #10b981;
    }
    .loading {
        display: flex;
        align-items: center;
        margin: 20px 0;
    }
    .loading-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        background-color: #10b981;
        margin-right: 8px;
        animation: pulse 1.5s infinite ease-in-out;
    }
    .loading-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    .loading-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes pulse {
        0%, 100% {
            transform: scale(0.8);
            opacity: 0.6;
        }
        50% {
            transform: scale(1);
            opacity: 1;
        }
    }
    .nav-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 1rem;
    }
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0 0.5rem;
        border-radius: 0.375rem;
        font-weight: 500;
    }
    .nav-item-active {
        background-color: #10b981;
        color: white !important;
    }
    .nav-item:hover:not(.nav-item-active) {
        background-color: #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

# Add navigation menu at the top
st.markdown("""
<div class="nav-container">
    <a href="main.py" class="nav-item">🔍 Web Scraper</a>
    <a href="chat.py" class="nav-item nav-item-active">💬 AI Chat</a>
</div>
""", unsafe_allow_html=True)

# Alternate navigation using Streamlit's built-in functionality
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Switch to Web Scraper"):
        # This will redirect to main.py
        st.switch_page("main.py")

st.markdown('<h1 class="main-header">DataForage AI Chat</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask questions about any website content</p>', unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'gemini_key_set' not in st.session_state:
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    st.session_state.gemini_key_set = bool(api_key)

# Handle API key input if not set
if not st.session_state.gemini_key_set:
    with st.container():
        st.warning("⚠️ Gemini API key not found in environment variables.")
        api_key = st.text_input("Enter your Google Gemini API key:", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            st.session_state.gemini_key_set = True
            st.success("API key set successfully! You can now use the chat feature.")
            st.rerun()

# Main chat interface
if st.session_state.gemini_key_set:
    # Sidebar for explaining how it works
    with st.sidebar:
        st.title("How It Works")
        st.markdown("""
        **DataForage AI Chat** uses Google's Gemini 2.0 model with web browsing capabilities to analyze websites and answer your questions.
        
        ### Examples:
        - "What are the best courses on this website?"
        - "Summarize the main features of this product"
        - "Find pricing information on this page"
        - "Extract contact details from this website"
        - "Compare different options mentioned on this page"
        
        ### Tips:
        - Be specific with your questions
        - Include the full URL to the website
        - One question at a time works best
        """)
        
        # Add a simple FAQ section
        with st.expander("FAQ"):
            st.markdown("""
            **Q: Is this the same as the web scraper?**  
            A: No. The web scraper extracts structured data in a spreadsheet format. This chat feature lets you ask natural language questions about website content.
            
            **Q: Can it access private or login-protected websites?**  
            A: No, it can only access publicly available content.
            
            **Q: How accurate is the information?**  
            A: The AI provides information based on the content it can access. Always verify critical information.
            """)
    
    # Main chat container
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input("Website URL:", placeholder="https://example.com")
        
        # Question input
        question = st.text_area("Your question about this website:", 
                               placeholder="What are the main topics/products/features on this website?",
                               height=100)
        
        # Chat submission
        if st.button("Ask AI"):
            if not url:
                st.error("Please enter a website URL")
            elif not question:
                st.error("Please enter a question")
            else:
                # Add user message to chat history
                user_message = f"Question: {question}\nWebsite: {url}"
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Display loading indicator
                with st.container():
                    st.markdown('<div class="loading"><div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div></div>', unsafe_allow_html=True)
                    
                    try:
                        # Initialize Gemini API
                        api_key = os.getenv("GEMINI_API_KEY")
                        client = genai.Client(api_key=api_key)
                        
                        # Construct the prompt with the URL and question
                        prompt = f"{question} from this URL: {url}"
                        
                        start_time = time.time()
                        # Call the Gemini API with web search capability
                        response = client.models.generate_content(
                            model='gemini-2.0-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                tools=[types.Tool(
                                    google_search=types.GoogleSearchRetrieval
                                )]
                            )
                        )
                        end_time = time.time()
                        
                        # Extract the response text
                        response_text = response.candidates[0].content.parts[0].text
                        
                        # Add AI response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                        # Display processing time
                        processing_time = end_time - start_time
                        st.caption(f"Processed in {processing_time:.2f} seconds")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Sorry, I encountered an error while processing your request: {str(e)}"
                        })
                    
                    # Clear the loading indicator and rerun to display messages
                    st.rerun()
        
        # Display chat messages
        if st.session_state.messages:
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ai-message'>{msg['content']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add a button to clear chat history
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.subheader("Features")
        
        # Feature boxes
        with st.container():
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">🔍</div>
                <h3>Web Browsing</h3>
                <p>AI can access and analyze website content in real-time</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">🤖</div>
                <h3>AI Analysis</h3>
                <p>Powered by Google's Gemini 2.0 for intelligent insights</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">⚡</div>
                <h3>Real-time Answers</h3>
                <p>Get immediate answers without manual searching</p>
            </div>
            """, unsafe_allow_html=True)
            
    # Add a separator
    st.markdown("---")
    
    # Add a link back to the scraper
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Web Scraper"):
            # Use streamlit navigation to main.py
            st.switch_page("main.py")
    
    with col2:
        st.markdown("Need structured data instead? Use our web scraper to extract data into Excel.")

# Footer
st.markdown("---")
st.caption("DataForage © 2025 | Made with Streamlit and Google Gemini")