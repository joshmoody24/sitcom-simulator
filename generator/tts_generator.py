from .integrations.tts import fakeyou, gtts

# takes in array of line models
def generate_voice_clips(lines, characters, high_quality=False, config=None):
    # generating voice clips can take a LONG time if args.high_quality_audio == True
    # because of long delays to avoid API timeouts on FakeYou.com
    if(high_quality):
        return fakeyou.generate_voice_clips(lines, characters, config)
    else:
        return gtts.generate_voice_clips(lines)