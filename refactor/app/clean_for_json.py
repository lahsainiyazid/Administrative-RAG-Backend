import json, re, unicodedata, requests

def clean_for_json(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    # remove control chars except \n and \t (they get escaped properly by json.dumps)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[\u00ad\u200b-\u200d\ufeff]", "", text)
    # drop lone surrogates / invalid chars
    return text.encode("utf-8", "ignore").decode("utf-8")
