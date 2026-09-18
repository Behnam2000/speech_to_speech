import asyncio
import sounddevice as sd
from google import genai
from google.genai import types

# Audio Stream Settings
CHANNELS = 1
INPUT_RATE = 16000  # The Live API expects 16kHz for input
OUTPUT_RATE = 24000 # The Live API returns 24kHz for output
CHUNK_SIZE = 1600   # Send 100ms chunks at a time

async def run_translator():
    client = genai.Client()
    
    config = types.LiveConnectConfig(
        translation_config=types.TranslationConfig(
            target_language_code="fa",
            echo_target_language=False
        )
    )
    
    print("Connecting to Gemini Live API...")
    
    async with client.aio.live.connect(
        model="gemini-3.5-live-translate-preview", 
        config=config
    ) as session:
        print("Connected! Play the video or speak into the mic to hear the Persian translation.")
        
        # Queue for passing audio from the mic thread to the async loop
        audio_in_queue = asyncio.Queue()

        def mic_callback(indata, frames, time, status):
            if status:
                print(status)
            # indata is a memoryview/buffer, convert to bytes and queue it non-blockingly
            audio_in_queue.put_nowait(bytes(indata))

        async def send_mic_audio():
            # Open a non-blocking input stream
            with sd.RawInputStream(samplerate=INPUT_RATE, channels=CHANNELS,
                                   dtype='int16', blocksize=CHUNK_SIZE,
                                   device=1,
                                   callback=mic_callback):
                while True:
                    data = await audio_in_queue.get()
                    await session.send_realtime_input(
                        audio=types.Blob(
                            data=data,
                            mime_type="audio/pcm;rate=16000"
                        )
                    )

        async def receive_and_play_audio():
            # Open a blocking output stream
            with sd.RawOutputStream(samplerate=OUTPUT_RATE, channels=CHANNELS, dtype='int16') as out_stream:
                async for response in session.receive():
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.inline_data:
                                # Play the translated audio chunk in a separate thread to prevent blocking the async loop
                                await asyncio.to_thread(out_stream.write, part.inline_data.data)

        # Run both the sender and receiver concurrently
        await asyncio.gather(send_mic_audio(), receive_and_play_audio())

if __name__ == "__main__":
    try:
        asyncio.run(run_translator())
    except KeyboardInterrupt:
        print("\nTranslation stopped.")