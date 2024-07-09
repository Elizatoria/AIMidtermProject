'''
1. Set up Evviroment by importing libraries and loading in the API Key
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
