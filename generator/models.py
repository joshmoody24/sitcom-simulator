from dataclasses import dataclass

@dataclass
class Character:
    name: str
    voice_token: str
    default_image_prompt: str

@dataclass
class Line:
    character: Character
    speech: str
    image_prompt: str