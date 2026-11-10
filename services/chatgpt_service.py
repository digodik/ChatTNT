#services/chatgpt_service.py
import logging
from typing import Tuple, Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger("chatgpt_service")

class ChatGPTService:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini-2025-04-14"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.default_prompt = "Summarize the following text, highlighting key points and main ideas."
    
    async def summarize(self, text: str, prompt: str = None) -> Tuple[bool, str]:
        if not self.client:
            return False, "API ключ не настроен"
        
        if not prompt:
            prompt = self.default_prompt
        
        try: 
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": prompt}]
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}]
                }
            ]
            
            logger.info(f"Отправляю запрос в OpenAI с моделью {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            return True, result
        
        except Exception as e:
            logger.error(f"Ошибка при вызове ChatGPT API: {e}", exc_info=True)
            return False, f"Ошибка при обработке текста: {str(e)}"