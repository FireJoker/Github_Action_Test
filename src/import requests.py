import requests
import datetime
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

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
        row = " | ".join(str(module_info[header]) for header in headers)
        rows.append(row)
    
    # Combine into a Markdown table
    table = f"{header_row}\n{separator_row}\n" + "\n".join(rows)
    return table

def read_all_json_files(directory):
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
            else: 
                return
            
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



def main():
    directory = 'src/modules'  # 目标目录

    # 读取目录中的所有 JSON 文件
    data = read_all_json_files(directory)
    
    table = generate_markdown_table(data)
    # 打印所有 JSON 文件的数据

    print(table)


if __name__ == '__main__':
    main()