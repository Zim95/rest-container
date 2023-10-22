# Makefile for building and pushing Docker image

# Define the script files
BUILD_SCRIPT = ./scripts/build.sh
PUSH_SCRIPT = ./scripts/push.sh
DOCKERRUN_SCRIPT = ./scripts/docker-run.sh

# Export the variables using the script
build:
	@chmod +x $(BUILD_SCRIPT)
	@echo "Building Docker image..."
	@$(BUILD_SCRIPT)
push:
	@chmod +x $(PUSH_SCRIPT)
	@echo "Pushing Docker image to the repository..."
	@$(PUSH_SCRIPT)
dockerrun:
	@chmod +x $(DOCKERRUN_SCRIPT)
	@echo "Running Docker container"
	@$(DOCKERRUN_SCRIPT)

buildpush: build push
builddockerrun: build dockerrun
buildpushdockerrun: buildpush dockerrun

.PHONY: build push dockerrun buildpush builddockerrun buildpushdockerrun