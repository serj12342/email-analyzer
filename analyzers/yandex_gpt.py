# analyzers/yandex_gpt.py
import os
from yandex_cloud import SDK

# Требуется предварительно настроенный OAuth-токен или сервисный аккаунт с правами
# и установленная переменная окружения YC_TOKEN или конфиг в ~/.config/yandex-cloud

sdk = SDK()


def summarize_report(report_path):
    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    prompt = f"""
    Сформируй краткое резюме и рекомендации на основе этого отчета об анализе письма:
    ===
    {report_text}
    ===
    """

    model = sdk.models.completions("gpt", model_version="latest")
    result = model.complete(
        prompt=prompt,
        temperature=0.3,
        max_tokens=500,
        stream=False
    )
    return result['result']['alternatives'][0]['message']['text']
