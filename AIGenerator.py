import os
import diskcache
from openai import OpenAI

cache = diskcache.Cache(os.path.join("static/"))
async def intell(text: str) -> str:
    try:
        if text in cache:
            return cache[text] # type: ignore
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant named dudu."},
                {"role": "user", "content": f"{text}"},
            ],
            max_tokens=40,
            temperature=0.4
        )
        result = completion.choices[0].message.content
        cache[text] = result
        return result # type: ignore
    except Exception as Error:
        print(Error)
    finally:
        cache.close()
