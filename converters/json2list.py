
from . import data_cleaner
import nltk

def get_data(json_obj):
    print("In json2list")
    docs = json_obj.get('documents')
    if not docs:
        return "No 'documents' key found", None

    paragraphs = []
    for paragraph_json in docs:
        id = paragraph_json.get("id")
        #print("id: ", id)
        paragraph_text = paragraph_json.get("text")
        #print("text: ", paragraph_text)
        
        # Make sure text is not over max tokens
        if len(nltk.word_tokenize(text)) > globalvars.MAX_TOKENS:
            paragraph_text = globalutils.get_last_sentence(paragraph_text)
        cleaned = data_cleaner.clean(paragraph_text)
        paragraphs.append(cleaned)

    return None, paragraphs
