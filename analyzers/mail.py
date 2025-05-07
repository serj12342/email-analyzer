import mailparser
from bs4 import BeautifulSoup

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body or "", 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def format_addresses(address_list):
    result = []
    for item in address_list:
        if isinstance(item, tuple):
            if len(item) == 2:
                name, email = item
                if name:
                    result.append(f"{name} <{email}>")
                else:
                    result.append(email)
            elif len(item) == 1:
                result.append(item[0])  # Только email
        elif isinstance(item, str):
            result.append(item)
    return ", ".join(result)

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)

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