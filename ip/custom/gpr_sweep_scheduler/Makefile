ROOT := $(abspath ../../..)
include $(ROOT)/config.mk
IP_OUT := $(CURDIR)/gpr_sweep_scheduler_hls/solution1/impl/ip
DEST := $(IP_REPO)/gpr_sweep_scheduler
.PHONY: all hls install clean
all: hls install
hls:
	$(VITIS_HLS) -f build_hls.tcl
install: hls
	@test -f "$(IP_OUT)/component.xml" || { echo "Missing HLS export $(IP_OUT)/component.xml"; exit 2; }
	rm -rf "$(DEST)"
	mkdir -p "$(DEST)"
	cp -a "$(IP_OUT)/." "$(DEST)/"
clean:
	rm -rf gpr_sweep_scheduler_hls vitis_hls.log
