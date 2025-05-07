import mailparser
from bs4 import BeautifulSoup

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def format_addresses(address_list):
    formatted = []
    for entry in address_list:
        # если это строка — сразу добавляем
        if isinstance(entry, str):
            formatted.append(entry)
        # если это кортеж длины 2 — парсим как (name, email)
        elif isinstance(entry, tuple) and len(entry) == 2:
            name, email = entry
            formatted.append(f"{name} <{email}>" if name else email)
        # fallback — просто строка представления
        else:
            formatted.append(str(entry))
    return ", ".join(formatted)

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)
    html_urls = extract_urls_from_html(mail.body or "")
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
