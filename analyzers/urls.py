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
        os.makedirs(output_dir_host, exist_ok=True)

        print(f"[→] Запускаем thug для: {url}")
        try:
            completed = subprocess.run([
                "sudo", "docker", "exec", "thug",
                "thug", url, "-o", f"/shared/thug_logs/report_{uid}", "-v"
            ], capture_output=True, text=True, check=True)

            print("[thug stdout]")
            print(completed.stdout)
            print("[thug stderr]")
            print(completed.stderr)

            results.append({
                "url": url,
                "report_dir": output_dir_host
            })

        except subprocess.CalledProcessError as e:
            print(f"[!] Thug error for {url}")
            print(e.stdout)
            print(e.stderr)
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}"
            })

    return results
