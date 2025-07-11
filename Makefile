NAME := alfred-coin-ticker
WORKFLOW_FILENAME := $(NAME).alfredworkflow
VERSION_FILE := version
TARGET_FILES := $(shell cat include.list)
VENV := ./.venv/bin

# must use system python
PYTHON := /usr/bin/python3

default: clean build

.PHONY: install-tools
install-tools:
	npm install -g commit-and-tag-version

.PHONY: .venv
.venv:
	uv sync --python $(PYTHON)

.PHONY: build
build: $(WORKFLOW_FILENAME)

requirements.txt:
	uv pip compile pyproject.toml -o requirements.txt

%/.site-packages:
	$(PYTHON) -m pip install \
		--prefer-binary \
		--upgrade \
		--target=$@ \
		${PACKAGES}

deps: requirements.txt
deps: PACKAGES=-r requirements.txt
deps: build/.site-packages
deps: $(TARGET_FILES)

$(WORKFLOW_FILENAME): deps
	@echo "> Packaging..."
	rm -f $(WORKFLOW_FILENAME)
	BUILD_DIR=$(BUILD_DIR) WORKFLOW_FILENAME=$(WORKFLOW_FILENAME) ./build.sh

.PHONY: test
test:
	python -m unittest discover -s tests -v

.PHONY: lint
lint:
	$(VENV)/ruff check tests api.py main.py utils.py

.PHONY: lint-fix
lint-fix:
	$(VENV)/ruff check --fix tests api.py main.py utils.py

.PHONY: format
format:
# sort imports
	$(VENV)/ruff check --select I --fix tests api.py main.py utils.py
# format code
	$(VENV)/ruff format --diff tests api.py main.py utils.py || true
	$(VENV)/ruff format tests api.py main.py utils.py

install: $(WORKFLOW_FILENAME)
	open $(WORKFLOW_FILENAME)

.PHONY: clean
clean:
	rm -rf \
		requirements.txt \
		./build/ \
		.mypy_cache/ \
		$(WORKFLOW_FILENAME)

.PHONY: bump_version
bump_version:
	@if [ -z $(version) ]; then \
		echo Usage: make bump_version version=1.0.0; \
		exit 1; \
	fi;
	@echo Current version: $(shell cat $(VERSION_FILE))
	@(read -e -p "Bump to version $(version)? [y/N]: " ans && case "$$ans" in [yY]) true;; *) false;; esac)
	@echo $(version) > version
	@sed -i.bak 's#<string>[0-9]*.[0-9]*.[0-9]*</string>#<string>$(version)</string>#' info.plist

.PHONY: release
release:
	@commit-and-tag-version -a -s

.PHONY: release-major
release-major:
	@commit-and-tag-version -a -s --release-as major

.PHONY: release-minor
release-minor:
	@commit-and-tag-version -a -s --release-as minor

.PHONY: release-patch
release-patch:
	@commit-and-tag-version -a -s --release-as patch

.PHONY: release-github
release-github: VERSION=$(shell cat $(VERSION_FILE))
release-github:
	@(read -e -p "Create Github release version $(VERSION)? [y/N]: " ans && case "$$ans" in [yY]) true;; *) false;; esac)
	gh release create $(VERSION) $(WORKFLOW_FILENAME)

EXECUTABLES = $(PYTHON) plutil open rsync uv
K := $(foreach exec,$(EXECUTABLES),\
        $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))
