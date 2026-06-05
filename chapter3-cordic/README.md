# Chapter 3: CORDIC

| Design | Code | Description |
| --- | --- | --- |
| CORDIC Sin/Cos | [`cordic_sin_cos`](cordic_sin_cos) | Computes sine and cosine for an input angle using CORDIC rotations. |
| Basic CORDIC | [`cordic_cart2pol`](cordic_cart2pol) | Implements Cartesian-to-polar conversion with the CORDIC rotation structure. |
| CORDIC LUT | [`cordic_cart2pol_lut`](cordic_cart2pol_lut) | Uses lookup tables for Cartesian-to-polar conversion. |
| FIR Frontend | [`phase_detector/fir_top`](phase_detector/fir_top) | Filters input I/Q samples before phase detection. |
| Phase Detector | [`phase_detector/phasedetector`](phase_detector/phasedetector) | Combines FIR filtering and CORDIC-based Cartesian-to-polar conversion. |

## What is CORDIC?

CORDIC, short for Coordinate Rotation Digital Computer, is an algorithm for
computing vector rotations using only additions, subtractions, shifts, and a
small table of precomputed angles. This makes it useful for hardware designs
where multipliers and trigonometric functions are expensive.

## Vector Rotation

A 2D vector can be rotated by an angle $\theta$ using the standard rotation
matrix:

$$
\begin{bmatrix}
x_i \\
y_i
\end{bmatrix}
=
\begin{bmatrix}
\cos\theta & -\sin\theta \\
\sin\theta & \cos\theta
\end{bmatrix}
\begin{bmatrix}
x_{i-1} \\
y_{i-1}
\end{bmatrix}
$$

This equation creates a new vector by rotating the previous vector by
$\theta$. However, directly computing $\sin\theta$ and $\cos\theta$ is
expensive in hardware, so CORDIC rewrites the rotation into a more
hardware-friendly form.

Using the trigonometric identities

$$
\cos(\theta_i) =
\frac{1}{\sqrt{1 + \tan^2(\theta_i)}} \quad
\sin(\theta_i) =
\frac{\tan(\theta_i)}{\sqrt{1 + \tan^2(\theta_i)}}
$$

the rotation matrix can be rewritten as

$$
R_i =
\frac{1}{\sqrt{1 + \tan^2(\theta_i)}}
\begin{bmatrix}
1 & -\tan(\theta_i) \\
\tan(\theta_i) & 1
\end{bmatrix}
$$

CORDIC does not allow arbitrary rotation angles at each step. Instead, it
restricts each micro-rotation to angles that are easy to implement in hardware:

$$
\tan(\theta_i) = 2^{-i}
$$

With this restriction, each rotation step becomes

$$
v_i =
K_i
\begin{bmatrix}
1 & -2^{-i} \\
2^{-i} & 1
\end{bmatrix}
\begin{bmatrix}
x_{i-1} \\
y_{i-1}
\end{bmatrix}
\quad
\text{, }
K_i = \frac{1}{\sqrt{1+2^{-2i}}}
$$

The key advantage is that multiplying by $2^{-i}$ can be implemented as a
right shift. This removes the need for general multipliers in the main
rotation loop.

The matrix above only rotates in one direction. To support both clockwise and
counterclockwise rotations, CORDIC introduces a direction variable
$\sigma_i \in \{-1, 1\}$:

$$
v_i =
K_i
\begin{bmatrix}
1 & -\sigma_i 2^{-i} \\
\sigma_i 2^{-i} & 1
\end{bmatrix}
\begin{bmatrix}
x_{i-1} \\
y_{i-1}
\end{bmatrix}
$$

At each iteration, the algorithm chooses $\sigma_i$ based on whether the
current accumulated angle should increase or decrease.

## Summary

CORDIC stores the angles that satisfy

$$
\theta_i = \arctan(2^{-i})
$$

in on-chip memory. By repeatedly applying the CORDIC rotation matrix with
different directions, the hardware can approximate almost any target angle.
The result is a hardware-friendly rotation method that replaces expensive
trigonometric operations with table lookup, addition, subtraction, and shifts.

## Optimization Result

The table below compares the floating-point CORDIC sin/cos implementation with
the fixed-point version using `ap_fixed<16, 2>`.

| Implementation | Sin RMSE | Cos RMSE | Latency | LUT | FF | DSP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [`cordic_sin_cos`](cordic_sin_cos) | `0.0000939686` | `0.0001302474` | `212 cycles` | `1847` | `1204` | `10` |
| [`cordic_sin_cos_optim_fixed_point`](cordic_sin_cos_optim_fixed_point) | `0.0001871195` | `0.0001241061` | `33 cycles` | `372` | `137` | `0` |

Using fixed-point arithmetic removes floating-point operators from the design.
The result is much lower LUT/FF usage, zero DSP usage, and shorter latency,
while keeping the C-simulation error around the `1e-4` range.
