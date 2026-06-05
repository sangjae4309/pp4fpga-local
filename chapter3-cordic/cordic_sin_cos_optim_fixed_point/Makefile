# Usage:
#   make test
#   make hls
#   make
#   make clean

TOP    := cordic
SRC    := src
HDRS   := $(wildcard $(SRC)/*.h)
TB     := $(SRC)/$(TOP)_test.cpp
SRCS   := $(SRC)/$(TOP).cpp

VITIS_RUN     := $(shell command -v vitis-run 2>/dev/null)
VITIS_HLS_BIN := $(shell command -v vitis_hls  2>/dev/null)
XILINX_HLS    ?= $(patsubst %/bin/vitis_hls,%,$(VITIS_HLS_BIN))
XILINX_VITIS  ?= $(patsubst %/bin/vitis-run,%,$(VITIS_RUN))
XILINX_INCLUDE := $(firstword $(wildcard $(XILINX_HLS)/include $(XILINX_VITIS)/include))

CXX      := g++
CXXFLAGS := -I$(SRC) -g
ifneq ($(strip $(XILINX_INCLUDE)),)
  CXXFLAGS += -I$(XILINX_INCLUDE)
endif
export LD_LIBRARY_PATH := /usr/lib/x86_64-linux-gnu:$(LD_LIBRARY_PATH)

.PHONY: all test hls check-hls-tools clean

all: test hls

test: $(SRCS) $(TB) $(HDRS)
	$(CXX) $(CXXFLAGS) $(SRCS) $(TB) -o $(TOP).bin
	./$(TOP).bin > $(TOP)_csim.log 2>&1
	@grep -q "PASS" $(TOP)_csim.log \
	  && echo "[PASS] $(TOP)" \
	  || { echo "[FAIL] $(TOP) - see $(TOP)_csim.log"; exit 1; }

check-hls-tools:
ifeq ($(strip $(VITIS_RUN)),)
	$(error vitis-run not found - source Xilinx tools first)
endif

hls: check-hls-tools $(SRCS) $(HDRS)
	$(VITIS_RUN) --mode hls --tcl script/syn.tcl

clean:
	rm -rf *.bin *.log *.comp .Xil vitis_hls.log hls_component out.dat *.jou
