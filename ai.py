import requests
from bs4 import BeautifulSoup

# Make an HTTP request to the website
url = 'https://www.railyatri.in/'
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract all text from the webpage
    all_text = soup.get_text()
    
    # Print the extracted text
    print(all_text)
else:
    print(f"Error: {response.status_code}")








