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

	acc = 0;
	Shift_Accum_Loop:
	for (i = N - 1; i > 0; i--){
		shift_reg[i] = shift_reg[i - 1];
		acc += shift_reg[i] * c[i];
	}
	acc += x * c[0];
	shift_reg[0] = x;
	*y = acc;
}
