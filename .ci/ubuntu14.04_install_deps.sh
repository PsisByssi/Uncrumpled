#!/usr/bin/env bash

# Install all ubuntu deps required for uncrumpled

######
# Kivy
######
sudo apt-get install -y \
    build-essential \
    git \
    python3-dev \
    libav-tools \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev

#####
# Fzf
#####
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
git checkout a5862d4b9cc5f57ef83174c0d714bfb485094a4f # PINNED
~/.fzf/install --bin # generate binary only
export PATH="$HOME/.fzf/bin:$PATH"

#####
# Xdotool
#####
sudo apt-get install -y xdotool

#####
# XCB for system hotkeys
#####
sudo apt-get install libxcb-render0-dev

