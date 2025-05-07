import os
import tempfile
import shutil
import requests
import zipfile
import rarfile
import py7zr
from oletools.olevba import VBA_Parser

def save_attachment(attachment, out_dir):
    filename = attachment['filename'] or 'unnamed'
    filepath = os.path.join(out_dir, filename)
    with open(filepath, 'wb') as f:
        payload = attachment['payload']
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        f.write(payload)
    return filepath

def extract_archive(filepath, extract_dir):
    try:
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath) as zf:
                zf.extractall(extract_dir)
        elif rarfile.is_rarfile(filepath):
            with rarfile.RarFile(filepath) as rf:
                rf.extractall(extract_dir)
        elif filepath.endswith('.7z'):
            with py7zr.SevenZipFile(filepath) as sz:
                sz.extractall(path=extract_dir)
    except Exception as e:
        return str(e)
    return None

def analyze_office_file(filepath):
    results = {}
    try:
        vba = VBA_Parser(filepath)
        results['has_macros'] = vba.detect_vba_macros()
        if results['has_macros']:
            results['macro_analysis'] = [str(m) for (_, _, _, m) in vba.extract_macros()]
    except Exception as e:
        results['error'] = str(e)
    return results

def send_to_virustotal(filepath, api_key):
    if not api_key:
        return {'skipped': 'VT_API_KEY not set'}
    try:
        with open(filepath, 'rb') as f:
            r = requests.post(
                'https://www.virustotal.com/api/v3/files',
                headers={'x-apikey': api_key},
                files={'file': f}
            )
            return r.json()
    except Exception as e:
        return {'error': str(e)}

def send_to_cape(filepath, cape_url):
    if not cape_url:
        return {'skipped': 'CAPE_URL not set'}
    try:
        with open(filepath, 'rb') as f:
            r = requests.post(
                f'{cape_url}/tasks/create/file/',
                files={'file': f}
            )
            return r.json()
    except Exception as e:
        return {'error': str(e)}

def process_attachments(attachments, vt_api_key, cape_url):
    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for att in attachments:
            filepath = save_attachment(att, tmpdir)
            result = {'filename': os.path.basename(filepath), 'path': filepath}

            if any(filepath.endswith(ext) for ext in ['.zip', '.rar', '.7z']):
                archive_dir = os.path.join(tmpdir, 'extracted', os.path.basename(filepath))
                os.makedirs(archive_dir, exist_ok=True)
                result['archive_extract_error'] = extract_archive(filepath, archive_dir)

            if filepath.endswith(('.doc', '.docm', '.xls', '.ppt')):
                result['office_analysis'] = analyze_office_file(filepath)

            result['virustotal'] = send_to_virustotal(filepath, vt_api_key)
            result['cape'] = send_to_cape(filepath, cape_url)

            results.append(result)

    return results
