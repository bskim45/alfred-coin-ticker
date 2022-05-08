NAME := alfred-coin-ticker
WORKFLOW_FILENAME := $(NAME).alfredworkflow
VERSION_FILE := version
TARGET_FILES := $(shell cat include.list)

# must use system python
PYTHON := /usr/bin/python3

default: clean build

.PHONY: .venv
.venv:
	poetry env use $(PYTHON)
	poetry install

.PHONY: build
build: $(WORKFLOW_FILENAME)

requirements.txt:
	poetry export --without-hashes > requirements.txt

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
	@potry version $(version)
	@sed -i.bak 's#<string>[0-9]*.[0-9]*.[0-9]*</string>#<string>$(version)</string>#' info.plist

.PHONY: release
release:
	@standard-version -a -s -t ""

.PHONY: release-major
release-major:
	@standard-version -a -s -t "" --release-as major

.PHONY: release-minor
release-minor:
	@standard-version -a -s -t "" --release-as minor

.PHONY: release-patch
release-patch:
	@standard-version -a -s -t "" --release-as patch

EXECUTABLES = $(PYTHON) plutil open rsync poetry
K := $(foreach exec,$(EXECUTABLES),\
        $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))
