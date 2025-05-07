import mailparser
from bs4 import BeautifulSoup

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body or "", 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)
    html_urls = extract_urls_from_html(mail.body)
    combined_urls = list(set((mail.urls or []) + html_urls))

    return {
        'subject': mail.subject or "",
        'from': ", ".join(mail.from_ or []),
        'to': ", ".join(mail.to or []),
        'date': str(mail.date) if mail.date else "",
        'body': mail.body or "",
        'urls': combined_urls,
        'attachments': mail.attachments or [],
    }
