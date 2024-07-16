
# Fitness Boxing feat. Hatsune Miku Savedata Patcher

Script that unlocks various progresses within the Fitness Boxing feat. Hatsune Miku for Nintendo Switch.

The savedata format should be shared across all variants of the game. Tested on Japanese (010045D01AFC8800) and Asian (010026801E0AC000) releases.

Requirements
- Python 3
- Existing savedata for the game (dump via JKSV or Switch emulator of your choice); should be something named `all.dat`

## Usage/Examples

```
usage: main.py [-h] [-e] [-i] [-m] [-c] [-a] input

positional arguments:
  input

options:
  -h, --help            show this help message and exit
  -e, --unlock-achievements
                        Unlocks all achievements.
  -i, --unlock-instructors
                        Unlocks all instructors.
  -m, --unlock-music    Unlocks all music.
  -c, --unlock-costumes
                        Unlocks all costumes.
  -a, --unlock-all      Unlocks everything.
```

## Technical Explanation

The savedata (`all.dat`) is compressed using gzip and can be uncompressed.

The uncompressed savedata is comprised of the following structure
- Header (`18 00 00 00 35 00 00 00`)
- Offsets
    - Offset to player profile JSON
    - Offset to player stats JSON
    - Offset to unlock status JSON
- Savedata size
- Concatenated JSON
    - System profile
    - Player profile
    - Player stats
    - Unlock status

Each of the JSON contains raw array structures for various progress types, and each array member does not have an associated name - meaning you'll just have to blindly guess which property relates to what item in-game. In the case of our script, it flips every false it finds under `isPurchased` and `isUnlocked` into true, thereby triggering the unlock status.
