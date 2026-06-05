#include "cordic.h"
#include <cmath>
#include <cstdio>

struct Rmse {
    int count;
    double sum_sq;
    double error;

    Rmse() : count(0), sum_sq(0), error(0) {}

    double add_value(double value)
    {
        count++;
        sum_sq += value * value;
        error = std::sqrt(sum_sq / count);
        return error;
    }
};

int main()
{
    const THETA_TYPE tests[] = {
        -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0,
    };

    Rmse sin_rmse;
    Rmse cos_rmse;

    std::printf("---Testing results----------------------------------\n");

    for (int i = 0; i < static_cast<int>(sizeof(tests) / sizeof(tests[0])); i++) {
        COS_SIN_TYPE s = 0;
        COS_SIN_TYPE c = 0;
        THETA_TYPE theta = tests[i];

        cordic(theta, s, c);

        double golden_s = std::sin(theta);
        double golden_c = std::cos(theta);

        sin_rmse.add_value(static_cast<double>(s) - golden_s);
        cos_rmse.add_value(static_cast<double>(c) - golden_c);

        std::printf(
            "theta=% .4f, golden sin=% .6f, golden cos=% .6f, "
            "cordic sin=% .6f, cordic cos=% .6f\n",
            static_cast<double>(theta), golden_s, golden_c,
            static_cast<double>(s), static_cast<double>(c));
    }

    std::printf("---RMS error----------------------------------\n");
    std::printf("----------------------------------------------\n");
    std::printf("   RMSE(Sin)        RMSE(Cos)\n");
    std::printf("%0.15f %0.15f\n", sin_rmse.error, cos_rmse.error);
    std::printf("----------------------------------------------\n");

    const double error_threshold = 0.001;
    bool success = sin_rmse.error < error_threshold && cos_rmse.error < error_threshold;

    std::printf("%s\n", success ? "PASS" : "FAIL");
    return success ? 0 : 1;
}
