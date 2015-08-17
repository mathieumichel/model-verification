#ifndef __PROJECT_CONF_H__
#define __PROJECT_CONF_H__

#define INTERFERER_ON_TIME  CLOCK_SECOND / 2
#define INTERFERER_OFF_TIME INTERFERER_ON_TIME * 1
/* CC2420 power levels: 3, 7, 11, 15, 19, 23, 27, 31. */
#define INTERFERER_TX_POWER 15

#undef RF_CHANNEL
#define RF_CHANNEL 26

#define WITH_NULLMAC 1
#ifndef WITH_NULLMAC
#define WITH_NULLMAC 0
#endif

#if WITH_NULLMAC
#undef NETSTACK_CONF_MAC
#define NETSTACK_CONF_MAC nullmac_driver

#undef NETSTACK_CONF_RDC
#define NETSTACK_CONF_RDC nullrdc_driver

#undef NETSTACK_CONF_FRAMER
#define NETSTACK_CONF_FRAMER framer_nullmac

#undef CC2420_CONF_AUTOACK
#define CC2420_CONF_AUTOACK 0
#endif

#endif /* __PROJECT_CONF_H__ */
