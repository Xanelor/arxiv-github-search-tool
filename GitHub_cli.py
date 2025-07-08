import sys
import subprocess
import json

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

# Ensure required packages
install_if_missing('requests')
install_if_missing('rich')

import requests
from requests.exceptions import RequestException
from rich import print

def search(search_query, token):

    # Search parameters
    sort = 'relevance'
    github_query = f'topic:{search_query}'

    url = f'https://api.github.com/search/repositories?q={github_query}&sort={sort}'

    headers = {
        'Authorization': f'Token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    repositories = []

    # perform a GET request using the url
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response_json = json.loads(response.text)

        if response.status_code == 200:
            repositories.extend(response_json['items'])

        response.raise_for_status()     # Raise error on bad status codes
    except RequestException as e:
        print(f"Error! Details: {e}")
        exit(1)

    filtered_repos = []

    # Get list of not empty repos
    if repositories is not None:
        for repo in repositories:
            filtered_repos.append(repo)


    if filtered_repos:
        for repo in filtered_repos:
            # print out information
            print(f'\nName: {repo['name']}')
            print(f'URL: {repo['html_url']}')
            print(f'Stars: {repo['stargazers_count']}')
            print(f'Forks: {repo['forks_count']}')
            print(f'Owner: {repo['owner']['login']}\n')



print("\n[cyan]Press Ctrl+C to quit or type 'quit'[/cyan]")
token = ''

while True:

    # Check if token is empty
    while not token:
        token = input("\nInput your GitHub access token: ")
        if not token:
            print("GitHub Access Token is required.")
        elif token == "quit":
            exit(0)

    usrinput = input("\nWhat would you like to find on GitHub?\n")

    # Check if query is empty
    while not usrinput:
        usrinput = input()

    # Close app
    if usrinput == "quit":
        exit(0)

    search(usrinput, token)
