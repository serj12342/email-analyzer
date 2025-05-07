import subprocess
import os
import tempfile

def analyze_urls_with_thug(urls):
    results = []
    for url in urls:
        with tempfile.TemporaryDirectory() as outdir:
            try:
                subprocess.run([
                    'thug', '-u', url, '-o', outdir, '-v'
                ], check=True)
                results.append({
                    'url': url,
                    'report_dir': outdir
                })
            except subprocess.CalledProcessError as e:
                results.append({
                    'url': url,
                    'error': str(e)
                })
    return results