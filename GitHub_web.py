import os
import sys
import subprocess
import webbrowser
import threading
import json

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

# Ensure required packages
install_if_missing('flask')
install_if_missing('requests')

import requests
from requests.exceptions import RequestException
from flask import Flask, render_template_string, request

app = Flask(__name__)

#HTML template for web output
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>GitHub Search</title>
  <style>
  body { font-family: Arial, sans-serif; margin: 40px; background-color: #302f39; color: #d8d4fa; }
  .container { max-width: 1000px; margin: auto; background: #1b1a24; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 5px;}
  .entry { border: 1px solid #d8d4fa; padding: 15px; margin-bottom: 20px; border-radius: 5px;}
  .error { color: red; }
  .search-button { padding: 3px 6px; background-color: #8d8aed; color: #1b1a24; border: none; transition: box-shadow 0.3s ease; border-radius: 5px; }
  .search-button:hover { box-shadow: 0px 2px 4px rgba(192,186,245,0.6); }
  .search-button:active { background-color: #656be6; }
  th { padding: 20px; }
  td { padding: 5px; }
  .search { width: 300px; border-radius: 5px; background-color: #302f39; color: #d8d4fa; }
  a {text-decoration: none; color: #8d8aed;}
  a:visited {color: #656be6}
  </style>
</head>
<body>
  <div class="container">
    <h1>GitHub Search Tool</h1>
    <form method="POST">
      <input type="text" name="q" placeholder="Search..." value="{{ query }}" class="search">
      <input type="text" name="token" placeholder="GitHub Access Token" value="{{ token }}" class="search">
      <input type="submit" value="Search" class="search-button">
    </form>

    {% if error %}
      <p class="error">Error: {{ error }}</p>
    {% endif %}

    {% if repositories}
      <div>
        <table class="table-striped">
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>URL</th>
              <th>Stars</th>
              <th>Forks</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            {% set counter = 1 %}

            {% for repo in repositories %}
              <tr>
                <td> {{loop.index}}</td>
                <td>{{ repo['name'] }}</td>
                <td><a href="{{ repo['html_url'] }}" target="_blank">{{ repo['html_url'] }}</a></td>
                <td>{{ repo['stargazers_count'] }}</td>
                <td>{{ repo['forks_count'] }}</td>
                <td>{{ repo['owner']['login'] }}</td>
                {% set counter = counter + 1 %}
              </tr>

            {% endfor %}
          </tbody>
        </table>
      </div>
    {% elif searched %}
        <p>No repositories found.</p>
    {% endif %}
  </div>
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def index():

    # Get Github token for authorization
    token = request.form.get("token", "").strip()

    # Search parameters
    query = request.form.get("q", "").strip()
    sort = 'relevance'
    github_query = f'topic:{query}'

    if not query:
        # Empty form
        return render_template_string(HTML_TEMPLATE, query=query, token=token, repositories=[])
    
    if not token:
        error = "GitHub Access Token is required."
        return render_template_string( HTML_TEMPLATE, query=query, token=token, repositories=[], error=error)

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
        return render_template_string(HTML_TEMPLATE, query=query, token=token, error=str(e))

    filtered_repos = []

    # Get list of not empty repos
    if repositories is not None:
        for repo in repositories:
            filtered_repos.append(repo)

    return render_template_string(HTML_TEMPLATE, query=query, token=token, repositories=filtered_repos, searched=bool(query))




if __name__ == "__main__":
    # Opening webpage
    def open_browser():
        webbrowser.open_new("http://localhost:5000/")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Only in the reloader's child process
        threading.Timer(1, open_browser).start()
    app.run(debug=True)