SHELL := /bin/bash

devel:
	uv sync --dev

version:
	@if [ "$(filter $(TYPE),major minor patch)" = "" ]; then \
		echo "Usage: make version TYPE=major|minor|patch"; \
		exit 1; \
	fi
	@current_version=$$(git tag -l | sort -V | tail -n1 | sed 's/^v//' || echo "0.0.0"); \
	IFS='.' read -ra version_parts <<< "$$current_version"; \
	major=$${version_parts[0]:-0}; \
	minor=$${version_parts[1]:-0}; \
	patch=$${version_parts[2]:-0}; \
	case "$(TYPE)" in \
		major) new_version=$$((major + 1)).0.0 ;; \
		minor) new_version=$$major.$$((minor + 1)).0 ;; \
		patch) new_version=$$major.$$minor.$$((patch + 1)) ;; \
	esac; \
	git tag -a $$new_version -m "Version $$new_version"; \
	echo "Created new tag: $$new_version" 