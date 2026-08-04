import os
import asyncio
from pydub import AudioSegment
from telethon import events, TelegramClient

# Add Homebrew to PATH so pydub can find ffmpeg and ffprobe when running in background via launchd
if "/opt/homebrew/bin" not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"
if "/usr/local/bin" not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"/usr/local/bin:{os.environ.get('PATH', '')}"

whisper_model = None

def setup(client: TelegramClient):
    @client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.voice(?:\s+([a-zA-Z\-]+))?$'))
    async def voice_handler(event):
        lang_code = event.pattern_match.group(1)
        whisper_lang = lang_code.split('-')[0].lower() if lang_code else None
        
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        # Use event.id to ensure unique filenames if multiple voices are running at once
        ogg_path = os.path.join(temp_dir, f"voice_{event.id}.ogg")
        wav_path = os.path.join(temp_dir, f"voice_{event.id}.wav")
        
        try:
            if not event.is_reply:
                await event.edit("Please reply to a voice message with `.voice [lang]`!")
                return
                
            reply_msg = await event.get_reply_message()
            if not reply_msg.voice:
                await event.edit("The replied message is not a voice note!")
                return
                
            await event.edit("Downloading voice note...")
            await event.client.download_media(reply_msg, file=ogg_path)
            
            await event.edit("Loading Whisper AI... (this may take a minute on first run)")
            
            # Run audio conversion in a separate thread
            def convert_audio():
                audio = AudioSegment.from_ogg(ogg_path)
                audio.export(wav_path, format="wav")
            await asyncio.to_thread(convert_audio)
            
            await event.edit(f"Transcribing with Whisper AI ({whisper_lang or 'auto'})...")
            
            # Run Whisper recognition
            def recognize_speech():
                global whisper_model
                from faster_whisper import WhisperModel
                if whisper_model is None:
                    # 'small' model provides excellent accuracy for Russian slang
                    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
                
                segments, info = whisper_model.transcribe(wav_path, language=whisper_lang)
                transcript = " ".join([segment.text for segment in segments])
                return transcript.strip()
            
            transcript = await asyncio.to_thread(recognize_speech)
            
            if not transcript:
                await event.edit("Could not understand the audio. It might be silent.")
            else:
                await event.edit(f"**Transcript:**\n\n{transcript}")
            
        except Exception as e:
            await event.edit(f"Voice transcription error: {e}")
            print(f"Voice error: {e}")
        finally:
            # Clean up temp files
            if os.path.exists(ogg_path):
                os.remove(ogg_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
