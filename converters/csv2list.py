import csv
import io
from io import StringIO
from io import BytesIO
import nltk
from globals import globalvars
from globals import globalutils
from . import data_cleaner
import pandas as pd

class CsvRow:
    def __init__(self, row_num, text):
        self.row_num = row_num
        self.text = text


def get_data(csv_bytes):
    fh_bytes = io.BytesIO(csv_bytes)
    fh = io.TextIOWrapper(fh_bytes, encoding='cp1252', errors='strict')
    reader = fh.readlines()
    #string_data = StringIO(csv_bytes.decode())
    #reader = csv.reader(df1, quotechar='"', delimiter=',')
    data = []
    for row in reader:
        text = "".join(row)
        #print("text: ", text)
        # Make sure text is not over max tokens
        if len(nltk.word_tokenize(text)) > globalvars.MAX_TOKENS:
            text = globalutils.get_last_sentence(text)

        cleaned = data_cleaner.clean(text)
        data.append(cleaned)

    return None, data