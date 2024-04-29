import json
import os
import time
from datetime import date

import streamlit as st
import openai
from dotenv import find_dotenv, load_dotenv
import requests

from AssistantManager import AssistantManager

# Load our environment variables
load_dotenv()


def main():
    # print(get_flights("DUB", "AGP"))
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
                             "traveller's interests and budget. If a user asks for information on flights between "
                             "specific destinations and on specific dates, you can use your available tools to return "
                             "that information.",
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
                                    },
                                    "dateFrom": {
                                        "type": "string",
                                        "description": "The earliest date the user is interested in for their flight, "
                                                       "to be formatted as DD/MM/YYYY"
                                    },
                                    "dateTo": {
                                        "type": "string",
                                        "description": "The latest date the user is interested in for their flight, "
                                                       "to be formatted as DD/MM/YYYY"
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

            # Wait for completion and process messages
            manager.wait_for_completion(st)

            summary = manager.get_summary()

            st.write(summary)


if __name__ == "__main__":
    main()
