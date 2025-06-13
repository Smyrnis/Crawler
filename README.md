# Web Crawler with MongoDB Storage

This is a responsible and respectful web crawler written in Python. It uses `requests` and `BeautifulSoup` to scrape web content, and stores extracted URLs, text content, and HTML attributes in MongoDB collections.

> ⚠️ **Note**: This tool must be used in compliance with `robots.txt` and not for illegal or unethical purposes.

## Features

- Obeys `robots.txt` using Python's `urllib.robotparser`
- Supports crawling depth configuration
- Stores:
  - Visited URLs
  - Page text content
  - HTML tag attributes
- Uses Breadth-First Search (BFS) for link traversal
- MongoDB integration

## Requirements

- Python 3.7+
- MongoDB running locally (`mongodb://localhost:27017/`)

## Install Dependencies

```bash
pip install -r requirements.txt
