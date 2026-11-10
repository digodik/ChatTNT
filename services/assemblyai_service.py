#services/assemblyai_service.py
import aiohttp
import asyncio
import logging
import os
import time
from typing import Tuple, Optional, Dict, List
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class AssemblyAIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _prepare_audio_file(self, audio_path: str) -> str:
        try:
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext == '.mp3':
                logger.info(f"File already in MP3 format: {audio_path}")
                return audio_path
            
            temp_dir = tempfile.gettempdir()
            temp_filename = f"converted_{int(time.time())}.mp3"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            logger.info(f"Converting {audio_path} to MP3: {temp_path}")
            
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-acodec', 'mp3',
                '-ab', '128k',
                '-ar', '44100',
                '-y', 
                temp_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return audio_path
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                logger.info(f"Conversion successful: {temp_path}")
                return temp_path
            else:
                logger.warning("Converted file not created, using original")
                return audio_path
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout during audio conversion")
            return audio_path
        except FileNotFoundError:
            logger.warning("FFmpeg not found, using original file")
            return audio_path
        except Exception as e:
            logger.error(f"Error preparing audio file: {e}")
            return audio_path
    
    async def _upload_file(self, file_path: str) -> str:
        upload_headers = {"authorization": self.api_key}
        
        with open(file_path, 'rb') as f:
            async with self.session.post(
                "https://api.assemblyai.com/v2/upload",
                headers=upload_headers,
                data=f
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"File upload error: {error_text}")
                
                result = await response.json()
                upload_url = result["upload_url"]
                logger.info(f"File uploaded successfully, URL: {upload_url}")
                return upload_url
    
    def _format_speakers_text(self, utterances: List[Dict], user_lang: str = "en", get_string_func=None) -> str:
        if not utterances:
            return ""
        
        speakers = set()
        for utterance in utterances:
            speaker = utterance.get('speaker')
            if speaker is not None:
                speakers.add(speaker)
        
        if len(speakers) <= 1:
            return " ".join(utterance.get('text', '').strip() for utterance in utterances if utterance.get('text', '').strip())
        
        if get_string_func:
            speaker_label = get_string_func("speaker_label", user_lang)
        else:
            speaker_labels = {
                "en": "Speaker",
                "ru": "Спикер", 
                "pl": "Mówca",
                "es": "Hablante",
                "fr": "Orateur",
                "de": "Sprecher",
                "it": "Oratore"
            }
            speaker_label = speaker_labels.get(user_lang, "Speaker")
        
        formatted_text = ""
        current_speaker = None
        
        for utterance in utterances:
            speaker_id = utterance.get('speaker')
            text = utterance.get('text', '').strip()
            
            if not text:
                continue
            
            if speaker_id is not None:
                if isinstance(speaker_id, str) and speaker_id.isalpha():
                    speaker_name = f"{speaker_label} {speaker_id}"
                else:
                    try:
                        speaker_num = int(speaker_id)
                        speaker_letter = chr(65 + speaker_num)
                        speaker_name = f"{speaker_label} {speaker_letter}"
                    except (ValueError, TypeError):
                        speaker_name = f"{speaker_label} {speaker_id}"
            else:
                speaker_name = speaker_label
            
            if speaker_name != current_speaker:
                if formatted_text:
                    formatted_text += "\n\n"
                formatted_text += f"{speaker_name}: "
                current_speaker = speaker_name
            else:
                formatted_text += " "
            
            formatted_text += text
        
        return formatted_text.strip()
    
    async def transcribe(self, audio_path: str, language_code: str = None, user_lang: str = "en", get_string_func=None, enable_speaker_diarization: bool = False, status_callback=None) -> Tuple[bool, str]:
        try:
            if status_callback:
                await status_callback("compressing")
            
            audio_file = await self._prepare_audio_file(audio_path)
            
            if status_callback:
                await status_callback("uploading")
            
            upload_url = await self._upload_file(audio_file)
            
            if status_callback:
                await status_callback("starting")
            
            config = {
                "audio_url": upload_url,
                "language_detection": True,
            }
            
            if enable_speaker_diarization:
                config["speaker_labels"] = True
                config["speakers_expected"] = 2
            
            if language_code and language_code != "auto":
                config["language_code"] = language_code
                config["language_detection"] = False
            
            logger.info(f"Creating transcription job with config: {config}")
            
            async with self.session.post(
                "https://api.assemblyai.com/v2/transcript",
                json=config,
                headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Job creation error: {error_text}")
                    return False, f"Job creation error: {error_text}"
                
                result = await response.json()
                transcript_id = result["id"]
                logger.info(f"Job created: {transcript_id}")
            
            start_time = time.time()
            while True:
                async with self.session.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    status = result["status"]
                    
                    if status == "completed":
                        detected_language = result.get("language_code", "unknown")
                        
                        if status_callback:
                            await status_callback("completed", detected_language)
                        
                        logger.info(f"Transcription completed. Detected language: {detected_language}")
                        
                        if enable_speaker_diarization and "utterances" in result and result["utterances"]:
                            text = self._format_speakers_text(result["utterances"], user_lang, get_string_func)
                        else:
                            text = result["text"]
                        
                        return True, text
                    
                    elif status == "error":
                        error_msg = result.get("error", "Unknown error")
                        logger.error(f"Transcription error: {error_msg}")
                        
                        if status_callback:
                            await status_callback("error", error_msg)
                        
                        return False, f"Transcription error: {error_msg}"
                    
                    elif status in ["queued", "processing"]:
                        if status_callback:
                            elapsed_time = time.time() - start_time
                            await status_callback("transcribing", elapsed_time)
                        
                        await asyncio.sleep(2)
                    else:
                        logger.warning(f"Unknown status: {status}")
                        await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"General transcription error: {e}", exc_info=True)
            if status_callback:
                await status_callback("error", str(e))
            return False, f"Transcription error: {str(e)}"
        
        finally:
            if 'audio_file' in locals() and audio_file != audio_path:
                try:
                    os.unlink(audio_file)
                    logger.info(f"Temporary file deleted: {audio_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {audio_file}: {e}")

def create_assemblyai_service(api_key: str) -> Optional[AssemblyAIService]:
    if not api_key:
        logger.warning("AssemblyAI API key not provided")
        return None
    
    return AssemblyAIService(api_key)