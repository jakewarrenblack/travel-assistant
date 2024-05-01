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


@socketio.on('message_from_frontend')
def handle_message(message):
    print('message from client: ', message)

    manager.add_message_to_thread(
        role="user",
        content=f"{message}"
    )

    # Wait for completion and process messages, the EventManager will look after running any necessary functions
    manager.wait_for_completion()


if __name__ == "__main__":
    # We pass the socketio instance here, so we can emit the assistant's response to the frontend
    manager = AssistantManager(socketio=socketio)

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
            },
            {
                "type": "function",
                "function": {
                    "name": "get_hotels",
                    "description": "Search for a given query on TripAdvisor. This can be a search for hotels, "
                                   "restaurants, or attractions for a given area. The parameters are the search query "
                                   "and the category of the search query, where the category can be 'hotels', "
                                   "'restaurants', or 'attractions', and the search query is the text to use for "
                                   "searching based on the name of the location, such as 'Malaga'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "The search query to search for on TripAdvisor, which is the text to "
                                               "use for searching based on the name of the location, such as 'Malaga'"
                            },
                            "category": {
                                "type": "string",
                                "description": "The category of the search query, which can be 'hotels', "
                                               "'restaurants', or 'attractions'"
                            }
                        }
                    },
                    "required": ["search_query", "category"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tripadvisor_location_details",
                    "description": "Get the details of a location on TripAdvisor. This can be a location such as a "
                                   "hotel, restaurant, or attraction. The parameters are the location ID, which will "
                                   "have been obtained from a previous search, and the category of the location, "
                                   "where the category can be 'hotels', 'restaurants', or 'attractions'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location_id": {
                                "type": "string",
                                "description": "The location ID to get the details of, which will have been obtained "
                                               "from the results of a request to the tripadvisor_search function"
                            },
                        }
                    },
                    "required": ["location_id"]
                }
            }
        ]
    )

    manager.create_thread()

    socketio.run(app, allow_unsafe_werkzeug=True)
