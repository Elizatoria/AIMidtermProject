'''
1. Set up Evviroment
pip install openai psutil requests

2. Create Data Retrieval Functions
get_current_datetime: Returns the current date and time.
get_battery_status: Returns the battery percentage and whether the device is plugged in.
get_top_headlines: Returns the top news headlines using the NewsAPI.
get_current_weather: Returns the current weather for a specified location using the OpenWeatherMap API.
get_wolfram_alpha_answer: Returns a factual answer to a query using the Wolfram Alpha Short Answers API.
'''
import datetime
import psutil
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os, json

load_dotenv("C:/Users/Eliza/Documents/MachineLearning/AI_API/midterm_api.env")

# Function to get current date and time
def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to get battery status
def get_battery_status():
    battery = psutil.sensors_battery()
    return {
        "percent": battery.percent,
        "plugged_in": battery.power_plugged
    }

# Function to get top news headlines
def get_top_headlines(News_API):
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={News_API}"
    response = requests.get(url)
    return response.json()

# Function to get current weather
def get_current_weather(Weather_API, location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={Weather_API}"
    response = requests.get(url)
    return response.json()

# Function to get factual information
def get_wolfram_alpha_answer(WolfRam_API, query):
    url = f"http://api.wolframalpha.com/v1/result?i={query}&appid={WolfRam_API}"
    response = requests.get(url)
    return response.text

'''
4. Implement Function Calling in Chatbot
'''

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

messages = []

def call_function(name, args):
    if name == "get_current_datetime":
        return get_current_datetime()
    elif name == "get_battery_status":
        return get_battery_status()
    elif name == "get_top_headlines":
        return get_top_headlines(args['api_key'])
    elif name == "get_current_weather":
        return get_current_weather(args['api_key'], args['location'])
    elif name == "get_wolfram_alpha_answer":
        return get_wolfram_alpha_answer(args['api_key'], args['query'])
    else:
        return "Function not recognized"

def chat(prompt):
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=[
            {
                "name": "get_current_datetime",
                "description": "Returns the current date and time.",
                "parameters": {}
            },
            {
                "name": "get_battery_status",
                "description": "Returns the battery percentage and whether the device is plugged in.",
                "parameters": {}
            },
            {
                "name": "get_top_headlines",
                "description": "Returns the top news headlines.",
                "parameters": {"api_key": "string"}
            },
            {
                "name": "get_current_weather",
                "description": "Returns the current weather for a specified location.",
                "parameters": {"api_key": "string", "location": "string"}
            },
            {
                "name": "get_wolfram_alpha_answer",
                "description": "Returns a factual answer to a query.",
                "parameters": {"api_key": "string", "query": "string"}
            }
        ]
    )
    message = response.choices[0].message
    if "function_call" in message:
        function_name = message['function_call']['name']
        function_args = message['function_call']['parameters']
        function_result = call_function(function_name, function_args)
        messages.append({"role": "tool", "content": function_result})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    messages.append({"role": "assistant", "content": response.choices[0].message['content']})
    return response.choices[0].message['content']

# Example of using the chat function
print(chat("What is the current weather in New York?"))