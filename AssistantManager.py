import time
import openai
import json

from EventHandler import EventHandler
from get_flights import get_flights

# I may switch this to GPT-4 at some point,
# but GPT-3.5-Turbo is fine
model = "gpt-3.5-turbo-16k"


class AssistantManager:
    thread_id = "thread_bG7ee22hatGA5BKCZOgPYV0x"
    assistant_id = "asst_tFQbjwc0qRlJp5nt6Z8Bjar7"

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

    def list_runs(self):
        runs = self.client.beta.threads.runs.list(
            self.thread.id
        )

        print("List of runs: ", runs)

        for run in runs:
            # Not allowed to cancel an expired, completed etc run
            if run.status == "queued" or run.status == "in_progress" or run.status == "requires_action":
                self.client.beta.threads.runs.cancel(
                    thread_id=self.thread.id,
                    run_id=run.id
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

        else:
            self.list_runs()
            return

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
            # At this point, we can override the tools made available at the assistant creation level if need be
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

    #     self.client.beta.threads.runs.submit_tool_outputs(
    #         thread_id=self.thread.id,
    #         run_id=self.run.id,
    #         tool_outputs=tool_outputs
    #     )

    def get_summary(self):
        return self.summary

    def wait_for_completion(self, socketio):

        with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                event_handler=EventHandler(client=self.client, socketio=socketio)
        ) as stream:
            stream.until_done()

            #self.summary = stream
