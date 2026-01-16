# CoreMark benchmark preparation

REPO_DIR = repo
CODE_DIR = code

# Files to copy from repo/
COREMARK_SOURCES = \
	core_list_join.c \
	core_matrix.c \
	core_state.c \
	core_util.c

COREMARK_HEADERS = \
	coremark.h

prepare:
	@echo "Preparing CoreMark code..."
	@mkdir -p $(CODE_DIR)
	@for file in $(COREMARK_SOURCES) $(COREMARK_HEADERS); do \
		if [ -f $(REPO_DIR)/$$file ]; then \
			cp $(REPO_DIR)/$$file $(CODE_DIR)/; \
			echo "  Copied $$file"; \
		else \
			echo "  ERROR: $$file not found"; \
			exit 1; \
		fi \
	done
	@echo "CoreMark code ready!"

clean:
	@echo "Cleaning prepared code..."
	@rm -rf $(CODE_DIR)

clone:
	@if [ ! -d $(REPO_DIR)/.git ]; then \
		git clone https://github.com/eembc/coremark.git $(REPO_DIR); \
	else \
		cd $(REPO_DIR) && git pull; \
	fi

setup: clean clone prepare

.PHONY: prepare clean clone setup