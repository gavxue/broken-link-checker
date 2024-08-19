# Broken Link Checker 🔍

A web application that automates broken link detection for UWaterloo webpages. Compatible with WCMS 3 sites only.

Web-based version of [previous script](https://github.com/gavxue/broken-link-automation).

## Tech Stack
- Jinja templateing for the frontend
- Flask for the backend
- BeautifulSoup4 module for web-scraping
- SocketIO for client-server communication
- Render (previously Heroku) for deployment

## How to Use
Visit the [webpage](https://ceeit-link-checker.onrender.com/) and follow the instructions. Note: it will take some time to startup since Render shuts down apps after inactivity.

## Future Improvements
- scale for more users (current deployment can only run one execution at a time)
- more error handling
- better detection algorithm

## Images
![image](https://github.com/user-attachments/assets/65ab1873-8c32-4fdc-b82f-be8c9ad33371)
![image](https://github.com/user-attachments/assets/923c3f70-823a-48ab-a810-36f2b5743b96)
