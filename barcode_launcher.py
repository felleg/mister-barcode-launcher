#!/usr/bin/env python3
"""
Launch a MiSTer FPGA game from a barcode
"""

__author__ = "Felix Leger"
__version__ = "0.1.0"
__license__ = "MIT"

import os
import sys
import csv
import subprocess

# The game folder mapping to handle variations in core names
GAMES_PATH = {
    "ARCADE": "/media/fat/_Arcade/",
    "GAMEBOY": "/media/fat/games/GameBoy/",
    "GAMEBOY.COL": "/media/fat/games/GameBoy/",
    "GBA": "/media/fat/games/GBA",
    "GENESIS": "/media/fat/games/Genesis/",
    "NEOGEO": "/media/fat/games/NEOGEO/",
    "NES": "/media/fat/games/NES/",
    "PSX": "/media/fat/games/PSX/",
    "SATURN": "/media/fat/games/SATURN",
    "SMS": "/media/fat/games/SMS/Master System/",
    "SMS.GG": "/media/fat/games/SMS/Game Gear/",
    "SNES": "/media/fat/games/SNES/",
    "TGFX16": "/media/fat/games/TGFX16/",
    "TGFX16-CD": "/media/fat/games/TGFX16-CD/",
    "WONDERSWAN.COL": "/media/fat/games/WonderSwan",
    "S32X": "/media/fat/games/S32X",
    "MEGACD": "/media/fat/games/MegaCD",
}

def hex_to_string(hex_string):
    """Convert hex string to a barcode number."""
    hex_map = {
        "1e": "1", "1f": "2", "20": "3", "21": "4",
        "22": "5", "23": "6", "24": "7", "25": "8",
        "26": "9", "27": "0"
    }

    digits = []
    for i in range(0, len(hex_string), 2):
        hex_code = hex_string[i:i+2].lower()
        if hex_code in hex_map:
            digits.append(hex_map[hex_code])
        else:
            print(f"Warning: Unrecognized hex code '{hex_code}'")
    return ''.join(digits)

def load_game(game, RAWHID):
    path = os.path.join(GAMES_PATH[game['CORE'].upper()], game['GAME_PATH'])
    cmd = f"/media/fat/Scripts/barcode_launcher/mbc load_rom {game['CORE'].upper()} \"{path}\""
    print("[INFO", RAWHID, "]: Launch game via", cmd)
    #subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    subprocess.run(cmd, shell=True, check=True)

def load_game_database(filename):
    """Load the game database from a CSV file."""
    game_db = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            barcode = row['BARCODE']
            game_db[barcode] = row
    return game_db

def main():
    """Main loop: reads hex from /dev/hidraw0, decodes it, and launches game."""
    GAME_DB_FILENAME = sys.argv[1]
    RAWHID = sys.argv[2]
    print("SCANNER STANDING BY! rawhid"+RAWHID)

    # Open the device file for reading barcode data
    with open("/dev/hidraw"+RAWHID, "rb") as f:
        line = ""
        byte = f.read(1)

        while byte != b"":
            byte = f.read(1)
            if byte != b"\x00":
                s = byte.hex()
                if s == "28":  # Newline/Enter, meaning barcode scan is complete
                    barcode = hex_to_string(line)
                    print(f"Scanned Barcode: {barcode}")

                    # Load game database
                    game_db = load_game_database(GAME_DB_FILENAME)

                    # Search the barcode in the loaded game database
                    found = game_db.get(barcode)

                    if found:
                        load_game(found, RAWHID)
                    else:
                        # Retry by removing leading zeroes
                        found = game_db.get(barcode.lstrip("0"))
                        if found:
                            load_game(found, RAWHID)
                        else:
                            print("No matching game for", barcode)
                    line = ""
                else:
                    line += s

if __name__ == "__main__":
    """Executed when run from the command line"""
    main()

