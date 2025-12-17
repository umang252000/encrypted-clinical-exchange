#!/bin/bash
# Usage: bash swap_key_to_kms.sh hospital_a

HOSP=$1
if [ -z "$HOSP" ]; then
  echo "Specify hospital folder (hospital_a or hospital_b)"
  exit 1
fi

BASE_DIR="$(dirname "$0")/.."
SRC="${BASE_DIR}/${HOSP}/keys"
KMS_DIR="${BASE_DIR}/${HOSP}/kms"

KEY_FILE="${HOSP}.key"

if [ ! -f "${SRC}/${KEY_FILE}" ]; then
  echo "Key file not found: ${SRC}/${KEY_FILE}"
  exit 1
fi

mkdir -p "$KMS_DIR"
cp "${SRC}/${KEY_FILE}" "${KMS_DIR}/${KEY_FILE}"
rm -f "${SRC}/${KEY_FILE}"

echo "✔ Key moved to ${KMS_DIR}/${KEY_FILE}"
echo "✔ Now set KEY_MODE=kms and KMS_KEY_PATH=/keys_kms/${KEY_FILE}"