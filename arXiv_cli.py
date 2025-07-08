import sys
import subprocess

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

# Ensure required packages
install_if_missing('requests')
install_if_missing('feedparser')
install_if_missing('rich')

import requests
from requests.exceptions import RequestException
import feedparser
from rich import print

def search(search_query):
    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    start = 0
    max_results = 5     # retreive the first 5 results

    query = f'search_query=all:{search_query}&sortBy=relevance&start={start}&max_results={max_results}'
    url = base_url + query

    # perform a GET request using the base_url and query
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()     # Raise error on bad status codes
    except RequestException as e:
        print(f"Network error! Details: {e}")
        exit(1)

    # parse the response using feedparser
    feed = feedparser.parse(response.content)

    # print out feed information
    print(f'Feed title: {feed.feed.get("title")}')
    print(f'Feed last updated: {feed.feed.get("updated")}')

    # print opensearch metadata
    print(f'Total results for this query: {feed.feed.get("opensearch_totalresults")}')
    print(f'Items per page for this query: {feed.feed.get("opensearch_itemsperpage")}')
    print(f'Start index for this query: {feed.feed.get("opensearch_startindex")}')

    # Run through each entry, and print out information
    for entry in feed.entries:
        print('\n=== e-print metadata ===')
        print(f'arXiv ID: {entry.id.split("/abs/")[-1]}')
        print(f'Published: {entry.published}')
        print(f'Title: {entry.title}')
        
        # Authors
        try:
            authors = ', '.join(author.name for author in entry.authors)
            print(f'Authors: {authors}')
        except AttributeError:
            print(f'Author: {entry.get("author")}')

        # Optional affiliation
        affiliation = entry.get('arxiv_affiliation')
        if affiliation:
            print(f'First author affiliation: {affiliation}')

        # get the links to the abs page and pdf for this e-print
        for link in entry.links:
            if link.rel == 'alternate':
                print(f'abs page link: {link.href}')
            elif link.get('title') == 'pdf':
                print(f'pdf link: {link.href}')
        
        # The journal reference, comments and primary_category sections live under the arxiv namespace
        print(f'Journal reference: {entry.get("arxiv_journal_ref", "No journal ref found")}')
        print(f'Comments: {entry.get("arxiv_comment", "No comment found")}')
        
        # Get primary category
        primary_category = entry.tags[0]['term'] if entry.tags else 'N/A'
        print(f'Primary category: {primary_category}')
        
        # Lets get all the categories
        all_categories = ', '.join(tag['term'] for tag in entry.tags) if entry.tags else 'N/A'
        print(f'All categories: {all_categories}')
        
        # The abstract is in the <summary> element
        print(f'Abstract: {entry.summary}')


print("\n[cyan]Press Ctrl+C to quit[/cyan]")

while True:
    
    usrinput = input("\nWhat would you like to find on arXiv?\n")
    search(usrinput)
