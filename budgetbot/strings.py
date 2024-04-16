import json
from conf import FOLDER
from string import Template

def load_locale(locale): # locale as in "ua", "en", etc
    f = open(FOLDER + 'locale_' + locale + '.json')
    return json.load(f)
    
locale = 'ua'

def get_string(key, **kwargs):
    try: 
        data = load_locale(locale)
        return Template(data[key]).safe_substitute(**kwargs)
    except Exception as e:
        print(e)
        return key