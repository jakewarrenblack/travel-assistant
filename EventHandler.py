import streamlit
from openai import AssistantEventHandler
from typing_extensions import dataclass_transform
import json
from get_flights import get_flights


class EventHandler(AssistantEventHandler):

    def __init__(self, client=None, st=None):
        super().__init__()
        self.client = client
        self.st = st

    @dataclass_transform()
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_flights":
                args = json.loads(tool.function.arguments)

                # submit_tool_outputs_stream (or just submit_tool_outputs) expects an object with the output in the form of a string
                output = get_flights(flyFrom=args["flyFrom"], flyTo=args["flyTo"])
                output_str = ""

                for item in output:
                    output_str += "".join(item)

                tool_outputs.append({"tool_call_id": tool.id, "output": output_str})

            elif tool.function.name == "get_booking_info":
                # Not implemented
                pass

        # Submit all tool_outputs at the same time
        # wrap in write_stream to write text chunks to the UI in a typewriter style
        # saw this here: https://community.openai.com/t/asynchronously-stream-openai-gpt-outputs-streamlit-app/612793
        self.st.write_stream(self.submit_tool_outputs(tool_outputs, run_id))

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:

                yield text

                #print(text, end="", flush=True)

            #print()





