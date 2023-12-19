from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse
from bs4 import BeautifulSoup
import httpx
import logging
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



class UrlModel(BaseModel):
    url: str


# Setting up logging to track application behavior
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initializing the FastAPI application
app = FastAPI()

# Defining a constant for the maximum number of redirects
MAX_REDIRECTS = 10

@app.get("/", response_class=HTMLResponse)
async def read_form():
    with open("index.html", 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


from fastapi import Form, Depends

@app.post("/scrape-url/")
async def scrape_url(form_data: UrlModel = Depends(), url: str = Form(None)):
    # Decide which data source to use
    target_url = url if url else form_data.url


# @app.post("/scrape-url/")
# async def scrape_url(request: Request):
#     # Extracting the URL from the form data
#     form_data = await request.form()
    logging.info(f"Form Data: {form_data}")
    # url = form_data.get("url")
    url = target_url
    logging.info(f"URL:{url}")
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

            # Extracting paragraphs and links
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Returning the scraped data
            return {"paragraphs": paragraphs, "links": links}

    except httpx.TooManyRedirects:
        # Handling the case where too many redirects occur
        logging.error(f'Too many redirects encountered for URL: {url}')
        raise HTTPException(status_code=400, detail="Too many redirects")

    except Exception as e:
        # General error handling
        logging.error(f'Error processing URL: {url}, Error: {str(e)}')
        raise HTTPException(status_code=500, detail="Internal server error")
