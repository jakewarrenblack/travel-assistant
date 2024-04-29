import time
import openai
import json
from get_flights import get_flights

# I may switch this to GPT-4 at some point,
# but GPT-3.5-Turbo is fine
model = "gpt-3.5-turbo-16k"


class AssistantManager:
    thread_id = "thread_VscIuPp7RinEr5Zqed9HXUiF"
    assistant_id = "asst_mMItjPckIcHQ3Zc5iU7OD9Qe"

    def __init__(self):
        self.client = openai.OpenAI()
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.flights = None
        self.summary = None

        # If assistant id already exists, set the assistant object to use that assistant
        # Instead of creating a new one
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=self.assistant_id
            )

        # Same thing, if already exists, use the existing one
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=self.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model
            )

            self.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"Assistant ID: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()  # no params

            self.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"Thread ID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        # Obviously, we need a thread ID to be able to add a message
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions
            )

    def process_messages(self):
        # Again, messages live inside threads, can't process messages without a thread
        if self.thread:
            # A list of messages
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value

            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"Summary: {role.capitalize()}: ==> {response}")

    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_flights":
                output = get_flights(flyFrom=arguments["flyFrom"], flyTo=arguments["flyTo"])
                print(f"OUTPUT FROM GET FLIGHTS CALL: {output}")

                output_str = ""

                for item in output:
                    output_str += "".join(item)

                tool_outputs.append({"tool_call_id": action["id"], "output": output_str})



            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Sending outputs back to the assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )

    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        # When a run is invoked, the steps the assistant goes through can take some time,
        # So we need a helper to wait until it's done
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id,
                )

                # generate a JSON representation of the model
                print(f"Run status: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_messages()
                    break

                # When the status says some action is required, figure out what function we need to run
                # And call that function, an external tool (which is e.g. our flights function)
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING HAPPENING...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    def run_steps(self):
        # Go through all the run steps, retrieve info
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id,
            run_id=self.run.id,
        )

        print(f"Run-Steps: {run_steps}")

        return run_steps.data
