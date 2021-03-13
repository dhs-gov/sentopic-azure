def clean(text):
    text = text.replace('"', '')
    text = text.replace("'", '')
    text = text.replace('\n','')
    text = text.replace('\t','')
    return text