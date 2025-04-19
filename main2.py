from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI(
    title="DataForage API",
    description="Extract structured data from any website and return it as Excel",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    """
    Scrape data from a given URL and return it as an Excel file.
    """
    url = request.url
    
    # Headers to avoid being blocked by websites
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Fetch the webpage content
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract domain for naming the sheet
    domain_match = re.search(r'//([^/]+)', url)
    domain = domain_match.group(1) if domain_match else "website"
    domain = domain.replace("www.", "").split('.')[0]
    
    # Create an Excel writer with pandas
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Try to extract tables first
        tables = soup.find_all('table')
        
        if tables:
            # Process all tables found on the page
            for i, table in enumerate(tables[:5]):  # Limit to first 5 tables
                try:
                    df = pd.read_html(str(table))[0]
                    sheet_name = f"Table_{i+1}" if i > 0 else domain
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception:
                    continue
        
        # If no tables or tables extraction failed, try to extract lists
        if not tables or writer.sheets == {}:
            lists = soup.find_all(['ul', 'ol'])
            if lists:
                list_items = []
                for list_tag in lists[:10]:  # Limit to first 10 lists
                    items = list_tag.find_all('li')
                    for item in items:
                        text = item.get_text(strip=True)
                        if text and len(text) > 3:  # Skip empty or very short items
                            list_items.append({"Text": text})
                
                if list_items:
                    list_df = pd.DataFrame(list_items)
                    list_df.to_excel(writer, sheet_name=f"{domain}_Lists", index=False)
        
        # If still no data, extract all paragraphs
        if writer.sheets == {}:
            paragraphs = soup.find_all('p')
            if paragraphs:
                para_texts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:  # Skip empty or very short paragraphs
                        para_texts.append({"Text": text})
                
                if para_texts:
                    para_df = pd.DataFrame(para_texts)
                    para_df.to_excel(writer, sheet_name=f"{domain}_Content", index=False)
                    
        # If we extracted nothing with the above methods, do a generic extraction
        if writer.sheets == {}:
            # Extract all text contents by tag type
            elements = {
                "Headers": soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
                "Links": soup.find_all('a', href=True),
                "Images": soup.find_all('img', alt=True)
            }
            
            for element_type, tags in elements.items():
                if tags:
                    data = []
                    for tag in tags:
                        if element_type == "Links":
                            href = tag.get('href', '')
                            # Make relative URLs absolute
                            if href.startswith('/'):
                                href = f"{response.url.scheme}://{response.url.host}{href}"
                            data.append({
                                "Text": tag.get_text(strip=True),
                                "URL": href
                            })
                        elif element_type == "Images":
                            data.append({
                                "Alt Text": tag.get('alt', ''),
                                "Source": tag.get('src', '')
                            })
                        else:
                            data.append({"Text": tag.get_text(strip=True)})
                    
                    if data:
                        element_df = pd.DataFrame(data)
                        element_df.to_excel(writer, sheet_name=element_type, index=False)
    
    # Check if we have any sheets
    output.seek(0)
    try:
        # Verify the Excel file is valid
        pd.read_excel(output)
        output.seek(0)
    except Exception:
        # If Excel validation fails, provide a fallback sheet
        output = BytesIO()
        df = pd.DataFrame({"Message": ["No structured data found on this page"]})
        df.to_excel(output, index=False)
        output.seek(0)
    
    # Return the Excel file as a download
    filename = f"{domain}_data.xlsx"
    return StreamingResponse(
        output, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)