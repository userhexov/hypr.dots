#!/bin/bash

# Toggle theme control window
current_state=$(eww get themectlrev)

if [ "$current_state" == "true" ]; then
    eww update themectlrev=false
else
    eww update themectlrev=true
fi
