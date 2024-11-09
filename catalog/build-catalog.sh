set -e
python3 catalog.py ../barcode-database.csv --artwork artwork --update-csv

echo "Generated catalog.pdf :)"
