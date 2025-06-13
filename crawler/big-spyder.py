# Based on the robots.txt not all the websites are crawlable
# The script provided is not provided for illigal use.
# Must be used with the regulations of the robots.txt that are provided by google.com

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib.robotparser
import time
from datetime import datetime, timezone

# Connection to a mongodb database.
client = MongoClient("mongodb://localhost:27017/")
db = client['web_crawler']
urls_collection = db['urls']
texts_collection = db['texts']
attributes_collection = db['attributes']

robots_cache = {}

def load_visited_urls():
    try:
        with open('visited_urls.txt', 'r') as f:#opens/creates a txt file that writes the parsed urls so it will not parse them again.
            visited = set(f.read().splitlines())
    except FileNotFoundError:
        visited = set()
    return visited

def save_visited_urls(visited):
    with open('visited_urls.txt', 'w') as f:
        f.write('\n'.join(visited))

def is_allowed_to_crawl(url, user_agent='MyCrawler'):
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    if parsed.netloc not in robots_cache:
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(base_url)
            rp.read()
            robots_cache[parsed.netloc] = rp
        except Exception as e:
            print(f"Could not check robots.txt for {url}: {e}")
            robots_cache[parsed.netloc] = None
    
    if robots_cache[parsed.netloc] is None:
        return False
    
    return robots_cache[parsed.netlot].can_fetch(user_agent, url)

def extract_and_save_data(url, response, depth, collection_name):
    soup = BeautifulSoup(response.text, 'html.parser')

    #This is the schema of the database how they will be saved.
    urls_collection.insert_one({
        "url": url,
        "status": response.status_code,
        "depth": depth,
        "timestamp": datetime.now(timezone.utc)
    })
    
    if collection_name == 'texts':
        text_content = soup.get_text(separator=' ', strip=True)
        texts_collection.insert_one({
            "url": url,
            "text": text_content,
            "timestamp": datetime.now(timezone.utc)
        })
    elif collection_name == 'attributes':
        for element in soup.find_all(True):
            if element.attrs:
                attributes_collection.insert_one({
                    "url": url,
                    "tag": element.name,
                    "attributes": element.attrs,
                    "timestamp": datetime.now(timezone.utc)
                })

def crawl_with_bfs(url, depth, visited, collection_name):
    queue = [(url, depth)]  
    
    while queue:
        current_url, current_depth = queue.pop(0)  
        
        if current_url in visited or current_depth == 0:
            continue  
        
        visited.add(current_url)
        print(f"Crawling URL for {collection_name.capitalize()}: {current_url}")

        headers = {'User-Agent': 'MyCrawler'}
        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code == 200:
                extract_and_save_data(current_url, response, current_depth, collection_name)
                
                soup = BeautifulSoup(response.text, 'html.parser')  

                links = soup.find_all('a', href=True)
                for link in links:
                    full_url = urllib.parse.urljoin(current_url, link['href'])
                    if full_url not in visited:
                        queue.append((full_url, current_depth - 1))  
                time.sleep(1)  
            else:
                print(f"Failed to retrieve page: {current_url} (Status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Request error while crawling {current_url}: {e}")
        
    save_visited_urls(visited)

def crawl_all(url, depth=2):
    visited = load_visited_urls()
    crawl_with_bfs(url, depth, visited, 'texts')
    crawl_with_bfs(url, depth, visited, 'attributes')
# The user get asked for the url that he wants to crawl.
# Also he get asked by the depth that the crawl he wants to go in.
if __name__ == "__main__":
    start_url = input("Please enter the URL of the website you want to crawl: ")
    crawl_depth = int(input("Please enter the depth level for crawling (e.g., 2): "))
    crawl_all(start_url, crawl_depth)
# Be responsible for the depth as the user that you will take. Avoid deep crawiling to prevent server overload.
# Be respectful to the owners of the websites.
