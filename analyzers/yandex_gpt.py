from yandex_cloud_ml_sdk import YCloudML
import os
import logging
import pkg_resources

# Настройка логирования
logging.basicConfig(filename='shared/logs/yandex_gpt.log', level=logging.DEBUG)

def summarize_report(report_path):
    auth_token = os.getenv("YC_AUTH")
    folder_id = os.getenv("YC_FOLDER_ID")

    if not auth_token or not folder_id:
        logging.error("YC_AUTH or YC_FOLDER_ID not set")
        return "🔕 GPT отключен: переменные YC_AUTH и YC_FOLDER_ID не заданы."

    try:
        # Логируем версию SDK
        sdk_version = pkg_resources.get_distribution("yandex_cloud_ml_sdk").version
        logging.debug(f"Using yandex_cloud_ml_sdk version: {sdk_version}")

        # Читаем отчет
        with open(report_path, 'r', encoding='utf-8') as f:
            report_text = f.read().strip()

        if not report_text:
            logging.error(f"Report file {report_path} is empty")
            return "❌ Ошибка: Отчет пустой, суммаризация невозможна"

        # Ограничиваем длину текста
        max_text_length = 10000
        if len(report_text) > max_text_length:
            report_text = report_text[:max_text_length] + "... [truncated]"
            logging.warning(f"Report text truncated to {max_text_length} characters")

        logging.debug(f"Report text length: {len(report_text)} characters")
        logging.debug(f"Report text preview: {report_text[:200]}...")

        # Проверяем валидность текста (только ASCII или UTF-8)
        try:
            report_text.encode('utf-8')
        except UnicodeEncodeError:
            logging.error("Report contains invalid characters")
            return "❌ Ошибка: Отчет содержит невалидные символы"

        sdk = YCloudML(folder_id=folder_id, auth=auth_token)
        model = sdk.models.completions("yandexgpt", model_version="latest")  # Пробуем latest
        model = model.configure(temperature=0.3)

        messages = [
            {
                "role": "system",
                "text": "Ты эксперт по кибербезопасности. Твоя задача — анализировать отчеты об анализе подозрительных писем, выделять ключевые моменты и оценивать угрозы. Дай краткую сводку и укажи, есть ли признаки фишинга или вредоносного ПО."
            },
            {
                "role": "user",
                "text": f"Суммаризируй и оцени следующий отчет об анализе письма:\n\n{report_text}"
            }
        ]

        logging.debug(f"Sending request to Yandex GPT with messages: {messages}")

        # Выполняем запрос
        result = model.run(messages)

        logging.debug(f"Yandex GPT result type: {type(result)}")
        logging.debug(f"Yandex GPT result content: {result}")

        if result is None:
            logging.error("Yandex GPT returned None")
            return "❌ GPT не вернул ответ"

        if not isinstance(result, list):
            logging.error(f"Unexpected result format: {type(result)}")
            return "❌ GPT вернул некорректный ответ"

        if len(result) == 0:
            logging.error("Yandex GPT returned empty list")
            return "❌ GPT вернул пустой ответ"

        # Проверяем атрибут text
        if hasattr(result[0], 'text') and result[0].text:
            logging.debug(f"Yandex GPT response: {result[0].text}")
            return result[0].text
        else:
            logging.error("Yandex GPT result has no text attribute or text is empty")
            return "❌ GPT не вернул текст ответа"

    except Exception as e:
        logging.error(f"Yandex GPT error: {str(e)}")
        return f"❌ Ошибка при обращении к Yandex GPT: {e}"