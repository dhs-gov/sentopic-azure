# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging
import sys
import json
import time
import jsonpickle
import azure.functions as func
import azure.durable_functions as df
import sentopic_activity

valid_func_name = ['sentopic', 'ner']

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:

    functionName = req.route_params.get('functionName')
    print("functionName: " + functionName)
    if functionName not in valid_func_name:
        return func.HttpResponse("Invalid endpoint name.", status_code=400)

    # Check if json payload is present
    json_obj_in = None
    try:
        json_obj_in = req.get_json()
        print("json_obj_in type: ", type(json_obj_in)) 
    except:
        print("Warning: JSON payload not found")

    # Check if files are present:
    files_list = None
    try:
        files_list = req.files.getlist
        print(files_list)
    except:
        print("Warning: Files payload not found")

    if not json_obj_in and not files_list:
        print("Warning: No json of files found")
        return func.HttpResponse("No payload detected.", status_code=400)

    for input_file in req.files.values():
        filename = input_file.filename
        contents = input_file.stream.read()

        logging.info('Filename: %s' % filename)
        logging.info('Contents:')
        logging.info(contents)

    return func.HttpResponse(f'Done\n')

    #return func.HttpResponse("No json found in body.", status_code=400)

    is_async = req.params.get('async')

    if not is_async or is_async == 'false':
        # ALL SYNCHRONOUS REQUESTS
        print("mode: synchronous")
        return func.HttpResponse("Due to the processing time required for sentiment analysis and topic modeling, only asynchronous requests are permitted. Please set async=true.", status_code=400)

        json_out = None
        error_msg = None
        
        if functionName == 'sentiment':  
            json_out, error_msg = sentiment_activity.run(json_obj_in)
        elif functionName == 'topics':
            json_out, error_msg = topics_activity.run(json_obj_in)
        elif functionName == 'ner':
            json_out, error_msg = ner_activity.run(json_obj_in)
        else:
            error_msg = "Unknown endpoint."

        if json_out:
            return func.HttpResponse(json_out, status_code=200)
        elif error_msg:
            return func.HttpResponse(error_msg, status_code=500)
        else:
            return func.HttpResponse("Unknown error occurred.", status_code=500)


    else:
        # ALL ASYNCHRONOUS REQUESTS
        print("mode: asynchronous")

        client = df.DurableOrchestrationClient(starter)
        # Note that "functionName" gets automatically resolved to req.method function name
        # (e.g., 'sentiment', 'topics', etc.).
        print("Running asynchronous " + functionName)

        #json_in = json.dumps(json_obj_in)
        #print("JSON IN: ", json_in)

        instance_id = await client.start_new(req.route_params["functionName"], 
                                        None, json_obj_in)

        logging.info(f"Started orchestration with ID = '{instance_id}'.")

        response = client.create_check_status_response(req, instance_id)

        # Always clear Azure cache so it doesn't try to 'replay' this activity
        #  in cache.
        purge_results = df.DurableOrchestrationClient.purge_instance_history
        print("purge_results: ", purge_results)

        return response

