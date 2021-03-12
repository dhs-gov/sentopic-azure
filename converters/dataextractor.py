from . import json2list
from . import csv2list
import logging

def get_data(req):
    print("In dataextractor.get_data()")
    # Check json payload
    json_obj_in = None
    data_in = None
    try:
        return json2list.get_data(req.get_json())
    except:
        print("Warning: JSON payload not found")

    # Check if files are present:
    #try:
    #    files_list = req.files.values()
    #    print("files_list: ", files_list.name)
    #except:
    #    print("Warning: Files payload not found")

    files_found = False
    for input_file in req.files.values():
        files_found = True
        filename = input_file.filename
        print("Filename: ", filename)
        contents = input_file.stream.read()

        print("contents type: ", type(contents))

        if filename.endswith('.csv'):
            return csv2list.get_data(contents)
        #elif filename.endswith('docx'):
        #    contents = input_file.stream.read()

        #logging.info('Contents:')
        #logging.info(contents)


    return None, None