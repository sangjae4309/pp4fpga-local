#include "cordiccart2pol.h"

data_t Kvalues[NO_ITER] = {
	1, 0.500000000000000, 0.250000000000000,
	0.125000000000000, 0.0625000000000000, 0.0312500000000000,
	0.0156250000000000, 0.00781250000000000, 0.00390625000000000,
	0.00195312500000000, 0.000976562500000000, 0.000488281250000000,
	0.000244140625000000, 0.000122070312500000, 6.10351562500000e-05,
	3.05175781250000e-05
};

// angles[i] = arctan(2^-i)
data_t angles[NO_ITER] = {
	0.785398163397448, 0.463647609000806, 0.244978663126864,
	0.124354994546761, 0.0624188099959574, 0.0312398334302683,
	0.0156237286204768, 0.00781234106010111, 0.00390623013196697,
	0.00195312251647882, 0.000976562189559320, 0.000488281211194898,
	0.000244140620149362, 0.000122070311893670, 6.10351561742088e-05,
	3.05175781155261e-05
};


void cordiccart2pol(data_t x, data_t y, data_t * r,  data_t * theta)
{
	// Write your code here
    data_t cur_x;
    data_t cur_y;
    data_t theta_p;
    data_t half_pi = 1.570796;

    // Initial - rorate +-90 degree
    cur_x = (y >= 0) ? y : -y;
    cur_y = (y >= 0) ? -x : x;
    theta_p = (y >= 0) ? half_pi : -half_pi;

    // Iteratively rotate the initial vector to find sine and cosine.
    for (int i = 0; i < NO_ITER; i++) {

        int sigma = (cur_y < 0) ? +1 : -1;

        data_t cur_x_shift = cur_x * sigma * Kvalues[i];
        data_t cur_y_shift = cur_y * sigma * Kvalues[i];

        // Perform the rotation.
        cur_x = cur_x - cur_y_shift;
        cur_y = cur_y + cur_x_shift;

        // Determine the new theta.
        theta_p = theta_p - sigma * angles[i];
    }
    *(theta) = theta_p;
    *(r) = cur_x * 0.60735;
}
