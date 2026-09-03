# Import required libraries 
from AppOpener import close, open as appopen  # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard-related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.
from AppOpener.features import AppNotFound

# Load environment variables from the .env file.

print("Loading Automation model...")
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.
# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "zCubwf", "hgKEIc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6r0c", "O5uR6d LTKOO",
    "vLzY6d", "webanswers-webanswers_table__webanswers-table", "dOoNo ikb4bB gsrt",
    "sXLA0e", "LWkFke", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don’t hesitate to ask."
]

# List to store chatbot messages.
messages = []



# System ChatBot Initialization
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)  # Use pywhatkit's search function to perform a Google search.
    return True  # Indicate success.

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'  # Default text editor.
        subprocess.Popen([default_text_editor, File])  # Open the file in Notepad.

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Specify the AI model.
            messages=SystemChatBot + messages,  # Include system instructions and chat history.
            max_tokens=2048,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness.
            top_p=1,  # Use nucleus sampling for response diversity.
            stream=True,  # Enable streaming response.
            stop=None  # Allow the model to determine stopping conditions.
        )

        Answer = ""  # Initialize an empty string for the response.

        # Process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Add the content to the answer.

        Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages.
        return Answer  # Return the generated content.
    Topic: str = Topic.replace("content" , "")
    ContentByAI = ContentWriterAI(Topic)

    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w" , encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYouTube(query):
    playonyt(query)
    return True

def OpenApp(app):
    try:
        # Try to open the app using AppOpener
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Opened {app} successfully.")
    except AppNotFound:
        # Remove spaces from the app name
        app_name = app.replace(" ", "")
        website_url = f"https://www.{app_name.lower()}.com"
        print(f"App '{app}' not found. Redirecting to {website_url}")
        webbrowser.open(website_url)  
def closeApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
        

def System(command):
    def press_key(key, times=1):
        for _ in range(times):
            keyboard.press_and_release(key)

    # Normalize command to lower case
    command = command.lower()

    if "mute" in command:
        press_key("volume mute")
    
    elif "unmute" in command:
        press_key("volume mute")  # Unmute is usually toggled with the same key
    
    elif "volume up" in command or "increase volume" in command:
        # Extracting number from command
        words = command.split()
        for word in words:
            if word.isdigit():
                times = max(1, int(word) // 2)  # Divide by 2 as per requirement
                break
        else:
            times = 1  # Default to 1 if no number found
        press_key("volume up", times)

    elif "volume down" in command or "decrease volume" in command:
        words = command.split()
        for word in words:
            if word.isdigit():
                times = max(1, int(word) // 2)
                break
        else:
            times = 1
        press_key("volume down", times)

    return True


async def TranslateAndExecute(commands: list[str]):

    funcs = []
    
    for command in commands:

        if command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)

        elif command.startswith("close"):
            fun = asyncio.to_thread(closeApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play"):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content"):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
       
        elif command.startswith("youtube search"):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif "mute" in command or "volume" in command or "increase" in command or "decrease" in command:
            fun = asyncio.to_thread(System, command)  # Pass full command to System()
            funcs.append(fun)

        else:
            print(f"No Function Found for {command}")
    
    results = await asyncio.gather(*funcs)

    for result in results:
        yield result
    

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


if __name__ == "__main__":
    asyncio.run(Automation([
        "increas volume by 10"
    ]))
