/*
	Filename: fir.h
		Header file
		FIR lab wirtten for WES/CSE237C class at UCSD.

*/
#ifndef FIR_BIT_OPT_H_
#define FIR_BIT_OPT_H_
#include "ap_int.h"

const int N=11;

typedef ap_int<11>	coef_t;
typedef int	data_t;
typedef int	acc_t;

void fir (
  data_t *y,
  data_t x
  );

#endif
