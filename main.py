import os
import sys
import argparse
from analyzers.mail import parse_email
from analyzers.urls import analyze_urls_with_thug
from analyzers.attachments import process_attachments
from analyzers.report import generate_report
from analyzers.yandex_gpt import summarize_report

def main(eml_path, vt_api_key, cape_url):
    print("[+] Parsing email...")
    mail_data = parse_email(eml_path)

    print("[+] Analyzing URLs with Thug...")
    thug_results = analyze_urls_with_thug(mail_data['urls'])

    print("[+] Processing attachments...")
    attachment_results = process_attachments(
        mail_data['attachments'], vt_api_key, cape_url
    )

    print("[+] Generating report...")
    report_path = generate_report(mail_data, thug_results, attachment_results)

    print("[+] Sending report to Yandex GPT...")
    summary = summarize_report(report_path)
    print("\n==== SUMMARY FROM GPT ====")
    print(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Threat Analyzer")
    parser.add_argument("--eml", required=True, help="Path to .eml file")
    parser.add_argument("--vt-key", required=True, help="VirusTotal API key")
    parser.add_argument("--cape-url", required=True, help="CAPE API URL")
    args = parser.parse_args()

    main(args.eml, args.vt_key, args.cape_url)
