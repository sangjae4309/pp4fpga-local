#ifndef FIR_BIT_OPT_H_
#define FIR_BIT_OPT_H_
#include "ap_int.h"

const int N=128;

typedef ap_int<5>	coef_t;
typedef int	data_t;
typedef int	acc_t;

void fir (
  data_t *y,
  data_t x
  );

#endif
