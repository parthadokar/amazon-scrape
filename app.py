import csv
import requests
from bs4 import BeautifulSoup

def scrape_product_listing_pages(url, pages):
    all_products = []

    for page in range(1, pages + 1):
        page_url = f"{url}&page={page}"
        resp = requests.get(page_url)
        soup = BeautifulSoup(resp.content, 'html.parser')

        products = soup.find_all('div', {'data-component-type': 's-search-result'})

        for product in products:
            product_data = {}

            # Extract product details
            product_name = product.find('span', {'class': 'a-size-medium'})
            product_price = product.find('span', {'class': 'a-price-whole'})
            product_rating = product.find('span', {'class': 'a-icon-alt'})
            product_reviews = product.find('span', {'class': 'a-size-base'})

            if product_name:
                product_data['Product Name'] = product_name.text.strip()
            if product_price:
                product_data['Product Price'] = product_price.text.strip()
            if product_rating:
                product_data['Rating'] = product_rating.text.strip()
            if product_reviews:
                product_data['Number of Reviews'] = product_reviews.text.strip()

            product_url = product.find('a', {'class': 'a-link-normal'})
            if product_url:
                product_data['Product URL'] = 'https://www.amazon.in' + product_url['href']

            all_products.append(product_data)

    return all_products

def scrape_product_details(products):
    all_product_details = []

    for product in products:
        if 'Product URL' in product:
            product_url = product['Product URL']
            resp = requests.get(product_url)
            soup = BeautifulSoup(resp.content, 'html.parser')

            product_details = {}

            product_description = soup.find('div', {'id': 'productDescription'})
            product_asin = soup.find('th', string='ASIN')
            product_manufacturer = soup.find('th', string='Manufacturer')

            if product_description:
                product_details['Description'] = product_description.text.strip()
            if product_asin:
                product_details['ASIN'] = product_asin.find_next('td').text.strip()
            if product_manufacturer:
                product_details['Manufacturer'] = product_manufacturer.find_next('td').text.strip()

            product_details.update(product)
            all_product_details.append(product_details)
            print("Scraped product:", product_details['Product Name'].encode('utf-8', 'ignore').decode('utf-8'))

    return all_product_details


def export_to_csv(data, filename):
    keys = set().union(*data)  

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

#Scraping product listing pages
url = "https://www.amazon.in/s?k=bags&ref=sr_pg_1"
pages = 20
product_listings = scrape_product_listing_pages(url, pages)

# Scraping product details
product_details = scrape_product_details(product_listings)

# Exporting data to CSV
filename = "products.csv"
export_to_csv(product_details, filename)