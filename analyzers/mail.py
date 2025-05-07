import mailparser

def parse_email(eml_path):
    mail = mailparser.parse_from_file(eml_path)
    return {
        'subject': mail.subject,
        'from': mail.from_,
        'to': mail.to,
        'date': mail.date,
        'body': mail.body,
        'urls': mail.urls,
        'attachments': mail.attachments,
    }
