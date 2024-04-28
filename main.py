import openai
from dotenv import find_dotenv, load_dotenv


# Load our environment variables
load_dotenv()

# Instantiate an OpenAI client
# Don't need to explicitly pass API key after loading all env vars above
client = openai.OpenAI()

# I may switch this to GPT-4 at some point,
# but GPT-3.5-Turbo is fine
model = "gpt-3.5-turbo-16k"

# Create an assistant
travel_agent_assistant = client.beta.assistants.create(
    name="Travel Agent",
    instructions="You are a digital travel agent assistant. Your primary role is to assist users in planning and "
                 "managing their travel. You provide peronalised recommendations for flights, accommodation, "
                 "restaurants, activities, and attractions based on the traveller's interests and budget.",
    model=model,
)


# Create a sample Thread
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Please recommend a travel itinerary for Paris"
        }
    ]
)


