import openai
import time
import requests

client = openai.OpenAI(
    api_key = 'your api key')

def get_oai_completion(prompt):

    try: 
        response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
       
    ],
   temperature=1,
   max_tokens=2048,
   top_p=0.95,
   frequency_penalty=0,
   presence_penalty=0,
   stop=None
)
        res = response.model_dump(mode='python')['choices'][0]['message']['content']
        return res
    except requests.exceptions.Timeout:
        # Handle the timeout error here
        print("The OpenAI API request timed out. Please try again later.")
        return None
    except openai.BadRequestError as e:
        # Handle the invalid request error here
        print(f"The OpenAI API request was invalid: {e}")
        return None
    except openai.APIError as e:
        if "The operation was timeout" in str(e):
            # Handle the timeout error here
            print("The OpenAI API request timed out. Please try again later.")
#             time.sleep(3)
            return get_oai_completion(prompt)            
        else:
            # Handle other API errors here
            print(f"The OpenAI API returned an error: {e}")
            return None
    except openai.RateLimitError as e:
        return get_oai_completion(prompt)

def call_chatgpt(ins):
    success = False
    re_try_count = 15
    ans = ''
    while not success and re_try_count >= 0:
        re_try_count -= 1
        try:
            ans = get_oai_completion(ins)
            success = True
        except:
            time.sleep(5)
            print('retry for sample:', ins)
    return ans
