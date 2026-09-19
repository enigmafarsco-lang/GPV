SHELL := /bin/bash
.DEFAULT_GOAL := help
include config.mk

STAMP_DIR := $(BUILD)/.stamps
LOG_DIR := $(BUILD)/logs

STAGES := \
 step00_preflight \
 step02_hls_scheduler \
 step03_hls_rxextract \
 step04_hls_sweepavg \
 step05_hls_cal \
 step06_hls_pad \
 step07_hls_background \
 step08_hls_power \
 step09_hls_cfar1d \
 step10_hls_imaging \
 step11_collect_ip \
 step12_vivado_project \
 step13_vivado_integrate \
 step14_vivado_validate \
 step15_synth \
 step16_impl \
 step17_bitstream \
 step18_export_xsa \
 step19_hil_vectors \
 step20_model_regression \
 step21_package

PRODUCTION_STAGES := $(STAGES)
ifeq ($(FORCE),1)
FORCE_DEP := FORCE
endif

.PHONY: help list lint pipeline all stage rebuild status clean-stage clean-build FORCE $(STAGES)

help:
	@echo "ZCU208 / XCZU48DR Complete GPR Hybrid V3"
	@echo "Architecture: shared sweep scheduler + residual RX derotation + dwell integration + coherent averaging"
	@echo "              Xilinx IFFT + selectable streaming EWMA / DDR median + coherent Kirchhoff + 2D CFAR + clustering"
	@echo
	@echo "Static checks: make lint"
	@echo "Structural BD: make step13_vivado_integrate BASE_XPR=/abs/base.xpr INTEGRATION_MODE=external_ports"
	@echo "Production: edit config/zcu208_gpr_bd_map.tcl against a VERIFIED RFDC/MTS base, then make pipeline ..."
	@echo
	@echo "Production mapping is fail-hard. No RFDC/MTS/clock interface is guessed."

list:
	@for s in $(STAGES); do echo "$$s"; done

lint:
	@./scripts/static_validate.sh

all: pipeline
pipeline:
	@set -e; for s in $(PRODUCTION_STAGES); do echo; echo "===== $$s ====="; $(MAKE) --no-print-directory $$s; done

stage:
	@test -n "$(STEP)" || { echo "ERROR: use make stage STEP=stepNN_name"; exit 2; }
	@case " $(STAGES) " in *" $(STEP) "*) ;; *) echo "ERROR: unknown STEP=$(STEP)"; exit 2;; esac
	@$(MAKE) --no-print-directory "$(STEP)"

rebuild:
	@test -n "$(STEP)" || { echo "ERROR: use make rebuild STEP=stepNN_name"; exit 2; }
	@$(MAKE) --no-print-directory FORCE=1 "$(STEP)"

status:
	@./scripts/stage_status.sh "$(BUILD)" $(STAGES)

clean-stage:
	@test -n "$(STEP)" || { echo "ERROR: use make clean-stage STEP=stepNN_name"; exit 2; }
	@./scripts/clean_stage.sh "$(STEP)" "$(BUILD)" "$(IP_REPO)" "$(PROJECT_NAME)"

clean-build:
	@./scripts/clean_build.sh "$(BUILD)" "$(IP_REPO)"

step00_preflight: $(STAMP_DIR)/step00_preflight.done
step02_hls_scheduler: $(STAMP_DIR)/step02_hls_scheduler.done
step03_hls_rxextract: $(STAMP_DIR)/step03_hls_rxextract.done
step04_hls_sweepavg: $(STAMP_DIR)/step04_hls_sweepavg.done
step05_hls_cal: $(STAMP_DIR)/step05_hls_cal.done
step06_hls_pad: $(STAMP_DIR)/step06_hls_pad.done
step07_hls_background: $(STAMP_DIR)/step07_hls_background.done
step08_hls_power: $(STAMP_DIR)/step08_hls_power.done
step09_hls_cfar1d: $(STAMP_DIR)/step09_hls_cfar1d.done
step10_hls_imaging: $(STAMP_DIR)/step10_hls_imaging.done
step11_collect_ip: $(STAMP_DIR)/step11_collect_ip.done
step12_vivado_project: $(STAMP_DIR)/step12_vivado_project.done
step13_vivado_integrate: $(STAMP_DIR)/step13_vivado_integrate.done
step14_vivado_validate: $(STAMP_DIR)/step14_vivado_validate.done
step15_synth: $(STAMP_DIR)/step15_synth.done
step16_impl: $(STAMP_DIR)/step16_impl.done
step17_bitstream: $(STAMP_DIR)/step17_bitstream.done
step18_export_xsa: $(STAMP_DIR)/step18_export_xsa.done
step19_hil_vectors: $(STAMP_DIR)/step19_hil_vectors.done
step20_model_regression: $(STAMP_DIR)/step20_model_regression.done
step21_package: $(STAMP_DIR)/step21_package.done

$(STAMP_DIR)/step00_preflight.done: Makefile config.mk scripts/preflight.sh scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step00_preflight --stamp "$@" --log "$(LOG_DIR)/step00_preflight.log" -- ./scripts/preflight.sh

