from google import genai
import os
from google.genai import errors
import time
from dotenv import load_dotenv
from google.genai import types
load_dotenv()
def embedd_query(prompt):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.embed_content(
            model="gemini-embedding-001",            
            contents=prompt,
        )
    return  response.embeddings[0].values

def response_generator(prompt):
  retries=5
  delay=2
  for attempt in range(retries):
    try:
      client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
      response = client.models.generate_content(
              model="gemini-3.5-flash",
              contents=prompt,
              config=types.GenerateContentConfig(
                  temperature=0,
                  
        ),
      ) 
      return response
    except errors.APIError as e:
      if  attempt < retries - 1:
        print(f"Encountered {e.code}. Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2 
        continue
              
      raise e

def response_generator_json(prompt):
  retries=5
  delay=2
  for attempt in range(retries):
    try:
      client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
      response = client.models.generate_content(
              model="gemini-3.5-flash",
              contents=prompt,
              config=types.GenerateContentConfig(
                  temperature=0,
                  response_mime_type="application/json",
        ),
      ) 
      return response
    except errors.APIError as e:
      if  attempt < retries - 1:
        print(f"Encountered {e.code}. Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2 
        continue
              
      raise e
