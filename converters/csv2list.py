import csv
from io import StringIO
import nltk
from globals import globalvars
from . import data_cleaner

class CsvRow:
    def __init__(self, row_num, text):
        self.row_num = row_num
        self.text = text


def get_data(csv_bytes):
    string_data = StringIO(csv_bytes.decode())
    reader = csv.reader(string_data, quotechar='"', delimiter=',')
    data = []
    for row in reader:
        text = "".join(row)
        # Make sure text is not over max tokens
        if len(nltk.word_tokenize(text)) > globalvars.MAX_TOKENS:
            text = globalutils.get_last_sentence(text)

        cleaned = data_cleaner.clean(text)
        data.append(cleaned)

    return None, data