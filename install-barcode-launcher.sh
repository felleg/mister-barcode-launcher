

BARCODE_LAUNCHER_DIR=/media/fat/Scripts/barcode-launcher
UPDATE_DATABASE_SCRIPT=/media/fat/Scripts/update_barcode_database.sh
USER_STARTUP_SCRIPT=/media/fat/linux/user-startup.sh
UNINSTALL_SCRIPT=/media/fat/Scripts/uninstall-barcode-launcher.sh

echo "
################################################################
Files for barcode launcher will be installed in $BARCODE_LAUNCHER_DIR

Cleaning up any previous installation of $BARCODE_LAUNCHER_DIR
################################################################
"
$UNINSTALL_SCRIPT

echo "
################################################################
# Installing MiSTer Batch Control (mbc) in /media/fat/Scripts/barcode-launcher
# This program is required to tell the MiSTer which game to launch.
################################################################
"
 wget -N -P $BARCODE_LAUNCHER_DIR https://github.com/pocomane/MiSTer_Batch_Control/releases/latest/download/mbc

echo "
################################################################
# Downloading the latest version of the barcode-launcher code
################################################################
"
 wget -N -P $BARCODE_LAUNCHER_DIR https://raw.githubusercontent.com/felleg/mister-barcode-launcher/refs/heads/main/barcode_launcher.py

echo "
################################################################
# Downloading the latest version of the barcode database
################################################################
"
 wget -N -P $BARCODE_LAUNCHER_DIR https://raw.githubusercontent.com/felleg/mister-barcode-launcher/refs/heads/main/barcode-database.csv

echo "
################################################################
# Creating a script ($UPDATE_DATABASE_SCRIPT)
################################################################
"
echo " wget -N -P $BARCODE_LAUNCHER_DIR https://raw.githubusercontent.com/felleg/mister-barcode-launcher/refs/heads/main/barcode-database.csv" > $UPDATE_DATABASE_SCRIPT

echo "
################################################################
# Adding barcode-launcher as a startup script
################################################################
"

if ! grep -q "$BARCODE_LAUNCHER_DIR/barcode_launcher.py" $USER_STARTUP_SCRIPT; then
  cat <<EOF >> $USER_STARTUP_SCRIPT
[[ -e $BARCODE_LAUNCHER_DIR/barcode_launcher.py ]] && tmux new-session -d -s barcode-launcher 'for rawhid in {0..3}; do python3 $BARCODE_LAUNCHER_DIR/barcode_launcher.py $BARCODE_LAUNCHER_DIR/barcode-database.csv \$rawhid & done; wait'
EOF
fi

echo "
################################################################
# Creating uninstall script ($UNINSTALL_SCRIPT)
################################################################
"
cat <<EOF > $UNINSTALL_SCRIPT
# Removing barcode-launcher from startup scripts
sed -i "/barcode-launcher/d" $USER_STARTUP_SCRIPT

# Remove $BARCODE_LAUNCHER_DIR
rm -r $BARCODE_LAUNCHER_DIR
EOF

echo "
################################################################
# DONE! Type reboot for changes to take effect.
#
# !FRIENDLY REMINDER! This setup will only work if your ROMs are
# organized following the standard pattern set by HTGDB.
# For your convenience, you will find maintained packs on archive.org.
# Google is your friend.
#
# Barcodes are available at https://felx.cc/barcodes
#
# Enjoy barcode-launcher :)
################################################################
"
