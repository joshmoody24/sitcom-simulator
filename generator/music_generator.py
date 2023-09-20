from .integrations.music import freepd

def generate_music(category: str):
    return freepd.download_random_music(category)