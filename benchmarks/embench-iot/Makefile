# Embench benchmark preparation

REPO_DIR = repo
CODE_DIR = code
SRC_DIR = $(CODE_DIR)/src

SOURCES = \
	aha-mont64/mont64.c \
	crc32/crc_32.c \
	cubic/libcubic.c \
	cubic/basicmath_small.c \
	cubic/pi.h \
	cubic/snipmath.h \
	cubic/sniptype.h \
	edn/libedn.c \
	huffbench/libhuffbench.c \
	matmult-int/matmult-int.c \
	md5sum/md5.c \
	minver/libminver.c \
	nbody/nbody.c \
	nettle-aes/nettle-aes.c \
	nettle-sha256/nettle-sha256.c \
	nsichneu/libnsichneu.c \
	picojpeg/libpicojpeg.c \
	picojpeg/picojpeg.h \
	picojpeg/picojpeg_test.c \
	primecount/primecount.c \
	qrduino/qrencode.c \
	qrduino/qrencode.h \
	qrduino/qrframe.c \
	qrduino/qrtest.c \
	qrduino/qrbits.h \
	qrduino/ecctable.h \
	sglib-combined/combined.c \
	sglib-combined/sglib.h \
	slre/libslre.c \
	slre/slre.h \
	st/libst.c \
	statemate/libstatemate.c \
	ud/libud.c \
	wikisort/libwikisort.c

prepare:
	@echo "Preparing Embench sources..."
	@mkdir -p $(SRC_DIR)
	@for src in $(SOURCES); do \
		if [ -f $(REPO_DIR)/src/$$src ]; then \
			cp $(REPO_DIR)/src/$$src $(SRC_DIR)/$$(basename $$src); \
			echo "  Copied $$src to src/"; \
		else \
			echo "  ERROR: $$src not found"; \
			exit 1; \
		fi \
	done
	@cp $(REPO_DIR)/support/beebsc.c $(CODE_DIR)/
	# REMOVE THIS LINE: @cp $(REPO_DIR)/support/dummy-libm.c $(CODE_DIR)/
	@echo "Embench sources ready!"

clean:
	@echo "Cleaning prepared code..."
	@rm -rf $(CODE_DIR)

clone:
	@if [ ! -d $(REPO_DIR)/.git ]; then \
		git clone https://github.com/embench/embench-iot.git $(REPO_DIR); \
	else \
		cd $(REPO_DIR) && git pull; \
	fi

setup: clean clone prepare

.PHONY: prepare clean clone setup