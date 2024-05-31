#!/bin/bash

load_src() {
    source /etc/bashrc.bashrc
    source ~/.bashrc
    source /etc/profile
    source ~/.bash_profile
    source ~/.profile
    source "$1"
}

load_src "$SCALPEL_VENV_ACTIVATE" 2>/dev/null
