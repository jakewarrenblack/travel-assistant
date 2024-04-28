import json
import os

import openai
from dotenv import find_dotenv, load_dotenv
import requests

# Load our environment variables
load_dotenv()

kiwi_api_key = os.environ.get("KIWI_API_KEY")

# Instantiate an OpenAI client
# Don't need to explicitly pass API key after loading all env vars above
client = openai.OpenAI()

# I may switch this to GPT-4 at some point,
# but GPT-3.5-Turbo is fine
model = "gpt-3.5-turbo-16k"


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
    print(get_flights("DUB", "AGP"))


if __name__ == "__main__":
    main()
