from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from typing import List, Dict, Optional
import numpy as np
from collections import defaultdict

app = FastAPI(title="DataForage API", 
              description="Web scraping API for extracting structured data from websites")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: HttpUrl
    tags: Optional[List[str]] = None  # Optional list of specific tags to scrape

class AnalyzeResponse(BaseModel):
    available_tags: List[str]

# Function to reformat DataFrame for better Excel structure
def reformat_for_excel(df):
    """
    Restructures data so tags become column headers
    Returns reformatted dataframe
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
            
        return pd.DataFrame(new_data)
    
    # If dataframe structure is different, return original
    return df

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_webpage(request: ScrapeRequest):
    """Analyze a webpage and return available HTML tags to scrape"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        response = requests.get(str(request.url), headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve page. Status code: {response.status_code}")
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract all unique tags
        all_tags = set([tag.name for tag in soup.find_all() if tag.name is not None])
        
        return {"available_tags": sorted(all_tags)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing page: {str(e)}")

@app.post("/scrape")
async def scrape_webpage(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Scrape data from a webpage and return as JSON"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        response = requests.get(str(request.url), headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve page. Status code: {response.status_code}")
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        results = []
        
        # If no specific tags are provided, get all tags
        tags_to_scrape = request.tags if request.tags else [tag.name for tag in soup.find_all() if tag.name is not None]
        
        for tag in tags_to_scrape:
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text:
                    results.append({"Tag": tag, "Text": text})
        
        if not results:
            raise HTTPException(status_code=404, detail="No data found for the selected tags.")
            
        return {"data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping page: {str(e)}")

@app.post("/scrape/excel")
async def scrape_to_excel(request: ScrapeRequest):
    """Scrape data from a webpage and return as Excel file"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        response = requests.get(str(request.url), headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve page. Status code: {response.status_code}")
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        results = []
        
        # If no specific tags are provided, get all tags
        tags_to_scrape = request.tags if request.tags else [tag.name for tag in soup.find_all() if tag.name is not None]
        
        for tag in tags_to_scrape:
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text:
                    results.append({"Tag": tag, "Text": text})
        
        if not results:
            raise HTTPException(status_code=404, detail="No data found for the selected tags.")
            
        # Create dataframe
        df = pd.DataFrame(results)
        
        # Reformat to put tags as columns
        reformatted_df = reformat_for_excel(df)
        
        # Create Excel file
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            reformatted_df.to_excel(writer, index=False, sheet_name="Scraped Data")
            
            # Get the xlsxwriter objects
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
            
            # Apply formatting to header
            for col_num, value in enumerate(reformatted_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Auto-adjust column widths
            for i, col in enumerate(reformatted_df.columns):
                max_len = max(
                    reformatted_df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, max_len)
        
        excel_buffer.seek(0)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=scraped_data.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Excel file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)