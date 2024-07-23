'''
1. Set up Evviroment
pip install psutil requests python-dotenv openai

2. Create Data Retrieval Functions
get_current_weather: Returns the current weather for a specified location using the OpenWeatherMap API.
ask_wolfram: Returns a factual answer to a query using the Wolfram Alpha Short Answers API.
get_current_time_and_date: Returns the current date and time.
get_top_headlines: Returns the top news headlines using the NewsAPI.
get_battery_status: Returns the battery percentage and whether the device is plugged in.
'''
import datetime
import psutil
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

# Load environment variables from .env file
load_dotenv("C:/Users/Eliza/Documents/MachineLearning/AI_API/midterm_api.env")

# Access environment variables
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
newsapi_key = os.getenv("NEWSAPI_KEY")
wolframalpha_app_id = os.getenv("WOLFRAMALPHA_APP_ID")

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

def ask_wolfram(query):
    url = f"http://api.wolframalpha.com/v1/result?i={query}&appid={wolframalpha_app_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return f"{query}: {response.text}."
    else:
        return "Sorry, I couldn't retrieve the answer."

def get_current_time_and_date():
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."

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

'''3. Create the Function to make the Conversation Chatbot'''
# Function to handle the conversation
def run_conversation():
    '''Test Messages to make sure the APIs are connected and the Functions are correct'''
    # messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]  # Weather for San Francisco, Tokyo, and Paris
    # messages = [{"role": "user", "content": "What is the percent of 68 out of 100?"}]  # 68/100 = 0.68
    # messages = [{"role": "user", "content": "What is the current date and time?"}]  # Today's date and time
    # messages = [{"role": "user", "content": "What are the top headlines?"}]  # Top headlines for today
    # messages = [{"role": "user", "content": "What is the battery status?"}]  # Battery status
    '''Actual Messages (Message_List)'''
    # Set up the initial message list with a system message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]
    '''
    Function Dictionaries
    Create the tool list that describes these functions and the arguments necessary for the function in natural language.
    '''
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ask_wolfram",
                "description": "Ask Wolfram Alpha a question for factual information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The question to ask Wolfram Alpha"},
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time_and_date",
                "description": "Get the current time and date",
            },
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
        }
    ]
    '''
    Begin the Loop and ask for a Prompt
    Make a loop where the prompt and response pairs are appended to the message list
    '''
    while True:
        prompt = input("Enter a prompt (or type 'exit' to quit): ")
        if prompt.lower() == 'exit':
            print("Goodbye!")
            break
        
        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Check if the model wanted to call a function
        if tool_calls:
            available_functions = {
                "get_current_weather": get_current_weather,
                "ask_wolfram": ask_wolfram,
                "get_current_time_and_date": get_current_time_and_date,
                "get_top_headlines": get_top_headlines,
                "get_battery_status": get_battery_status
            }
            messages.append(response_message)
            
            '''
            Append the data returned from the called function to the message list with the role “tool” 
            and make another API call for the final response
            '''
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            print(second_response.choices[0].message.content)

print(run_conversation())

'''
Addition Test Questions for the actual prompt

1. Who is the Director for Transformers One? The director for the first Transformers movie is Michael Bay.  
# Transformers One seems to be too new, so they give informtion for the first live action Transformers movie instead. 
# However, Michael Bay is still on the Production Team, just not the Director.

2. What is a top headline for today? Here are some top headlines for today: (07/21/2024)
# 1. Bangladesh Cops Given Shoot-On-Sight Orders Amid Curfew To Quell Student Protests - from NDTV
# 2. WNBA All-Stars vs. Team USA: Caitlin Clark, Angel Reese make rookie debuts - from USA TODAY
# 3. Israeli military airstrikes hit Houthi targets in Yemen in retaliation to attacks - from CBS News
# 4. Country singer Rory Feek marries his daughter’s teacher 8 years after death of his wife Joey - from Page Six
# 5. NASA’s Curiosity rover makes ‘mind-blowing’ discovery on Mars - from New York Post
(Function is coded to give five Headlines)

3. What is the weather for Rome? The current weather in Rome is 80.11 degrees Fahrenheit with broken clouds. (07/21/2024 9:38 PM)

4. What is the weather for New York? The current weather in New York is 77.95 degrees Fahrenheit with light rain. (07/21/2024 9:38 PM)

5. What is the battery status? The battery is at 98% and is currently charging.

6. What is the date and time for today? The current date and time for today is 2024-07-21 21:57:58.

# "Is there anything else you would like to know?" is the response if it doesn't understand a question.
'''