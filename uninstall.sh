#!/bin/bash

RECONO_TOOLS="$HOME/.config/recono-suite/recono-tools" 
for FILE in "$RECONO_TOOLS"/*.sh; do
    if [ -f "$FILE" ]; then
        FILENAME=$(basename -- "$FILE")
        MODIFIED_FILENAME="${FILENAME%.sh}"
        rm -f "$HOME/.local/bin/$MODIFIED_FILENAME"
    fi
done

rm -rf "$HOME/.config/recono-suite"

echo "💣💥 recono-suite has been uninstalled"