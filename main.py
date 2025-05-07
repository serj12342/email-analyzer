# main.py
import os
import argparse
import datetime
from datetime import datetime, timezone
from analyzers.mail import parse_email
from analyzers.urls import analyze_urls_with_thug
from analyzers.attachments import process_attachments
from analyzers.report import generate_report
from analyzers.yandex_gpt import summarize_report

def print_banner():
    banner = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠁⣠⣶⠞⠁⠀⠀⠀⠀⠀⠈⠑⠒⠤⡀⠀⠀⣀⡠⠔⠒⠉⠉⠉⠙⠛⠿⣶⡄⠀⠀⠀⠈⣷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠓⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠁⠀⠀⠀⠀⣀⠤⠒⠃⠉⠉⠉⠑⠓⠶⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⡀⢀⣯⣀⣀⣀⣀⠀⠀
⠀⠀⠀⠀⠀⢀⠀⣰⡞⠀⠀⠀⠀⠊⠉⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⠀⠉⢷⠀⠉⠈⠉⠉⠉⠉⠉⠉⠉⠉⠀⠛⠿⣿⣯⣹⣿⢯⡉⠳⣄
⠀⢀⣤⠄⠀⣩⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⠾⠛⠉⠉⠉⠛⠻⢶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣽⡄⢻⡄⠉
⣰⠟⠀⢀⣴⠟⣻⠃⠀⠀⠀⠀⠀⠀⠀⣠⠴⢟⣉⠴⣲⣿⣿⣿⣯⣭⣖⣲⣮⣝⠶⡄⠀⠀⢀⡠⠔⠒⠈⢉⣉⠤⣤⣤⣾⣿⣿⣶⢷⣤
⠁⠀⢠⡾⠋⠀⡿⠀⠀⠀⠀⠀⠀⣀⣤⠴⢾⣫⠵⠟⠉⠁⠀⠀⠀⠀⠉⠙⠛⠿⢷⣞⡒⠉⡁⠠⠒⢒⣉⣵⠶⠟⠛⠉⠀⠈⠉⠙⡆⠁
⠀⣠⡟⠁⠀⠀⠁⠀⠀⠀⠀⠘⠿⠤⢴⣶⡿⠁⠀⠀⠀⠀⠀⠀⠀⣾⣿⡆⠀⠀⢀⣈⣿⣶⡶⠶⠚⠉⠉⠀⠀⠀⠀⢰⣿⣷⠀⢀⡇⠀
⢰⡟⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢉⡻⠷⣦⣄⣀⣀⣀⣀⣀⣈⣿⣵⠶⠟⠛⠿⣯⣥⣤⣤⣤⣤⣤⣤⣤⣤⣤⣼⣿⣶⣿⣿⠁⠀
⡿⠀⢀⣼⣁⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠲⠦⣤⣭⣍⣉⣉⣉⣉⣀⣀⢠⡶⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣰⡿⠟⠋⠁⠀⠀
⣟⣦⠞⠋⠉⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⡤⠂⡉⠐⠂⠀⠀⠐⠠⠤⣤⡤⠤⠴⠒⠺⣿⣻⡀⠀⠀⠀⠀⠀
⡟⠁⠀⠀⠀⠀⠀⠀⠀⣀⣴⡾⠛⠋⠉⣉⣉⣉⡉⠛⠛⠒⠶⠦⠴⢯⣴⣧⣤⣤⣄⣀⣀⣀⣀⢀⣀⣀⣠⣤⣤⡶⣿⣿⡇⠀⠀⠀⠀⠀
⠄⠀⠀⠀⠀⠀⠀⣠⣾⡿⠋⣠⣤⣶⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣀⣀⠀⠀⠀⠉⠉⠛⠙⢛⢻⣿⣿⡿⢻⣏⣁⣤⣿⡿⠃⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⣿⠋⢡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣶⣶⡾⠟⠛⠛⠛⠛⠛⠛⠛⠋⢁⣀⣀⣀⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⠏⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⠿⠛⠻⠿⣦⡀⠀
⣤⣾⣻⡗⠀⢸⣿⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢛⣿⣭⣭⣭⣿⣟⣛⠿⢷⣶⣤⣤⣤⣤⣤⣴⣾⣿⣿⣿⠿⠷⣤⡀⢈⡷⠀
⡏⠉⠉⠁⠀⢸⡟⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⣴⣿⣿⣿⣿⣿⣿⣿⠿⠿⢷⣦⣬⣭⣩⣏⣽⣿⣿⡿⣿⡁⠀⠀⠀⠈⠉⠉⠀⠀
⣿⠀⠀⠀⠀⢸⣿⡀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠉⠉⠛⠛⠋⠉⠀⠰⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢻⣧⡀⠀⠀⡸⣿⣷⡀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣤⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠾⠿⣷⣄⠀⠉⠹⣿⣧⣄⣀⣈⣻⣿⣿⣿⣭⣿⣿⣭⣭⣉⣉⣹⣿⣛⣛⣛⣻⣿⣿⣿⠿⠟⠛⠛⢛⣛⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠛⠿⢶⣦⣾⣟⣛⠋⠉⠉⠉⠉⠉⠉⣽⣿⠉⠉⢉⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⢛⣻⣿⠿⢻⡟⠁⠀⠀⠀⠀⢠⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⠛⠿⠷⣶⣦⣴⡿⢿⣿⡤⠖⡟⠁⠀⠀⠀⠀⠀⠀⢀⣀⣠⣴⡾⠋⠉⠀⢸⣿⡇⠀⠀⠀⠀⠐⢑⠀⠀⠈⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠟⠁⠀⠀⠀⠀⠾⠭⢍⣉⡉⠉⠉⠉⠉⠉⠁⠙⠻⣷⣄⠀⠀⠘⣸⡇⠀⠄⠂⠀⠀⠀⠀⠐⠠⢀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠔⠊⠁⠀⠀⠀⠀⠀⠀⣀⣠⠤⠖⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣜⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠄⠘
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣇⠀⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀
email-analyzer | powered by sad frog intelligence ✉️
"""
    print(banner)

def log_analysis_result(eml_file, summary):
    os.makedirs("shared/logs", exist_ok=True)
    log_path = "shared/logs/analysis.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {eml_file}\n")
        log_file.write(summary + "\n\n")

def main():
    samples_dir = "samples"
    eml_files = [f for f in os.listdir(samples_dir) if f.endswith(".eml")]

    if not eml_files:
        print("[!] Нет .eml файлов в папке samples. Поместите хотя бы один.")
        return

    vt_api_key = os.getenv("VT_API_KEY")
    cape_url = os.getenv("CAPE_URL")

    if not vt_api_key:
        print("[!] VirusTotal API не задан. Пропускаем анализ на VT.")
    if not cape_url:
        print("[!] CAPE URL не задан. Пропускаем анализ в CAPE.")

    for eml_file in eml_files:
        eml_path = os.path.join(samples_dir, eml_file)
        print(f"[→] Анализ файла: {eml_file}")

        mail_data = parse_email(eml_path)
        thug_results = analyze_urls_with_thug(mail_data['urls'])
        attachment_results = process_attachments(mail_data['attachments'], vt_api_key, cape_url)
        report_path = generate_report(mail_data, thug_results, attachment_results)
        summary = summarize_report(report_path)

        print("\n==== 📄 Итог от GPT ====")
        print(summary)

        summary_path = report_path.replace(".md", "_gpt.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\n[✓] Результат GPT сохранён в: {summary_path}\n")

        log_analysis_result(eml_file, summary)

if __name__ == "__main__":
    print_banner()
    main()
