#include "fir.h"
#include "fir_coef.h"

void fir (
  data_t *y,
  data_t x
  )
{
	coef_t c[N] = FIR_COEFS;
	static data_t shift_reg[N];
	acc_t acc;
	int i;

	TDL:
	for (i = N - 1; i >= 1; i--){
		#pragma HLS PIPELINE II=1
		shift_reg[i] = shift_reg[i - 1];
	}
	shift_reg[0] = x;

	acc = 0;
	MAC:
	for (i = 0; i < N; i++){
		#pragma HLS PIPELINE II=1
		acc += shift_reg[i] * c[i];
	}

	*y = acc;
}
