#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT" || exit 1

input_required() {
  local value prompt="$1" default="$2"
  while true; do
    if [[ -n "$default" ]]; then
      read -p "$prompt [$default]: " value
      if [[ -n "$value" ]]; then
        echo "$value"
        break
      else
        echo "$default"
        break
      fi
    else
      read -p "$prompt: " value
      if [[ -n "$value" ]]; then
        echo "$value"
        break
      else
        echo "This field is required, enter a value."
      fi
    fi
  done
}


KEYSTORE_NAME=$(input_required "Keystore name (e.g. mykeystore)" "mykeystore")
KEYSTORE_PASSWORD=$(input_required "Keystore password (must be at least 6 characters)")
KEYSTORE_ALIAS=$(input_required "Keystore alias (e.g. key0)" "key0")
# KEYSTORE_ALIAS_PASSWORD=$(input_required "Alias password")
DNAME=$(input_required "Distinguished Name (e.g. CN=Android,O=Test,C=US)" "CN=Luniume,O=Luniume")


KEYSTORE_PATH="$PROJECT_ROOT/keystore/$KEYSTORE_NAME.p12"

echo "Creating PKCS keystore..."
keytool -genkeypair \
  -alias "$KEYSTORE_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -keystore "$KEYSTORE_PATH" \
  -storetype PKCS12 \
  -storepass "$KEYSTORE_PASSWORD" \
  -dname "$DNAME"

if [[ $? -ne 0 ]]; then
  echo "Failed to create keystore."
  exit 1
fi

echo "Keystore created at $KEYSTORE_PATH"

BC_URL="https://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk18on/1.81/bcprov-jdk18on-1.81.jar"
BC_JAR="$PROJECT_ROOT/bcprov-jdk15on.jar"
echo "Downloading Bouncy Castle provider..."
curl -L "$BC_URL" -o "$BC_JAR"
if [[ $? -ne 0 ]]; then
  echo "Failed to download Bouncy Castle jar."
  exit 1
fi

BKS_PATH="$PROJECT_ROOT/keystore/${KEYSTORE_NAME}.bks"
echo "Converting to Revanced compatible keystore (BKS)..."
keytool -importkeystore \
  -srckeystore "$KEYSTORE_PATH" \
  -srcstoretype JKS \
  -srcstorepass "$KEYSTORE_PASSWORD" \
  -srcalias "$KEYSTORE_ALIAS" \
  -destkeystore "$BKS_PATH" \
  -deststoretype BKS \
  -deststorepass "$KEYSTORE_PASSWORD" \
  -destalias "$KEYSTORE_ALIAS" \
  -provider org.bouncycastle.jce.provider.BouncyCastleProvider \
  -providerpath "$BC_JAR"

if [[ $? -ne 0 ]]; then
  echo "Failed to convert to Revanced keystore."
  rm -f "$BC_JAR"
  exit 1
fi

echo "Revanced keystore created at $BKS_PATH"

rm -f "$BC_JAR"
