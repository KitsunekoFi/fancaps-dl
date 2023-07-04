import argparse
import concurrent.futures
import os
import re
import requests
import urllib.request
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('url', nargs='?', help='URL untuk dibuka')
parser.add_argument('--bulk', help='File txt yang berisi daftar URL untuk diproses')
parser.add_argument('--user-agent', default='Mozilla/5.0', help='User Agent untuk digunakan')
parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of worker threads to use for downloading files simultaneously')
parser.add_argument('--output-folder', type=str, default=None, help='Folder to save downloaded images')
parser.add_argument('--interval', type=int, default=1, help='Interval of images to download')
parser.add_argument('--same-folder', action='store_true', help='Save all images to the same folder')
parser.add_argument('--each-folder', action='store_true', default=True, help='Save images to separate subfolders for each URL') # Set default value to True
args = parser.parse_args()

user_agent = args.user_agent
headers = {'User-Agent': user_agent}

def get_links(url):
    links = []
    next_page_url = url
    page_num = 1
    anime_name = None
    print(f"Scraping List Episode from Link: {url}")
    while next_page_url:
        req = urllib.request.Request(next_page_url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, "html.parser")
        for link in soup.find_all("a", href=re.compile("^https://fancaps.net/anime/episodeimages.php\?")):
            href = link.get("href")
            if href:
                match = re.search(r"https://fancaps.net/anime/episodeimages.php\?\d+-(.*?)/", href)
                if match:
                    if not anime_name:
                        anime_name = match.group(1)
                    if anime_name == match.group(1):
                        links.append(href)
        next_page = soup.find("a", title="Next Page")
        if next_page:
            page_num += 1
            next_page_url = url + f"&page={page_num}"
        else:
            next_page_url = None
    return links

if args.url:
    # Check if the URL already contains an episode number
    match = re.search(r"https://fancaps.net/anime/episodeimages.php\?\d+-.*/Episode_\d+", args.url)
    if match:
        urls = [args.url]
    else:
        urls = get_links(args.url)
    filename = 'episode_links.txt'
elif args.bulk:
    with open(args.bulk, 'r') as f:
        urls = f.read().splitlines()
    filename = 'pagination_links.txt'
else:
    raise ValueError('Harap tentukan URL atau --bulk')

if os.path.exists(filename):
    os.remove(filename)

with open(filename, 'w') as f:
    for url in urls:
        f.write(url + '\n')

for url in urls:

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    with open(filename, 'a') as f:
        f.write(url.split('&page=')[0] + '\n')

    pagination_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and '&page=' in href:
            pagination_links.append('https://fancaps.net/anime/' + href)

    with open(filename, 'a') as f:
        for link in pagination_links:
            f.write(link + '\n')

    max_page = 1
    for link in pagination_links:
        page_num = int(link.split('&page=')[1])
        if page_num > max_page:
            max_page = page_num

    prev_page_content = None
    while True:
        next_page_url = url.split('&page=')[0] + '&page=' + str(max_page + 1)
        page = requests.get(next_page_url, headers=headers)
        if page.content == prev_page_content:
            break
        prev_page_content = page.content
        soup = BeautifulSoup(page.content, 'html.parser')
        new_links_found = False
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and '&page=' in href:
                full_href = 'https://fancaps.net/anime/' + href
                with open(filename, 'r') as f:
                    existing_links = f.read().splitlines()
                if full_href not in existing_links:
                    with open(filename, 'a') as f:
                        f.write(full_href + '\n')
                    new_links_found = True
                    page_num = int(href.split('&page=')[1])
                    if page_num > max_page:
                        max_page = page_num
        if not new_links_found:
            break

# Remove duplicate links from the file and sort them in ascending order
with open(filename, 'r') as f:
    links = f.read().splitlines()
unique_links = list(set(links))
unique_links.sort()
with open(filename, 'w') as f:
    for link in unique_links:
        f.write(link + '\n')

def download_file(url, filename):
    new_url = url.replace("https://fancaps.net/anime/picture.php?/", "https://ancdn.fancaps.net/")
    new_url += ".jpg"
    req = urllib.request.Request(new_url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Downloading image from URL: {new_url}")
    with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
        data = response.read()
        out_file.write(data)

input_urls = []
with open(filename, 'r') as f:
    input_urls = f.read().splitlines()

# Determine the output folder based on the input URL or the current working directory
if not args.output_folder:
    match = re.search(r"https://fancaps.net/anime/episodeimages.php\?(\d+-.*?)/", args.url)
    if match:
        args.output_folder = match.group(1)
    else:
        args.output_folder = os.getcwd()

# Create the output folder if it doesn't exist
if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)

for input_url in input_urls:

    pages = []

    urls = []
    urls.append(input_url)

    image_urls = []
    for url in urls:

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')

        for a in soup.find_all('a', href=True):
            if a['href'].startswith("https://fancaps.net/anime/picture.php?/"):
                image_urls.append(a['href'])

    with open('download.txt', 'w') as f:
        for url in image_urls:
            f.write(url + '\n')

    # Only download images at the specified interval
    image_urls = image_urls[::args.interval]

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        for url in image_urls:
            # Determine local file name to save image
            new_url = url.replace("https://fancaps.net/anime/picture.php?/", "https://ancdn.fancaps.net/")
            new_url += ".jpg"
            
            # Determine the subfolder to save the image based on the selected option
            if args.each_folder:
                subfolder_name = input_url.split('/')[-1].split('&')[0]
                subfolder_path = os.path.join(args.output_folder, subfolder_name)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                filename = os.path.join(subfolder_path, new_url.split('/')[-1])
                print(f"Downloading {subfolder_name} from {url}")
            else:
                filename = os.path.join(args.output_folder, new_url.split('/')[-1])
            
            executor.submit(download_file, url, filename)

print("Done")
