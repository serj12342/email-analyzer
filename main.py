import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from analyzers.mail import parse_email
from analyzers.urls import analyze_urls_with_thug
from analyzers.attachments import process_attachments
from analyzers.report import generate_report
from analyzers.yandex_gpt import summarize_report

from datetime import datetime, timezone

PROCESSED = set()
SAMPLES_DIR = "samples"
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

def analyze_file(eml_file):
    eml_path = os.path.join(SAMPLES_DIR, eml_file)
    print(f"[→] Анализ файла: {eml_file}")
    mail_data = parse_email(eml_path)
    thug_results = analyze_urls_with_thug(mail_data['urls'])

    vt_api_key = os.getenv("VT_API_KEY")
    cape_url = os.getenv("CAPE_URL")

    attachment_results = process_attachments(mail_data['attachments'], vt_api_key, cape_url)
    report_path = generate_report(mail_data, thug_results, attachment_results)

    summary = summarize_report(report_path)
    print("\n==== 📄 Итог от GPT ====")
    print(summary)

    summary_path = report_path.replace(".md", "_gpt.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"[✓] Результат GPT сохранён в: {summary_path}\n")
    log_analysis_result(eml_file, summary)

class NewEmailHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".eml"):
            filename = os.path.basename(event.src_path)
            if filename not in PROCESSED:
                time.sleep(1)  # чуть подождать чтобы файл дописался
                try:
                    analyze_file(filename)
                    PROCESSED.add(filename)
                except Exception as e:
                    print(f"[!] Ошибка при анализе {filename}: {e}")

def main():
    print_banner()

    os.makedirs(SAMPLES_DIR, exist_ok=True)
    already_existing = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".eml")]
    for f in already_existing:
        analyze_file(f)
        PROCESSED.add(f)

    print(f"[👀] Ожидание новых .eml файлов в папке {SAMPLES_DIR}...\n")

    observer = Observer()
    observer.schedule(NewEmailHandler(), path=SAMPLES_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()