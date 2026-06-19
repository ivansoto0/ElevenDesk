# ElevenDesk

ElevenDesk is an accessible desktop client for the ElevenLabs API. It provides text-to-speech, speech-to-text, sound-effect generation, voice design, voice cloning, history, and voice-library tools in a native wxPython interface.

## Why this project exists

I created ElevenDesk because the accessibility of the ElevenLabs website seems to be degrading. Tasks that should be direct and predictable with a keyboard and screen reader have become harder to complete reliably.

ElevenDesk provides a focused desktop alternative where controls have meaningful names, keyboard navigation follows a deliberate order, status changes are communicated as text, and common actions do not require navigating a changing web interface.

This project is an independent client and is not affiliated with or endorsed by ElevenLabs.

## Requirements

- Python 3.10 through 3.12
- An ElevenLabs API key
- Windows or macOS
- A working audio-output device

Python 3.12 is recommended. The application currently uses Python's `audioop` module for u-law playback, which is not included in Python 3.13 and later.

## Installation

Clone the repository and enter its directory:

```shell
git clone <repository-url>
cd elevenClient
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```shell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run ElevenDesk:

```shell
python -m elevendesk
```

On first launch, ElevenDesk opens Preferences so you can enter your ElevenLabs API key and choose an output directory.

## API-key storage

The API key is saved only in ElevenDesk's per-user settings file outside the repository:

- Windows: the ElevenDesk directory under `%APPDATA%`
- macOS: the standard per-user application-data directory selected by wxPython

Do not add settings files, environment files, credentials, generated audio, or transcripts to the repository. The included `.gitignore` uses an allowlist and admits only project source and documentation.

## Keyboard and accessibility behavior

- The Text to Speech editor receives focus at startup.
- Press `Ctrl+Enter` to generate and automatically play speech.
- All selection controls use read-only combo boxes.
- Voice settings expose labels and current values to screen readers.
- Controls have explicit accessible names and logical tab order.
- Status and error information is communicated with text.

## Main features

- Text to speech with voice, model, output-format, and voice-setting controls
- Automatic playback after speech generation
- Speech-to-text transcription
- Sound-effect generation
- Voice design and cloning
- Recursive audio-directory import with file metadata
- Voice library and generation history
- Friendly local history dates
- Pronunciation-dictionary listing

## Sensitive-data policy

Before committing changes, verify the staged files:

```shell
git status --short
git diff --cached
```

Never commit API keys, settings files, `.env` files, credentials, audio output, transcripts, virtual environments, caches, or compiled Python files.
