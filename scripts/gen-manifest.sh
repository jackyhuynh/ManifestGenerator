#!/bin/bash

MANIFESTS_DIR="manifests"
VALUES_DIR="values"

if [[ ! -d "${MANIFESTS_DIR}" && ! -d "${VALUES_DIR}" ]]; then
    # Make an allowance for people running this from the scripts directory
    if [[ -d "../${MANIFESTS_DIR}" && -d "../${VALUES_DIR}" ]]; then
        cd ../
    else
        echo "[-] This script should be run from the top level of this repository"
        exit 1
    fi
fi

# connect to the upstream Helm repository
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# Pull the default values and store them for reference
CHARTS=("base" "istiod" "gateway")

mkdir -p "${VALUES_DIR}/default"
for chart in "${CHARTS[@]}"
do
    helm show values "istio/${chart}" > "${VALUES_DIR}/default/${chart}-default-values.yaml"
done

# Generate the final manifests
for dir in $(ls "${VALUES_DIR}")
do
    # Don't worry about generating a default manifest
    if [[ "${dir}" == "default" ]]
    then
        continue
    fi

    # Make sure we have a spot to put the generated manifest
    mkdir -p "${MANIFESTS_DIR}/${dir}"

    for chart in "${CHARTS[@]}"
    do
        echo "[*] Generating ${MANIFESTS_DIR}/${dir}/${chart}.yaml"
        UNIQUE_VALUES=""
        if [[ -f "${VALUES_DIR}/${dir}/${chart}-values.yaml" ]]
        then
            UNIQUE_VALUES="-f ${VALUES_DIR}/${dir}/${chart}-values.yaml"
        fi

        EXTRA_INSTALL_VALUES=""
        if [[ "${chart}" == "base" ]]
        then
            EXTRA_INSTALL_VALUES="--include-crds --create-namespace"
        fi

        echo "helm template istio istio/${chart} ${EXTRA_INSTALL_VALUES} ${UNIQUE_VALUES} > ${MANIFESTS_DIR}/${dir}/${chart}.yaml"
        helm template istio "istio/${chart}" "${EXTRA_INSTALL_VALUES}" "${UNIQUE_VALUES}" > "${MANIFESTS_DIR}/${dir}/${chart}.yaml"
    done
done