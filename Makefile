.PHONY: help get-urls download clean convert format test install

# Default variables
URLS_FILE ?= urls.txt
OUTPUT_DIR ?= downloads
CONCURRENCY ?= 4
TITLE ?= "Wattpad Story"
AUTHOR ?= "Unknown"
COVER ?= cover.png
INPUT_DIR ?= downloads

help:
	@echo "Wattpad EPUB Downloader Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make get-urls URL=\"API_URL\" FROM=1 TO=10 [URLS_FILE=urls.txt]"
	@echo "  make download [URLS_FILE=urls.txt] [OUTPUT_DIR=downloads] [CONCURRENCY=4]"
	@echo "  make clean [OUTPUT_DIR=downloads]"
	@echo "  make convert [TITLE=\"Story Title\"] [AUTHOR=\"Author Name\"] [COVER=cover.png] [INPUT_DIR=downloads] [OUTPUT_FILE=path/to/epub]"
	@echo "  make format"
	@echo "  make test"
	@echo "  make install"

install:
	pip install -r requirements.txt
	playwright install chromium

get-urls:
	@chmod +x ./bin/get-urls.sh
	./bin/get-urls.sh "$(URL)" "$(FROM)" "$(TO)" "$(URLS_FILE)"

download:
	@chmod +x ./bin/download.sh
	./bin/download.sh "$(URLS_FILE)" "$(OUTPUT_DIR)" "$(CONCURRENCY)"

clean:
	@chmod +x ./bin/clean.sh
	./bin/clean.sh "$(OUTPUT_DIR)"

convert:
	@chmod +x ./bin/convert.sh
	./bin/convert.sh "$(TITLE)" "$(AUTHOR)" "$(COVER)" "$(INPUT_DIR)" "$(OUTPUT_FILE)"

format:
	@chmod +x ./bin/format.sh
	./bin/format.sh

test:
	@chmod +x ./bin/test.sh
	./bin/test.sh
