# main.py
import os
import argparse
from analyzers.mail import parse_email
from analyzers.urls import analyze_urls_with_thug
from analyzers.attachments import process_attachments
from analyzers.report import generate_report
from analyzers.yandex_gpt import summarize_report

def print_banner():
    banner = r"""
 ______        _ _       _                 _                            
|  ____|      (_) |     | |               | |                           
| |__    _ __  _| |_ ___| |__   ___   ___ | | ___   __ _ _ __ ___   ___ 
|  __|  | '_ \| | __/ __| '_ \ / _ \ / _ \| |/ _ \ / _` | '_ ` _ \ / _ \
| |____ | | | | | || (__| | | | (_) | (_) | | (_) | (_| | | | | | |  __/
|______||_| |_|_|\__\___|_| |_|\___/ \___/|_|\___/ \__, |_| |_| |_|\___|
                                                   __/ |               
                                                  |___/                
email-analyzer v1.0 | sandbox your spam ✉️
"""
    print(banner)

def main(eml_path):
    if not os.path.exists(eml_path):
        print(f"❌ Файл {eml_path} не найден. Положите .eml в папку /samples/")
        return

    print(f"[🔍] Начат анализ письма: {eml_path}")

    vt_api_key = os.getenv("VT_API_KEY")
    cape_url = os.getenv("CAPE_URL")

    if not vt_api_key or not cape_url:
        print("❌ Переменные окружения VT_API_KEY и CAPE_URL обязательны.")
        return

    print("[📨] Парсинг письма...")
    mail_data = parse_email(eml_path)

    print("[🌐] Анализ ссылок через Thug...")
    thug_results = analyze_urls_with_thug(mail_data['urls'])

    print("[📎] Анализ вложений...")
    attachment_results = process_attachments(
        mail_data['attachments'], vt_api_key, cape_url
    )

    print("[📝] Генерация отчёта...")
    report_path = generate_report(mail_data, thug_results, attachment_results)

    print("[🤖] Отправка отчёта в Yandex GPT...")
    summary = summarize_report(report_path)

    print("\n==== 📄 Итог от GPT ====")
    print(summary)

    summary_path = report_path.replace(".md", "_gpt.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"\n[✓] Результат GPT сохранён в: {summary_path}")

if __name__ == "__main__":
    print_banner()
    parser = argparse.ArgumentParser(description="Email Threat Analyzer")
    parser.add_argument("--eml", required=True, help="Path to .eml file")
    args = parser.parse_args()

    main(args.eml)