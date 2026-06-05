// The file cordic.h holds definitions for the data types and constant values.
#include "cordic.h"

// The cordic_phase array holds the angle for the current rotation.
// cordic_phase[0] ~= 0.785
// cordic_phase[1] ~= 0.463

/*
 * theta: target angle to approximate
 */
void cordic(THETA_TYPE theta, COS_SIN_TYPE &s, COS_SIN_TYPE &c)
{
    // Set the initial vector that we will rotate.
    // current_cos = I; current_sin = Q
    COS_SIN_TYPE cur_cos = 0.60735;
    COS_SIN_TYPE cur_sin = 0.0;

    // Iteratively rotate the initial vector to find sine and cosine.
    for (int j = 0; j < NUM_ITERATIONS; j++) {
        // Determine if we are rotating by a positive or negative angle.
        int sigma = (theta < 0) ? -1 : 1;

        // Multiply previous iteration by 2^(-i).
        COS_SIN_TYPE cos_shift = cur_cos >> j;
        COS_SIN_TYPE sin_shift = cur_sin >> j;

        if(theta >=0) {
            cur_cos = cur_cos - sin_shift;
            cur_sin = cur_sin + cos_shift;
            theta = theta - cordic_phase[j];
        }
        else {
            cur_cos = cur_cos + sin_shift;
            cur_sin = cur_sin - cos_shift;
            theta = theta + cordic_phase[j];
        }
    }

    // Set the final sine and cosine values.
    s = cur_sin;
    c = cur_cos;
}
