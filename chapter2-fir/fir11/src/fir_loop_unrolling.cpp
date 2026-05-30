/*
	Filename: fir.cpp
		FIR lab wirtten for WES/CSE237C class at UCSD.

	INPUT:
		x: signal (chirp)

	OUTPUT:
		y: filtered output

*/
#include "fir.h"

void fir (
  data_t *y,
  data_t x
  )
{
	coef_t c[N] = {53, 0, -91, 0, 313, 500, 313, 0, -91, 0,53};
	// Write your code here
	static data_t shift_reg[N];
	acc_t acc;
	int i;

	TDL:
	for (i=N-1; i>1; i=i-2){
		shift_reg[i] = shift_reg[i-1];
		shift_reg[i-1] = shift_reg[i-2];
	}
	//partial iteration
	if(i==1){
		shift_reg[1] = shift_reg[0];
	}
	shift_reg[0] = x;


	acc = 0;
	MAC:
	for (i=N-1; i>=1; i=i-2){
		acc += shift_reg[i] * c[i] + shift_reg[i-1] * c[i-1];
	}
	//partial iteration
	for (; i>=0; i--){
		acc += shift_reg[i] * c[i];
	}

	*y = acc;
}


