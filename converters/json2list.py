
from . import data_cleaner
from globals import globalvars
import nltk


def get_data(json_obj):
    print("In json2list")
    docs = json_obj.get('documents')
    if not docs:
        return "No 'documents' key found", None

    paragraphs = []
    for doc in docs:
        text = doc.get('text')
        print("text: ", text)
        
        # Make sure text is not over max tokens
        if len(nltk.word_tokenize(text)) > globalvars.MAX_TOKENS:
            print("len: ", nltk.word_tokenize(text))
            text = globalutils.get_last_sentence(text)
        print("para 1: ", text)
        cleaned = data_cleaner.clean(text)

        print("para 2: ", cleaned)
        paragraphs.append(cleaned)

    if not paragraphs:
        print("WARNING: No paragraphs found!")

    return None, paragraphs
