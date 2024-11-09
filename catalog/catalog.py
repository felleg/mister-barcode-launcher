#!/usr/bin/env python3
"""
Generate a PDF of games with their matching barcode
"""

__author__ = "Felix Leger"
__version__ = "0.1.0"
__license__ = "MIT"

import os
import sys
import barcode
import argparse
from barcode.writer import ImageWriter
import subprocess
import pandas as pd
import datetime

CUSTOM_BARCODE_COUNTER = 1

def GenCustomBarcode(barcode_list):
  """
  Generate a custom barcode based on global counter.
  Each time this function is called, the global counter increases by
  1.

  Params:
  -------
  barcodes (list):
    List of barcodes against which we will check the generated barcode.
    The returned barcode value cannot be in this list.

  Returns:
  --------

  custom_barcode (str):
    UPC-A valid barcode.
  """
  global CUSTOM_BARCODE_COUNTER
  retry_counter = 0
  while retry_counter < 1000000:
    # Counter is on the left of the barcode, and the check digit
    # will appear on the right.
    custom_barcode = (str(CUSTOM_BARCODE_COUNTER) + "0000000000")[0:11]
    # Calculate the check digit
    # (https://en.wikipedia.org/wiki/Universal_Product_Code#Check_digit_calculation)
    odd_sum = int(custom_barcode[0]) + \
      int(custom_barcode[2]) + \
      int(custom_barcode[4]) + \
      int(custom_barcode[6]) + \
      int(custom_barcode[8]) + \
      int(custom_barcode[10])
    even_sum = int(custom_barcode[1]) + \
      int(custom_barcode[3]) + \
      int(custom_barcode[5]) + \
      int(custom_barcode[7]) + \
      int(custom_barcode[9])
    modulo = (3 * odd_sum + even_sum) % 10
    if modulo == 0:
      custom_barcode += str(modulo)
    else:
      custom_barcode += str(10 - modulo)
    CUSTOM_BARCODE_COUNTER = CUSTOM_BARCODE_COUNTER + 1

    if custom_barcode not in list(barcode_list):
      return custom_barcode
    retry_counter += 1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("game_database_csv", help="The filename of the csv game database")
  parser.add_argument("--output_pdf", help="The filename of the output pdf to generate", default="catalog.pdf")
  parser.add_argument("--artwork", help="Path to artwork folder", default="artwork")
  parser.add_argument("--barcodes", help="Path to output barcode images", default="barcodes")
  parser.add_argument("--update-csv",
      help="If set, will add custom barcode values in game_database_csv",
      action="store_true",
      dest="save_custom_barcodes_to_csv")
  args = parser.parse_args()
  ARTWORK_FOLDER = args.artwork
  BARCODE_FOLDER = args.barcodes
  GAME_CSV = args.game_database_csv
  OUTPUT_PDF = args.output_pdf
  output_md = "." + OUTPUT_PDF.split(".")[0] + ".md"

  df = pd.read_csv(GAME_CSV, dtype=str, keep_default_na=False)

  # Generate barcode for games with no barcode specified
  for index, row in df.iterrows():
    if row.BARCODE == "":
      df.loc[index, "BARCODE"] = GenCustomBarcode(df.BARCODE)

  df.loc[df["CATEGORY"] == "", "CATEGORY"] = "Other"

  if args.save_custom_barcodes_to_csv is True:
    df.to_csv(GAME_CSV, index=False)

  # Cleanup previous output file
  if os.path.exists(output_md):
    os.remove(output_md)
  # Start writing new output file
  with open(output_md, "w") as f:
    # Write import for latex style
    f.write("---\n")
    f.write("header-includes: |\n")
    f.write("    \\usepackage{felix-gamelist}\n")
    f.write("    \\usepackage{soul}\n")
    f.write("---\n")
    f.write("\\title{Félix's MiSTer Games}\n")
    f.write("\\date{" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "}\n")
    f.write("\\maketitle\n")
    f.write("\\tableofcontents\n")
    f.write("\\newpage\n")

  for category in df.CATEGORY.sort_values().unique():
    with open(output_md, "a") as f:
      f.write(f"# \\Huge {category}\n\n")
      f.write("Game Name | Image | Barcode | Year\n")
      f.write(":---|:--:|:--:|:-:\n")

      subdf = df[df.CATEGORY == category].copy()

      # Extract game names from game path (to allow sorting in catalog
      # by game name)
      for index, row in subdf.iterrows():
        if row.GAME_NAME == "":
          subdf.loc[index, "GAME_NAME"] = os.path.splitext(os.path.basename(row.GAME_PATH))[0]
      subdf.sort_values(by="GAME_NAME", inplace=True)

      # Loop over games inside a category
      for index, row in subdf.iterrows():
        artwork_path = "![]("+ARTWORK_FOLDER+"/"+row.ARTWORK_PATH+"){ height=80px }" if len(row.ARTWORK_PATH) > 0 else ""
        barcode_path = ""
        if len(row.BARCODE) < 12:
          # In case the stupid csv edit program removed leading 0's
          row.BARCODE = row.BARCODE.zfill(12)

        if len(row.BARCODE) == 12:
          barcode_gen = barcode.get_barcode_class('upca')
          barcode_path = barcode_gen(row.BARCODE,
              writer=ImageWriter()).save(os.path.join(BARCODE_FOLDER,
                row.BARCODE))
        elif len(row.BARCODE) == 13:
          barcode_gen = barcode.get_barcode_class('ean13')
          barcode_path = barcode_gen(row.BARCODE,
              writer=ImageWriter()).save(os.path.join(BARCODE_FOLDER,
                row.BARCODE))

        game_name = os.path.splitext(os.path.basename(row.GAME_PATH))[0] if len(row.GAME_NAME) == 0 else row.GAME_NAME
        if len(row.HIGHLIGHT) > 0:
          game_name = "\\hl{\\textbf{"+game_name+"}}"
        f.write(game_name + "|" + \
            artwork_path + "|" + \
            "![]("+barcode_path+"){ width=150px } |" + \
            row.YEAR + "\n")
      f.write("\n")
  result = subprocess.run(["pandoc", "-s", "--columns=10", "-o", OUTPUT_PDF, output_md])
  sys.exit(result.returncode)



if __name__ == "__main__":
    main()
