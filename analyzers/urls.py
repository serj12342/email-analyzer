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
        output_dir_host = os.path.join(THUG_LOG_DIR, f"report_{uid}")
        output_dir_container = f"/shared/thug_logs/report_{uid}"
        os.makedirs(output_dir_host, exist_ok=True)

        try:
            print(f"[→] Запускаем Thug: {url}")
            subprocess.run([
                "docker", "exec", "thug",
                "thug", url,
                "-o", output_dir_container,
                "-v"
            ], check=True)

            # Проверка логов внутри директории
            files = os.listdir(output_dir_host)
            artifact_list = [f for f in files if os.path.isfile(os.path.join(output_dir_host, f))]

            results.append({
                "url": url,
                "report_path": output_dir_host,
                "artifacts": artifact_list
            })

        except subprocess.CalledProcessError as e:
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}"
            })

    return results
