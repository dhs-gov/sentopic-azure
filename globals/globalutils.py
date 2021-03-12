def get_last_sentence(text):
    sentences = text.split('.')
    for s in reversed(sentences):
        if s:
            return s
