import json
import os
import time
import streamlit as st
import openai
from dotenv import find_dotenv, load_dotenv
import requests

# Load our environment variables
load_dotenv()

kiwi_api_key = os.environ.get("KIWI_API_KEY")

# Instantiate an OpenAI client
# Don't need to explicitly pass API key after loading all env vars above
#client = openai.OpenAI()

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


# Create an assistant
# travel_agent_assistant = client.beta.assistants.create(
#     name="Travel Agent",
#     instructions="You are a digital travel agent assistant. Your primary role is to assist users in planning and "
#                  "managing their travel. You provide peronalised recommendations for flights, accommodation, "
#                  "restaurants, activities, and attractions based on the traveller's interests and budget.",
#     model=model,
# )
#

#
# # Create a sample Thread
# thread = client.beta.threads.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Please recommend a travel itinerary for Paris"
#         }
#     ]
# )

# print('thread id: ', thread.id)
# print('assistant id: ', travel_agent_assistant.id)

# Previously retrieved these IDs in the first run, which created the assistant
# Hard coding them
# thread_id = "thread_grtb25OdIZT8MtLUiG5osdKr"
# assistant_id = "asst_6M1WTN9790nHJqneE52qfLB5"

# Creating a message
# message = "Please help me to plan an itinerary for a trip to Paris"

# message = client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=message
# )

# Run the assistant
# Run must know the assistant ID and the thread ID
# run = client.beta.threads.runs.create(
#     thread_id=thread_id,
#     assistant_id=assistant_id,
#     instructions="Please address the user as Jake "
# )


def get_flights(flyFrom, flyTo, dateFrom=None, dateTo=None):
    # apiKey = ***REMOVED***
    # To be passed in headers
    url = f'https://api.tequila.kiwi.com/v2/search?flyFrom={flyFrom}&to={flyTo}'

    try:
        response = requests.get(url, headers={
            "apiKey": kiwi_api_key
        })

        if response.status_code == 200:
            res = json.dumps(response.json(), indent=4)
            res_json = json.loads(res)['data']

            flights = res_json

            concatenated_flights_info = []

            for flight in flights:
                cityFrom = flight["cityFrom"]
                cityTo = flight["cityTo"]
                depart_at = flight["local_departure"]
                arrive_at = flight["local_arrival"]
                price_per_person = flight["price"]
                available_seats = flight["availability"]["seats"]

                info = f"""
                    From: {cityFrom},
                    To: {cityTo},
                    Depart at: {depart_at},
                    Arrive at: {arrive_at},
                    Price per person: {price_per_person},
                    Available sets: {available_seats}
                """

                concatenated_flights_info.append(info)

            return concatenated_flights_info

        else:
            return []  # No flights found

    except requests.RequestException as e:
        print("Error occurred during API call: ", e)


def main():
    #print(get_flights("DUB", "AGP"))
    manager = AssistantManager()

    st.title("Travel Helper")

    with st.form(key="user_input_form"):
        instructions = st.text_input("Enter message")
        submit_button = st.form_submit_button(label="Run Assistant")

        # Handle form submit
        if submit_button:
            manager.create_assistant(
                name="Travel helper",
                instructions="You are a digital travel agent assistant. Your primary role is to assist users in "
                             "planning and managing their travel. You provide personalised recommendations for "
                             "flights, accommodation, restaurants, activities, and attractions based on the "
                             "traveller's interests and budget.",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_flights",
                            "description": "Get flight information for two given locations",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "flyFrom": {
                                        "type": "string",
                                        "description": "The start airport for the flight, e.g. DUB (Dublin airport)"
                                    },
                                    "flyTo": {
                                        "type": "string",
                                        "description": "The end destination for the flight, e.g. AGP (Malaga airport)"
                                    }
                                }
                            },
                            "required": ["flyFrom", "flyTo"]
                        }
                    }
                ]
            )

            manager.create_thread()

            manager.add_message_to_thread(
                role="user",
                content=f"{instructions}"
            )

            manager.run_assistant(instructions="Follow the user's instructions")

            # Wait for completion and process messages
            manager.wait_for_completion()

            summary = manager.get_summary()

            st.write(summary)

            st.text("Run steps:")

            st.code(manager.run_steps(), line_numbers=True)


if __name__ == "__main__":
    main()
