# 🌐 LangNet

LangNet is a utility powered by OpenAI Whisper and DeepL. It incorporates speech recognition and an optional translation feature, allowing it to recognize speech in one language and translate it to another in real-time.

## Requirements

- Python 3.10
- ffmpeg

Additionally you have to install dependencies for Python from the requirements.txt file, you can do so by running.

```
pip install -r requirements.txt
```

## Usage

To use LangNet simply launch either run.bat or run_bin.bat if you have downloaded the portable version, alternatively, you can manually run the app.py python file.

If you wish to use the optional translation feature, you can choose to opt-in to use either the built-in Whisper translation method which is limited to English only and may not be very accurate, or you can choose DeepL instead. To use DeepL, you will need to obtain an API key from https://www.deepl.com/pro-api?cta=header-pro-api/.

If you wish to transcribe and translate audio that is coming from an audio output instead of an audio input you can use a virtual audio mixer such as [Voicemeeter](https://vb-audio.com/Voicemeeter/) to route audio into a virtual microphone.

## References

[OpenAI Whisper](https://github.com/openai/whisper) is the main technology powering LangNet, additionally [Whisper Real Time](https://github.com/davabase/whisper_real_time) has been used to get an understanding of how to detect and obtain audio data from a microphone in real-time.

## Screenshots

![Screenshot](https://github.com/rs189/LangNet/blob/main/Thumbnail.png?raw=true)
