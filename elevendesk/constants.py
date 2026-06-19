APP_NAME = "ElevenDesk"
APP_TITLE = "ElevenDesk"
APP_VERSION = "1.0.0"
CONFIG_FILE_NAME = "settings.json"
MAIN_MODULE_NAME = "__main__"

MODEL_FLASH_V2_5 = "eleven_flash_v2_5"
MODEL_TURBO_V2_5 = "eleven_turbo_v2_5"
MODEL_MULTILINGUAL_V2 = "eleven_multilingual_v2"
MODEL_V3 = "eleven_v3"
MODEL_SCRIBE_V1 = "scribe_v1"
MODEL_IDS = (
	MODEL_FLASH_V2_5,
	MODEL_TURBO_V2_5,
	MODEL_MULTILINGUAL_V2,
	MODEL_V3,
)

OUTPUT_MP3_44100_128 = "mp3_44100_128"
OUTPUT_MP3_44100_192 = "mp3_44100_192"
OUTPUT_PCM_44100 = "pcm_44100"
OUTPUT_ULAW_8000 = "ulaw_8000"
OUTPUT_FORMATS = (
	OUTPUT_MP3_44100_128,
	OUTPUT_MP3_44100_192,
	OUTPUT_PCM_44100,
	OUTPUT_ULAW_8000,
)

KEY_API_KEY = "api_key"
KEY_DEFAULT_MODEL = "default_model"
KEY_DEFAULT_VOICE_ID = "default_voice_id"
KEY_DEFAULT_OUTPUT_FORMAT = "default_output_format"
KEY_OUTPUT_DIRECTORY = "output_directory"
KEY_ID = "id"
KEY_VOICE_ID = "voice_id"
KEY_NAME = "name"
KEY_CATEGORY = "category"
KEY_DESCRIPTION = "description"
KEY_DATE = "date"
KEY_TYPE = "type"
KEY_VOICE = "voice"
KEY_MODEL = "model"
KEY_PREVIEW = "preview"
KEY_HISTORY_ITEM_ID = "history_item_id"
KEY_AUDIO = "audio"
KEY_FILE_PATH = "file_path"
KEY_FILE_NAME = "file_name"
KEY_FILE_DURATION = "file_duration"
KEY_FILE_FORMAT = "file_format"
KEY_FILE_SAMPLE_RATE = "file_sample_rate"
KEY_FILE_CHANNELS = "file_channels"
KEY_FILE_SIZE = "file_size"

EMPTY_TEXT = ""
SPACE = " "
COLON_SPACE = ": "
NEWLINE = "\n"
ELLIPSIS = "..."
DOT = "."
WILDCARD_ALL = "*.*"
JSON_ENCODING = "utf-8"
TEXT_ENCODING = "utf-8"
FILE_MODE_BINARY_READ = "rb"
FILE_MODE_BINARY_WRITE = "wb"
FILE_MODE_TEXT_WRITE = "w"

