from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

print("Loading Chatbot model...")

env_vers = dotenv_values(".env")

Username = env_vers.get("Username")
AssistantName = env_vers.get("AssistantName")
GroqAPIKey = env_vers.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** You are a Ai made by Erito Ayan ***
*** Do not give any information about yourself, just answer the question. ***
"""


SystemChatBot =[
    {"role": "system", "content": System}
]

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    # Initialize `messages` as an empty list if the file doesn't exist or is empty.
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")   # Day of the week
    date = current_date_time.strftime("%d")  # Day of the month
    month = current_date_time.strftime("%B") # Full month name
    year = current_date_time.strftime("%Y")  # Year
    hour = current_date_time.strftime("%H")  # Hour in 24-hour format
    minute = current_date_time.strftime("%M") # Minute
    second = current_date_time.strftime("%S") # Second        

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return  data




def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines)  # Join the cleaned lines back together.
    return modified_answer




def ChatBot(Query):
    """
    This function sends the user's query to the chatbot and returns the AI's response.
    """
    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        
        # Append the user's query to the messages list.
        messages.append({'role': 'user', 'content': f"{Query}"})
        
        # Make a request to the Grog API for a response.
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Specify the AI model to use.
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,  # Include system instructions.
            max_tokens=1024,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness (higher means more random).
            top_p=1,  # Use nucleus sampling to control diversity.
            stream=True,  # Enable streaming response.
            stop=None  # Allow the model to determine when to stop.
        )
        
        Answer = ""  # Initialize an empty string to store the AI's response.
        # Process the response...
          




        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check if there's content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})

            # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json", "w") as f:
                dump(messages, f, indent=4)

            # Return the formatted response.
        return AnswerModifier(Answer=Answer)

    except Exception as e:
                # Handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
             dump([], f, indent=4)
        return ChatBot(Query)  # Retry the query after resetting the log.

    # Main program entry point.
if __name__ == "__main__":
    while True:
       user_input = input("Enter your Question:")
       print(ChatBot(user_input))
