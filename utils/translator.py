import requests
import time

api_url = 'https://api-free.deepl.com/v2/translate'
api_key = ''

original_language = 'JA'
target_language = 'EN'

def convert_language_to_code(language):
    if language == "English":
        language = "EN"
    elif language == "Spanish":
        language = "ES"
    elif language == "French":
        language = "FR"
    elif language == "German":
        language = "DE"
    elif language == "Italian":
        language = "IT"
    elif language == "Portuguese":
        language = "PT"
    elif language == "Russian":
        language = "RU"
    elif language == "Chinese":
        language = "ZH"
    elif language == "Japanese":
        language = "JA"
    elif language == "Korean":
        language = "KO"
    return language

def deepl_translate(text, api_key=api_key, original_language=original_language, target_language=target_language):
    params = {
        "auth_key": api_key,
        "text": text,
        "source_lang": original_language,
        "target_lang": target_language
    }

    response = requests.post(api_url, data=params)
    return response.json()['translations'][0]['text']