
all: reflect
	cd ../games && make
	cd ../scipy && make

.PHONY: reflect
reflect:
	pwiz.py -v chess > reflection.py
