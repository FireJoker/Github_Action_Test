import re
import json
import datetime

def read_json_file(file_path):
    """Reads a JSON file and returns the data."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


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
    json_file_path = 'data.json'  # Path to the JSON file
    readme_path = 'README.md'  # Path to the README.md file
    
    # Read and parse JSON file
    data = read_json_file(json_file_path)
    
    # Generate Markdown table
    table = generate_markdown_table(data)
    
    # Update README.md file
    update_readme(readme_path, table)

