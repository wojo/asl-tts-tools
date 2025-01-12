# ASL TTS Tools

A collection of text-to-speech tools for AllStarLink that provide playback through Asterisk's local audio system.

## Requirements

- Python 3.7+
- PyYAML
- sox
- ASL Text-to-Speech ([docs](https://allstarlink.github.io/adv-topics/tts/), [GitHub](https://github.com/AllStarLink/asl3-tts))

## Installation

1. Update your system:
```bash
sudo apt update && sudo apt upgrade
```

2. Install required packages:
```bash
sudo apt install python3-yaml asl3-tts
```

#### Configuration
Default config location: `/etc/asl-tts-tools/config.yaml`

Example configuration:
```yaml
# Directories
sounds_directory: /usr/share/asterisk/sounds/en
custom_sounds_directory: /usr/share/asterisk/sounds/custom 
cache_directory: /usr/share/asterisk/sounds/custom/cache

# Sound handling
on_missing: error # error, beep or skip
beep_sound: beeperr
silence_sound: silence/1

# TTS settings
auto_generate_words: true
asl_tts_bin: asl-tts

# Cache settings
max_cache_files: 100
max_cache_age_days: -1 # -1 means no limit
```

## Installation

1. Copy scripts to your preferred location (e.g., `/usr/local/asl-tts-tools/`)
2. Make scripts executable:
   ```bash
   chmod +x asl-tts-concat.py asl-tts-wrapper.py
   ```
3. Create configuration directory:
   ```bash
   mkdir -p /etc/asl-tts-tools
   ```
4. Create basic configuration:
   ```bash
   cp config.yaml.example /etc/asl-tts-tools/config.yaml
   ```

## Tools Included

### asl-tts-concat.py

A simple concatenative TTS system that combines Asterisk sound files to create speech output. It uses existing sound files and can handle phonetic pronunciations.

The primary goal of this is to be fast. Where full TTS with `asl-tts` takes 6-7s on a Pi 3B, this is done in 500ms.

#### Features
- Fast, but does not support true TTS -- only supports and combines existing Asterisk sound files
  - However, you can create custom sound files and they will be utilized for words or phrases
- Automatic TTS generation for unknown words (when enabled)
- Supports forced phonetic pronunciation, direct file references and phrases to be specified as a single unit
- Can output to file or play directly through Asterisk
- Intelligent phrase matching that tries to find the longest possible matches first

#### Usage
```bash
./asl-tts-concat.py "Text to speak" [options]
```

Options:
- `-n NODE`: Node number for playback (required for direct playback)
- `-f FILE`: Output file to save the audio
- `-c CONFIG`: Path to config file (default: /etc/asl-tts-tools/config.yaml)
- `-v`: Enable verbose output (-v for verbose, -vv for very verbose)
- `-g`: Enable auto-generation of TTS for missing words

#### Token Processing
The script processes text in the following order:

1. Text is first tokenized into individual words and special syntax
2. For each token or group of tokens:
   - Try to match the longest possible phrase first
   - Try exact matches for bracketed tokens (e.g. {word})
   - Try phonetic matches for square-bracketed tokens (e.g. [ABC])
   - Try uppercase words as individual letters (e.g. DMR -> D M R)
   - Try digit sequences (e.g. 123 -> one two three)
   - Try punctuation/special characters
   - Try mixed alphanumeric as individual characters
   - If enabled, generate TTS for unknown words
3. All matched sounds are concatenated into the final output

#### Special Syntax 
- `[W0JO]`: Uses phonetic pronunciation for letters/numbers (e.g. [W0JO] -> "whiskey zero juliet oscar")
- `{word}`: Forces exact match of word/path in the sounds directory (e.g. {rpt/connected-to})
- `,`, `.`, `;`, `:`, `-`: Adds a brief pause
- Hyphenated words (e.g. "connected-to") are treated as phrases and matched accordingly
- `(phrase here)`: Forces a full phrase to be considered in both matching but also passed to TTS if enabled

#### Configuration
The behavior for missing words with TTS and other sounds can be configured:
```yaml
on_missing: error  # Raise an error if word not found
on_missing: beep   # Play a beep sound
on_missing: skip   # Skip the word silently

beep_sound: beep
silence_sound: silence/1

auto_generate_words: true  # Enable TTS generation for missing words
```

#### Examples

Basic usage:
```bash
./asl-tts-concat.py "Node 123 connected"
```

Using phonetic pronunciation and exact matches:
```bash
./asl-tts-concat.py "[W0JO] {rpt/connected-to} repeater"
```

With verbose output to see token processing, adding more will increase verbosity:
```bash
./asl-tts-concat.py "Node 123 connected" -v
```

Using auto-generation for missing words:
```bash
./asl-tts-concat.py "Specialized vocabulary here" -g
```

Crazy example:
```bash
 ./asl-tts-concat.py -c config.yaml "ABC ## - #-## -- abc / ! * connected-to Something-new (this is a phrase) dmr d-star AllStar D-Star connected to testing 123456, [W0JO], A1 B2 {rpt/connected-to} 123456" -g -v -f test
Configuration:
  sounds_directory: /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en
  custom_sounds_directory: /Users/robert/Documents/GitHub/asl-tts-tools/sounds/custom
  cache_directory: /Users/robert/Documents/GitHub/asl-tts-tools/sounds/cache
  beep_sound: beeperr
  silence_sound: silence/1
  auto_generate_words: True
  on_missing: beep
  asl_tts_bin: /Users/robert/Documents/GitHub/asl-tts-tools/macos-tts.sh
  max_cache_files: 10
  max_cache_age_days: 1
Loading sounds from directory: /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en
Loaded 636 sound files from /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en
Loading sounds from directory: /Users/robert/Documents/GitHub/asl-tts-tools/sounds/custom
Loaded 0 sound files from /Users/robert/Documents/GitHub/asl-tts-tools/sounds/custom
Warning: Normalized phrase sorry already exists in mapping at /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/sorry.ulaw, skipping /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/followme/sorry.ulaw
Warning: Normalized phrase pls hold while try already exists in mapping at /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/pls-hold-while-try.ulaw, skipping /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/followme/pls-hold-while-try.ulaw
Warning: Normalized phrase seconds already exists in mapping at /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/seconds.ulaw, skipping /Users/robert/Documents/GitHub/asl-tts-tools/sounds/en/rpt/seconds.ulaw
Text: ABC ## - #-## -- abc / ! * connected-to Something-new (this is a phrase) dmr d-star AllStar D-Star connected to testing 123456, [W0JO], A1 B2 {rpt/connected-to} 123456
Initial tokens: ['ABC', '#', '#', '-', '#', '-', '#', '#', '-', 'abc', '/', '!', '*', 'connected-to', 'Something-new', '(this is a phrase)', 'dmr', 'd-star', 'AllStar', 'D-Star', 'connected', 'to', 'testing', '123456', ',', '[W0JO]', ',', 'A1', 'B2', '{rpt/connected-to}', '123456']
Found letter match: A -> letters/a
Found letter match: B -> letters/b
Found letter match: C -> letters/c
Found digit sound match for '#' -> digits/pound
Found digit sound match for '#' -> digits/pound
Using silence sound for '-' -> silence/1
Found digit sound match for '#' -> digits/pound
Using silence sound for '-' -> silence/1
Found digit sound match for '#' -> digits/pound
Found digit sound match for '#' -> digits/pound
Using silence sound for '-' -> silence/1
Generated TTS file for word: abc
Found letter sound match for '/' -> letters/slash
Found letter sound match for '!' -> letters/exclaimation-point
Found letter sound match for '*' -> letters/asterisk
Generated TTS file for word: connected-to
Generated TTS file for word: Something-new
Generated TTS file for word: this is a phrase
Generated TTS file for word: dmr
Generated TTS file for word: d-star
Generated TTS file for word: AllStar
Found existing TTS file for word: D-Star
Generated TTS file for word: connected
Generated TTS file for word: to
Generated TTS file for word: testing
Found digit match: 1 -> digits/1
Found digit match: 2 -> digits/2
Found digit match: 3 -> digits/3
Found digit match: 4 -> digits/4
Found digit match: 5 -> digits/5
Found digit match: 6 -> digits/6
Using silence sound for ',' -> silence/1
Found phonetic match: W -> phonetic/w_p
Found phonetic match: 0 -> digits/0
Found phonetic match: J -> phonetic/j_p
Found phonetic match: O -> phonetic/o_p
Using silence sound for ',' -> silence/1
Found char match: A -> letters/a
Found char match: 1 -> digits/1
Found char match: B -> letters/b
Found char match: 2 -> digits/2
Found exact match for '{rpt/connected-to}' -> connected to
Found digit match: 1 -> digits/1
Found digit match: 2 -> digits/2
Found digit match: 3 -> digits/3
Found digit match: 4 -> digits/4
Found digit match: 5 -> digits/5
Found digit match: 6 -> digits/6
```

### asl-tts-wrapper.py

A wrapper script that provides more advanced TTS functionality using external services with caching.

#### Features
- Caches generated audio files as initial generation can take many seconds
- Configurable cache size and management
- Integration with Asterisk playback
- Ability to save to a file manually

#### Usage
```bash
./asl-tts-wrapper.py "Text to speak" -n <node_number> [options]
```

Options:
- `-n NODE`: Node number for playback
- `-c CONFIG`: Path to config file (default: /etc/asl-tts-tools/config.yaml)
- `-f FILE`: Output file to save the audio instead of playing
- `-v`: Enable verbose output

## Tips and Tricks
1. For best phonetic pronunciation, use `[A]` style notation for individual letters
2. Use braces `{word}` to force exact matches
3. Add commas or periods for natural pauses
4. The simple TTS works best with existing Asterisk sound files
5. Use the wrapper for more complex text-to-speech needs

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
