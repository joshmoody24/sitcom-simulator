from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Character:
    name: str
    voice_token: str

    @staticmethod
    def from_dict(data: dict):
        return Character(
            name=data['name'],
            voice_token=data['voice_token']
        )
    
    def replace(self, **kwargs):
        return replace(self, **kwargs)

@dataclass(frozen=True)
class Clip:
    speaker: str | None
    speech: str | None
    image_prompt: str | None
    image_path: str | None
    audio_url: str | None
    audio_path: str | None
    title: str | None
    duration: str | None

    @property
    def needs_audio(self):
        return self.speech and not (self.audio_path or self.audio_url)
    
    @property
    def needs_image(self):
        return self.image_prompt and not self.image_path

    @staticmethod
    def from_dict(data: dict):
        return Clip(
            speaker=data.get('speaker'),
            speech=data.get('speech'),
            image_prompt=data.get('image_prompt'),
            image_path=data.get('image_path'),
            audio_url=data.get('audio_url'),
            audio_path=data.get('audio_path'),
            title=data.get('title'),
            duration=data.get('duration')
        )

    def replace(self, **kwargs):
        return replace(self, **kwargs)

@dataclass(frozen=True)
class ScriptMetadata:
    title: str
    bgm_style: str
    art_style: str
    bgm_path: str | None

    @staticmethod
    def from_dict(data: dict):
        return ScriptMetadata(
            title=data['title'],
            bgm_style=data['bgm_style'],
            art_style=data['art_style'],
            bgm_path=data.get('bgm_path'),
        )
    
    def replace(self, **kwargs):
        return replace(self, **kwargs)

@dataclass(frozen=True)
class Script:
    characters: list[Character]
    clips: list[Clip]
    metadata: ScriptMetadata

    @staticmethod
    def from_dict(data: dict):
        return Script(
            characters=[Character.from_dict(character) for character in data['characters']],
            clips=[Clip.from_dict(clip) for clip in data['clips']],
            metadata=ScriptMetadata.from_dict(data['metadata'])
        )
    
    def replace(self, **kwargs):
        return replace(self, **kwargs)
    
@dataclass(frozen=True)
class VideoResult:
    path: str
    title: str
    description: str