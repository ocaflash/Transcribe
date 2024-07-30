import speech_recognition as sr
import os
from googletrans import Translator
import logging
from pydub import AudioSegment
import magic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_audio_format(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    if file_type.startswith('audio/'):
        return file_type.split('/')[-1]
    return None

def convert_to_wav(file_path):
    audio_format = get_audio_format(file_path)
    if audio_format == 'wav':
        return file_path

    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
    if audio_format == 'mp3':
        audio = AudioSegment.from_mp3(file_path)
    elif audio_format == 'ogg':
        audio = AudioSegment.from_ogg(file_path)
    elif audio_format == 'flac':
        audio = AudioSegment.from_file(file_path, format="flac")
    else:
        audio = AudioSegment.from_file(file_path)

    audio.export(wav_path, format="wav")
    return wav_path

def split_audio(audio_path, segment_length_ms=30000):
    audio = AudioSegment.from_wav(audio_path)
    segments = [audio[i:i + segment_length_ms] for i in range(0, len(audio), segment_length_ms)]
    return segments

def recognize_speech_from_segment(segment_path, recognizer, language="en-US"):
    with sr.AudioFile(segment_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition API request error: {e}")
        return None
    except sr.UnknownValueError:
        logger.warning("Google Speech Recognition could not understand audio.")
        return "[recognition failed]"

def transcribe_audio(file_path: str, target_language="en") -> dict:
    recognizer = sr.Recognizer()

    # Convert the file to WAV if necessary
    wav_file_path = convert_to_wav(file_path)

    segments = split_audio(wav_file_path)

    transcribed_texts = []

    total_segments = len(segments)
    for i, segment in enumerate(segments):
        segment_path = f"/tmp/segment_{i}.wav"
        segment.export(segment_path, format="wav")

        logger.info(f"Processing segment {i + 1}/{total_segments}")

        text = recognize_speech_from_segment(segment_path, recognizer)
        transcribed_texts.append(text)

        os.remove(segment_path)  # Remove temporary segment

    final_transcription = " ".join(transcribed_texts)

    logger.info("Transcription completed")
    logger.debug(f"Final transcription: {final_transcription}")

    # Initialize the translator
    translator = Translator()

    # Prepare the result dictionary
    result = {
        "original_text": final_transcription,
        "translation": {}
    }

    # Translate if the target language is not English
    if target_language.lower() != "en":
        try:
            translation = translator.translate(final_transcription, src='en', dest=target_language)
            result["translation"][target_language] = translation.text
            logger.info(f"Translated to {target_language}")
            logger.debug(f"Translated transcription: {translation.text}")
        except Exception as e:
            logger.error(f"Translation to {target_language} failed: {str(e)}")
            result["translation"][target_language] = "[translation failed]"

    # Additionally translate to Russian
    if target_language.lower() != "ru":
        try:
            translation_ru = translator.translate(final_transcription, src='en', dest='ru')
            result["translation"]["ru"] = translation_ru.text
            logger.info("Translated to Russian (ru)")
            logger.debug(f"Translated transcription (ru): {translation_ru.text}")
        except Exception as e:
            logger.error(f"Translation to Russian failed: {str(e)}")
            result["translation"]["ru"] = "[translation failed]"

    # Remove temporary WAV file if it was created
    if wav_file_path != file_path:
        os.remove(wav_file_path)

    return result

