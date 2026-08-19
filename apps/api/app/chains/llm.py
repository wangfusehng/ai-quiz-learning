from app.config import get_settings


def build_chat_model():
    from langchain.chat_models import init_chat_model

    settings = get_settings()
    model_name = settings.deepseek_model.strip() or "deepseek-v4-flash"
    kwargs = {
        "model_provider": "deepseek",
        "timeout": 90,
        "max_tokens": 8192,
        "max_retries": 2,
        "extra_body": {"thinking": {"type": "disabled"}},
    }
    if settings.deepseek_api_key:
        kwargs["api_key"] = settings.deepseek_api_key
    return init_chat_model(model_name, **kwargs)
