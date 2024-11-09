set -e
python3 catalog.py ../barcode_database.csv --artwork artwork --update-csv

echo "Generated catalog.pdf :)"
