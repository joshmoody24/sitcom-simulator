def chat(prompt: str, max_tokens:int=2048, temperature:float=1):
    from .integrations.chatgpt import chatgpt
    return chatgpt.chat(prompt, max_tokens, temperature)