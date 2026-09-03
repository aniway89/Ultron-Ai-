# ============================================================
# WHISPER FIRST TEST
# ============================================================

print("==========================================")
print("TESTING WHISPER BEFORE OTHER MODULES")
print("==========================================")

from faster_whisper import WhisperModel

print("faster-whisper imported.")
print("Creating WhisperModel...")

try:

    whisper_model = WhisperModel(
        "tiny.en",
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        num_workers=1
    )

    print()
    print("==========================================")
    print("WHISPER WORKS INSIDE MAIN.PY")
    print("==========================================")
    print()

except Exception as e:

    print()
    print("==========================================")
    print("WHISPER ERROR")
    print("==========================================")
    print(type(e).__name__)
    print(str(e))
    print("==========================================")

    input("Press ENTER to close...")
    raise


# ============================================================
# NOW IMPORT THE REST OF YOUR PROGRAM
# ============================================================

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation

from Backend.SpeechToText import SpeechRecognition

from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageGeneration import GenerateImages

from dotenv import dotenv_values

from asyncio import run
from time import sleep

import subprocess
import threading
import json
import os
import sys

# ============================================================
# ENVIRONMENT
# ============================================================

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")


# ============================================================
# DEFAULT MESSAGE
# ============================================================

DefaultMessage = f"""
{Username} : Hello {AssistantName}, How are you?

{AssistantName} : Welcome {Username}. I am doing well. How may I help you?
"""


# ============================================================
# PROCESSES
# ============================================================

# IMPORTANT:
# Do NOT write:
#
# subprocess = []
#
# because subprocess is also the Python module.

processes = []


# ============================================================
# FUNCTIONS
# ============================================================

Functions = [
    "open",
    "close",
    "play",
    "system",
    "content",
    "google search",
    "youtube search"
]


# ============================================================
# SHOW DEFAULT CHAT
# ============================================================

def ShowDefaultChatIfNoChats():

    file_path = r"Data\ChatLog.json"

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as File:

            data = File.read()

        if len(data) < 5:

            with open(
                TempDirectoryPath("Database.data"),
                "w",
                encoding="utf-8"
            ) as file:

                file.write("")

            with open(
                TempDirectoryPath("Responses.data"),
                "w",
                encoding="utf-8"
            ) as file:

                file.write(DefaultMessage)

    except Exception as e:

        print("Chat log error:", e)


# ============================================================
# READ CHAT LOG
# ============================================================

def ReadChatLogJson():

    with open(
        r"Data\ChatLog.json",
        "r",
        encoding="utf-8"
    ) as file:

        chatlog_data = json.load(file)

    return chatlog_data


# ============================================================
# CHAT LOG INTEGRATION
# ============================================================

def ChatLogIntegration():

    try:

        json_data = ReadChatLogJson()

        formatted_chatlog = ""

        for entry in json_data:

            if entry["role"] == "user":

                formatted_chatlog += (
                    f"User: {entry['content']}\n"
                )

            elif entry["role"] == "assistant":

                formatted_chatlog += (
                    f"Assistant: {entry['content']}\n"
                )

        formatted_chatlog = formatted_chatlog.replace(
            "User",
            Username + " "
        )

        formatted_chatlog = formatted_chatlog.replace(
            "Assistant",
            AssistantName + " "
        )

        with open(
            TempDirectoryPath("Database.data"),
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                AnswerModifier(formatted_chatlog)
            )

    except Exception as e:

        print("Chat integration error:", e)


# ============================================================
# SHOW CHATS ON GUI
# ============================================================

def ShowChatsOnGUI():

    try:

        with open(
            TempDirectoryPath("Database.data"),
            "r",
            encoding="utf-8"
        ) as File:

            Data = File.read()

        if len(str(Data)) > 0:

            lines = Data.split("\n")

            result = "\n".join(lines)

            with open(
                TempDirectoryPath("Responses.data"),
                "w",
                encoding="utf-8"
            ) as File:

                File.write(result)

    except Exception as e:

        print("GUI chat error:", e)


# ============================================================
# INITIAL EXECUTION
# ============================================================

def InitialExecution():

    print("Running initial execution...")

    SetMicrophoneStatus("False")

    ShowTextToScreen("")

    ShowDefaultChatIfNoChats()

    ChatLogIntegration()

    ShowChatsOnGUI()

    print("Initial execution complete.")


# ============================================================
# MAIN EXECUTION
# ============================================================

