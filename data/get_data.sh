#!/usr/bin/env bash
set -euo pipefail

# This script downloads ADS-B state vector data from the OpenSky Network.
# Use of this data is subject to the OpenSky Network
# General Terms of Use & Data License Agreement.
# See data/LICENSE_OPENSKY.txt for details.

URL="https://s3.opensky-network.org/data-samples/states/2022-06-27/15/states_2022-06-27-15.csv.tar"
TAR_FILE="states_2022-06-27-15.csv.tar"
GZ_FILE="states_2022-06-27-15.csv.gz"
CSV_FILE="states_2022-06-27-15.csv"

FILTER_SCRIPT="filter.py"

echo "Downloading OpenSky state vectors..."
curl -L -o "$TAR_FILE" "$URL"

echo "Extracting TAR archive..."
tar -xf "$TAR_FILE"

echo "Decompressing CSV..."
gunzip "$GZ_FILE"

echo "Cleaning up archives..."
rm "$TAR_FILE"

echo "Running filter script..."
python "$FILTER_SCRIPT"

echo "Done."
