# Usage:
#   make [IMPL=fir] test   - C-simulation
#   make [IMPL=fir] hls    - HLS synthesis
#   make [IMPL=fir]        - test + hls
#   make clean

IMPL   ?= fir
SRC    := src
HDRS   := $(wildcard $(SRC)/*.h)
TB     := $(SRC)/fir_test.cpp

# Tool discovery
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

test: $(SRC)/$(IMPL).cpp $(TB) $(HDRS)
	$(CXX) $(CXXFLAGS) $< $(TB) -o $(IMPL).bin
	./$(IMPL).bin > $(IMPL)_csim.log 2>&1
	@grep -q "PASS" $(IMPL)_csim.log \
	  && echo "[PASS] $(IMPL)" \
	  || { echo "[FAIL] $(IMPL) - see $(IMPL)_csim.log"; exit 1; }

check-hls-tools:
ifeq ($(strip $(VITIS_RUN)),)
	$(error vitis-run not found - source Xilinx tools first)
endif

hls: check-hls-tools $(SRC)/$(IMPL).cpp $(HDRS)
	sed 's/__IMPL__/$(IMPL)/g' script/syn.tcl > /tmp/$(IMPL)_syn.tcl
	$(VITIS_RUN) --mode hls --tcl /tmp/$(IMPL)_syn.tcl
	@rm -f /tmp/$(IMPL)_syn.tcl

clean:
	rm -rf *.bin *.log *.comp .Xil vitis_hls.log hls_component out.dat
