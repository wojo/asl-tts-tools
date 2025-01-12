"""Constants for ASL TTS tools."""

# Exit codes
EXIT_CODES = {
    "SUCCESS": 0,
    "INVALID_ARGS": 1,
    "NO_MATCHES": 2,
    "AUDIO_PROCESSING_ERROR": 3,
    "CONFIG_ERROR": 4,
    "FILE_ERROR": 5,
}

# Maps special characters to letter sounds (letters/X.ulaw)
CHAR_TO_LETTER_MAP = {
    "=": "equals",
    "*": "asterisk",  # could also be digits/star
    '"': "ascii34",
    "?": "ascii63",
    #';': 'ascii59',    # pause character
    #'.': 'dot',        # pause character
    "`": "ascii96",
    "|": "ascii124",
    "&": "ascii38",
    #'-': 'dash',       # silent character
    "'": "ascii39",
    #'}': 'ascii125',   # exact filename match escape character
    #':': 'ascii58',    # pause character
    ">": "ascii62",
    #',': 'ascii44',    # pause character
    "+": "plus",
    #' ': 'space',      # ignored by tokenizer
    #'[': 'ascii91',    # exact filename match escape character
    #'{': 'ascii123',   # phonetic character sequence escape character
    "\\": "ascii92",
    "!": "exclaimation-point",
    #']': 'ascii93',    # phonetic character sequence escape character
    "$": "ascii36",
    "/": "slash",
    "@": "at",
    ")": "ascii41",
    "~": "ascii126",
    "^": "ascii94",
    "_": "ascii95",
    "(": "ascii40",
    "%": "ascii37",
    "<": "ascii60",
}

# Maps special characters to digit sounds (digits/X.ulaw)
CHAR_TO_DIGIT_MAP = {
    "#": "pound",
    #'*': 'star'        # could also be letters/asterisk
}

# Special characters that map to silence
PAUSE_CHARS = {",", ".", ";", ":", "-"}
