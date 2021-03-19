import logging
import sys
import json
import time
import jsonpickle
import azure.functions as func
import azure.durable_functions as df
import sentop_activity
from converters import data_extractor


class DataIn:
    def __init__(self, data_in, stop_words):
        self.data_in = data_in
        self.stop_words = stop_words

    
valid_endpoint_namesnames = ['sentop']


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:

    # ----------------------------- CONVERT INCOMING DATA ------------------------------

    print("SenTopic received request")

    endpoint_name = req.route_params.get('functionName')
    #print("functionName: " + endpoint_name)
    if endpoint_name not in valid_endpoint_namesnames:
        return func.HttpResponse("Invalid endpoint name.", status_code=400)

    # Get incoming data
    data_in, error, stop_words = data_extractor.get_data(req)

    if error:
        return func.HttpResponse(error, status_code=400)
    #print("Data in: ", data_in)
    data_in_obj = DataIn(data_in, stop_words)
    json_obj = jsonpickle.encode(data_in_obj, unpicklable=True)

    # Since Azure requires that we must pass an object that is JSON
    # serializable, we have to convert to a JSON object.


    # ------------------------ DELETE EXISTING RUN INSTANCES ------------------------------

    # Create orchestration client
    client = df.DurableOrchestrationClient(starter)

    # Delete any existing (old) run instances, otherwise previous runs will 'replay'.
    print("Getting existing run instances:")
    instances = await client.get_status_all()
    print("Num instances: ", len(instances))
    for instance in instances:
        print("*INSTANCE FOUND! ", instance)
        #logging.log(json.dumps(instance))
        old_instance_id = instance.instance_id

        reason = "To prevent replay."
        # Terminate existing instances
        status = await client.get_status(old_instance_id)
        print("## Instance status: ", status.runtime_status)
        status_str = str(status.runtime_status)
        print("status_str: ", status_str)
        if status_str == 'OrchestrationRuntimeStatus.Completed':
            # Purge completed status from history
            purge_results = await client.purge_instance_history(old_instance_id)
            print("Purged instance: ", purge_results)
        else:
            print("Instance NOT COMPLETED-TERMINATING!: ", old_instance_id)
            await client.terminate(old_instance_id, "Trying to terminate")
            purge_results = await client.purge_instance_history(old_instance_id)
            print("Terminated old instance: ", purge_results)

    # Make sure old instances are deleted
    all_instances_deleted = True
    instances = await client.get_status_all()
    for instance in instances:
        if instance:
            all_instances_deleted = False
            print("WARNING! Old instance still alive! ", instance)
    if all_instances_deleted:
        print("ALL PREVIOUS INSTANCES DELETED!")


    # ------------------------------ CREATE NEW INSTANCE -------------------------------

    # Note that "functionName" gets automatically resolved to req.method function name
    # (e.g., 'sentopic').
    print("Running " + endpoint_name)

    #json_in = json.dumps(json_obj_in)
    #print("JSON IN: ", json_in)

    instance_id = await client.start_new(req.route_params["functionName"], None, json_obj)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")


    # -------------------------------- RETURN RESPONSE ---------------------------------

    response = client.create_check_status_response(req, instance_id)
   
    return response
