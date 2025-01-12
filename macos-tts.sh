#!/bin/bash
# This is mostly for local testing on macOS to simulate `asl-tts` functionality
# It uses the `say` command to generate an AIFF file and then converts it to ulaw format

usage() {
    echo "Usage: $0 -t \"text\" -f output_filename"
    exit 1
}

TEXT=""
FILENAME=""

while getopts "t:f:n:" opt; do
    case $opt in
        t) TEXT="$OPTARG" ;;
        f) FILENAME="$OPTARG.ul" ;;
        n) ;; # Ignore node parameter
        *) usage ;;
    esac
done

if [ -z "$TEXT" ] || [ -z "$FILENAME" ]; then
    usage
fi

TEMP_AIFF=$(mktemp).aiff
say -r 150 "$TEXT" -o "$TEMP_AIFF"
sox "$TEMP_AIFF" -t ul -r 8000 -c 1 "$FILENAME"
rm "$TEMP_AIFF"