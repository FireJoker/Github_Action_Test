import json
import os
import requests

def read_json_file(directory):
    """Reads all JSON file and returns a list of data."""
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data.extend(json.load(file))
    return data

def fetch_github_release_info(repo_url):
    """Fetches the latest release info from a GitHub repository."""
    # Extract owner and repo from the URL
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an error for bad status codes
    release_info = response.json()
    
    return {
        "tag_name": release_info["tag_name"],
        "published_at": release_info["published_at"]
    }

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
    for entry in data:
        row = " | ".join(str(entry[header]) for header in headers)
        rows.append(row)
    
    # Combine into a Markdown table
    table = f"{header_row}\n{separator_row}\n" + "\n".join(rows)
    return table

def update_readme(readme_path, table):
    """Updates the README.md file with the generated table."""
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write("# Data Table\n\n")
        file.write(table)


if __name__ == "__main__":
    json_directory = 'src'  # Path to the JSON file
    readme_path = 'README.md'  # Path to the README.md file
    
    # Read and parse JSON file
    data = read_json_file(json_directory)
    
    # Generate Markdown table
    table = generate_markdown_table(data)
    
    # Update README.md file
    update_readme(readme_path, table)