TAB_TTS = "Text to Speech"
TAB_STT = "Speech to Text"
TAB_SFX = "Sound Effects"
TAB_VOICE_DESIGN = "Voice Design"
LABEL_VOICE = "Voice"
LABEL_MODEL = "Model"
LABEL_OUTPUT_FORMAT = "Output Format"
LABEL_TEXT = "Text"
LABEL_VOICE_SETTINGS = "Voice Settings"
LABEL_STABILITY = "Stability"
LABEL_SIMILARITY = "Similarity Boost"
LABEL_STYLE = "Style"
LABEL_SPEED = "Speed"
LABEL_GENERATE = "Generate"
NAME_GENERATE_SPEECH_SHORTCUT = "Generate speech, Ctrl+Enter"
NAME_PLAY_GENERATED_SPEECH = "Play generated speech"
NAME_SAVE_GENERATED_SPEECH = "Save generated speech"
NAME_GENERATE_SOUND_EFFECT = "Generate sound effect"
NAME_PLAY_GENERATED_SOUND_EFFECT = "Play generated sound effect"
NAME_SAVE_GENERATED_SOUND_EFFECT = "Save generated sound effect"
NAME_DESIGN_NEW_VOICE = "Design new voice"
NAME_VOICE_DESIGN_RESULT = "Designed voice result, read only"
NAME_ADD_DESIGNED_VOICE = "Add designed voice to Text to Speech voice list"
NAME_OPEN_TRANSCRIPTION_AUDIO = "Open audio file for transcription"
NAME_SELECTED_TRANSCRIPTION_FILE = "Selected transcription audio file, read only"
NAME_TRANSCRIBE_SELECTED_AUDIO = "Transcribe selected audio file"
NAME_TRANSCRIPT_OUTPUT = "Transcript output, read only"
NAME_COPY_TRANSCRIPT = "Copy transcript to clipboard"
NAME_SAVE_TRANSCRIPT = "Save transcript to a text file"
SLIDER_ACCESSIBLE_NAME_TEMPLATE = "{0}, {1} percent"
SPEED_ACCESSIBLE_NAME_TEMPLATE = "{0}, {1:.2f} times normal speed"
LABEL_PLAY = "Play"
LABEL_SAVE = "Save"
LABEL_STATUS = "Status"
LABEL_OPEN_AUDIO = "Open Audio File"
LABEL_SELECTED_FILE = "Selected File"
LABEL_TRANSCRIBE = "Transcribe"
LABEL_TRANSCRIPT = "Transcript"
LABEL_COPY = "Copy"
LABEL_SAVE_TRANSCRIPT = "Save Transcript"
LABEL_SOUND_PROMPT = "Describe the sound"
LABEL_DURATION = "Duration (seconds)"
LABEL_VOICE_DESCRIPTION = "Describe the voice"
LABEL_VOICE_NAME = "Name for new voice"
LABEL_DESIGN_VOICE = "Design Voice"
LABEL_RESULT = "Result"
LABEL_ADD_TO_VOICE_LIST = "Add to Voice List"
LABEL_SEARCH = "Search"
LABEL_USE_VOICE = "Use Voice"
LABEL_ADD_FILE = "Add File"
LABEL_ADD_DIRECTORY = "Add Directory"
LABEL_REMOVE_FILE = "Remove File"
LABEL_CLONE = "Clone"
LABEL_DELETE = "Delete"
LABEL_API_KEY = "API Key"
LABEL_DEFAULT_MODEL = "Default Model"
LABEL_DEFAULT_VOICE_ID = "Default Voice ID"
LABEL_DEFAULT_OUTPUT_FORMAT = "Default Output Format"
LABEL_OUTPUT_DIRECTORY = "Output Directory"
LABEL_BROWSE = "Browse"
LABEL_CANCEL = "Cancel"
LABEL_CLOSE = "Close"
LABEL_AUDIO_FILES = "Audio files"

MENU_FILE = "&File"
MENU_TOOLS = "&Tools"
MENU_SETTINGS = "&Settings"
MENU_HELP = "&Help"
MENU_SAVE_LAST_OUTPUT = "Save Last Output...\tCtrl+S"
MENU_OPEN_AUDIO_FILE = "Open Audio File...\tCtrl+O"
MENU_EXIT = "Exit\tAlt+F4"
MENU_VOICE_LIBRARY = "Voice Library..."
MENU_CLONE_VOICE = "Clone Voice..."
MENU_HISTORY = "Generation History..."
MENU_PRONUNCIATION = "Pronunciation Dictionaries..."
MENU_PREFERENCES = "Preferences..."
MENU_ABOUT = "About"

TITLE_VOICE_LIBRARY = "Voice Library"
TITLE_CLONE_VOICE = "Clone Voice"
TITLE_HISTORY = "Generation History"
TITLE_PRONUNCIATION = "Pronunciation Dictionaries"
TITLE_PREFERENCES = "Preferences"
TITLE_ABOUT = "About ElevenDesk"
TITLE_ERROR = "ElevenDesk Error"
TITLE_SUCCESS = "Success"
TITLE_SELECT_AUDIO = "Select an audio file"
TITLE_SELECT_AUDIO_DIRECTORY = "Select a directory containing audio files"
TITLE_SELECT_OUTPUT_DIRECTORY = "Select output directory"
TITLE_SAVE_AUDIO = "Save audio"
TITLE_SAVE_TRANSCRIPT = "Save transcript"

COLUMN_NAME = "Name"
COLUMN_CATEGORY = "Category"
COLUMN_DESCRIPTION = "Description"
COLUMN_DATE = "Date"
COLUMN_TYPE = "Type"
COLUMN_VOICE = "Voice"
COLUMN_MODEL = "Model"
COLUMN_PREVIEW = "Preview"
COLUMN_ID = "ID"
COLUMN_FILE = "File"
COLUMN_DURATION = "Duration"
COLUMN_FORMAT = "Format"
COLUMN_SAMPLE_RATE = "Sample Rate"
COLUMN_CHANNELS = "Channels"
COLUMN_SIZE = "Size"
COLUMN_PATH = "Path"

