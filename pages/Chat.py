import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
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
    
    /* Chat Container Styling */
    .chat-container {
        border: 1px solid #e5e7eb;
        border-radius: var(--rounded-lg);
        padding: 1.5rem;
        margin-top: 1.5rem;
        background-color: #ffffff;
        box-shadow: var(--shadow-md);
    }
    
    /* Message Bubble Styling */
    .user-message {
        background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
        color: #1e3a8a;
        padding: 1rem 1.25rem;
        border-radius: 1rem 1rem 0.25rem 1rem;
        margin-bottom: 1rem;
        display: inline-block;
        max-width: 85%;
        box-shadow: var(--shadow-sm);
        font-weight: 500;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #064e3b;
        padding: 1rem 1.25rem;
        border-radius: 1rem 1rem 1rem 0.25rem;
        margin-bottom: 1rem;
        display: inline-block;
        max-width: 85%;
        box-shadow: var(--shadow-sm);
        position: relative;
        border-left: 4px solid var(--primary-color);
    }

    /* Loading Animation */
    .loading {
        display: flex;
        align-items: center;
        margin: 1.25rem 0;
        padding: 0.5rem 1rem;
        background-color: #f3f4f6;
        border-radius: var(--rounded-md);
        width: fit-content;
    }
    
    .loading-dot {
        height: 0.75rem;
        width: 0.75rem;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        margin-right: 0.5rem;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dot:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .loading-dot:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Feature Boxes */
    .features-grid {
        display: grid;
        gap: 1.25rem;
    }
    
    .feature-box {
        background: white;
        border-radius: var(--rounded-lg);
        padding: 1.5rem;
        transition: all 0.3s ease;
        height: 100%;
        border: 1px solid #e5e7eb;
        box-shadow: var(--shadow-sm);
    }
    
    .feature-box:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-5px);
        border-color: var(--primary-light);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-box h3 {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: var(--text-color);
    }
    
    .feature-box p {
        color: var(--text-light);
        line-height: 1.5;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: white;
        padding: 1.5rem;
        border-radius: var(--rounded-lg);
        box-shadow: var(--shadow-md);
    }
    
    /* Expander Customization */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--primary-color);
    }
    
    /* Footer */
    footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: var(--text-light);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c5c5c5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a3a3a3;
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .feature-box, .chat-container {
            background-color: #1f2937;
            border-color: #374151;
        }
        
        .feature-box h3 {
            color: white;
        }
        
        .feature-box p, .sub-header {
            color: #9ca3af;
        }
        
        .stTextInput input, .stTextArea textarea {
            background-color: #111827;
            border-color: #374151;
            color: white;
        }
        
        .loading {
            background-color: #1f2937;
        }
        
        .user-message {
            background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            color: #bfdbfe;
        }
        
        .ai-message {
            background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
            color: #d1fae5;
        }
    }
</style>
""", unsafe_allow_html=True)

# Create app header with improved styling
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; margin-bottom: 2rem;">
    <h1 class="main-header">DataForage AI Chat</h1>
    <p class="sub-header">Analyze any website content with AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

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
        # URL input (now optional)
        url = st.text_input("Website URL (optional):", placeholder="https://example.com")
        
        # Question input
        question = st.text_area("Your question:", 
                               placeholder="Ask about a website or any general question",
                               height=100)
        
        # Chat submission
        if st.button("Ask AI"):
            if not question:
                st.error("Please enter a question")
            else:
                # Add user message to chat history
                user_message = f"Question: {question}" + (f"\nWebsite: {url}" if url else "\nUsing Google Search")
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Display loading indicator
                with st.container():
                    st.markdown('<div class="loading"><div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div></div>', unsafe_allow_html=True)
                    
                    try:
                        # Initialize Gemini API using the correct method
                        api_key = os.getenv("GEMINI_API_KEY")
                        genai.configure(api_key=api_key)
                        
                        # Create model instance - use the latest model that supports Google Search
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        start_time = time.time()
                        
                        # Determine which mode to use based on URL presence
                        if url:
                            # URL-specific question
                            prompt = f"{question} from this URL: {url}"
                            
                            # Standard generation config
                            generation_config = {
                                "temperature": 0.7,
                                "top_p": 0.95,
                                "top_k": 64,
                                "candidate_count": 1,
                                "max_output_tokens": 2048,
                            }
                            
                            # Call the Gemini API with the prompt
                            response = model.generate_content(
                                prompt,
                                generation_config=generation_config
                            )
                        else:
                            # Use Google Search functionality
                            try:
                                # Create a safety settings object
                                safety_settings = {
                                    "HARASSMENT": "BLOCK_NONE",
                                    "HATE": "BLOCK_NONE",
                                    "SEXUAL": "BLOCK_NONE",
                                    "DANGEROUS": "BLOCK_NONE",
                                }
                                
                                # Configure generation settings
                                generation_config = {
                                    "temperature": 0.7,
                                    "top_p": 0.95,
                                    "top_k": 64,
                                    "candidate_count": 1,
                                    "max_output_tokens": 2048,
                                }
                                
                                # Call the model with the web search capability
                                # The model will automatically perform web search for the query
                                response = model.generate_content(
                                    question,
                                    generation_config=generation_config,
                                    safety_settings=safety_settings,
                                    tools=[{"web_search": {}}]  # Enable web search through tools parameter
                                )
                                print("Web search query sent successfully")
                            except Exception as search_error:
                                print(f"Web search error: {search_error}")
                                # Fallback to regular query without web search
                                response = model.generate_content(
                                    f"Please answer this question to the best of your ability without web search: {question}",
                                    generation_config=generation_config
                                )
                                print("Falling back to regular query without web search")
                        
                        end_time = time.time()
                        
                        # Extract the response text safely
                        if hasattr(response, 'text'):
                            response_text = response.text
                            if not response_text:
                                response_text = "The AI generated an empty response. Please try rephrasing your question."
                        else:
                            # Alternative way to extract text for newer API versions
                            try:
                                response_text = response.candidates[0].content.parts[0].text
                                if not response_text:
                                    response_text = "The AI generated an empty response. Please try rephrasing your question."
                            except:
                                response_text = "Error: Could not extract text from the AI response."
                        
                        # Print to console for debugging
                        print(f"AI Response: {response_text[:100]}...")
                        
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
                    # For AI responses, process them through Streamlit's markdown renderer
                    with st.container():
                        st.markdown("<div class='ai-message'>", unsafe_allow_html=True)
                        st.write(msg["content"])  # Using st.write instead of markdown for better rendering
                        st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add a button to clear chat history
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.subheader("Features")
        
        st.markdown("""
        <div class="features-grid">
            <div class="feature-box">
                <div class="feature-icon">🔍</div>
                <h3>Web Browsing</h3>
                <p>AI can access and analyze website content in real-time</p>
            </div>
            
            <div class="feature-box">
                <div class="feature-icon">🤖</div>
                <h3>AI Analysis</h3>
                <p>Powered by Google's Gemini 2.0 for intelligent insights</p>
            </div>
            
            <div class="feature-box">
                <div class="feature-icon">⚡</div>
                <h3>Real-time Answers</h3>
                <p>Get immediate answers without manual searching</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("DataForage © 2025 | Made with Streamlit and Google Gemini")