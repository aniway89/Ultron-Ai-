import os
import sys
import time
import wave
import tempfile
import traceback

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1

SILENCE_THRESHOLD = 0.012
SILENCE_DURATION = 0.75
MAX_RECORDING_TIME = 12
MIN_SPEECH_TIME = 0.25


# ============================================================
# WHISPER SETTINGS
# ============================================================

WHISPER_MODEL_NAME = "tiny.en"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"


# ============================================================
# GLOBAL MODEL
# ============================================================

model = None


# ============================================================
# LOAD WHISPER MODEL
# ============================================================

def LoadWhisperModel():

    global model

    # Already loaded
    if model is not None:

        print("Whisper already loaded.")

        return True

    print()
    print("==========================================")
    print("LOADING WHISPER MODEL")
    print("==========================================")
    print("Model :", WHISPER_MODEL_NAME)
    print("Device:", WHISPER_DEVICE)
    print("Type  :", WHISPER_COMPUTE_TYPE)
    print("Python:", sys.version)
    print("------------------------------------------")

    try:

        print("Creating WhisperModel...")

        model = WhisperModel(
            WHISPER_MODEL_NAME,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            cpu_threads=4,
            num_workers=1
        )

        print("------------------------------------------")
        print("Whisper ready.")
        print("==========================================")
        print()

        return True

    except Exception as e:

        print()
        print("==========================================")
        print("WHISPER ERROR")
        print("==========================================")
        print(
            type(e).__name__,
            str(e)
        )

        traceback.print_exc()

        print("==========================================")

        model = None

        return False


# ============================================================
# AUDIO LEVEL
# ============================================================

def get_audio_level(audio):

    if len(audio) == 0:

        return 0.0

    return float(
        np.sqrt(
            np.mean(audio ** 2)
        )
    )


# ============================================================
# RECORD AUDIO
# ============================================================

def record_audio():

    print()
    print("Listening...")

    audio_chunks = []

    speech_started = False

    silence_start = None

    start_time = time.time()


    def callback(
        indata,
        frames,
        time_info,
        status
    ):

        nonlocal speech_started
        nonlocal silence_start

        if status:

            print(
                "Audio:",
                status
            )

        audio = indata[:, 0].copy()

        audio_chunks.append(audio)

        level = get_audio_level(audio)

        # ----------------------------------------------------
        # SPEECH
        # ----------------------------------------------------

        if level > SILENCE_THRESHOLD:

            if not speech_started:

                speech_started = True

                print(
                    "🎤 Speaking..."
                )

            silence_start = None

        # ----------------------------------------------------
        # SILENCE
        # ----------------------------------------------------

        elif speech_started:

            if silence_start is None:

                silence_start = time.time()


    # ========================================================
    # MICROPHONE
    # ========================================================

    try:

        print(
            "Opening microphone..."
        )

        with sd.InputStream(

            samplerate=SAMPLE_RATE,

            channels=CHANNELS,

            dtype="float32",

            blocksize=1024,

            callback=callback

        ):

            print(
                "Microphone opened."
            )

            while True:

                time.sleep(0.05)

                current_time = time.time()

                # ------------------------------------------------
                # MAXIMUM TIME
                # ------------------------------------------------

                if (
                    current_time - start_time
                    >= MAX_RECORDING_TIME
                ):

                    print(
                        "Maximum recording time reached."
                    )

                    break

                # ------------------------------------------------
                # SILENCE
                # ------------------------------------------------

                if (
                    speech_started
                    and
                    silence_start is not None
                ):

                    silence_time = (
                        current_time
                        -
                        silence_start
                    )

                    if silence_time >= SILENCE_DURATION:

                        print(
                            "Speech ended."
                        )

                        break

    except Exception as e:

        print()
        print("==========================================")
        print("MICROPHONE ERROR")
        print("==========================================")

        print(
            type(e).__name__,
            str(e)
        )

        traceback.print_exc()

        return None


    # ========================================================
    # CHECK AUDIO
    # ========================================================

    if not audio_chunks:

        print(
            "No audio captured."
        )

        return None


    audio = np.concatenate(
        audio_chunks
    )


    duration = (
        len(audio)
        /
        SAMPLE_RATE
    )


    print(
        f"Recorded {duration:.2f} seconds."
    )


    if duration < MIN_SPEECH_TIME:

        print(
            "Recording too short."
        )

        return None


    return audio


# ============================================================
# SAVE WAV
# ============================================================

def save_wav(audio):

    temp = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    filename = temp.name

    temp.close()


    # --------------------------------------------------------
    # FLOAT32 -> INT16
    # --------------------------------------------------------

    audio_int16 = np.clip(
        audio * 32767,
        -32768,
        32767
    ).astype(
        np.int16
    )


    # --------------------------------------------------------
    # WRITE WAV
    # --------------------------------------------------------

    with wave.open(
        filename,
        "wb"
    ) as wav:

        wav.setnchannels(1)

        wav.setsampwidth(2)

        wav.setframerate(
            SAMPLE_RATE
        )

        wav.writeframes(
            audio_int16.tobytes()
        )


    return filename


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def SpeechRecognition():

    print()
    print("==========================================")
    print("SPEECH RECOGNITION")
    print("==========================================")


    # --------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------

    if model is None:

        print(
            "Whisper model is not loaded."
        )

        print(
            "Please call LoadWhisperModel() first."
        )

        return ""


    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    audio = record_audio()


    if audio is None:

        return ""


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    filename = save_wav(audio)


    try:

        print()
        print(
            "Transcribing..."
        )


        # ----------------------------------------------------
        # TRANSCRIBE
        # ----------------------------------------------------

        segments, info = model.transcribe(

            filename,

            language="en",

            beam_size=1,

            condition_on_previous_text=False,

            vad_filter=True,

            temperature=0.0,

            task="transcribe"
        )


        # ----------------------------------------------------
        # GET TEXT
        # ----------------------------------------------------

        text_parts = []


        for segment in segments:

            text_parts.append(
                segment.text
            )


        text = " ".join(
            text_parts
        ).strip()


        # ----------------------------------------------------
        # CLEAN
        # ----------------------------------------------------

        text = " ".join(
            text.split()
        )


        print()
        print(
            "Recognized:",
            text
        )


        return text


    except Exception as e:

        print()
        print("==========================================")
        print("TRANSCRIPTION ERROR")
        print("==========================================")

        print(
            type(e).__name__,
            str(e)
        )

        traceback.print_exc()

        print("==========================================")


        return ""


    finally:

        # ----------------------------------------------------
        # DELETE TEMP FILE
        # ----------------------------------------------------

        if os.path.exists(filename):

            try:

                os.remove(filename)

            except Exception:

                pass


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("LIGHTWEIGHT ENGLISH STT")
    print("==========================================")

    # Load on MAIN thread
    if not LoadWhisperModel():

        print(
            "Could not load Whisper."
        )

        sys.exit(1)


    try:

        while True:

            text = SpeechRecognition()

            if text:

                print()
                print(
                    "You:",
                    text
                )


    except KeyboardInterrupt:

        print()
        print(
            "Speech recognition stopped."
        )
