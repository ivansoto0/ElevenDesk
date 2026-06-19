# ElevenDesk

A desktop client for the ElevenLabs API. Not affiliated with or endorsed by ElevenLabs.

## Why this project exists

I created ElevenDesk because the accessibility of the ElevenLabs website has been degrading. Tasks that should be straightforward with a keyboard and screen reader have become harder to complete reliably.

## Requirements

- Python 3.13 or 3.14
- An ElevenLabs API key
- Windows or macOS
- A working audio output device

## Installation

Install dependencies with [uv](https://docs.astral.sh/uv/):

```shell
uv sync
```

Run ElevenDesk:

```shell
uv run python -m elevendesk
```

On first launch, ElevenDesk opens Preferences so you can enter your API key and choose an output directory.

## API key storage

The API key is saved to ElevenDesk's per-user settings file outside the repository:

- Windows: `%APPDATA%\ElevenDesk\settings.json`
- macOS: standard per-user application data directory

## Keyboard shortcuts

- `Ctrl+Enter` — generate and play speech (Text to Speech tab)
- `Ctrl+S` — save last output
- `Ctrl+O` — open audio file for transcription

## Features

- Text to speech with voice, model, output format, and voice setting controls
- Speech to text transcription
- Sound effect generation
- Voice design and cloning
- Voice library browser
- Generation history with playback and download
- Pronunciation dictionary listing
- Recursive audio directory import for voice cloning

