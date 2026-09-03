from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os


print("Loading")


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

env_vars = dotenv_values(".env")

InputLanguage = env_vars.get("InputLanguage", "en")


# ============================================================
# HTML SPEECH RECOGNITION
# ============================================================

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>

<body>

    <button id="start" onclick="startRecognition()">
        Start Recognition
    </button>

    <button id="end" onclick="stopRecognition()">
        Stop Recognition
    </button>

    <p id="output"></p>

    <script>

        const output = document.getElementById('output');

        let recognition;


        function startRecognition() {

            recognition =
                new webkitSpeechRecognition() ||
                new SpeechRecognition();

            recognition.lang = 'en';

            recognition.continuous = true;


            recognition.onresult = function(event) {

                const transcript =
                    event.results[
                        event.results.length - 1
                    ][0].transcript;

                output.textContent += transcript;
            };


            recognition.onend = function() {

                recognition.start();

            };


            recognition.start();
        }


        function stopRecognition() {

            if (recognition) {

                recognition.stop();

            }

            output.innerHTML = "";

        }

    </script>

</body>
</html>'''


print("Loading checkpoint 1")


# ============================================================
# SET LANGUAGE
# ============================================================

HtmlCode = str(HtmlCode).replace(
    "recognition.lang = 'en';",
    f"recognition.lang = '{InputLanguage}';"
)


# ============================================================
# WRITE HTML FILE
# ============================================================

with open(
    "Data/Voice.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(HtmlCode)


# ============================================================
# CURRENT DIRECTORY
# ============================================================

current_dir = os.getcwd()

Link = f"{current_dir}/Data/Voice.html"


print("Loading checkpoint 2")


# ============================================================
# CHROME OPTIONS
# ============================================================

chrome_options = Options()

user_agent = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/151.0.0.0 "
    "Safari/537.36"
)

chrome_options.add_argument(
    f"user-agent={user_agent}"
)

# Allow microphone access
chrome_options.add_argument(
    "--use-fake-ui-for-media-stream"
)

# Keep browser visible
chrome_options.add_argument("--headless=new")


print("Loading checkpoint 3")


# ============================================================
# START CHROME
# ============================================================

service = Service(
    ChromeDriverManager().install()
)

driver = webdriver.Chrome(
    service=service,
    options=chrome_options
)


print("Chrome ready.")


# ============================================================
# TEMP DIRECTORY
# ============================================================

TempDirPath = (
    f"{current_dir}/Frontend/Files"
)


# ============================================================
# ASSISTANT STATUS
# ============================================================

def SetAssistantStatus(Status):

    with open(
        f"{TempDirPath}/Status.data",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Status)


# ============================================================
# QUERY MODIFIER
# ============================================================

def QueryModifier(query):

    new_query = query.lower().strip()

    if not new_query:

        return ""


    query_words = new_query.split()


    question_words = [
        "how",
        "what",
        "who",
        "where",
        "when",
        "why",
        "which",
        "whose",
        "whom",
        "can you",
        "what's",
        "where's",
        "how's"
    ]


    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    if any(
        word + " " in new_query
        for word in question_words
    ):

        if query_words[-1][-1] in [
            ".",
            "?",
            "!"
        ]:

            new_query = (
                new_query[:-1]
                +
                "?"
            )

        else:

            new_query += "?"


    # --------------------------------------------------------
    # NORMAL STATEMENT
    # --------------------------------------------------------

    else:

        if query_words[-1][-1] in [
            ".",
            "?",
            "!"
        ]:

            new_query = (
                new_query[:-1]
                +
                "."
            )

        else:

            new_query += "."


    return new_query.capitalize()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def SpeechRecognition():

    # --------------------------------------------------------
    # OPEN SPEECH RECOGNITION PAGE
    # --------------------------------------------------------

    driver.get(
        "file:///" + Link
    )


    # --------------------------------------------------------
    # START RECOGNITION
    # --------------------------------------------------------

    driver.find_element(
        by=By.ID,
        value="start"
    ).click()


    # --------------------------------------------------------
    # WAIT FOR SPEECH
    # --------------------------------------------------------

    while True:

        try:

            Text = driver.find_element(
                by=By.ID,
                value="output"
            ).text


            if Text:

                # ------------------------------------------------
                # STOP RECOGNITION
                # ------------------------------------------------

                driver.find_element(
                    by=By.ID,
                    value="end"
                ).click()


                # ------------------------------------------------
                # RETURN RECOGNIZED TEXT
                # NO TRANSLATION
                # ------------------------------------------------

                return QueryModifier(Text)


        except Exception:

            pass


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    while True:

        Text = SpeechRecognition()

        print(
            "Recognized:",
            Text
        )
