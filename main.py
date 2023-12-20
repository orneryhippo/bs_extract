from fastapi import FastAPI, HTTPException, Request
from bs4 import BeautifulSoup
import httpx
import logging
from pydantic import BaseModel
from typing import Optional

class ScrapeRequest(BaseModel):
    productName: Optional[str] = None
    manufacturer: Optional[str] = None
    key_claims_prod: Optional[str] = None
    key_claims_category: Optional[str] = None
    experts: Optional[str] = None
    studies: Optional[str] = None
    other_input: Optional[str] = None
    url: Optional[str] = None


# Setting up logging to track application behavior
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initializing the FastAPI application
app = FastAPI()

# Defining a constant for the maximum number of redirects
MAX_REDIRECTS = 1

# @app.post("/scrape-url/")
# async def scrape_url(request: Request):
@app.post("/scrape-url/")
async def scrape_url(request_body: ScrapeRequest):
    url = request_body.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    logging.info(f'URL: {url}')

    # body = await request.body()
    # logging.info(f"Raw request body: {body}")
    # # Extracting the URL from the form data
    # form_data = await request.form()
    # url = form_data.get("urls")
    # logging.info(f'URLs: {url}')
    # Validating the URL
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Setting up an HTTP client with redirect handling
    try:
        with httpx.Client(follow_redirects=True, max_redirects=MAX_REDIRECTS) as client:
            # Fetching the content from the URL
            response = client.get(url)

            # Logging redirect information, if any
            if response.is_redirect:
                logging.info(f'Redirected to {response.url}')

            # Parsing the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text=soup.get_text()
            # Extracting paragraphs and links
            # paragraphs = soup.p.get_text() # [p.get_text() for p in soup.find_all('p')]

            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Returning the scraped data
            return {"paragraphs":full_text.strip(), "links": links}

    except httpx.TooManyRedirects:
        # Handling the case where too many redirects occur
        logging.error(f'Too many redirects encountered for URL: {url}')
        raise HTTPException(status_code=400, detail="Too many redirects")

    except Exception as e:
        # General error handling
        logging.error(f'Error processing URL: {url}, Error: {str(e)}')
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def index():
    return {"content":"hello"}