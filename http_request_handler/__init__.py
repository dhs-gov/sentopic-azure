import logging
import sys
import json
import time
import jsonpickle
import azure.functions as func
import azure.durable_functions as df
import sentopic_activity
from converters import dataextractor

valid_endpoint_namesnames = ['sentopic']

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:

    endpoint_name = req.route_params.get('functionName')
    print("functionName: " + endpoint_name)
    if endpoint_name not in valid_endpoint_namesnames:
        return func.HttpResponse("Invalid endpoint name.", status_code=400)

    # Get incoming data
    error, data_in = dataextractor.get_data(req)

    if error:
        return func.HttpResponse("Error: " + error, status_code=400)

    if not data_in:
        return func.HttpResponse("Error: Could not extract data." + error, status_code=400)

    # ALL ASYNCHRONOUS REQUESTS
    print("mode: asynchronous")

    client = df.DurableOrchestrationClient(starter)
    # Note that "functionName" gets automatically resolved to req.method function name
    # (e.g., 'sentopic').
    print("Running " + endpoint_name)

    #json_in = json.dumps(json_obj_in)
    #print("JSON IN: ", json_in)

    instance_id = await client.start_new(req.route_params["functionName"], None, data_in)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    response = client.create_check_status_response(req, instance_id)

    # Always clear Azure cache so it doesn't try to 'replay' this activity
    #  in cache.
    purge_results = client.purge_instance_history(instance_id)
    print("purge_results 2: ", purge_results)

    return response
