#!/bin/bash

CONFIG_FILE="config.json"

USE_CUSTOM_KEYSTORE=false
KS_PASSWORD=""

for arg in "$@"; do
    case $arg in
        --use-custom-keystore)
            USE_CUSTOM_KEYSTORE=true
            ;;
        --ks-password=*)
            KS_PASSWORD="${arg#*=}"
            ;;
        *)
            ;;
    esac
done

if [[ "$USE_CUSTOM_KEYSTORE" == true && -z "$KS_PASSWORD" ]]; then
    echo "Error: --ks-password must be provided with --use-custom-keystore"
    exit 1
fi

KEYSTORE_NAME=$(jq -r '.keystore.name' "$CONFIG_FILE")
KEYSTORE_ALIAS=$(jq -r '.keystore.alias' "$CONFIG_FILE")

readarray -t APPS < <(jq -r '.bulk_patch_apps[]' "$CONFIG_FILE")

for app in "${APPS[@]}"; do
    echo "Patching app: $app"
    if [ "$USE_CUSTOM_KEYSTORE" = true ]; then
        python3 src/patch.py "$app" \
            --keystore-path keystore/"$KEYSTORE_NAME".p12 \
            --keystore-password "$KS_PASSWORD" \
            --keystore-alias "$KEYSTORE_ALIAS" 
    else
        python3 src/patch.py "$app"
    fi
done
