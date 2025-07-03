import os
import sys
import subprocess
import webbrowser
import threading

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

# Ensure required packages
install_if_missing('flask')
install_if_missing('requests')
install_if_missing('feedparser')


from flask import Flask, render_template_string, request
import requests
import feedparser
from requests.exceptions import RequestException

app = Flask(__name__)

#HTML template for web output
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>arXiv Search</title>
  <style>
  body { font-family: Arial, sans-serif; margin: 40px; background-color: #302f39; color: #d8d4fa; }
  .container { max-width: 800px; margin: auto; background: #1b1a24; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 5px;}
  .entry { border: 1px solid #d8d4fa; padding: 15px; margin-bottom: 20px; border-radius: 5px;}
  .error { color: red; }
  .search-button { padding: 3px 6px; background-color: #8d8aed; color: #1b1a24; border: none; transition: box-shadow 0.3s ease; border-radius: 5px; }
  .search-button:hover { box-shadow: 0px 2px 4px rgba(192,186,245,0.6); }
  .search-button:active { background-color: #656be6; }
  .search { width: 300px; border-radius: 5px; background-color: #302f39; color: #d8d4fa; }
  a {text-decoration: none; color: #8d8aed;}
  a:visited {color: #656be6}
  </style>
</head>
<body>
  <div class="container">
    <h1>arXiv Search Results</h1>
    <form method="get">
      <input type="text" name="q" placeholder="Search..." value="{{ query }}" class="search">
      <input type="submit" value="Search" class="search-button">
    </form>

    {% if error %}
      <p class="error">Error: {{ error }}</p>
    {% endif %}

    {% if feed %}
      <p>Last Updated: {{ feed.feed.updated }}</p>
      <p>Total Results: {{ feed.feed.get('opensearch_totalresults') }}</p>

      {% for entry in feed.entries %}
        <div class="entry">
          <h3>{{ entry.title }}</h3>
          <p><strong>arXiv ID:</strong> {{ entry.id.split('/abs/')[-1] }}</p>
          <p><strong>Published:</strong> {{ entry.published }}</p>

          <p><strong>Authors:</strong>
            {% if entry.authors %}
              {% for author in entry.authors %}
                {{ author.name }}{% if not loop.last %}, {% endif %}
              {% endfor %}
            {% else %}
              {{ entry.get("author", "N/A") }}
            {% endif %}
          </p>

          <p><strong>Primary Category:</strong>
            {% if entry.tags %}
              {{ entry.tags[0]['term'] }}
            {% else %}
              N/A
            {% endif %}
          </p>

          <p><strong>All Categories:</strong>
            {% if entry.tags %}
              {% for tag in entry.tags %}
                {{ tag.term }}{% if not loop.last %}, {% endif %}
              {% endfor %}
            {% else %}
              N/A
            {% endif %}
          </p>

          <p><strong>Abstract:</strong> {{ entry.summary }}</p>

          <p>
            <a href="{{ entry.link }}">abs page</a>
            {% for link in entry.links %}
              {% if link.get('title') == 'pdf' %}
                | <a href="{{ link.href }}">PDF</a>
              {% endif %}
            {% endfor %}
          </p>

          <p><strong>Journal Reference:</strong> {{ entry.get("arxiv_journal_ref", "No journal ref found") }}</p>
          <p><strong>Comments:</strong> {{ entry.get("arxiv_comment", "No comment found") }}</p>
        </div>
      {% endfor %}
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    
    # Search parameters
    query = request.args.get("q", "")
    start = 0
    max_results = 5   # retreive the first 5 results

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    api_query = f'search_query={query}&start={start}&max_results={max_results}'
    url = base_url + api_query

    #Using proxy to avoid geo-restrictions
    proxy = {"http": "http://205.198.65.77:80"}

    # perform a GET request using the base_url and query
    try:
        response = requests.get(url, proxies=proxy, timeout=10)
        response.raise_for_status()    # Raise error on bad status codes

        # parse the response using feedparser
        feed = feedparser.parse(response.content)
        return render_template_string(HTML_TEMPLATE, feed=feed, query=query, error=None)
    
    except RequestException as e:
        return render_template_string(HTML_TEMPLATE, feed=None, query=query, error=str(e))

if __name__ == "__main__":
    # Opening webpage
    def open_browser():
        webbrowser.open_new("http://localhost:5000/")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Only in the reloader's child process
        threading.Timer(1, open_browser).start()
    app.run(debug=True)