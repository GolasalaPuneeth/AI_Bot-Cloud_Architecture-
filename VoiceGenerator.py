import diskcache
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
import base64


# Initialize the Polly client
polly = boto3.client('polly', aws_access_key_id="",
                     aws_secret_access_key="", region_name="us-east-1")
cache = diskcache.Cache(os.path.join("static/CachePolly/"))

 
async def mapy(text):
    # Check if the audio data is already in the cache
    if text in cache:
        encoded_string = cache[text]

    else:
        try:
            # If not in the cache, make a request to Polly
            response = polly.synthesize_speech(Text=text, OutputFormat='pcm', VoiceId='Brian')
            audio_data = response['AudioStream'].read()
            encoded_string = base64.b64encode(audio_data).decode("utf-8") # type: ignore

            # Save the audio data to the cache
            cache[text] = encoded_string
        except (BotoCoreError, ClientError) as e:
            # Handle errors from Polly
            print(f"Error: {e}")
            return

    #audio_bytes = base64.b64decode(encoded_string.encode('ascii')) # type: ignore
    return encoded_string