STATUS_READY = "Ready"
STATUS_LOADING_VOICES = "Loading voices..."
STATUS_GENERATING = "Generating audio..."
STATUS_GENERATED = "Audio generated."
STATUS_TRANSCRIBING = "Transcribing audio..."
STATUS_TRANSCRIBED = "Transcription complete."
STATUS_GENERATING_EFFECT = "Generating sound effect..."
STATUS_EFFECT_GENERATED = "Sound effect generated."
STATUS_DESIGNING_VOICE = "Designing voice..."
STATUS_VOICE_DESIGNED = "Voice designed."
STATUS_CLONING_VOICE = "Cloning voice..."
STATUS_PLAYING = "Playing audio."
STATUS_SAVED = "Saved: "
STATUS_COPIED = "Transcript copied."
STATUS_VOICES_REFRESHED = "Voice list refreshed."
STATUS_LOADING = "Loading..."
STATUS_AUDIO_FILES_ADDED_TEMPLATE = "Added {0} audio files; skipped {1} unreadable files."

ERROR_CONFIG_READ = "The settings file could not be read."
ERROR_CONFIG_WRITE = "The settings file could not be saved."
ERROR_API_KEY_REQUIRED = "Enter an ElevenLabs API key in Preferences."
ERROR_API_REQUEST = "The ElevenLabs request failed."
ERROR_LOAD_VOICES = "Voices could not be loaded."
ERROR_TEXT_REQUIRED = "Enter text to synthesize."
ERROR_VOICE_REQUIRED = "Select a voice."
ERROR_AUDIO_REQUIRED = "Select an audio file."
ERROR_PROMPT_REQUIRED = "Enter a sound description."
ERROR_VOICE_DESCRIPTION_REQUIRED = "Enter a voice description."
ERROR_VOICE_NAME_REQUIRED = "Enter a voice name."
ERROR_CLONE_FILES_REQUIRED = "Add at least one audio file before cloning."
ERROR_SELECTION_REQUIRED = "Select an item first."
ERROR_PLAYBACK = "Audio playback failed."
ERROR_SAVE = "The file could not be saved."
ERROR_CLIPBOARD = "The clipboard could not be opened."
ERROR_HISTORY_AUDIO = "Audio is not available for this history item."
ERROR_UNSUPPORTED_AUDIO = "The selected output format cannot be played."
ERROR_AUDIO_METADATA = "Audio metadata could not be read."
ERROR_SDK_RESPONSE = "The ElevenLabs SDK returned an unexpected response."
ERROR_DELETE_HISTORY = "The history item could not be deleted."

ABOUT_TEXT_TEMPLATE = "{0} version {1}\nAccessible desktop client for ElevenLabs."
VOICE_RESULT_TEMPLATE = "Name: {0}\nVoice ID: {1}"
VOICE_CHOICE_TEMPLATE = "{0} ({1})"
SLIDER_VALUE_TEMPLATE = "{0}: {1}"
SPEED_VALUE_TEMPLATE = "{0}: {1:.2f}"
SUCCESS_CLONE_TEMPLATE = "Voice cloned.\nVoice ID: {0}"
ERROR_DETAIL_TEMPLATE = "{0}\n\n{1}"

AUDIO_FILE_WILDCARD = "Audio files (*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.opus;*.aac;*.wma)|*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.opus;*.aac;*.wma|All files (*.*)|*.*"
MP3_FILE_WILDCARD = "MP3 audio (*.mp3)|*.mp3|All files (*.*)|*.*"
WAV_FILE_WILDCARD = "WAV audio (*.wav)|*.wav|All files (*.*)|*.*"
PCM_FILE_WILDCARD = "PCM audio (*.pcm)|*.pcm|All files (*.*)|*.*"
ULAW_FILE_WILDCARD = "u-law audio (*.ulaw)|*.ulaw|All files (*.*)|*.*"
BIN_FILE_WILDCARD = "Binary audio (*.bin)|*.bin|All files (*.*)|*.*"
TEXT_FILE_WILDCARD = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
DEFAULT_AUDIO_BASENAME = "elevendesk_audio"
DEFAULT_TRANSCRIPT_BASENAME = "elevendesk_transcript.txt"
EXTENSION_MP3 = ".mp3"
EXTENSION_WAV = ".wav"
EXTENSION_PCM = ".pcm"
EXTENSION_ULAW = ".ulaw"
EXTENSION_BIN = ".bin"
EXTENSION_TXT = ".txt"
OUTPUT_FILE_OPTIONS = {
	OUTPUT_MP3_44100_128: (EXTENSION_MP3, MP3_FILE_WILDCARD),
	OUTPUT_MP3_44100_192: (EXTENSION_MP3, MP3_FILE_WILDCARD),
	OUTPUT_PCM_44100: (EXTENSION_PCM, PCM_FILE_WILDCARD),
	OUTPUT_ULAW_8000: (EXTENSION_ULAW, ULAW_FILE_WILDCARD),
}
DEFAULT_OUTPUT_FILE_OPTION = (EXTENSION_BIN, BIN_FILE_WILDCARD)
AUDIO_FILE_EXTENSIONS = (
	".mp3",
	".wav",
	".m4a",
	".flac",
	".ogg",
	".opus",
	".aac",
	".wma",
)

