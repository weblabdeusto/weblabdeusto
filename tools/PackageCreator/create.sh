#!/bin/bash

#
# Current version
# 
VERSION="3.9.0"

# 
# Set up this revision number or we'll retrieve the last one from the SVN 
# 
REVISION=""

# 
# In WebLab 3.9, the different zip files were:
# 
#  - weblab_3.9.zip:            8 MB
#  - weblab-with-libs_3.9.zip: 57 MB  
#  - weblab-windows_3.9.zip:   51 MB  
#  - weblab-linux_3.9.zip:     41 MB  
#  - weblab-macosx_3.9.zip:    41 MB  
# 
# So we finally only provide the first two files (there is not such a huge difference
# between weblab-with-libs_3.9.zip and weblab-linux_3.9.zip -just 16 MB-)
# 
VERSION_PER_OS=false

# 
# SVN path
# 
SVN_PATH="http://weblabdeusto.googlecode.com/svn/trunk/weblab/"

if [ "$REVISION" == "" ] ; then
    REVISION=$(svn info --xml 2> /dev/null |grep revision|head -1|cut -d\" -f2)
fi

if [ "$REVISION" == "" -o "$REVISION" == "0" ] ; then
    REVISION_ARG=""
else
    REVISION_ARG="-r $REVISION"
fi

# 
# Create the packages directory
# 
rm -rf packages
mkdir packages
cd packages

echo -n "Creating source only zip file..."

# 
# Download the project, without .svn folders, without libs
# 
svn export --ignore-externals $REVISION_ARG $SVN_PATH weblab > /dev/null

# 
# Zip it
zip -r weblabdeusto_$VERSION.zip weblab > /dev/null
echo "[done]"

# 
# Remove the folder and download it again, but with libs this time
#
rm -rf weblab

echo -n "Creating zip file with libs..."

svn export $REVISION_ARG $SVN_PATH weblab > /dev/null

# 
# Zip the with-libs version
# 
zip -r weblabdeusto-with-libs_$VERSION.zip weblab > /dev/null
echo "[done]"

if $VERSION_PER_OS; then

    # 
    # Copy it to three different folders:
    #   - weblab_windows
    #   - weblab_linux
    #   - weblab_macosx
    # 
    rm -rf weblab_windows weblab_linux weblab_macosx
    cp -R weblab weblab_windows
    cp -R weblab weblab_linux
    mv weblab weblab_macosx

    #
    # For each folder, rename it as weblab, remove all the not required
    # libraries for that OS, zip it and remove the folder.
    # 
    mv weblab_windows weblab
    rm -rf weblab/server/lib/{darwin,linux2}
    zip -r weblabdeusto-windows_$VERSION.zip weblab > /dev/null
    rm -rf weblab

    mv weblab_linux weblab
    rm -rf weblab/server/lib/{darwin,win32}
    zip -r weblabdeusto-linux_$VERSION.zip weblab > /dev/null
    rm -rf weblab

    mv weblab_macosx weblab
    rm -rf weblab/server/lib/{linux2,win32}
    zip -r weblabdeusto-macosx_$VERSION.zip weblab > /dev/null
    rm -rf weblab
else
    rm -rf weblab
fi

