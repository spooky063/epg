PHONY: build run

build:
	docker build \
		-t json-creator-from-xml \
		--build-arg INPUT=https://xmltvfr.fr/xmltv/xmltv_tnt.xml.gz \
		--build-arg OUTPUT=output.json \
		.

run:
	docker run -it --rm json-creator-from-xml

up:
	docker-compose up