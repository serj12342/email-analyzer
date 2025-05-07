import mailparser
from bs4 import BeautifulSoup

print("DEBUG: Loading parser module (version 2025-05-08)")  # Подтверждение загрузки

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body or "", 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def format_addresses(address_list):
    result = []
    print(f"DEBUG: Processing address_list = {address_list}")
    for item in address_list:
        print(f"DEBUG: Processing item = {item}")
        if isinstance(item, tuple):
            if len(item) >= 1:
                email = item[-1]  # Берем последний элемент (email)
                name = item[0] if len(item) == 2 else None
                if name and name.strip():  # Проверяем, что имя не пустое
                    result.append(f"{name} <{email}>")
                else:
                    result.append(email)  # Если имя пустое или отсутствует, только email
            else:
                print(f"DEBUG: Empty tuple: {item}")
                result.append(str(item))
        elif isinstance(item, str):
            result.append(item)
        else:
            print(f"DEBUG: Unexpected item type: {item}")
            result.append(str(item))
    print(f"DEBUG: Formatted addresses = {result}")
    return ", ".join(result)

def parse_email(eml_path):
    try:
        mail = mailparser.parse_from_file(eml_path)
        print(f"DEBUG: mail.from_ = {mail.from_}")
        print(f"DEBUG: mail.to = {mail.to}")
    except Exception as e:
        print(f"DEBUG: Failed to parse {eml_path}: {e}")
        raise

    html_urls = extract_urls_from_html(mail.body)
    combined_urls = list(set((mail.urls or []) + html_urls))

    return {
        'subject': mail.subject or "",
        'from': format_addresses(mail.from_ or []),
        'to': format_addresses(mail.to or []),
        'date': str(mail.date) if mail.date else "",
        'body': mail.body or "",
        'urls': combined_urls,
        'attachments': mail.attachments or [],
    }