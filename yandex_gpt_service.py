import requests
import logging
from config import Config

logger = logging.getLogger(__name__)


class YandexGPTService:
    def __init__(self):
        self.api_key = Config.YANDEX_API_KEY
        self.folder_id = Config.YANDEX_FOLDER_ID
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def generate_report(self, system_prompt, user_prompt):
        """Генерация отчета с помощью Yandex GPT API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}"
            }

            data = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.1,
                    "maxTokens": 4000
                },
                "messages": [
                    {
                        "role": "system",
                        "text": system_prompt
                    },
                    {
                        "role": "user",
                        "text": user_prompt
                    }
                ]
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully received response from Yandex GPT API")
                return result['result']['alternatives'][0]['message']['text']
            else:
                logger.error(f"Yandex GPT API error: {response.status_code}")
                return f"ОШИБКА: Yandex GPT API вернул код {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error("Yandex GPT API timeout")
            return "ОШИБКА: Превышено время ожидания ответа от Yandex GPT API"
        except requests.exceptions.ConnectionError:
            logger.error("Yandex GPT API connection error")
            return "ОШИБКА: Не удается подключиться к Yandex GPT API"
        except Exception as e:
            logger.error(f"Error calling Yandex GPT API: {e}")
            return f"ОШИБКА: Неожиданная ошибка при обращении к Yandex GPT API: {str(e)}"
