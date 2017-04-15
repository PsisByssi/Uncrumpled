#!/bin/zsh

VERSION=$1
APP=$2
# LOWERAPP=${APP,,}
ARCH=$3

# get helper functions
wget -q https://github.com/probonopd/AppImages/raw/master/functions.sh -O ./functions.sh

# Source some helper functions
. ./functions.sh

# Finish the appimage
generate_appimage
