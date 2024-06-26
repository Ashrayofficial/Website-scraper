# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# def get_last_page_number(url):
#     with requests.get(url) as response:
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, 'html.parser')
#             pagination = soup.find('ul', class_='pagination')
#             last_page_element = pagination.find_all('li')[-2]
#             last_page_number = int(last_page_element.text.strip())
#             return last_page_number
#         else:
#             print(f"Failed to fetch the page. Status code: {response.status_code}")
#             return 1  # Default to one page if unable to determine the last page

def extract_hrefs_from_div(url, div_class):
    with requests.get(url) as response:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div_elements = soup.find_all('div', class_=div_class)
            hrefs = [a['href'] for div in div_elements for a in div.find_all('a', href=True)]
            return hrefs
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return []

def clean_data(value):
    # Replace or remove illegal characters from the value
    value = value.replace("", "")  # Replace with an appropriate replacement or remove entirely
    return value

def extract_data_from_link(link):
    with requests.get(link) as response:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            data_elements = soup.find('div', class_='companyDetails').find_all('p')
            data = {}
            for i, element in enumerate(data_elements, start=1):
                key, value = map(str.strip, element.text.split(':', 1))
                data[f"Column{i}"] = clean_data(value)
            return data
        else:
            print(f"Failed to fetch the link. Status code: {response.status_code}")
            return None

def extract_data_from_all_links_page(base_url, page_num, div_class):
    url = f"{base_url}/page:{page_num}"
    hrefs = extract_hrefs_from_div(url, div_class)
    data = [extract_data_from_link(href) for href in hrefs if extract_data_from_link(href) is not None]
    return data

def extract_data_from_all_links(base_url, num_pages, div_class):
    with ThreadPoolExecutor(max_workers= 5) as executor:
        all_data = []
        futures = []
        # Use list comprehension to create a list of futures
        for page_num in range(1, num_pages + 1):
            futures.append(executor.submit(extract_data_from_all_links_page, base_url, page_num, div_class))

        # Use as_completed to iterate over completed futures
        for future in as_completed(futures):
            all_data.extend(future.result())
        return all_data

def save_to_excel(data, excel_filename):
    df = pd.DataFrame(data)
    df.to_excel(excel_filename, index=False)

# Provide base URL
base_url = ""
div_class = "boxDetails bg-white p-3 mt-3"
num_pages = ""  # You can adjust the number of pages you want to scrape

all_data = extract_data_from_all_links(base_url, num_pages, div_class)

# Provide a filename for the Excel file
excel_filename = ""

# Save the data to an Excel file
save_to_excel(all_data, excel_filename)

print(f"Data has been saved to {excel_filename}")
