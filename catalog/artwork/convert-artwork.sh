for i in *.jpg *.jpeg *.png; do convert $i -resize 200x200 $i; done
