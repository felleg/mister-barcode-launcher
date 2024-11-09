# Catalog

These files are used to generate a catalog of barcodes. It can
conveniently printed or viewed from a browser.

To manually generate the catalog.pdf, perform these commands:

1. From `mister-barcode-launcher/catalog`, run `docker build -t catalog .`
1. From `mister-barcode-launcher/`, run `docker run -it -v
   $(pwd):/catalog --rm --entrypoint=bash catalog
    - Then, do `cd catalog/catalog && ./build-catalog.sh
    - Then, exit

You should find `catalog.pdf` waiting for you right here
(`mister-barcode-launcher/catalog`)!
