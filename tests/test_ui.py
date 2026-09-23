import os
from bs4 import BeautifulSoup

def test_dark_mode_theme():
    # Parse the HTML file
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    body = soup.find('body')
    assert body is not None, "Body tag not found"
    
    # Check that body has dark-mode class
    classes = body.get('class', [])
    assert 'dark-mode' in classes, f"Expected 'dark-mode' in body classes, got {classes}"