import sys, os
sys.path.insert(0, os.path.abspath("."))
import time
import json
from google import genai
import passage_service

keys = passage_service.get_api_keys()
client = genai.Client(api_key=keys[0])
t0 = time.time()
prompt = 'Generate JSON array with 3 Oxford 3000 words: comfortable, convenient, flexible. Format: [{"word": "...", "ipa": "...", "pos": "...", "meaning_vi": "...", "example_sentence": "...", "topic": "...", "level": "..."}]'
resp = client.models.generate_content(
    model='gemini-flash-lite-latest',
    contents=prompt,
    config=genai.types.GenerateContentConfig(
        response_mime_type='application/json'
    )
)
dt = time.time() - t0
print(f"Time: {dt:.2f}s")
print(resp.text)
