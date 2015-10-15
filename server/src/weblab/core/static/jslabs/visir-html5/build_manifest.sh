#!/bin/sh

MANIFEST="visir.appcache"

echo "CACHE MANIFEST" > $MANIFEST
echo "#" `date -u`>> $MANIFEST
#date -u >> $MANIFEST

echo "CACHE:" >> $MANIFEST

#find -X . -name "*.js" | sed "s/\.\///" >> $MANIFEST
find -X . -name "*.css" -or -name "*.tpl" | sed "s/\.\///" >> $MANIFEST
find -X . -name "*.png" -or -name "*.jpg" | sed "s/\.\///" >> $MANIFEST

echo "NETWORK:" >> $MANIFEST
echo "*" >> $MANIFEST
