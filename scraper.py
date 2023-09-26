import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def links_scraper(pages_to_scrape=2476):
    base_url = 'https://www.dasoertliche.de/?zvo_ok=0&buc=2249&plz=&quarter=&district=&ciid=&kw=Sport%C3%A4rzte&ci=&kgs=&buab=71100098&zbuab=&form_name=search_nat&recFrom='
    scrape_pages = [1] + [i for i in range(26, pages_to_scrape + 1, 25)]

    links = []
    with requests.Session() as session:
        for page_num in scrape_pages:
            url = f'{base_url}{page_num}'
            print(url)
            response = session.get(url=url)
            soup = BeautifulSoup(response.text, 'lxml')
            parent = soup.find('div', class_='clearfix')

            link_elements = parent.find_all('a', class_='hitlnk_name')
            for element in link_elements:
                link_element = element.get('href')
                links.append(link_element)
    
    return links

def scrape_contact(link):
    result = {}
    with requests.Session() as session:
        response = session.get(url=link)
        soup = BeautifulSoup(response.text, 'lxml')
        parent = soup.find('div', class_='clearfix detailpage')

        title_element = parent.find('div', class_='name').find('h1')
        result['title'] = title_element.text.strip() if title_element else None

        site_element = parent.find('a', class_='www')
        result['site'] = site_element.text.strip() if site_element else None

        result['mail'] = None
        try:
            mail = parent.find('a', class_='mail').find('span')
            result['mail'] = mail.text
        except (AttributeError, ValueError):
            pass
        
        result['phone_num'] = None
        try:
            phone = parent.find('table', class_='det_numbers').find('span')
            result['phone_num'] = phone.text
        except (AttributeError, ValueError):
            pass
            
        address_element = parent.find('div', class_='det_address').next_element
        address_text = address_element.text.strip() if address_element else None
        address_text = address_text.replace('\xa0', ' ')
        result['address'] = address_text
        
    return result

def contact_scraper():
    links = links_scraper(pages_to_scrape=2476) 
    scraped_results = []  
    unique_results = set()  
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_contact, links))
        scraped_results.extend(results)

    for result in scraped_results:
        result_tuple = tuple(result.items())
        unique_results.add(result_tuple)

    unique_results = [dict(result_tuple) for result_tuple in unique_results]

    with open('scraped_results.csv', mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['title', 'site', 'mail', 'phone_num', 'address']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()  

        for result in unique_results:
            writer.writerow(result)

if __name__ == "__main__":
    contact_scraper()