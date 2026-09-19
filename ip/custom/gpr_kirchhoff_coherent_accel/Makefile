ROOT := $(abspath ../../..)
include $(ROOT)/config.mk
IP_OUT := $(CURDIR)/gpr_kirchhoff_coherent_accel_hls/solution1/impl/ip
DEST := $(IP_REPO)/gpr_kirchhoff_coherent_accel
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
	rm -rf gpr_kirchhoff_coherent_accel_hls vitis_hls.log