API_ATTR_VOICES = "voices"
API_ATTR_MODELS = "models"
API_ATTR_GET_ALL = "get_all"
API_ATTR_GET = "get"
API_ATTR_TEXT_TO_SPEECH = "text_to_speech"
API_ATTR_CONVERT = "convert"
API_ATTR_SPEECH_TO_TEXT = "speech_to_text"
API_ATTR_SOUND_GENERATION = "text_to_sound_effects"
API_ATTR_VOICE_DESIGN = "text_to_voice"
API_ATTR_CREATE = "create"
API_ATTR_CREATE_PREVIEWS = "create_previews"
API_ATTR_PREVIEWS = "previews"
API_ATTR_VOICE_PREVIEW = "voice_preview"
API_ATTR_VOICE_DESIGN_CREATE = "create_voice_from_preview"
API_ATTR_ADD = "add"
API_ATTR_HISTORY = "history"
API_ATTR_DELETE = "delete"
API_ATTR_GET_AUDIO = "get_audio"
API_ATTR_PRONUNCIATION = "pronunciation_dictionaries"
API_ATTR_PRONUNCIATION_DICTIONARY = "pronunciation_dictionary"
API_ATTR_LIST = "list"
API_ATTR_DATA = "data"
API_ATTR_VOICE_ID = "voice_id"
API_ATTR_NAME = "name"
API_ATTR_CATEGORY = "category"
API_ATTR_DESCRIPTION = "description"
API_ATTR_MODELS = "models"
API_ATTR_MODEL_ID = "model_id"
API_ATTR_HISTORY_ITEMS = "history"
API_ATTR_DICTIONARIES = "pronunciation_dictionaries"
API_ATTR_ID = "id"
API_ATTR_DATE = "date_unix"
API_ATTR_TYPE = "source"
API_ATTR_VOICE_NAME = "voice_name"
API_ATTR_TEXT = "text"
API_ATTR_HISTORY_ITEM_ID = "history_item_id"

API_KW_TEXT = "text"
API_KW_VOICE_ID = "voice_id"
API_KW_MODEL_ID = "model_id"
API_KW_VOICE_SETTINGS = "voice_settings"
API_KW_OUTPUT_FORMAT = "output_format"
API_KW_FILE = "file"
API_KW_AUDIO = "audio"
API_KW_DURATION_SECONDS = "duration_seconds"
API_KW_PROMPT = "prompt"
API_KW_TEXT_DESCRIPTION = "text"
API_KW_VOICE_DESCRIPTION = "voice_description"
API_KW_VOICE_NAME = "voice_name"
API_KW_GENERATED_VOICE_ID = "generated_voice_id"
API_KW_NAME = "name"
API_KW_DESCRIPTION = "description"
API_KW_FILES = "files"
API_KW_PAGE_SIZE = "page_size"
API_KW_VOICE_PREVIEW_ID = "voice_preview_id"
API_KW_HISTORY_ITEM_ID = "history_item_id"
API_KEY_SIMILARITY_BOOST = "similarity_boost"
API_KEY_STABILITY = "stability"
API_KEY_STYLE = "style"
API_KEY_SPEED = "speed"

METHOD_SAVE_LAST_OUTPUT = "save_last_output"
METHOD_GET_LAST_OUTPUT = "get_last_output"

DEFAULT_API_KEY = EMPTY_TEXT
DEFAULT_VOICE_ID = EMPTY_TEXT
DEFAULT_MODEL = MODEL_MULTILINGUAL_V2
DEFAULT_OUTPUT_FORMAT = OUTPUT_MP3_44100_128
DEFAULT_OUTPUT_DIRECTORY_NAME = APP_NAME
DEFAULT_SETTINGS = {
	KEY_API_KEY: DEFAULT_API_KEY,
	KEY_DEFAULT_MODEL: DEFAULT_MODEL,
	KEY_DEFAULT_VOICE_ID: DEFAULT_VOICE_ID,
	KEY_DEFAULT_OUTPUT_FORMAT: DEFAULT_OUTPUT_FORMAT,
	KEY_OUTPUT_DIRECTORY: EMPTY_TEXT,
}

