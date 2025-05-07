import os
import uuid
import subprocess
import chmod

SHARED_DIR = "shared"
THUG_LOG_DIR = os.path.join(SHARED_DIR, "thug_logs")
os.makedirs(THUG_LOG_DIR, exist_ok=True)
os.chmod(THUG_LOG_DIR, 0o777)  # Открытые права для директории

def analyze_urls_with_thug(urls):
    results = []

    for url in urls:
        uid = str(uuid.uuid4())
        # Директория на хосте для хранения отчетов
        output_dir_host = os.path.join(THUG_LOG_DIR, f"report_{uid}")
        os.makedirs(output_dir_host, exist_ok=True)
        os.chmod(output_dir_host, 0o777)  # Открытые права для поддиректории
        
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

            # Убедимся, что файл имеет правильные права
            report_path_host = os.path.join(output_dir_host, "report.json")
            if os.path.exists(report_path_host):
                os.chmod(report_path_host, 0o666)

            results.append({
                "url": url,
                "report_path": report_path_host,
                "stdout": completed.stdout,
                "stderr": completed.stderr
            })

        except subprocess.CalledProcessError as e:
            error_log_path = os.path.join(output_dir_host, "error.log")
            with open(error_log_path, "w") as f:
                f.write(e.stderr)
            os.chmod(error_log_path, 0o666)
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error_log": error_log_path
            })
        except Exception as e:
            error_log_path = os.path.join(output_dir_host, "error.log")
            with open(error_log_path, "w") as f:
                f.write(str(e))
            os.chmod(error_log_path, 0o666)
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}",
                "stdout": "",
                "stderr": "",
                "error_log": error_log_path
            })

    return results