# nippyshare-downloader

Simple file downloader for [nippyshare](https://nippyshare.com) in Python.

## Installation

```
# clone repo 
$ git clone https://github.com/dix0nym/nippyshare-downloader

# or, only download single file
$ wget https://raw.githubusercontent.com/dix0nym/nippyshare-downloader/main/downloader.py

# install required pip packages
$ pip install -r requirements.txt
# or as command
$ pip install requests bs4
```

## Usage

```bash
$  python .\nippy.py -h
usage: nippy.py [-h] (-c {latest,popular} | -u URL) [-w [WHITELIST ...]] [-o OUTPUT]

Simple Nippyshare downloader

options:
  -h, --help            show this help message and exit
  -c {latest,popular}, --category {latest,popular}
                        download all files in a category
  -u URL, --url URL     nippyshare url to download
  -w [WHITELIST ...], --whitelist [WHITELIST ...]
                        whitelisted extensions as 'ext1 ext2 ext3'
  -o OUTPUT, --output OUTPUT
                        output directory for downloads. Will be created if not exists.
```

## How does it work?

1. Keeping cookies in a Sessions
2. requesting by `requests` and parsing using `BeautifulSoup`
3. download parsed file-link