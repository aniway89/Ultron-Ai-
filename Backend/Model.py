import cohere
from rich import print
from dotenv import dotenv_values


# ============================================================
# SETUP
# ============================================================

print("Loading Thinking model...")

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("COHERE_API_KEY")

if not CohereAPIKey:
    raise ValueError("COHERE_API_KEY not found in .env")

co = cohere.ClientV2(api_key=CohereAPIKey)


# ============================================================
# VALID FUNCTIONS
# ============================================================

funcs = [
    "exit",
    "general",
    "realtime",
    "open",
    "close",
    "play",
    "generate image",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder"
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

preamble = """
You are a very accurate Decision-Making Model.

Your ONLY job is to classify the user's query into one or more
commands.

DO NOT answer the user's question.
DO NOT explain anything.
ONLY return the required command(s).

Available commands:

general
realtime
open
close
play
generate image
system
content
google search
youtube search
reminder
exit


RULES
-----

1. GENERAL

Use:

general <query>

when the query can normally be answered by an LLM and does not
require current information.

Examples:

"how are you?"
-> general how are you?

"do you like pizza?"
-> general do you like pizza?

"what is python?"
-> general what is python?

"help me solve this math problem"
-> general help me solve this math problem

"who is he?"
-> general who is he?

"tell me more about him"
-> general tell me more about him

Also use general for questions about the current time, date,
day, month or year.

Example:

"what is today's date?"
-> general what is today's date?


2. REALTIME

Use:

realtime <query>

when the query requires current or up-to-date information.

Examples:

"who is the Indian prime minister?"
-> realtime who is the Indian prime minister?

"what is today's news?"
-> realtime what is today's news?

"what is the latest update from Facebook?"
-> realtime what is the latest update from Facebook?

"who is Akshay Kumar?"
-> realtime who is Akshay Kumar?


3. OPEN

Use:

open <application or website>

when the user wants to open an application or website.

Example:

"open chrome"
-> open chrome

"open facebook and telegram"
-> open facebook, open telegram


4. CLOSE

Use:

close <application or website>

when the user wants to close an application or website.

Example:

"close chrome"
-> close chrome

"close chrome and notepad"
-> close chrome, close notepad


5. PLAY

Use:

play <song name>

when the user wants to play a song.

Example:

"play let her go"
-> play let her go

"play afsanay and let her go"
-> play afsanay, play let her go


6. GENERATE IMAGE

Use:

generate image <image prompt>

when the user wants an image generated.

Example:

"generate an image of a lion"
-> generate image a lion

"generate an image of a futuristic city"
-> generate image a futuristic city


7. REMINDER

Use:

reminder <datetime and message>

when the user wants to set a reminder.

Example:

"remind me at 9 PM tomorrow about my meeting"
-> reminder 9 PM tomorrow my meeting

If the user asks for multiple reminders, return multiple
reminder commands.


8. SYSTEM

Use:

system <task>

for system-level tasks such as:

mute
unmute
volume up
volume down
increase volume
decrease volume
shutdown
restart
etc.

Example:

"mute the computer"
-> system mute

"volume up and then mute"
-> system volume up, system mute


9. CONTENT

Use:

content <topic>

when the user wants content created.

This includes:

applications
emails
letters
messages
essays
code
scripts
documents
etc.

Example:

"write an email to my teacher"
-> content email to my teacher

"write python code for a calculator"
-> content python code for a calculator


10. GOOGLE SEARCH

Use:

google search <topic>

when the user specifically asks to search something on Google.

Example:

"search Google for Python tutorials"
-> google search Python tutorials


11. YOUTUBE SEARCH

Use:

youtube search <topic>

when the user specifically asks to search something on YouTube.

Example:

"search YouTube for Python tutorials"
-> youtube search Python tutorials


12. EXIT

If the user wants to end the conversation, return:

exit

Example:

"bye"
-> exit

"goodbye jarvis"
-> exit


MULTIPLE COMMANDS
-----------------

If the user asks for multiple tasks, return each command
separated by a comma.

Example:

"open chrome and search Google for Python"

-> open chrome, google search Python

Example:

"open chrome, open telegram and close notepad"

-> open chrome, open telegram, close notepad


IMPORTANT
---------

Return ONLY commands.

Never provide explanations.

Never answer the actual question.

Never write "(query)" literally.

If you cannot determine the correct command, use:

general <query>
"""


# ============================================================
# CHAT HISTORY
# ============================================================

ChatHistory = [
    {"role": "user", "message": "how are you?"},
    {"role": "assistant", "message": "general how are you?"},

    {"role": "user", "message": "do you like pizza?"},
    {"role": "assistant", "message": "general do you like pizza?"},

    {"role": "user", "message": "open chrome"},
    {"role": "assistant", "message": "open chrome"},

    {"role": "user", "message": "open chrome and"},
    {"role": "assistant", "message": "open chrome"},

    {"role": "user", "message": "what is today's date?"},
    {"role": "assistant", "message": "general what is today's date"},

    {"role": "user", "message": "chat with me."},
    {"role": "assistant", "message": "general chat with me."},

    {"role": "user", "message": "tell me about mahatma gandhi."},
    {"role": "assistant", "message": "general tell me about mahatma gandhi."},

    {"role": "user", "message": "open firefox"},
    {"role": "assistant", "message": "open firefox"},

    {
        "role": "user",
        "message": "date and by the way remind me that I have a dancing performance on 5th Aug at 11 PM"
    },
    {
        "role": "assistant",
        "message": "general date, reminder 11 PM 5th Aug dancing performance"
    }
]


# ============================================================
# DECISION MAKING MODEL
# ============================================================

def FirstLayerDMM(prompt: str = "test"):

    print(f"\nSending: {prompt}")

    response = co.chat(
        model="command-a-plus-05-2026",

        messages=[
            {
                "role": "system",
                "content": preamble
            },

            *[
                {
                    "role": item["role"],
                    "content": item["message"]
                }
                for item in ChatHistory
            ],

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.0
    )


    # ========================================================
    # GET MODEL TEXT
    # ========================================================

    answer = ""

    for item in response.message.content:

        if hasattr(item, "text"):
            answer += item.text

        elif isinstance(item, dict) and "text" in item:
            answer += item["text"]


    # Remove unnecessary whitespace/newlines
    answer = answer.replace("\n", " ").strip()

    print("\nRAW RESPONSE:")
    print(repr(answer))


    # ========================================================
    # SPLIT MULTIPLE COMMANDS
    # ========================================================

    tasks = answer.split(",")

    tasks = [
        task.strip()
        for task in tasks
        if task.strip()
    ]


    # ========================================================
    # FILTER VALID COMMANDS
    # ========================================================

    valid_tasks = []

    for task in tasks:

        for func in funcs:

            if task.startswith(func):

                valid_tasks.append(task)
                break


    # ========================================================
    # FALLBACK
    # ========================================================

    if not valid_tasks:

        return [f"general {prompt}"]


    # ========================================================
    # RETRY IF MODEL RETURNS "(query)"
    # ========================================================

    for task in valid_tasks:

        if "(query)" in task:

            print("Model returned invalid query placeholder. Retrying...")

            return FirstLayerDMM(prompt)


    return valid_tasks


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    while True:

        user_input = input(">>> ")

        if not user_input.strip():
            continue

        result = FirstLayerDMM(user_input)

        print("\nRESULT:")
        print(result)