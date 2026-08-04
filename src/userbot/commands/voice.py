import os
import asyncio
import speech_recognition as sr
from pydub import AudioSegment
from telethon import events, TelegramClient

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.voice$'))
    async def voice_handler(event):
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        ogg_path = os.path.join(temp_dir, "voice.ogg")
        wav_path = os.path.join(temp_dir, "voice.wav")
        
        try:
            if not event.is_reply:
                await event.edit("Please reply to a voice message with `.voice`!")
                return
                
            reply_msg = await event.get_reply_message()
            if not reply_msg.voice:
                await event.edit("The replied message is not a voice note!")
                return
                
            await event.edit("Downloading voice note...")
            await event.client.download_media(reply_msg, file=ogg_path)
            
            await event.edit("Transcribing audio...")
            
            # Run audio conversion in a separate thread to avoid blocking
            def convert_audio():
                audio = AudioSegment.from_ogg(ogg_path)
                audio.export(wav_path, format="wav")
            
            await asyncio.to_thread(convert_audio)
            
            # Run speech recognition
            def recognize_speech():
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                    return recognizer.recognize_google(audio_data)
            
            transcript = await asyncio.to_thread(recognize_speech)
            
            await event.edit(f"**Transcript:**\n\n{transcript}")
            
        except sr.UnknownValueError:
            await event.edit("Could not understand the audio. It might be silent or unclear.")
        except sr.RequestError as e:
            await event.edit(f"Speech recognition service error: {e}")
        except Exception as e:
            await event.edit(f"Voice transcription error: {e}")
            print(f"Voice error: {e}")
        finally:
            # Clean up temp files
            if os.path.exists(ogg_path):
                os.remove(ogg_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
