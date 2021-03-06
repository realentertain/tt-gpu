.PHONY: all clean target_clean
HOST ?= tx2fk
EXE=2DConvolution
REMOTE_TARGET = nvidia@$(HOST)
REMOTE_WORKING_DIR = ~/prem-2dconvolution
REMOTE_OUTPUT_DIR ?=$(REMOTE_WORKING_DIR)/out
CFLAGS := -Wall -Werror -O3 -lpthread -lrt 

cachemode ?=cg

PF_PHASEOFFSET ?=0
WB_PHASEOFFSET ?=0
KERNELWISE_SYNC?=no
SCHED_ALL_PHASES?=no
WB_SHIFT_BACK ?=0
USE_SCHED?=no
PREM_PROF?=no

ifeq ($(KERNELWISE_SYNC), no) 
	KWS:=
else
	KWS:= -DKERNELWISE_SYNC
endif

ifeq ($(USE_SCHED), no) 
	SCHED:=
else
	SCHED:= -DSCHEDULE
endif

ifeq ($(SCHED_ALL_PHASES), no) 
	PSA:=
else
	PSA:= -DPREM_SCHEDULE_ALL_PHASES
endif

ifeq ($(PREM_PROF), no) 
	PF:=
else
	PF:= -DUSE_PREM_PROF
endif

NVCCFLAGS := -Xptxas -O3 --ptxas-options=-v --compiler-options="$(CFLAGS)" \
	--generate-code arch=compute_62,code=[compute_62,sm_62] \
	--maxrregcount=32 -Xptxas -dlcm=$(cachemode) \

#Export CUDA paths
export LIBRARY_PATH:=/usr/local/cuda/lib64:$(LIBRARY_PATH)
export LD_LIBRARY_PATH:=/usr/local/cuda/lib64:$(LD_LIBRARY_PATH)
export PATH:=/usr/local/cuda/bin:$(PATH)


all: $(EXE)

$(EXE): main.c $(EXE).cu
	nvcc $(NVCCFLAGS) -DPREM_PF_PHASE_OFFSET=$(PF_PHASEOFFSET) -DPREM_WB_PHASE_OFFSET=$(WB_PHASEOFFSET) $(KWS) $(SCHED) $(PSA) $(PF) -DWB_SHIFT_BACK=$(WB_SHIFT_BACK) $^ -o $@

target_build: deploy
	ssh -t $(REMOTE_TARGET) "cd $(REMOTE_WORKING_DIR) && make clean && make all"

target_run: target_build
	ssh -t $(REMOTE_TARGET) "cd $(REMOTE_WORKING_DIR) && export LD_BIND_NOW && python3 run.py"
	rsync -avz ${REMOTE_TARGET}:${REMOTE_OUTPUT_DIR} .

deploy:
		rsync -avz . ${REMOTE_TARGET}:${REMOTE_WORKING_DIR}

clean:
	rm -f $(EXE)

target_clean:
	ssh $(REMOTE_TARGET) "rm -rf $(REMOTE_WORKING_DIR)"
