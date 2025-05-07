# analyzers/report.py
import os
import datetime

def generate_report(mail_data, thug_results, attachment_results):
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_path = f"reports/final/report_{now}.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 📬 Email Threat Analysis Report\n\n")

        f.write("## ✉️ Email Metadata\n")
        f.write(f"- Subject: {mail_data['subject']}\n")
        f.write(f"- From: {mail_data['from']}\n")
        f.write(f"- To: {mail_data['to']}\n")
        f.write(f"- Date: {mail_data['date']}\n\n")

        f.write("## 📝 Body\n")
        f.write(f"{mail_data['body']}\n\n")

        f.write("## 🔗 URL Analysis (Thug)\n")
        for result in thug_results:
            f.write(f"- URL: {result['url']}\n")
            if 'error' in result:
                f.write(f"  - ❌ Error: {result['error']}\n")
            else:
                f.write(f"  - ✅ Report Dir: {result['report_dir']}\n")

        f.write("\n## 📎 Attachment Analysis\n")
        for result in attachment_results:
            f.write(f"- File: {result['filename']}\n")
            if 'archive_extract_error' in result and result['archive_extract_error']:
                f.write(f"  - ⚠️ Archive extract error: {result['archive_extract_error']}\n")

            if 'office_analysis' in result:
                f.write("  - Office analysis:\n")
                for k, v in result['office_analysis'].items():
                    f.write(f"    - {k}: {v}\n")

            f.write("  - VirusTotal result:\n")
            vt = result['virustotal']
            if 'error' in vt:
                f.write(f"    - ❌ {vt['error']}\n")
            else:
                f.write(f"    - ✅ Scan ID: {vt.get('data', {}).get('id', 'N/A')}\n")

            f.write("  - CAPE result:\n")
            cape = result['cape']
            if 'error' in cape:
                f.write(f"    - ❌ {cape['error']}\n")
            else:
                f.write(f"    - ✅ Task ID: {cape.get('task_id', 'N/A')}\n")

            f.write("\n")

    return report_path
