from dataclasses import dataclass, replace

@dataclass
class Character:
    """
    A character in a script and information about their voice.

    :param name: The name of the character
    :param voice_token: The token for the character's voice
    """
    name: str
    voice_token: str

    @staticmethod
    def from_dict(data: dict[str, str]):
        """
        Creates a Character from a dictionary with the same shape.
        """
        return Character(
            name=data['name'],
            voice_token=data['voice_token']
        )
    
    def replace(self, **kwargs):
        """
        Returns a new Character with the specified fields replaced.
        """
        return replace(self, **kwargs)

@dataclass
class Clip:
    """
    A clip in a script, including the speaker, speech, and audio.

    :param speaker: The name of the speaker
    :param speech: The speech for the clip
    :param image_prompt: The prompt for the image
    :param image_url: The URL for the image (currently unused, but may be used in the future with a different image engine)
    :param image_path: The path to the image
    :param audio_url: The URL for the audio (currently unused, but may be used in the future with a different TTS engine)
    :param audio_path: The path to the audio
    :param title: The title of the clip
    :param duration: The duration of the clip
    """
    speaker: str | None
    speech: str | None
    image_prompt: str | None
    image_path: str | None
    image_url: str | None
    audio_url: str | None
    audio_path: str | None
    title: str | None
    duration: str | None

    @property
    def needs_audio(self):
        """
        Returns True if the clip needs audio, and False if it doesn't.
        """
        return bool(self.speech and not (self.audio_path or self.audio_url))
    
    @property
    def needs_image(self):
        """
        Returns True if the clip needs an image, and False if it doesn't.
        """
        return bool(self.image_prompt and not (self.image_path or self.image_url))

    @staticmethod
    def from_dict(data: dict):
        """
        Creates a Clip from a dictionary with the same shape.
        All fields are optional.
        """
        return Clip(
            speaker=data.get('speaker'),
            speech=data.get('speech'),
            image_prompt=data.get('image_prompt'),
            image_path=data.get('image_path'),
            image_url=data.get('image_url'),
            audio_url=data.get('audio_url'),
            audio_path=data.get('audio_path'),
            title=data.get('title'),
            duration=data.get('duration')
        )

    def replace(self, **kwargs):
        """
        Returns a new Clip with the specified fields replaced.
        """
        return replace(self, **kwargs)

@dataclass
class ScriptMetadata:
    """
    Metadata for a script.

    :param title: The title of the script
    :param bgm_style: The style of the background music
    :param art_style: The style of the art
    :param prompt: The prompt for the script
    :param bgm_path: The path to the background music
    :param misc: Any additional metadata
    """
    title: str | None
    bgm_style: str | None
    art_style: str | None
    prompt: str | None
    bgm_path: str | None

    @staticmethod
    def from_dict(data: dict):
        """
        Creates a ScriptMetadata from a dictionary with the same shape.
        All fields are required except for bgm_path.
        """
        # creates misc from all data attributes besides the main ones
        return ScriptMetadata(
            title=data.get('title'),
            bgm_style=data.get('bgm_style'),
            art_style=data.get('art_style'),
            prompt=data.get('prompt'),
            bgm_path=data.get('bgm_path'),
        )
    
    def replace(self, **kwargs):
        """
        Returns a new ScriptMetadata with the specified fields replaced.
        """
        return replace(self, **kwargs)

@dataclass
class Script:
    """
    Contains all the data for a script, including characters, clips, and metadata.
    
    The clips are ordered in the order they should be played.

    In general, the fields should be populated in the following order:
    1. characters
    2. clips
    3. metadata

    Metadata is last to give the language model more context before summarizing the script.

    :param characters: A list of characters in the script
    :param clips: A list of clips in the script
    :param metadata: The metadata for the script
    """
    characters: list[Character]
    clips: list[Clip]
    metadata: ScriptMetadata

    @staticmethod
    def from_dict(data: dict):
        """
        Returns a Script from a dictionary with the same shape.
        """
        return Script(
            characters=[Character.from_dict(character) for character in data['characters']],
            clips=[Clip.from_dict(clip) for clip in data['clips']],
            metadata=ScriptMetadata.from_dict(data['metadata'])
        )
    
    def replace(self, **kwargs):
        """
        Returns a new Script with the specified fields replaced.
        """
        return replace(self, **kwargs)
    
@dataclass
class VideoResult:
    """
    The result of rendering a video.

    :param path: The path to the rendered video
    :param title: The title of the video
    :param description: The description of the video
    """
    path: str
    title: str
    description: str