FRAME_SIZE = (900, 720)
DIALOG_SIZE = (760, 520)
SMALL_DIALOG_SIZE = (620, 440)
PANEL_BORDER = 12
CONTROL_GAP = 8
SECTION_GAP = 12
TEXT_MIN_HEIGHT = 180
RESULT_MIN_HEIGHT = 80
LIST_MIN_HEIGHT = 260
COLUMN_WIDTH_NAME = 180
COLUMN_WIDTH_CATEGORY = 130
COLUMN_WIDTH_DESCRIPTION = 360
COLUMN_WIDTH_DATE = 220
COLUMN_WIDTH_TYPE = 100
COLUMN_WIDTH_VOICE = 140
COLUMN_WIDTH_MODEL = 170
COLUMN_WIDTH_PREVIEW = 260
COLUMN_WIDTH_ID = 240
COLUMN_WIDTH_FILE = 180
COLUMN_WIDTH_DURATION = 100
COLUMN_WIDTH_FORMAT = 80
COLUMN_WIDTH_SAMPLE_RATE = 110
COLUMN_WIDTH_CHANNELS = 90
COLUMN_WIDTH_SIZE = 100
COLUMN_WIDTH_PATH = 360
SLIDER_MINIMUM = 0
SLIDER_MAXIMUM = 100
SLIDER_DEFAULT_STABILITY = 50
SLIDER_DEFAULT_SIMILARITY = 75
SLIDER_DEFAULT_STYLE = 0
SLIDER_SPEED_MINIMUM = 50
SLIDER_SPEED_MAXIMUM = 200
SLIDER_SPEED_DEFAULT = 100
SLIDER_SPEED_DIVISOR = 100.0
PERCENT_DIVISOR = 100.0
DURATION_MINIMUM = 0.5
DURATION_MAXIMUM = 22.0
DURATION_DEFAULT = 5.0
DURATION_INCREMENT = 0.5
SPIN_DIGITS = 1
PREVIEW_MAX_LENGTH = 80
HISTORY_PAGE_SIZE = 100
HISTORY_DATE_PREFIX_FORMAT = "%A, %B"
HISTORY_DATE_TEMPLATE = "{0} {1}, {2}"
FILE_DURATION_TEMPLATE = "{0:.2f} seconds"
FILE_SAMPLE_RATE_TEMPLATE = "{0} Hz"
FILE_SIZE_TEMPLATE = "{0:.2f} MB"
BYTES_PER_MEGABYTE = 1048576.0
AUDIO_SAMPLE_WIDTH = 2
PCM_SAMPLE_RATE = 44100
ULAW_SAMPLE_RATE = 8000
MONO_CHANNEL_COUNT = 1
FORMAT_MP3 = "mp3"
FORMAT_WAV = "wav"
OUTPUT_MP3_PREFIX = "mp3_"
PLAYBACK_POLL_SECONDS = 0.05
TEMP_AUDIO_PREFIX = "elevendesk_"
SOUNDOBJ_ATTR_LOADED = "_loaded"
SOUNDOBJ_FORMAT_POINTER = "ma_format*"
SOUNDOBJ_UINT_POINTER = "unsigned int*"
SOUNDOBJ_CHANNEL_MAP_CAPACITY = 0
ULAW_BYTE_MASK = 255
ULAW_SIGN_BIT = 128
ULAW_EXPONENT_SHIFT = 4
ULAW_EXPONENT_MASK = 7
ULAW_MANTISSA_MASK = 15
ULAW_MANTISSA_SHIFT = 3
ULAW_BIAS = 132
PCM_SAMPLE_PACK_FORMAT = "<h"
THREAD_DAEMON = True
FILE_DIALOG_MULTIPLE = 0
SIZER_PROPORTION_NONE = 0
SIZER_PROPORTION_EXPAND = 1
DEFAULT_SIZE_WIDTH = -1
FIRST_ITEM_INDEX = 0
INDEX_STEP = 1
COLUMN_INDEX_NAME = 0
COLUMN_INDEX_CATEGORY = 1
COLUMN_INDEX_DESCRIPTION = 2
COLUMN_INDEX_DATE = 0
COLUMN_INDEX_TYPE = 1
COLUMN_INDEX_VOICE = 2
COLUMN_INDEX_MODEL = 3
COLUMN_INDEX_PREVIEW = 4
COLUMN_INDEX_FILE = 0
COLUMN_INDEX_DURATION = 1
COLUMN_INDEX_FORMAT = 2
COLUMN_INDEX_SAMPLE_RATE = 3
COLUMN_INDEX_CHANNELS = 4
COLUMN_INDEX_SIZE = 5
COLUMN_INDEX_PATH = 6
