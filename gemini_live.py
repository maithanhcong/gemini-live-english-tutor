import asyncio
import inspect
import logging
import os
import traceback

logger = logging.getLogger(__name__)
from google import genai
from google.genai import types
from tutor_system_instruction import get_system_instruction

# Model aliases to guarantee resolution between human-friendly names and API endpoints
MODEL_ALIASES = {
    "gemini-3-flash-live": ["gemini-3.1-flash-live-preview", "gemini-3-flash-live"],
    "gemini-2.5-flash-native-audio": [
        "gemini-2.5-flash-native-audio-latest",
        "gemini-2.5-flash-native-audio",
        "gemini-2.5-flash-native-audio-dialog",
        "gemini-2.5-flash-native-audio-preview-12-2025",
    ],
    "gemini-2.0-flash-exp": ["gemini-2.0-flash-exp", "gemini-2.0-flash-realtime-exp"],
}


def is_quota_error(error_str: str) -> bool:
    s = str(error_str).lower()
    return any(
        term in s
        for term in [
            "429",
            "resource_exhausted",
            "quota",
            "rate limit",
            "too many requests",
            "exhausted",
        ]
    )


def is_model_error(error_str: str) -> bool:
    s = str(error_str).lower()
    return any(
        term in s
        for term in [
            "not found",
            "not supported",
            "is not found for api version",
            "503",
            "unavailable",
            "overloaded",
            "capacity",
        ]
    )


