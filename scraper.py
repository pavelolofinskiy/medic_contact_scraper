from bs4 import BeautifulSoup
import requests

def links_scraper(pages_to_scrape=150):
    base_url = 'https://www.dasoertliche.de/?zvo_ok=0&buc=2249&plz=&quarter=&district=&ciid=&kw=Sport%C3%A4rzte&ci=&kgs=&buab=71100098&zbuab=&form_name=search_nat&recFrom='
    scrape_pages = [1] + [i for i in range(26, pages_to_scrape + 1, 25)]
    links = []
    for page_num in scrape_pages:
        url = f'{base_url}{page_num}'
        print(url)
        response = requests.get(url=url)
        soup = BeautifulSoup(response.text, 'lxml')
        parent = soup.find('div', class_='clearfix')

        link_elements = parent.find_all('a', class_='hitlnk_name')
        for element in link_elements:
            link_element = element.get('href')
            links.append(link_element)
        return links

links_scraper(pages_to_scrape=150)
def contact_scraper():
    links = links_scraper(pages_to_scrape=150)  # Get a list of links
    scraped_results = []  # Create a list to store scraped results
    
    for link in links:
        response = requests.get(url=link)
        soup = BeautifulSoup(response.text, 'lxml')
        parent = soup.find('div', class_='clearfix detailpage')

        result = {}

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

        # Check if the result is already in the scraped_results list
        if result not in scraped_results:
            scraped_results.append(result)
    for element in scraped_results:
        print(element)

contact_scraper()