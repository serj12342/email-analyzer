import mailparser
from bs4 import BeautifulSoup

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def format_addresses(address_list):
    # [(None, 'example@mail.com')] или [('John', 'john@mail.com')]
    return ", ".join(
        f"{name} <{email}>" if name else email
        for name, email in address_list
    )

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)
    html_urls = extract_urls_from_html(mail.body)
    combined_urls = list(set(mail.urls + html_urls))

    return {
        'subject': mail.subject,
        'from': format_addresses(mail.from_),
        'to': format_addresses(mail.to),
        'date': str(mail.date),
        'body': mail.body,
        'urls': combined_urls,
        'attachments': mail.attachments,
    }
