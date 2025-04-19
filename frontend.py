import streamlit as st
st.write('AI WEB APP')
st.write('This is a simple web app to demonstrate the use of Streamlit.')
url = st.text_input('Enter a URL to scrape:')
if st.button('Scrape'):
    st.write(f'Scraping the URL: {url}')