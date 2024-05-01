from openai import AssistantEventHandler
from typing_extensions import dataclass_transform
import json
from get_flights import get_flights
from time import sleep

from tripadvisor_search import tripadvisor_search, tripadvisor_location_details


class EventHandler(AssistantEventHandler):

    def __init__(self, client=None, socketio=None):
        super().__init__()
        self.client = client
        self.socketio = socketio

    @dataclass_transform()
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        print('Sending this text to frontend: ', delta.value)
        self.socketio.emit('message_to_frontend', delta.value, namespace='/')

    # Text output without any action required is simply handled by on_text_delta, sends text directly to the frontend
    # If an action is required, the run is initialised and we iterate through whatever tools we need to call, the outputs of which are all sent to the frontend as the same stream
    @dataclass_transform()
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)
        elif event.event == 'thread.run.completed':
            # If the run is completed, we should send a special message to the frontend, so it knows the assistant is done
            if self.socketio is not None:
                sleep(
                    2)  # make sure we're definitely finished processing the message on the client side before telling it we're finished
                print('Run has completed')
                # Need to be sure that at this point, the assistant is finished sending messages
                # because on the client side, I want to take the complete message and add it to the chat history
                self.socketio.emit('run_completed')

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_flights":
                args = json.loads(tool.function.arguments)


                # IF the user asks for flights to a specific destination, but does not provide a flyFrom argument, we can assume they are asking for flights from Dublin
                if "flyFrom" not in args:
                    args["flyFrom"] = "DUB"
                # This is obviously not the best assumption to make, but for this example it's fine
                # I COULD send a message to the user saying to specify a flyFrom location...
                # but then I'd need to cancel the run, and rerun it when the user responds, providing the original flyTo location and the new flyFrom location


                # submit_tool_outputs_stream (or just submit_tool_outputs) expects an object with the output in the form of a string

                if "dateFrom" not in args:
                    args["dateFrom"] = None

                if "dateTo" not in args:
                    args["dateTo"] = None

                output = get_flights(flyFrom=args["flyFrom"], flyTo=args["flyTo"], dateFrom=args["dateFrom"], dateTo=args["dateTo"])
                output_str = ""

                for item in output:
                    output_str += "".join(item)

                tool_outputs.append({"tool_call_id": tool.id, "output": output_str})

            elif tool.function.name == "tripadvisor_search":
                args = json.loads(tool.function.arguments)

                # The LLM makes assumptions about what the function name should be, or what the parameters should be
                # The argument is really called search_query, but the LLM assumes it's called destination
                if "destination" in args:
                    args["search_query"] = args["destination"]
                    del args["destination"]


                output = tripadvisor_search(search_query=args["search_query"], category=args["category"])
                output_str = ""

                for item in output:
                    output_str += "".join(item)

                tool_outputs.append({"tool_call_id": tool.id, "output": output_str})
            elif tool.function.name == "tripadvisor_location_details":
                args = json.loads(tool.function.arguments)

                output = tripadvisor_location_details(location_id=args["location_id"])
                output_str = ""

                for item in output:
                    output_str += "".join(item)

                tool_outputs.append({"tool_call_id": tool.id, "output": output_str})

        # Submit all tool_outputs at the same time
        # wrap in write_stream to write text chunks to the UI in a typewriter style
        # saw this here: https://community.openai.com/t/asynchronously-stream-openai-gpt-outputs-streamlit-app/612793
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                # Simply passing 'self' here would raise the following error:
                # "A single event handler cannot be shared between multiple streams; You will need to construct a new event handler instance"
                event_handler=EventHandler(self.client, self.socketio)
        ) as stream:
            stream.until_done()
            # I was handling sending messages here, but there's no need. The on_text_delta method will handle this

    def handle_completed(self, event, run_id):
        # Use the submit_tool_outputs_stream helper
        with self.client.beta.threads.runs.stream(
                thread_id=self.client.thread.id,
                assistant_id=self.client.assistant.id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                event_handler=EventHandler(self.client, self.socketio)
        ) as stream:
            stream.until_done()
