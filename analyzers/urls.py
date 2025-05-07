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

        thug_log_dir_in_container = f"/shared/thug_logs/report_{uid}"

        try:
            completed = subprocess.run([
                "/usr/bin/docker", "exec", "thug",
                "thug", url, "-o", thug_log_dir_in_container, "-v"
            ],
                check=True,
                capture_output=True,
                text=True
            )

            results.append({
                "url": url,
                "report_path": output_dir_host,
                "stdout": completed.stdout,
                "stderr": completed.stderr
            })

        except subprocess.CalledProcessError as e:
            results.append({
                "url": url,
                "error": f"Thug failed: {str(e)}",
                "stdout": e.stdout,
                "stderr": e.stderr
            })

    return results
