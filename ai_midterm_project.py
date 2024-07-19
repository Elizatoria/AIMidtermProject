import openai
import os
import json
import requests
from datetime import datetime
import psutil
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv("C:/Users/Eliza/Documents/MachineLearning/AI_API/midterm_api.env")

# Access environment variables
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
newsapi_key = os.getenv("NEWSAPI_KEY")
wolframalpha_app_id = os.getenv("WOLFRAMALPHA_APP_ID")

# Initialize the message list
message_list = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]

# Define the functions to interact with external APIs and libraries
def get_current_weather(location, unit="fahrenheit"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units={'imperial' if unit == 'fahrenheit' else 'metric'}&appid={openweathermap_api_key}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return f"The current weather in {location} is {temperature} degrees {unit} with {weather_description}."
    else:
        return "Sorry, I couldn't retrieve the weather data."

def get_top_headlines():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi_key}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        headlines = [article['title'] for article in data['articles'][:5]]
        return "Here are the top headlines:\n" + "\n".join(headlines)
    else:
        return "Sorry, I couldn't retrieve the news."

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"The battery is at {battery.percent}% and it is {'charging' if battery.power_plugged else 'not charging'}."
    else:
        return "Sorry, I couldn't retrieve the battery status."

def get_current_time_and_date():
    now = datetime.now()
    return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."

def ask_wolfram(query):
    url = f"http://api.wolframalpha.com/v1/result?i={query}&appid={wolframalpha_app_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Sorry, I couldn't retrieve the answer."

# Define the tool list with function descriptions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    },
                },
                "required": ["location"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_headlines",
            "description": "Get the current top news headlines.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_battery_status",
            "description": "Get the current battery status of the device.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time_and_date",
            "description": "Get the current time and date.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_wolfram",
            "description": "Ask Wolfram Alpha a question for factual information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to ask Wolfram Alpha.",
                    },
                },
                "required": ["query"],
            },
        }
    }
]
'''___Above Working___'''
# Function to handle the conversation
def run_conversation():
    while True:
        user_input = input("Enter a message: ")
        message_list.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_list,
            functions=tools,
            function_call="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response.message.get("function_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                function_result = globals()[function_name](**function_args)
                message_list.append({
                    "role": "tool",
                    "content": function_result
                })
                message_list.append({
                    "role": "assistant",
                    "content": function_result
                })
        else:
            message_list.append(response_message)

        print(response_message["content"])

# Run the conversation
run_conversation()