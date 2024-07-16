import argparse
from io import BytesIO

from pathlib import Path
import gzip
import struct
import json
import os
import shutil


def set_array_values_to_true(array: list) -> list:
    return [True if not val else val for val in array]


def process_file(input_path: Path, unlock_achievement: bool, unlock_instructors: bool, unlock_music: bool, unlock_costumes: bool, unlock_all: bool):
    if unlock_all:
        unlock_instructors, unlock_achievement, unlock_music, unlock_costumes = True
    decompressed = gzip.decompress(input_path.read_bytes())
    # with open(f"{input_path.resolve()}.decompressed", "wb") as f:
    #     f.write(decompressed)
    with BytesIO(decompressed) as buffer:
        header = buffer.read(8)
        json_profile_offset = buffer.read(4)
        unpacked_json_profile_offset = struct.unpack(
            "<I", json_profile_offset)[0]
        json_stats_offset = buffer.read(4)
        unpacked_json_stats_offset = struct.unpack("<I", json_stats_offset)[0]
        json_unlock_status_offset = buffer.read(4)
        unpacked_json_unlock_status_offset = struct.unpack(
            "<I", json_unlock_status_offset)[0]
        save_data_size = buffer.read(4)
        save_data_size = struct.unpack("<I", save_data_size)[0]

        json_system = decompressed[buffer.tell():unpacked_json_profile_offset]
        json_profile = decompressed[unpacked_json_profile_offset:unpacked_json_stats_offset]
        json_stats = decompressed[unpacked_json_stats_offset:
                                  unpacked_json_unlock_status_offset]
        json_unlock = decompressed[unpacked_json_unlock_status_offset:]

        parsed_json_unlock = json.loads(json_unlock)
        if unlock_achievement:
            parsed_json_unlock['achievement']['isCompleted'] = set_array_values_to_true(
                parsed_json_unlock['achievement']['isCompleted'])
        if unlock_music:
            parsed_json_unlock['music']['isUnlocked'] = set_array_values_to_true(
                parsed_json_unlock['music']['isUnlocked'])
            parsed_json_unlock['music']['isPurchased'] = set_array_values_to_true(
                parsed_json_unlock['music']['isPurchased'])
        if unlock_instructors:
            parsed_json_unlock['instructor']['isUnlocked'] = set_array_values_to_true(
                parsed_json_unlock['instructor']['isUnlocked'])
            parsed_json_unlock['instructor']['isPurchased'] = set_array_values_to_true(
                parsed_json_unlock['instructor']['isPurchased'])
        if unlock_costumes:
            costumes = parsed_json_unlock['instructor']['costumes']
            i = 0
            for _ in costumes:
                current_costume = costumes[i]
                current_costume['isUnlocked'] = set_array_values_to_true(
                    current_costume['isUnlocked'])
                current_costume['isPurchased'] = set_array_values_to_true(
                    current_costume['isPurchased'])
                i += 1
            parsed_json_unlock['instructor']['costumes'] = costumes
        json_unlock = json.dumps(
            parsed_json_unlock, separators=(',', ':')).encode()

    modified_buffer_len = len(header + json_profile_offset + json_stats_offset +
                              json_unlock_status_offset + json_system + json_profile + json_stats + json_unlock) + 4
    modified_buffer_len = struct.pack("<I", modified_buffer_len)
    modified_buffer = header + json_profile_offset + json_stats_offset + json_unlock_status_offset + \
        modified_buffer_len + json_system + json_profile + json_stats + json_unlock
    compressed_buffer = gzip.compress(modified_buffer)

    full_path = input_path.resolve()
    shutil.copy(full_path, f"{full_path}.bak")
    with open(full_path, "wb") as f:
        f.write(compressed_buffer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to the savedata (e.g., C:\\all.dat).")
    parser.add_argument("-e", "--unlock-achievements",
                        action="store_true", help="Unlocks all achievements.")
    parser.add_argument("-i", "--unlock-instructors",
                        action="store_true", help="Unlocks all instructors.")
    parser.add_argument("-m", "--unlock-music",
                        action="store_true", help="Unlocks all music.")
    parser.add_argument("-c", "--unlock-costumes",
                        action="store_true", help="Unlocks all costumes.")
    parser.add_argument("-a", "--unlock-all",
                        action="store_true", help="Unlocks everything.")
    args = parser.parse_args()
    parsed_path = Path(args.input)
    if not parsed_path.exists():
        raise FileNotFoundError(f"File {args.input} not found.")
    process_file(parsed_path, unlock_achievement=args.unlock_achievements,
                 unlock_costumes=args.unlock_costumes, unlock_instructors=args.unlock_instructors, unlock_music=args.unlock_music, unlock_all=args.unlock_all)


if __name__ == '__main__':
    main()
