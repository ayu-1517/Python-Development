import requests
from bs4 import BeautifulSoup
import csv
import asyncio
import aiohttp

# Define the base URL and the number of pages to scrape
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
num_pages = 20
num_products_per_page = 10  # Assuming 10 products per page
num_products_to_fetch = 200

# Initialize an empty list to store the product data
product_data = []

async def fetch_product_info(session, product_url):
    async with session.get(product_url) as response:
        html_content = await response.text()
        soup = BeautifulSoup(html_content, 'html.parser')
        product_description = soup.find('div', {'id': 'productDescription'}).text.strip() if soup.find('div', {'id': 'productDescription'}) else 'N/A'
        asin_tag = soup.find('th', string='ASIN') if soup.find('th', string='ASIN') else None
        asin = asin_tag.find_next('td').text.strip() if asin_tag else 'N/A'
        manufacturer_tag = soup.find('th', string='Manufacturer') if soup.find('th', string='Manufacturer') else None
        manufacturer = manufacturer_tag.find_next('td').text.strip() if manufacturer_tag else 'N/A'
        
        return product_description, asin, manufacturer

async def scrape_data():
    async with aiohttp.ClientSession() as session:
        for page in range(1, num_pages + 1):
            url = base_url + str(page)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers:
                if len(product_data) >= num_products_to_fetch:
                    break
                
                product_url = "https://www.amazon.in" + container.find('a', class_='a-link-normal')['href']
                product_name = container.find('span', class_='a-text-normal').text
                product_price = container.find('span', class_='a-price-whole').text
                rating = container.find('span', class_='a-icon-alt').text if container.find('span', class_='a-icon-alt') else 'N/A'
                num_reviews = container.find('span', class_='a-size-base').text if container.find('span', class_='a-size-base') else 'N/A'

                product_description, asin, manufacturer = await fetch_product_info(session, product_url)

                product_info = {
                    'Product URL': product_url,
                    'Product Name': product_name,
                    'Product Price': product_price,
                    'Rating': rating,
                    'Number of Reviews': num_reviews,
                    'Description': product_description,
                    'ASIN': asin,
                    'Manufacturer': manufacturer
                }

                product_data.append(product_info)

asyncio.run(scrape_data())

# Export the scraped product data to a CSV file
csv_filename = 'amazon_products.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Manufacturer']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerows(product_data)

print(f'Data has been successfully exported to {csv_filename}')
