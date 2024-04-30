from flask import Flask
from flask_socketio import SocketIO, emit
from dotenv import find_dotenv, load_dotenv
from AssistantManager import AssistantManager
from flask_cors import CORS

# Load our environment variables
load_dotenv()

global manager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

import streamlit as st

st.write_stream

@socketio.on('message_from_frontend')
def handle_message(message):

    print('message from client: ', message)

    manager.add_message_to_thread(
        role="user",
        content=f"{message}"
    )

    # Wait for completion and process messages, the EventManager will look after running any necessary functions
    # We pass the socketio instance here, so we can emit the assistant's response to the frontend
    manager.wait_for_completion(socketio)


if __name__ == "__main__":
    manager = AssistantManager()

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

    socketio.run(app)
