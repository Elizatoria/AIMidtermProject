'''
1. Set up Evviroment by importing libraries and loading in the API Keys
pip install python-dotenv openai psutil requests

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

def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_battery_status():
    battery = psutil.sensors_battery()
    return {
        "percent": battery.percent,
        "plugged_in": battery.power_plugged
    }

def get_top_headlines(api_key):
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    return response.json()

def get_current_weather(api_key, location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url)
    return response.json()

def get_wolfram_alpha_answer(api_key, query):
    url = f"http://api.wolframalpha.com/v1/result?i={query}&appid={api_key}"
    response = requests.get(url)
    return response.text

# print(get_top_headlines("News_API"))  # {'status': 'error', 'code': 'apiKeyInvalid', 'message': 'Your API key is invalid or incorrect. Check your key, or go to https://newsapi.org to create a free API key.'}
# print(get_current_weather("Weather_API", "Rome, NY"))  # {'cod': 401, 'message': 'Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.'}
# print(get_wolfram_alpha_answer("Wolfram_Alpha_API", "What is the percent of 68 out of 100?"))  # Error 1: Invalid appid