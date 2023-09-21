#!/bin/bash

# Build timer_api image
source ./timer_api/.cicd/project.properties
echo "Build $IMAGE_NAME:$VERSION Image"

docker build --tag $IMAGE_NAME:$VERSION ./timer_api/.
# Build timer_controller image
source ./timer_controller/.cicd/project.properties
echo "Build $IMAGE_NAME:$VERSION Image"

docker build --tag $IMAGE_NAME:$VERSION ./timer_controller/.

