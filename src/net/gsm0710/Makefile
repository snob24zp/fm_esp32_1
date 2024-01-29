# Location of top-level MicroPython directory
MPY_DIR = $(shell realpath ~/wrk/dlab/micropython)

# Name of module
MOD = gsm0710

# Source files (.c or .py)
SRC = mpy.c gsm0710.c buffer.c

# Architecture to build for (x86, x64, armv6m, armv7m, xtensa, xtensawin)
ARCH ?= x64

# Include to get the rules for compiling and linking the module
include $(MPY_DIR)/py/dynruntime.mk