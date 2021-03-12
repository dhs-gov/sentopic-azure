from docx import Document


def iterate_paragraphs(doc):
    in_data = False
    data = []
    for para in doc.paragraphs:
        if para.text == 'data-start':
            in_data = True
        elif para.text == 'data-end':
            in_data = False
        elif in_data:
            print(para.text)
            if para.text:
                data.append(para.text)
    return data


def get_data(docx_file):
    doc = Document(docx_file)
    return iterate_paragraphs(doc)
