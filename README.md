# DataForage (OrbitCrawl)

<div align="center">
  <img src="dataforage-frontend/public/logo-df.jpg" alt="DataForage Logo" width="200"/>
  <h3>Web Data Extraction Made Simple</h3>
  <p>Extract, transform, and download web data instantly without coding</p>
</div>

## 🚀 Overview

DataForage is a powerful web scraping platform that transforms any website into structured data without requiring programming knowledge. The application intelligently identifies content patterns, tables, and lists, allowing you to extract specific types of data with ease.

**Key features:**

- 🔍 **Intelligent Data Detection**: Automatically identifies and categorizes different types of content
- 📊 **Excel Export**: Download scraped data instantly as formatted Excel spreadsheets
- 🔄 **JavaScript Support**: Handles modern JS-heavy websites with dynamic content
- 🔧 **User-Friendly Interface**: Simple point-and-click data extraction without coding
- 💬 **AI-Powered Insights**: Get intelligent analysis of your scraped data

## 🖥️ Project Structure

The application consists of two main components:

- **Frontend (`dataforage-frontend/`)**: Next.js application providing the user interface
- **Backend (`py-back/`)**: Python-based scraping engine built with FastAPI, BeautifulSoup, and Pandas

## 📋 Requirements

### Backend

- Python 3.9+
- FastAPI
- BeautifulSoup4
- Pandas
- Selenium/ChromeDriver (for JavaScript-rendered sites)
- Other dependencies specified in `py-back/requirements.txt`

### Frontend

- Node.js 18+
- Next.js 14+
- TailwindCSS
- TypeScript

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:

   ```
   cd py-back
   ```

2. Create a virtual environment (recommended):

   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Optional: Create a `.env` file for API keys:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd dataforage-frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

## 🚀 Running the Application

### Start the Backend

1. From the `py-back` directory, run:

   ```
   streamlit run main.py
   ```

   This will start the Streamlit interface.

2. For the API backend (optional):

   ```
   uvicorn api:app --reload
   ```

### Start the Frontend

1. From the `dataforage-frontend` directory, run:

   ```
   npm run dev
   ```

2. Access the application at `http://localhost:3000`

## 📊 Using DataForage

### Basic Usage

1. Enter a URL to scrape
2. DataForage analyzes the page and shows examples of available data
3. Select the type of data you want to extract:
   - Page Titles and Headers
   - Product Information
   - Prices and Costs
   - Contact Information
   - Links and Navigation
   - Article Content
   - Custom Query
4. Click "Extract Data"
5. Download your data as Excel or CSV

### Command-Line Usage

You can also use the Python script directly:

```
python py.py
```

Follow the prompts to:

1. Enter a URL
2. View available data examples
3. Specify the type of data you need
4. Receive your data in an Excel file

## 🧩 Features

- **Intelligent Content Identification**: Automatically detects and categorizes content
- **Natural Language Queries**: Describe the data you want in plain English
- **Excel Export**: Download data in perfectly formatted Excel spreadsheets
- **AI-Powered Analysis**: Get insights about your scraped data
- **Modern Web Support**: Works with JavaScript-heavy websites and dynamic content
- **Privacy-Focused**: All processing happens locally without storing data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions, please open an issue in the GitHub repository.

---

<div align="center">
  Made with ❤️ by RedRanger Team
</div>
