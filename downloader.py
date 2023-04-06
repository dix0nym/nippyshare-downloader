import json
import re
from pathlib import Path
import argparse

import requests
from bs4 import BeautifulSoup as bs

BASE_URL = "https://nippyshare.com"
HEADER = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def isAllowed(name, whitelist):
    tmp = name.lower().split(".")
    if tmp:
        ext = tmp[-1]
        return ext in whitelist
    return False 

def parse_item(session, url):
    soup = get_soup(session, url)
    name = soup.select_one("div.container > ul > li").text.replace("Name: ", "")
    dl_button = soup.select_one("div.container > h2 > a.btn.btn-info")
    download_url = dl_button["href"]
    download_url = "https:" + download_url if download_url.startswith("//") else download_url
    return name, download_url

def get_items(session, url):
    soup = get_soup(session, url)
    return [ BASE_URL + i["href"] for i in soup.select("li.list-group-item > a")]

def get_soup(session, url):
    rq = session.get(url)
    if rq.status_code != 200:
        print(f"failed to get {url} - {rq.status_code}")
        return -1
    return bs(rq.text, 'html.parser')

def download_item(session, url, path):
    r = session.get(url, allow_redirects=True, stream=True)
    if r.status_code == 200:
        with path.open('wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        print(f"\t[-] download failed for {url} with {r.status_code}")
        
def process_item(session, url, output, whitelist):
    print(f"[+] parsing {url}")
    name, dl = parse_item(session, url)
    if not isAllowed(name, whitelist):
        print(f"\t[-] {name}: extension not allowed ({', '.join(whitelist)})")
        return name, dl
    filename = get_valid_filename(name)
    path = output.joinpath(filename)
    if path.exists():
        print(f"\t[-] {name} already exists => skip")
        return name, dl
    print(f"[+] downloading {dl}")
    download_item(session, dl, path)
    return name, dl

def process_category(session, items, info, output, whitelist):
    for url in items:
        if url in info:    
            print(f"\t[-] {url}: already downloaded => skip")
            continue
        name, dl = process_item(session, url, output, whitelist)
        info[url] = {"name": name, "url": dl}

def main():
    parser = argparse.ArgumentParser(description="Simple Nippyshare downloader")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--category', choices=["latest", "popular"], help="download all files in a category")
    group.add_argument('-u', '--url', help="nippyshare url to download")
    parser.add_argument('-w', '--whitelist', nargs='*', help="whitelisted extensions as 'ext1 ext2 ext3'", default=['rar', 'zip', 'pdf', 'epub', '7z'])
    parser.add_argument('-o', '--output', type=Path, default=Path("./output/"), help="output directory for downloads. Will be created if not exists." )
    args = parser.parse_args()
    
    # create output dir
    if not args.output.exists():
        args.output.mkdir(exist_ok=True, parents=True)
    
    # setup session
    session = requests.Session()
    session.headers.update(HEADER)    
    
    # handle single url
    if args.url:
        process_item(session, args.url, args.output, args.whitelist)
    # handle category
    if args.category:
        info_path = Path("info.json")
        info = json.load(info_path.open('r')) if info_path.exists() else {}
        items = get_items(session, f"{BASE_URL}/{args.category}.html")
        print(f"[+] getting {args.category}")
        process_category(session, items, info, args.output, args.whitelist)
        # save downloaded urls to file
        with info_path.open('w+') as f:
            json.dump(info, f, indent=4, sort_keys=True)
    print("[+] done")
   
if __name__ == "__main__":
    main()
