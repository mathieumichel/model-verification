all: net-test
CONTIKI=/home/macfly/Git/contiki

APPS += powertrace

CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\"
CFLAGS += -DPERF_TEST=1 -DCONTIKIMAC_CONF_WITH_PHASE_OPTIMIZATION=1


CONTIKI_WITH_RIME = 1

include $(CONTIKI)/Makefile.include
