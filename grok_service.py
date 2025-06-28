import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class GrokService:
    def __init__(self):
        self.api_key = Config.GROK_API_KEY
        self.base_url = "https://api.x.ai/v1"
        self.model = "xAI Grok-3 mini beta"  # Используем легкую модель

    def generate_report(self, system_prompt, user_prompt):
        """Генерация отчета с помощью Grok API"""
        try:
            if not self.api_key:
                return "ОШИБКА: Не указан API ключ Grok в файле .env"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # Формируем запрос в формате OpenAI (Grok совместим)
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "stream": False
            }

            logger.info(f"Sending request to Grok API with model: {self.model}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully received response from Grok API")
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return f"ОШИБКА: Grok API вернул код {response.status_code}"

        except requests.exceptions.Timeout:
            logger.error("Grok API timeout")
            return "ОШИБКА: Превышено время ожидания ответа от Grok API"
        except requests.exceptions.ConnectionError:
            logger.error("Grok API connection error")
            return "ОШИБКА: Не удается подключиться к Grok API"
        except Exception as e:
            logger.error(f"Error calling Grok API: {e}")
            return f"ОШИБКА: Неожиданная ошибка при обращении к Grok API: {str(e)}"
