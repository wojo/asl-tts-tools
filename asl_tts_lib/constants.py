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
    "1st": "h-1",
    "2nd": "h-2",
    "3rd": "h-3",
    "4th": "h-4",
    "5th": "h-5",
    "6th": "h-6",
    "7th": "h-7",
    "8th": "h-8",
    "9th": "h-9",
    "10th": "h-10",
    "11th": "h-11",
    "12th": "h-12",
    "13th": "h-13",
    "14th": "h-14",
    "15th": "h-15",
    "16th": "h-16",
    "17th": "h-17",
    "18th": "h-18",
    "19th": "h-19",
    "20th": "h-20",
    "30th": "h-30",
    "40th": "h-40",
    "50th": "h-50",
    "60th": "h-60",
    "70th": "h-70",
    "80th": "h-80",
    "90th": "h-90",
    "100th": "h-hundred",
    "hundredth": "h-hundred",
    "thousandth": "h-thousand",
    "millionth": "h-million",
    "january": "mon-0",
    "february": "mon-1",
    "march": "mon-2",
    "april": "mon-3",
    "may": "mon-4",
    "june": "mon-5",
    "july": "mon-6",
    "august": "mon-7",
    "september": "mon-8",
    "october": "mon-9",
    "november": "mon-10",
    "december": "mon-11",
    "sunday": "day-0",
    "monday": "day-1",
    "tuesday": "day-2",
    "wednesday": "day-3",
    "thursday": "day-4",
    "friday": "day-5",
    "saturday": "day-6",
    "pm": "p-m",
    "am": "a-m",
}

# Special characters that map to silence
PAUSE_CHARS = {",", ".", ";", ":", "-"}
