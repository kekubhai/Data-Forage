from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from google.generativeai import types
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Google Gemini API client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ChatRequest(BaseModel):
    url: str
    question: str

# Define response model
class ChatResponse(BaseModel):
    response: str

# Initialize Gemini client
client = genai.Client(api_key=api_key)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_url(chat_request: ChatRequest):
    """Process a chat request that asks a question about a URL."""
    try:
        # Construct the prompt with the URL and question
        prompt = f"{chat_request.question} from this URL: {chat_request.url}"
        
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
        
        # Extract the response text
        response_text = response.candidates[0].content.parts[0].text
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        error_message = str(e)
        # Log the error for server-side debugging
        print(f"Error in chat_with_url: {error_message}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {error_message}")

# For development testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)