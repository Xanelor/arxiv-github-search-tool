## arXiv Search Tools

A simple Python-based project to search and display results from arXiv.org using their public API.

Includes:
- A command-line interface (CLI) script
- A Flask-based web app with a clean HTML interface

Requirements:
- Python 3.7+
- Internet connection
- arXiv API (public, no key needed)

All required Python packages are automatically installed if missing:
- requests
- feedparser
- rich
- flask (for web version)

Proxy Note:

These scripts use an example HTTP proxy to avoid geo-restrictions:
> http://205.198.65.77:80

Feel free to edit or remove the proxy settings as needed.

Proxy reliability is not guaranteed.

Thank you to arXiv for use of its open access interoperability.