def MainExecution():

    TaskExecution = False

    ImageExecution = False

    ImageGenerationQuery = ""

    print("\n==========================================")
    print("Starting MainExecution")
    print("==========================================")

    SetAssistantStatus("Listening ...")

    # --------------------------------------------------------
    # SPEECH TO TEXT
    # --------------------------------------------------------

    print("Calling SpeechRecognition...")

    Query = SpeechRecognition()

    print("SpeechRecognition returned:")
    print(Query)

    # --------------------------------------------------------
    # If nothing was recognized
    # --------------------------------------------------------

    if not Query:

        print("No query detected.")

        SetAssistantStatus("Available ...")

        return False

    ShowTextToScreen(
        f"{Username} : {Query}"
    )

    # --------------------------------------------------------
    # THINKING
    # --------------------------------------------------------

    SetAssistantStatus("Thinking ...")

    print("Running decision model...")

    Decision = FirstLayerDMM(Query)

    print()
    print("Decision :", Decision)
    print()

    # --------------------------------------------------------
    # GENERAL / REALTIME
    # --------------------------------------------------------

    G = any(
        i.startswith("general")
        for i in Decision
    )

    R = any(
        i.startswith("realtime")
        for i in Decision
    )

    # --------------------------------------------------------
    # MERGED QUERY
    # --------------------------------------------------------

    Mearged_query = " and ".join(

        [
            " ".join(i.split()[1:])
            for i in Decision
            if (
                i.startswith("general")
                or
                i.startswith("realtime")
            )
        ]

    )

    # --------------------------------------------------------
    # IMAGE GENERATION
    # --------------------------------------------------------

    for queries in Decision:

        if "generate " in queries:

            ImageGenerationQuery = str(
                queries
            )

            ImageExecution = True

    # --------------------------------------------------------
    # AUTOMATION
    # --------------------------------------------------------

    for queries in Decision:

        if TaskExecution is False:

            if any(
                queries.startswith(func)
                for func in Functions
            ):

                print(
                    "Running Automation..."
                )

                run(
                    Automation(
                        list(Decision)
                    )
                )

                TaskExecution = True

    # --------------------------------------------------------
    # IMAGE GENERATION
    # --------------------------------------------------------

    if ImageExecution is True:

        try:

            with open(
                r"Frontend\Files\ImageGeneratioin.data",
                "w"
            ) as file:

                file.write(
                    f"{ImageGenerationQuery},True"
                )

            print(
                "Starting ImageGeneration.py..."
            )

            p1 = subprocess.Popen(

                [
                    "python",
                    r"Backend\ImageGeneration.py"
                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                stdin=subprocess.PIPE,

                shell=False
            )

            processes.append(p1)

        except Exception as e:

            print(
                f"Error starting ImageGeneration.py: {e}"
            )

    # --------------------------------------------------------
    # REALTIME SEARCH
    # --------------------------------------------------------

    if G and R or R:

        SetAssistantStatus(
            "Searching ..."
        )

        Answer = RealtimeSearchEngine(
            QueryModifier(
                Mearged_query
            )
        )

        ShowTextToScreen(
            f"{AssistantName} : {Answer}"
        )

        SetAssistantStatus(
            "Answering ..."
        )

        TextToSpeech(Answer)

        return True

    # --------------------------------------------------------
    # GENERAL / OTHER
    # --------------------------------------------------------

    else:

        for Queries in Decision:

            # ------------------------------------------------
            # GENERAL
            # ------------------------------------------------

            if "general" in Queries:

                SetAssistantStatus(
                    "Thinking..."
                )

                QueryFinal = Queries.replace(
                    "general ",
                    ""
                )

                Answer = ChatBot(
                    QueryModifier(
                        QueryFinal
                    )
                )

                ShowTextToScreen(
                    f"{AssistantName} : {Answer}"
                )

                SetAssistantStatus(
                    "Answering...."
                )

                TextToSpeech(Answer)

                return True

            # ------------------------------------------------
            # REALTIME
            # ------------------------------------------------

            elif "realtime" in Queries:

                SetAssistantStatus(
                    "Searching..."
                )

                QueryFinal = Queries.replace(
                    "realtime ",
                    ""
                )

                Answer = RealtimeSearchEngine(
                    QueryModifier(
                        QueryFinal
                    )
                )

                ShowTextToScreen(
                    f"{AssistantName} : {Answer}"
                )

                SetAssistantStatus(
                    "Answering.."
                )

                TextToSpeech(Answer)

                return True

            # ------------------------------------------------
            # EXIT
            # ------------------------------------------------

            elif "exit" in Queries:

                QueryFinal = "Okay, Bye!"

                Answer = ChatBot(
                    QueryModifier(
                        QueryFinal
                    )
                )

                ShowTextToScreen(
                    f"{AssistantName} : {Answer}"
                )

                SetAssistantStatus(
                    "Answering..."
                )

                TextToSpeech(Answer)

                os._exit(1)

    return False


# ============================================================
# FIRST THREAD
# ============================================================

def FirstThread():

    print("FirstThread started.")

    while True:

        try:

            CurrentStatus = GetMicrophoneStatus()

            # DEBUG
            # This tells us whether GUI is enabling microphone.

            if CurrentStatus == "True":

                print(
                    "\nMicrophone activated."
                )

                MainExecution()

            else:

                AIStatus = GetAssistantStatus()

                if "Available ..." in AIStatus:

                    sleep(0.1)

                else:

                    SetAssistantStatus(
                        "Available ..."
                    )

                    sleep(0.1)

        except Exception as e:

            print(
                "\n=========================================="
            )

            print(
                "FIRST THREAD ERROR"
            )

            print(
                "=========================================="
            )

            print(
                type(e).__name__,
                e
            )

            print(
                "==========================================\n"
            )

            sleep(1)


# ============================================================
# SECOND THREAD / GUI
# ============================================================

def SecondThread():

    print("Starting GUI...")

    GraphicalUserInterface()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("          AI ASSISTANT STARTING")
    print("==========================================")


    # ========================================================
    # INITIAL SETUP
    # ========================================================

    InitialExecution()


    # ========================================================
    # LOAD WHISPER ON MAIN THREAD
    # ========================================================

    print()
    print("Preparing Speech Recognition...")

    whisper_ready = LoadWhisperModel()


    if not whisper_ready:

        print()
        print("==========================================")
        print("ERROR: WHISPER COULD NOT LOAD")
        print("==========================================")
        print()
        print(
            "The assistant cannot continue."
        )

        input(
            "Press ENTER to close..."
        )

        sys.exit(1)


    print()
    print(
        "Speech Recognition ready."
    )


    # ========================================================
    # START BACKGROUND THREAD
    # ========================================================

    thread2 = threading.Thread(
        target=FirstThread,
        daemon=True
    )

    thread2.start()


    print(
        "Background thread started."
    )


    # ========================================================
    # START GUI
    # ========================================================

    SecondThread()
