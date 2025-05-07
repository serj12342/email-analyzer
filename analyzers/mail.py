import mailparser
from bs4 import BeautifulSoup

def extract_urls_from_html(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)
    html_urls = extract_urls_from_html(mail.body)
    combined_urls = list(set(mail.urls + html_urls))  # удалим дубликаты, если есть

    # Преобразуем from/to в строки
    from_str = ", ".join(email for name, email in mail.from_)
    to_str = ", ".join(email for name, email in mail.to)

    return {
        'subject': mail.subject,
        'from': from_str,
        'to': to_str,
        'date': mail.date,
        'body': mail.body,
        'urls': combined_urls,
        'attachments': mail.attachments,
    }
