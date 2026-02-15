user_preferences = {}

def set_language(chat_id: str, lang: str):
    user_preferences[str(chat_id)] = lang

def get_language(chat_id: str) -> str:
    return user_preferences.get(str(chat_id), "pt")