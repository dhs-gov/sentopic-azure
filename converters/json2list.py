
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
        paragraphs.append(paragraph_text)

    return None, paragraphs
