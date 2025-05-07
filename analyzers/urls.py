import os
import uuid
import subprocess
import logging
from urllib.parse import urlparse

# Настройка логирования
logging.basicConfig(filename='shared/logs/thug.log', level=logging.DEBUG)

SHARED_DIR = "shared"
THUG_LOG_DIR = os.path.join(SHARED_DIR, "thug_logs")
os.makedirs(THUG_LOG_DIR, exist_ok=True)
try:
    os.chmod(THUG_LOG_DIR, 0o777)
    logging.debug(f"Set permissions 777 on {THUG_LOG_DIR}")
except Exception as e:
    logging.error(f"Failed to set permissions on {THUG_LOG_DIR}: {e}")

def is_valid_url(url):
    """Проверка, что URL имеет схему http или https."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"]
    except Exception:
        return False

def analyze_urls_with_thug(urls):
    results = []

    # Фильтрация только валидных URL
    valid_urls = [url for url in urls if is_valid_url(url)]
    if not valid_urls:
        logging.debug("No valid URLs to analyze")
        return results

    for url in valid_urls:
        uid = str(uuid.uuid4())
        # Директория для хранения отчетов
        output_dir_host = os.path.join(THUG_LOG_DIR, f"report_{uid}")
        os.makedirs(output_dir_host, exist_ok=True)
        try:
            os.chmod(output_dir_host, 0o777)
            logging.debug(f"Set permissions 777 on {output_dir_host}")
        except Exception as e:
            logging.error(f"Failed to set permissions on {output_dir_host}: {e}")

        # Путь к файлу лога
        report_path_host = os.path.join(output_dir_host, "report.json")

        # Проверка возможности записи
        try:
            test_file = os.path.join(output_dir_host, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.chmod(test_file, 0o666)
            os.remove(test_file)
            logging.debug(f"Successfully wrote and removed test file in {output_dir_host}")
        except Exception as e:
            logging.error(f"Cannot write to {output_dir_host}: {e}")
            results.append({
                "url": url,
                "error": f"Cannot write to log directory: {e}",
                "stdout": "",
                "stderr": ""
            })
            continue

        cmd = ["thug", url, "-o", report_path_host, "-v"]
        logging.debug(f"Running Thug command: {' '.join(cmd)}")

        try:
            completed = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            if os.path.exists(report_path_host):
                try:
                    os.chmod(report_path_host, 0o666)
                    logging.debug(f"Set permissions 666 on {report_path_host}")
                except Exception as e:
                    logging.error(f"Failed to set permissions on {report_path_host}: {e}")

            results.append({
                "url": url,
                "report_path": report_path_host,
                "stdout": completed.stdout,
                "stderr": completed.stderr
            })

        except subprocess.CalledProcessError as e:
            error_log_path = os.path.join(output_dir_host, "error.log")
            try:
                with open(error_log_path, "w") as f:
                    f.write(e.stderr)
                os.chmod(error_log_path, 0o666)
            except Exception as e2:
                logging.error(f"Failed to write error log {error_log_path}: {e2}")
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error_log": error_log_path
            })
        except Exception as e:
            error_log_path = os.path.join(output_dir_host, "error.log")
            try:
                with open(error_log_path, "w") as f:
                    f.write(str(e))
                os.chmod(error_log_path, 0o666)
            except Exception as e2:
                logging.error(f"Failed to write error log {error_log_path}: {e2}")
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}",
                "stdout": "",
                "stderr": "",
                "error_log": error_log_path
            })

    return results