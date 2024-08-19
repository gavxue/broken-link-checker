# Broken Link Checker 🔍

A web application that automates broken link detection for UWaterloo webpages. Compatible with WCMS 3 sites only.

Web-based version of [previous script](https://github.com/gavxue/broken-link-automation).

## Tech Stack
- Jinja templateing for the frontend
- Flask for the backend
- BeautifulSoup4 module for web-scraping
- SocketIO for client-server communication
- Render (previous Heroku) for deployment

## How to Use
Visit the [webpage](https://ceeit-link-checker.onrender.com/) and follow the instructions. Note: it will take some time to startup since Render shuts down apps after inactivity.

## Future Improvements
- scale for more users (current deployment can only run one execution at a time)
- more error handling
- better detection algorithm
