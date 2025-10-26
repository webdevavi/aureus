from openai import OpenAI
from backend.workers.extractor.config.settings import get_settings

settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)
