import openai
import tomllib

def generate_script(prompt, temperature: float, max_tokens:int=2048) -> dict:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": "You are a helpful code-generating assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message["content"].strip()
    try:
        parsed_data = tomllib.loads(response)
    except tomllib.TOMLDecodeError:
        try:
            parsed_data = tomllib.loads(response + '"')
        except tomllib.TOMLDecodeError:
            raise tomllib.TOMLDecodeError("ChatGPT output was cut off midway through generation.", response)

    return parsed_data