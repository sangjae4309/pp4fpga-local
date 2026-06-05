#ifndef CORDIC_H
#define CORDIC_H

#include <ap_fixed.h>

typedef ap_fixed<16, 2> THETA_TYPE;
typedef ap_fixed<16, 2> COS_SIN_TYPE;

const int NUM_ITERATIONS = 16;

// cordic_phase[j] = atan(2^-j), the micro-rotation angle for iteration j.
// Swept j starting from 0. 
static const THETA_TYPE cordic_phase[NUM_ITERATIONS] = {
    0.7853981633974483, // arctan(2^-0)
    0.4636476090008061, // arctan(2^-1)
    0.2449786631268641,
    0.1243549945467614,
    0.0624188099959574,
    0.0312398334302683,
    0.0156237286204768,
    0.0078123410601011,
    0.0039062301319670,
    0.0019531225164788,
    0.0009765621895593,
    0.0004882812111949,
    0.0002441406201494,
    0.0001220703118937,
    0.0000610351561742,
    0.0000305175781155,
};

void cordic(THETA_TYPE theta, COS_SIN_TYPE &s, COS_SIN_TYPE &c);

#endif
