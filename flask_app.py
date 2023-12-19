from flask import Flask, request, render_template
import logging

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        # Extract data from form
        product_name = request.form.get('productName')
        manufacturer = request.form.get('manufacturer')
        key_claims_product = request.form.get('keyClaimsProduct')
        key_claims_category = request.form.get('keyClaimsCategory')
        experts = request.form.get('experts')
        studies = request.form.get('studies')
        other_input = request.form.get('otherInput')
        urls = request.form.get('urls')

        data = {
            'productName': product_name,
            'manufacturer': manufacturer,
            'key_claims_prod':key_claims_product,
            'key_claims_category': key_claims_category,
            'experts':experts,
            'studies':studies,
            'other_input':other_input,
            'urls':urls,
        }
        logging.info("Sending data to API: %s", data)

        # TODO: Send data to API
        API_ENDPOINT_URL = 'http://127.0.0.1:8000/scrape-url'
        response = requests.post(API_ENDPOINT_URL, json=data)
        if response.status_code == 200:
            response_data = response.json()
            paragraphs = response_data.get('paragraphs', [])
            links = response_data.get('links', [])

            # Pass the data to the template
            return render_template('success.html', paragraphs=paragraphs, links=links)
        else:
            # Handle error or invalid response
            logging.error("API call failed with status code: %s", response.status_code)
            # You can render an error page or pass an error message to the template
            return render_template('error.html', error_message="Failed to get data from API.")

    


if __name__ == '__main__':
    app.run(debug=True)
