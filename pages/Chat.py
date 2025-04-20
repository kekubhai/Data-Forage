import streamlit as st

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
        font-size: 3em;
        color: #4CAF50;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5em;
        color: #4CAF50;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Remove the old HTML navigation and button navigation as they're not needed
# Streamlit will automatically add sidebar navigation for multi-page apps

st.markdown('<h1 class="main-header">DataForage AI Chat</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask questions about any website content</p>', unsafe_allow_html=True)