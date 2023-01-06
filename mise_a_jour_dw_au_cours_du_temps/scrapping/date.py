def trait_date(text,dictio):
    for key in dictio:
        text = text.replace(key, dictio[key]).strip()
    
    return text
