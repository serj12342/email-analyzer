from yandex_cloud_ml_sdk import YCloudML
import os


def summarize_report(report_path):
    auth_token = os.getenv("YC_AUTH")
    folder_id = os.getenv("YC_FOLDER_ID")

    if not auth_token or not folder_id:
        return "🔕 GPT отключен: переменные YC_AUTH и YC_FOLDER_ID не заданы."

    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    try:
        sdk = YCloudML(folder_id=folder_id, auth=auth_token)
        model = sdk.models.completions("yandexgpt", model_version="rc")
        model = model.configure(temperature=0.3)
        result = model.run([
            {"role": "system", "text": ""},
            {
                "role": "user",
                "text": f"Суммаризируй и оцени следующий отчёт об анализе письма:\n\n{report_text}"
            }
        ])
        return result[0]["text"] if result else "❌ GPT не вернул ответ"
    except Exception as e:
        return f"❌ Ошибка при обращении к Yandex GPT: {e}"