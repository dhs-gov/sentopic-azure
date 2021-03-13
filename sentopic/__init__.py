import logging
import json
import jsonpickle

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    print("Running sentiment orchestrator")

    data_in = context.get_input()

    result1 = yield context.call_activity('sentopic_activity', data_in)
    print("RESULT: ", result1)
    context.set_custom_status("NOTE: Asynchronous Azure Durable Functions add quotes around JSON output and also add escaped double quotes around keys in the JSON output.")
    return [result1]


main = df.Orchestrator.create(orchestrator_function)