class GeminiLive:
    """
    Handles interaction with Gemini Live API with automatic API Key and Model Failover.
    """

    def __init__(
        self,
        api_key=None,
        api_keys=None,
        model=None,
        models=None,
        input_sample_rate=16000,
        tools=None,
        tool_mapping=None,
        system_instruction=None,
        mastered_words=None,
    ):
        # 1. Resolve API Keys (Primary -> Backup)
        if api_keys:
            self.api_keys = [k.strip() for k in api_keys if k and k.strip()]
        elif api_key:
            self.api_keys = [api_key.strip()]
        else:
            env_keys = os.getenv("GEMINI_API_KEYS")
            if env_keys:
                self.api_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
            else:
                single_k = os.getenv("GEMINI_API_KEY")
                self.api_keys = [single_k.strip()] if single_k else []

        if not self.api_keys:
            raise ValueError(
                "No Gemini API Key provided or found in environment variables."
            )

        # 2. Resolve Models with intelligent fallback order
        raw_models = []
        if models:
            raw_models = [m.strip() for m in models if m and m.strip()]
        elif model:
            raw_models = [model.strip()]
        else:
            env_models = os.getenv("FALLBACK_MODELS")
            if env_models:
                raw_models = [m.strip() for m in env_models.split(",") if m.strip()]
            else:
                single_m = os.getenv("MODEL", "gemini-3.8-live")
                raw_models = [single_m.strip()]

        # Expand aliases while preserving priority and removing duplicates
        resolved_models = []
        for rm in raw_models:
            if rm in MODEL_ALIASES:
                for candidate in MODEL_ALIASES[rm]:
                    if candidate not in resolved_models:
                        resolved_models.append(candidate)
            else:
                if rm not in resolved_models:
                    resolved_models.append(rm)

        self.models = resolved_models
        self.input_sample_rate = input_sample_rate
        self.tools = tools or []
        self.tool_mapping = tool_mapping or {}
        self.mastered_words = mastered_words or []
        self.system_instruction = system_instruction or get_system_instruction(
            mastered_words=self.mastered_words
        )
        self.stop_requested = asyncio.Event()
        self._active_event_queue = None

    def stop(self):
        """Signals the session to terminate gracefully."""
        self.stop_requested.set()
        if self._active_event_queue:
            try:
                self._active_event_queue.put_nowait(None)
            except Exception:
                pass

    async def start_session(
        self,
        audio_input_queue,
        video_input_queue,
        text_input_queue,
        audio_output_callback,
        audio_interrupt_callback=None,
    ):
        voice_name = os.getenv("VOICE_NAME", "Puck")
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
            system_instruction=types.Content(
                parts=[types.Part(text=self.system_instruction)]
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            realtime_input_config=types.RealtimeInputConfig(
                turn_coverage="TURN_INCLUDES_ONLY_ACTIVITY",
            ),
            tools=self.tools,
        )

        key_idx = 0
        model_idx = 0
        total_keys = len(self.api_keys)
        total_models = len(self.models)

        while not self.stop_requested.is_set():
            if model_idx >= total_models:
                logger.error(
                    "[Live Connect] All fallback models and API keys have been exhausted!"
                )
                yield {
                    "type": "error",
                    "error": "Tất cả Model và API Key dự phòng đều gặp lỗi.",
                }
                break

            current_key = self.api_keys[key_idx]
            current_model = self.models[model_idx]
            key_name = f"Key {key_idx + 1}"

            logger.info(
                f"[Live Connect] Initializing connection with {key_name} | Model: {current_model}"
            )

            client = genai.Client(api_key=current_key)
            session_event_queue = asyncio.Queue()
            self._active_event_queue = session_event_queue
            failover_needed = False
            failover_type = None
            failover_error = None

            try:
                async with client.aio.live.connect(
                    model=current_model, config=config
                ) as session:
                    logger.info(
                        f"[Live Connect] Session established with {key_name} | Model: {current_model}"
                    )
                    await session_event_queue.put(
                        {
                            "type": "connect_status",
                            "status": "connected",
                            "model": current_model,
                            "key_index": key_idx + 1,
                        }
                    )

                    async def send_audio():
                        try:
                            while not self.stop_requested.is_set():
                                chunk = await audio_input_queue.get()
                                await session.send_realtime_input(
                                    audio=types.Blob(
                                        data=chunk,
                                        mime_type=f"audio/pcm;rate={self.input_sample_rate}",
                                    )
                                )
                        except asyncio.CancelledError:
                            logger.debug("send_audio task cancelled")
                        except Exception as e:
                            logger.error(f"send_audio error: {e}")

                    async def send_video():
                        try:
                            while not self.stop_requested.is_set():
                                chunk = await video_input_queue.get()
                                logger.info(
                                    f"Sending video frame to Gemini: {len(chunk)} bytes"
                                )
                                await session.send_realtime_input(
                                    video=types.Blob(
                                        data=chunk, mime_type="image/jpeg"
                                    )
                                )
                        except asyncio.CancelledError:
                            logger.debug("send_video task cancelled")
                        except Exception as e:
                            logger.error(f"send_video error: {e}")

                    async def send_text():
                        try:
                            while not self.stop_requested.is_set():
                                text = await text_input_queue.get()
                                logger.info(f"Sending text to Gemini: {text}")
                                await session.send_realtime_input(text=text)
                        except asyncio.CancelledError:
                            logger.debug("send_text task cancelled")
                        except Exception as e:
                            logger.error(f"send_text error: {e}")

                    async def receive_loop():
                        try:
                            while not self.stop_requested.is_set():
                                async for response in session.receive():
                                    if self.stop_requested.is_set():
                                        break
                                    logger.debug(
                                        f"Received response from Gemini: {response}"
                                    )

                                    if response.go_away:
                                        logger.warning(
                                            f"Received GoAway from Gemini: {response.go_away}"
                                        )
                                    if response.session_resumption_update:
                                        logger.info(
                                            f"Session resumption update: {response.session_resumption_update}"
                                        )

                                    server_content = response.server_content
                                    tool_call = response.tool_call

                                    if server_content:
                                        if server_content.model_turn:
                                            for (
                                                part
                                            ) in server_content.model_turn.parts:
                                                if part.inline_data:
                                                    if inspect.iscoroutinefunction(
                                                        audio_output_callback
                                                    ):
                                                        await audio_output_callback(
                                                            part.inline_data.data
                                                        )
                                                    else:
                                                        audio_output_callback(
                                                            part.inline_data.data
                                                        )

                                        if (
                                            server_content.input_transcription
                                            and server_content.input_transcription.text
                                        ):
                                            await session_event_queue.put(
                                                {
                                                    "type": "user",
                                                    "text": server_content.input_transcription.text,
                                                }
                                            )

                                        if (
                                            server_content.output_transcription
                                            and server_content.output_transcription.text
                                        ):
                                            await session_event_queue.put(
                                                {
                                                    "type": "gemini",
                                                    "text": server_content.output_transcription.text,
                                                }
                                            )

                                        if server_content.interaction_status:
                                            status_val = (
                                                server_content.interaction_status
                                            )
                                            status_str = (
                                                status_val.name
                                                if hasattr(status_val, "name")
                                                else str(status_val)
                                            )
                                            await session_event_queue.put(
                                                {
                                                    "type": "interaction_status",
                                                    "status": status_str,
                                                }
                                            )

                                        if server_content.turn_complete:
                                            await session_event_queue.put(
                                                {"type": "turn_complete"}
                                            )

                                        if server_content.interrupted:
                                            if audio_interrupt_callback:
                                                if inspect.iscoroutinefunction(
                                                    audio_interrupt_callback
                                                ):
                                                    await audio_interrupt_callback()
                                                else:
                                                    audio_interrupt_callback()
                                            await session_event_queue.put(
                                                {"type": "interrupted"}
                                            )

                                    if tool_call:
                                        function_responses = []
                                        for fc in tool_call.function_calls:
                                            func_name = fc.name
                                            args = fc.args or {}
                                            if func_name in self.tool_mapping:
                                                try:
                                                    tool_func = (
                                                        self.tool_mapping[
                                                            func_name
                                                        ]
                                                    )
                                                    if (
                                                        inspect.iscoroutinefunction(
                                                            tool_func
                                                        )
                                                    ):
                                                        result = (
                                                            await tool_func(
                                                                **args
                                                            )
                                                        )
                                                    else:
                                                        loop = (
                                                            asyncio.get_running_loop()
                                                        )
                                                        result = await loop.run_in_executor(
                                                            None,
                                                            lambda: tool_func(
                                                                **args
                                                            ),
                                                        )
                                                except Exception as e:
                                                    result = f"Error: {e}"

                                                function_responses.append(
                                                    types.FunctionResponse(
                                                        name=func_name,
                                                        id=fc.id,
                                                        response={
                                                            "result": result
                                                        },
                                                    )
                                                )
                                                await session_event_queue.put(
                                                    {
                                                        "type": "tool_call",
                                                        "name": func_name,
                                                        "args": args,
                                                        "result": result,
                                                    }
                                                )

                                        await session.send_tool_response(
                                            function_responses=function_responses
                                        )

                        except asyncio.CancelledError:
                            logger.debug("receive_loop task cancelled")
                        except Exception as e:
                            err_str = str(e)
                            if not self.stop_requested.is_set():
                                if is_quota_error(err_str):
                                    await session_event_queue.put(
                                        {"_failover": "quota", "error": e}
                                    )
                                elif is_model_error(err_str):
                                    await session_event_queue.put(
                                        {"_failover": "model", "error": e}
                                    )
                                else:
                                    logger.warning(f"[Live Connect] receive_loop caught unexpected error: {type(e).__name__}: {e}")
                                    await session_event_queue.put(
                                        {"_failover": "error", "error": e}
                                    )
                        finally:
                            await session_event_queue.put(None)

                    send_audio_task = asyncio.create_task(send_audio())
                    send_video_task = asyncio.create_task(send_video())
                    send_text_task = asyncio.create_task(send_text())
                    receive_task = asyncio.create_task(receive_loop())

                    try:
                        while not self.stop_requested.is_set():
                            event = await session_event_queue.get()
                            if event is None:
                                break
                            if isinstance(event, dict) and "_failover" in event:
                                failover_needed = True
                                failover_type = event["_failover"]
                                failover_error = event["error"]
                                break
                            yield event
                    finally:
                        send_audio_task.cancel()
                        send_video_task.cancel()
                        send_text_task.cancel()
                        receive_task.cancel()

            except Exception as exc:
                if self.stop_requested.is_set():
                    break
                failover_needed = True
                failover_error = exc
                err_str = str(exc)
                if is_quota_error(err_str):
                    failover_type = "quota"
                elif is_model_error(err_str):
                    failover_type = "model"
                else:
                    failover_type = "error"

            if self.stop_requested.is_set():
                break

            if not failover_needed:
                logger.info("[Live Connect] Session completed normally.")
                break

            # --- Failover Handling ---
            err_msg = str(failover_error)

            if failover_type == "quota" or is_quota_error(err_msg):
                # 1. Quota Error -> Switch API Key
                if key_idx + 1 < total_keys:
                    old_k = key_idx + 1
                    key_idx += 1
                    logger.warning(
                        f"[Live Connect] Key {old_k} quota exceeded -> Switching to Backup Key {key_idx + 1}..."
                    )
                    yield {
                        "type": "gemini",
                        "text": f"*(Hệ thống: Key {old_k} hết hạn ngạch. Đang tự động chuyển sang Key dự phòng {key_idx + 1}...)*",
                    }
                    await asyncio.sleep(0.5)
                    continue
                else:
                    # All keys exhausted for current model -> Switch Model
                    old_m = current_model
                    model_idx += 1
                    if model_idx < total_models:
                        fallback_model = self.models[model_idx]
                        logger.warning(
                            f"[Live Connect] All API Keys quota exceeded for model '{old_m}' -> Switching to fallback model: '{fallback_model}'..."
                        )
                        key_idx = 0  # Reset to primary key for fallback model
                        yield {
                            "type": "gemini",
                            "text": f"*(Hệ thống: Model {old_m} hết quota trên tất cả các Key. Chuyển sang model dự phòng: {fallback_model})*",
                        }
                        await asyncio.sleep(0.5)
                        continue
                    else:
                        logger.error(
                            f"[Live Connect] All keys and models exhausted on quota error: {err_msg}"
                        )
                        yield {
                            "type": "error",
                            "error": f"Hết hạn ngạch trên toàn bộ key và model: {err_msg}",
                        }
                        break

            elif failover_type == "model" or is_model_error(err_msg):
                # 2. Model Error / Overload -> Switch Model
                old_m = current_model
                model_idx += 1
                if model_idx < total_models:
                    fallback_model = self.models[model_idx]
                    logger.warning(
                        f"[Live Connect] Model '{old_m}' error/overloaded -> Switching to fallback model: '{fallback_model}'..."
                    )
                    yield {
                        "type": "gemini",
                        "text": f"*(Hệ thống: Model {old_m} gặp sự cố hoặc quá tải. Chuyển sang model: {fallback_model})*",
                    }
                    await asyncio.sleep(0.5)
                    continue
                else:
                    logger.error(
                        f"[Live Connect] All fallback models exhausted: {err_msg}"
                    )
                    yield {
                        "type": "error",
                        "error": f"Tất cả model dự phòng đều gặp sự cố: {err_msg}",
                    }
                    break

            else:
                # 3. Other connection errors -> Try next key, then next model
                if key_idx + 1 < total_keys:
                    old_k = key_idx + 1
                    key_idx += 1
                    logger.warning(
                        f"[Live Connect] Connection issue on Key {old_k} -> Switching to Backup Key {key_idx + 1}..."
                    )
                    await asyncio.sleep(0.5)
                    continue
                elif model_idx + 1 < total_models:
                    old_m = current_model
                    model_idx += 1
                    fallback_model = self.models[model_idx]
                    logger.warning(
                        f"[Live Connect] Switching to fallback model: '{fallback_model}'..."
                    )
                    key_idx = 0
                    await asyncio.sleep(0.5)
                    continue
                else:
                    logger.error(
                        f"[Live Connect] All failover attempts exhausted: {err_msg}"
                    )
                    break
