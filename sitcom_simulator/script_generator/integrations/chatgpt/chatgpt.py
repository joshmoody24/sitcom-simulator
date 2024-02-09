import openai

def chat(prompt: str, max_tokens:int=2048, temperature:float=1):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": "You are a helpful script-writing assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message["content"].strip()