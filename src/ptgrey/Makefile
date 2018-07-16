################################################################################
# AcquisitionMultipleCamera Makefile
################################################################################
PROJECT_ROOT=../../
OPT_INC = ${PROJECT_ROOT}/common/make/common_spin.mk
-include ${OPT_INC}

################################################################################
# Key paths and settings
################################################################################
ifeq ($(wildcard ${OPT_INC}),)
CFLAGS += -std=c++11
CXX = g++ ${CFLAGS}
ODIR  = .obj/build${D}
SDIR  = .
MKDIR = mkdir -p
endif

OUTPUTNAME = SessionVideo${D}
OUTDIR = ../../bin

################################################################################
# Dependencies
OPENCV_LIB = -L/usr/local/lib -lopencv_highgui -lopencv_core
################################################################################
# Spinnaker deps
SPINNAKER_LIB = -L../../lib -lSpinnaker${D} ${SPIN_DEPS}

################################################################################
# Master inc/lib/obj/dep settings
################################################################################
_OBJ = SessionVideo.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))
INC = -I../../include -I/usr/include/spinnaker -I/usr/local/include/opencv
LIB += -Wl,-Bdynamic ${SPINNAKER_LIB}
LIB += -Wl,-rpath-link=../../lib
LIB += ${OPENCV_LIB}

################################################################################
# Rules/recipes
################################################################################
# Final binary
${OUTPUTNAME}: ${OBJ}
	${CXX} -o ${OUTPUTNAME} ${OBJ} ${LIB}
	mv ${OUTPUTNAME} ${OUTDIR}

# Intermediate object files
${OBJ}: ${ODIR}/%.o : ${SDIR}/%.cpp
	@${MKDIR} ${ODIR}
	${CXX} ${CFLAGS} ${INC} -Wall -D LINUX -c $< -o $@

# Clean up intermediate objects
clean_obj:
	rm -f ${OBJ}
	@echo "intermediate objects cleaned up!"

# Clean up everything.
clean: clean_obj
	rm -f ${OUTDIR}/${OUTPUTNAME}
	@echo "all cleaned up!"
