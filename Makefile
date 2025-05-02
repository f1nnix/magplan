SHELL := /bin/bash

devel:
	uv sync --dev

bump-version:
	@if [ "$(filter $(TYPE),major minor patch)" = "" ]; then \
		echo "Usage: make bump-version TYPE=major|minor|patch"; \
		exit 1; \
	fi
	@current_version=$$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	IFS='.' read -ra version_parts <<< "$$current_version"; \
	major=$${version_parts[0]:-0}; \
	minor=$${version_parts[1]:-0}; \
	patch=$${version_parts[2]:-0}; \
	case "$(TYPE)" in \
		major) new_version=$$((major + 1)).0.0 ;; \
		minor) new_version=$$major.$$((minor + 1)).0 ;; \
		patch) new_version=$$major.$$minor.$$((patch + 1)) ;; \
	esac; \
	sed -i '' "s/version = \".*\"/version = \"$$new_version\"/" pyproject.toml; \
	echo "Updated version in pyproject.toml to: $$new_version"

create-tag:
	@version=$$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	git tag -a $$version -m "Version $$version"; \
	echo "Created git tag: $$version" 