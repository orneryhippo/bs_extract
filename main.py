from fastapi import FastAPI, HTTPException, Request
from bs4 import BeautifulSoup
import httpx
import logging

# Setting up logging to track application behavior
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initializing the FastAPI application
app = FastAPI()

# Defining a constant for the maximum number of redirects
MAX_REDIRECTS = 10

@app.post("/scrape-url/")
async def scrape_url(request: Request):
    # Extracting the URL from the form data
    form_data = await request.form()
    url = form_data.get("url")

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
# from fastapi import FastAPI, HTTPException, Request
# from bs4 import BeautifulSoup
# import httpx
# import logging
# from databases import Database

# # Database configuration
# DATABASE_URL = "postgresql://user:password@localhost/dbname"
# database = Database(DATABASE_URL)

# # Setting up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# # Initializing the FastAPI application
# app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# # Define a constant for the maximum number of redirects
# MAX_REDIRECTS = 10

# @app.post("/scrape-url/")
# async def scrape_url(request: Request):
#     form_data = await request.form()
#     url = form_data.get("url")

#     if not url:
#         raise HTTPException(status_code=400, detail="URL is required")

#     try:
#         with httpx.Client(follow_redirects=True, max_redirects=MAX_REDIRECTS) as client:
#             response = client.get(url)
#             if response.is_redirect:
#                 logging.info(f'Redirected to {response.url}')
#             soup = BeautifulSoup(response.content, 'html.parser')
#             paragraphs = [p.get_text() for p in soup.find_all('p')]
#             links = [a['href'] for a in soup.find_all('a', href=True)]

#             # Save data to database before returning
#             await save_scraped_data(url, paragraphs, links)

#             return {"paragraphs": paragraphs, "links": links}
#     except httpx.TooManyRedirects:
#         logging.error(f'Too many redirects encountered for URL: {url}')
#         raise HTTPException(status_code=400, detail="Too many redirects")
#     except Exception as e:
#         logging.error(f'Error processing URL: {url}, Error: {str(e)}')
#         raise HTTPException(status_code=500, detail="Internal server error")

# async def save_scraped_data(url, paragraphs, links):
#     query = "INSERT INTO your_table_name (url, paragraphs, links) VALUES (:url, :paragraphs, :links)"
#     await database.execute(query, {"url": url, "paragraphs": paragraphs, "links": links})

# Additional routes and logic can be added here...
