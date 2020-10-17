#!/usr/bin/env sh

# Expects:
# 1. docker to be on PATH and runnable
# 2. User running this script to be logged into the docker repository (if they are pushing)
# 3. date program (expected to be compatible with GNU date)
# 4. realpath

set -e

usage() {
    echo "$0 [TAGS...]"
    echo
    echo "Builds locust Docker image with repository specified by the LOCUST_DOCKER_REPOSITORY environment variable."
    echo "If LOCUST_DOCKER_REPOSITORY is not specified, builds bugout/locust image."
    echo "If LOCUST_DOCKER_PUSH=true, pushes the tags to the specified repository."
    echo
    echo "Always pushes with a date tag constructed with: date -u +%Y%m%d-%H%M"
    echo "You can pass additional tags as arguments to this script."
}

if [ "${1}" = "-h" ] || [ "${1}" = "--help" ]
then
    usage
    exit 2
fi

LOCUST_DOCKER_REPOSITORY="${LOCUST_DOCKER_REPOSITORY:-bugout/locust}"

DATE_TAG="t-$(date -u +%Y%m%d-%H%M)"
LOCUST_DOCKER_TAG="$LOCUST_DOCKER_REPOSITORY:$DATE_TAG"
SCRIPT_DIR=$(realpath "$(dirname "$0")")
LOCUST_DIR=$(dirname "$SCRIPT_DIR")

docker build -t "$LOCUST_DOCKER_TAG" -f "$SCRIPT_DIR/Dockerfile" "$LOCUST_DIR"

for tag in "$@"
do
    docker tag "$LOCUST_DOCKER_TAG" "$LOCUST_DOCKER_REPOSITORY:$tag"
done

if [ "$LOCUST_DOCKER_PUSH" = "true" ]
then
    docker push "$LOCUST_DOCKER_TAG"
    for tag in "$@"
    do
        docker push "$LOCUST_DOCKER_REPOSITORY:$tag"
    done
fi
