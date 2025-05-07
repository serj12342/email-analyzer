import os
import uuid
import subprocess

SHARED_DIR = "/shared"
THUG_LOG_DIR = os.path.join(SHARED_DIR, "thug_logs")
os.makedirs(THUG_LOG_DIR, exist_ok=True)

def analyze_urls_with_thug(urls):
    results = []

    for url in urls:
        uid = str(uuid.uuid4())
        url_file = os.path.join(SHARED_DIR, f"url_{uid}.txt")
        output_dir = os.path.join(THUG_LOG_DIR, f"report_{uid}")
        os.makedirs(output_dir, exist_ok=True)

        with open(url_file, "w") as f:
            f.write(url)

        try:
            subprocess.run([
                "docker", "exec", "thug",
                "thug", "-u", url, "-o", f"/shared/thug_logs/report_{uid}", "-v"
            ], check=True)

            results.append({
                "url": url,
                "report_path": f"shared/thug_logs/report_{uid}"
            })

        except subprocess.CalledProcessError as e:
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}"
            })

    return results
