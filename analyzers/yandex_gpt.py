from yandex_cloud_ml_sdk import YCloudML
import os
import logging
import pkg_resources

# Настройка логирования
log_dir = 'shared/logs'
os.makedirs(log_dir, exist_ok=True)  # Создаем папку shared/logs
log_file = os.path.join(log_dir, 'yandex_gpt.log')

# Проверяем права на запись
try:
    with open(log_file, 'a') as f:
        pass
except Exception as e:
    print(f"Cannot write to log file {log_file}: {e}")
    raise

# Настройка логирования с принудительной записью
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    force=True  # Принудительно инициализируем логгер
)

# Создаем логгер
logger = logging.getLogger(__name__)

def summarize_report(report_path):
    logger.debug("Starting summarize_report")

    auth_token = os.getenv("YC_AUTH")
    folder_id = os.getenv("YC_FOLDER_ID")

    logger.debug(f"YC_AUTH: {'set' if auth_token else 'not set'}")
    logger.debug(f"YC_FOLDER_ID: {'set' if folder_id else 'not set'}")

    if not auth_token or not folder_id:
        logger.error("YC_AUTH or YC_FOLDER_ID not set")
        return "🔕 GPT отключен: переменные YC_AUTH и YC_FOLDER_ID не заданы."

    try:
        # Логируем версию SDK
        sdk_version = pkg_resources.get_distribution("yandex_cloud_ml_sdk").version
        logger.debug(f"Using yandex_cloud_ml_sdk version: {sdk_version}")

        # Читаем отчет
        logger.debug(f"Reading report from {report_path}")
        with open(report_path, 'r', encoding='utf-8') as f:
            report_text = f.read().strip()

        if not report_text:
            logger.error(f"Report file {report_path} is empty")
            return "❌ Ошибка: Отчет пустой, суммаризация невозможна"

        # Ограничиваем длину текста
        max_text_length = 10000
        if len(report_text) > max_text_length:
            report_text = report_text[:max_text_length] + "... [truncated]"
            logger.warning(f"Report text truncated to {max_text_length} characters")

        logger.debug(f"Report text length: {len(report_text)} characters")
        logger.debug(f"Report text preview: {report_text[:200]}...")

        # Проверяем валидность текста
        try:
            report_text.encode('utf-8')
        except UnicodeEncodeError:
            logger.error("Report contains invalid characters")
            return "❌ Ошибка: Отчет содержит невалидные символы"

        # Инициализация SDK
        logger.debug("Initializing YCloudML SDK")
        try:
            sdk = YCloudML(folder_id=folder_id, auth=auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize YCloudML: {str(e)}")
            return f"❌ Ошибка при инициализации Yandex GPT: {e}"

        # Настройка модели
        logger.debug("Configuring model yandexgpt, version: latest")
        try:
            model = sdk.models.completions("yandexgpt", model_version="latest")
            model = model.configure(temperature=0.3)
        except Exception as e:
            logger.error(f"Failed to configure model: {str(e)}")
            return f"❌ Ошибка при настройке модели Yandex GPT: {e}"

        messages = [
            {
                "role": "system",
                "text": "Ты эксперт по кибербезопасности. Твоя задача — анализировать отчеты об анализе подозрительных писем, выделять ключевые моменты и оценивать угрозы. Дай краткую сводку (до 200 слов) и укажи, есть ли признаки фишинга или вредоносного ПО."
            },
            {
                "role": "user",
                "text": f"Суммаризируй и оцени следующий отчет об анализе письма:\n\n{report_text}"
            }
        ]

        logger.debug(f"Sending request to Yandex GPT with messages: {messages}")

        # Выполняем запрос
        logger.debug("Executing model.run")
        try:
            result = model.run(messages)
        except Exception as e:
            logger.error(f"Failed to run model: {str(e)}")
            return f"❌ Ошибка при выполнении запроса Yandex GPT: {e}"

        logger.debug(f"Yandex GPT result type: {type(result)}")
        logger.debug(f"Yandex GPT result content: {result}")
        logger.debug(f"Yandex GPT result dir: {dir(result) if result else 'None'}")

        if result is None:
            logger.error("Yandex GPT returned None")
            return "❌ GPT не вернул ответ"

        # Проверяем, является ли результат объектом GPTModelResult
        if not hasattr(result, 'alternatives'):
            logger.error(f"Result does not have 'alternatives' attribute: {type(result)}")
            return "❌ GPT вернул некорректный ответ"

        alternatives = result.alternatives
        if not alternatives or not isinstance(alternatives, (list, tuple)):
            logger.error(f"Alternatives is empty or not a list/tuple: {type(alternatives)}")
            return "❌ GPT вернул пустой ответ"

        if len(alternatives) == 0:
            logger.error("Alternatives list is empty")
            return "❌ GPT вернул пустой ответ"

        # Проверяем атрибут text в первом элементе alternatives
        if hasattr(alternatives[0], 'text') and alternatives[0].text:
            logger.debug(f"Yandex GPT response: {alternatives[0].text}")
            return alternatives[0].text
        else:
            logger.error("Yandex GPT alternative has no text attribute or text is empty")
            return "❌ GPT не вернул текст ответа"

    except Exception as e:
        logger.error(f"Yandex GPT error: {str(e)}")
        return f"❌ Ошибка при обращении к Yandex GPT: {e}"