define HLS_STAGE
$(STAMP_DIR)/$(1).done: $$(shell find ip/custom/$(2) -type f 2>/dev/null) config.mk scripts/run_stage.sh $$(FORCE_DEP)
	@./scripts/run_stage.sh --id $(1) --stamp "$$@" --log "$$(LOG_DIR)/$(1).log" -- $$(MAKE) --no-print-directory -C ip/custom/$(2) all
endef

$(eval $(call HLS_STAGE,step02_hls_scheduler,gpr_sweep_scheduler))
$(eval $(call HLS_STAGE,step03_hls_rxextract,gpr_rx_tone_extractor))
$(eval $(call HLS_STAGE,step04_hls_sweepavg,gpr_sweep_average))
$(eval $(call HLS_STAGE,step05_hls_cal,gpr_cal_window))
$(eval $(call HLS_STAGE,step06_hls_pad,gpr_zero_pad_cfg))
$(eval $(call HLS_STAGE,step07_hls_background,gpr_background_ewma))
$(eval $(call HLS_STAGE,step08_hls_power,gpr_power32))
$(eval $(call HLS_STAGE,step09_hls_cfar1d,gpr_cfar1d))

$(STAMP_DIR)/step10_hls_imaging.done: $(shell find ip/custom/gpr_background_median_accel ip/custom/gpr_kirchhoff_coherent_accel ip/custom/gpr_cfar2d_accel ip/custom/gpr_cluster2d_accel -type f 2>/dev/null) config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step10_hls_imaging --stamp "$@" --log "$(LOG_DIR)/step10_hls_imaging.log" -- bash -lc '$(MAKE) --no-print-directory -C ip/custom/gpr_background_median_accel all && $(MAKE) --no-print-directory -C ip/custom/gpr_kirchhoff_coherent_accel all && $(MAKE) --no-print-directory -C ip/custom/gpr_cfar2d_accel all && $(MAKE) --no-print-directory -C ip/custom/gpr_cluster2d_accel all'

$(STAMP_DIR)/step11_collect_ip.done: scripts/collect_ip.sh config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step11_collect_ip --stamp "$@" --log "$(LOG_DIR)/step11_collect_ip.log" -- ./scripts/collect_ip.sh

$(STAMP_DIR)/step12_vivado_project.done: common/vivado/11_create_project_from_base.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step12_vivado_project --stamp "$@" --log "$(LOG_DIR)/step12_vivado_project.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/11_create_project_from_base.tcl

$(STAMP_DIR)/step13_vivado_integrate.done: common/vivado/12_integrate_gpr_v3.tcl common/vivado/create_gpr_v3_hier.tcl config/zcu208_gpr_bd_map.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step13_vivado_integrate --stamp "$@" --log "$(LOG_DIR)/step13_vivado_integrate.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/12_integrate_gpr_v3.tcl

$(STAMP_DIR)/step14_vivado_validate.done: common/vivado/13_validate.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step14_vivado_validate --stamp "$@" --log "$(LOG_DIR)/step14_vivado_validate.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/13_validate.tcl

$(STAMP_DIR)/step15_synth.done: common/vivado/14_synth.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step15_synth --stamp "$@" --log "$(LOG_DIR)/step15_synth.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/14_synth.tcl

$(STAMP_DIR)/step16_impl.done: common/vivado/15_impl.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step16_impl --stamp "$@" --log "$(LOG_DIR)/step16_impl.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/15_impl.tcl

$(STAMP_DIR)/step17_bitstream.done: common/vivado/16_bitstream.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step17_bitstream --stamp "$@" --log "$(LOG_DIR)/step17_bitstream.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/16_bitstream.tcl

$(STAMP_DIR)/step18_export_xsa.done: common/vivado/17_export_xsa.tcl config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step18_export_xsa --stamp "$@" --log "$(LOG_DIR)/step18_export_xsa.log" -- $(VIVADO) -mode batch -nojournal -nolog -source common/vivado/17_export_xsa.tcl

$(STAMP_DIR)/step19_hil_vectors.done: hil/matlab/generate_gpr_hil_vectors.m scripts/generate_hil.sh config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step19_hil_vectors --stamp "$@" --log "$(LOG_DIR)/step19_hil_vectors.log" -- ./scripts/generate_hil.sh

$(STAMP_DIR)/step20_model_regression.done: scripts/hybrid_model_test.py scripts/run_stage.sh config.mk $(FORCE_DEP)
	@./scripts/run_stage.sh --id step20_model_regression --stamp "$@" --log "$(LOG_DIR)/step20_model_regression.log" -- $(PYTHON3) scripts/hybrid_model_test.py

$(STAMP_DIR)/step21_package.done: scripts/package_release.sh config.mk scripts/run_stage.sh $(FORCE_DEP)
	@./scripts/run_stage.sh --id step21_package --stamp "$@" --log "$(LOG_DIR)/step21_package.log" -- ./scripts/package_release.sh

FORCE:
