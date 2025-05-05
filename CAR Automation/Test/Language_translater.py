from langdetect import detect
from googletrans import Translator

def translate_text(text, source_language='pt', target_language='en'):
    translator = Translator()
    translation = translator.translate(text, src=source_language, dest=target_language)
    return translation.text


title = "Effect of mode of delivery on postpartum health-related quality of lifeOriginal Article"

translated_title = translate_text(title)
print(translated_title)