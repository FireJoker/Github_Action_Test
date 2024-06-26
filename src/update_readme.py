import requests
import datetime
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

def update_readme(readme_path, new_content, marker_start, marker_end):
    """
    Updates a section of the README file marked by specific comments.

    Args:
        readme_path (str):  The path to the README file.
        new_content (str):  The new content to insert between the markers.
        marker_start (str): The start marker comment.
        marker_end (str):   The end marker comment.
    """
    
    with open(readme_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the start and end positions of the markers
    start = content.find(marker_start) + len(marker_start)
    end = content.find(marker_end)
    
    if start == -1 or end == -1 or start > end:
        raise ValueError("Markers not found or misordered in README file.")
    
    # Replace the content between the markers
    updated_content = f"{content[:start]}\n{new_content}\n{content[end:]}"

    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def generate_markdown_table(data):
    """Generates a Markdown table from a list of dictionaries."""
    if not data:
        return ""

    # Extract headers
    headers = data[0].keys()
    header_row = " | ".join(headers)
    separator_row = " | ".join(["---"] * len(headers))
    
    # Extract rows
    rows = []
    for module_info in data:
        row_items = []
        for header in headers:
            value = str(module_info[header])
            if header == 'download_url':
                value = f'[download]({value})'
            row_items.append(value)
        row = " | ".join(row_items)
        rows.append(row)
    
    # Combine into a Markdown table
    table = f"{header_row}\n{separator_row}\n" + "\n".join(rows)
    return table


def read_json_files(directory):
    """Read all json files from given directory."""

    json_data_list = []
    directory_path = Path(directory)
    
    for file_path in directory_path.glob('*.json'):
        try:
            with open(file_path, 'r') as file:
                module = json.load(file)

            if 'repo' in module:
                data = fetch_repo_info(module)
            elif 'url' in module:
                data = fetch_url_info(module)
                
            json_data_list.append(data)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {file_path}.")
    return json_data_list


def fetch_repo_info(module):
    """Fetches the latest release info from a GitHub repository."""
    
    api_url = f"https://api.github.com/repos/{module['repo']}/releases/latest"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        response_info = response.json()
        
        published_at = response_info['published_at']
        published_date = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').date()
        
        assets = response_info['assets']
        url = assets[0]['browser_download_url']
        for patton in module['assetRegex']:
            for asset in assets:
                if re.search(patton, asset['name']):
                    url = asset['browser_download_url']
                    
        latest_release = {
            'module': module['name'],
            'version': response_info['tag_name'],
            'published_at': published_date.strftime('%Y-%m-%d'),
            'download_url': url
        }
        return latest_release
    
    
def fetch_url_info(module):
    """Fetches the release info from a url."""

    response = requests.get(module['url'])
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        version_info = None
        full_url = None
        published_date = None
        
        version_span = soup.find('span', id=lambda t: 'version-ams' in t if t else False)
        if version_span:
            version_info = version_span.get_text(strip=True)
            
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if module['name'] in href:
                full_url = urljoin(module['url'], href)
                
                match = re.search(r'\?(\d{2})\.(\d{2})\.(\d{4})', full_url)
                if match:
                    month,day,year = match.groups()
                    published_date = f'{year}-{month}-{day}'
                
        latest_release = {
            'module': module['name'],
            'version': version_info,
            'published_at': published_date,
            'download_url': full_url
        }
        return latest_release

if __name__ == "__main__":
    json_path = 'src/modules'  # Path to the JSON file
    readme_path = 'README.md'  # Path to the README.md file
    
    # Read JSON file
    data = read_json_files(json_path)
    
    # Generate Markdown table
    table = generate_markdown_table(data)
    
    # Update README.md file
    marker_start = "<!-- recent_releases starts -->"
    marker_end = "<!-- recent_releases ends -->"
    update_readme(readme_path, table,marker_start,marker_end)

