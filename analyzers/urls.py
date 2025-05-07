import os
import uuid
import subprocess

SHARED_DIR = "shared"
THUG_LOG_DIR = os.path.join(SHARED_DIR, "thug_logs")
os.makedirs(THUG_LOG_DIR, exist_ok=True)

def analyze_urls_with_thug(urls):
    results = []

    for url in urls:
        uid = str(uuid.uuid4())
        # Директория на хосте для хранения отчетов
        output_dir_host = os.path.join(THUG_LOG_DIR, f"report_{uid}")
        os.makedirs(output_dir_host, exist_ok=True)
        
        # Путь к файлу лога внутри контейнера
        thug_log_file_in_container = f"/shared/thug_logs/report_{uid}/report.json"

        try:
            completed = subprocess.run([
                "/usr/bin/docker", "exec", "thug",
                "thug", url, "-o", thug_log_file_in_container, "-v"
            ],
                check=True,
                capture_output=True,
                text=True
            )

            results.append({
                "url": url,
                "report_path": os.path.join(output_dir_host, "report.json"),
                "stdout": completed.stdout,
                "stderr": completed.stderr
            })

        except subprocess.CalledProcessError as e:
            results.append({
                "url": url,
                "error": f"Thug error: {e.stderr}"
            })

    return results