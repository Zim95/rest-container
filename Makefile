# Makefile for building and pushing Docker image

# Define the script files
EXPORT_SCRIPT = $(CURDIR)/scripts/exports.sh
BUILD_SCRIPT = $(CURDIR)/scripts/build.sh
PUSH_SCRIPT = $(CURDIR)/scripts/push.sh

# Export the variables using the script
export_variables:
	@chmod +x $(EXPORT_SCRIPT)
	@echo "Exporting variables..."
	@$(EXPORT_SCRIPT)
build:
  	$(eval $(shell $(MAKE) export_variables))
	@chmod +x $(BUILD_SCRIPT)
	@echo "Building Docker image..."
	@$(BUILD_SCRIPT)
push:
	$(eval $(shell $(MAKE) export_variables))
	@chmod +x $(PUSH_SCRIPT)
	@echo "Pushing Docker image to the repository..."
	@$(PUSH_SCRIPT)

buildpush: build push

.PHONY: export_variables build push buildpush