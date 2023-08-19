import re
import unicodedata


def slugify(s):
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    s = s.lower().strip()
    s = delete_accent(s)
    return s

def delete_accent(text):
    text = unicodedata.normalize('NFKD', text)
    return "".join([c for c in text if not unicodedata.combining(c)]) 