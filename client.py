from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
  api_key= OPENAI_API_KEY
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  store=True,
  messages=[{"role": "system", "content": "You are a virtual assitant skilled in general logic and reasoning tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message.content);
