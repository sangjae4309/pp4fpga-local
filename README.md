# pp4fpga Lab

Local Vitis HLS lab implementations based on **[Parallel Programming for FPGAs](https://kastner.ucsd.edu/hlsbook/)** by R. Kastner, J. Matai, and S. Neuendorffer (UCSD).

The original lab materials target Xilinx/AMD tools. This repository adapts them to run locally using the Vitis HLS command-line flow (`vitis-run`), with a Python-based script.

---

## Practice List

| Practice | Repository | Description |
| --- | --- | --- |
| FIR 11-tap | [`chapter2-fir/fir11`](chapter2-fir/fir11) | FIR filter implementations and optimization variants. |
| FIR 128-tap | [`chapter2-fir/fir128`](chapter2-fir/fir128) | Larger FIR filter implementations and optimization variants. |
| CORDIC Sin/Cos | [`chapter3-cordic/cordic_sin_cos`](chapter3-cordic/cordic_sin_cos) | Computes sine and cosine for an input angle using CORDIC rotations. |
| CORDIC Cart2Pol | [`chapter3-cordic/cordic_cart2pol`](chapter3-cordic/cordic_cart2pol) | Converts Cartesian coordinates to polar coordinates. |
| CORDIC Cart2Pol LUT | [`chapter3-cordic/cordic_cart2pol_lut`](chapter3-cordic/cordic_cart2pol_lut) | Uses lookup tables for Cartesian-to-polar conversion. |


---

## Prerequisites

| Tool | Version tested |
|------|---------------|
| AMD Vitis Unified Software Platform | 2025.2 |
| Python | 3.8+ |
| GCC/G++ | System default |

### Installing AMD Vitis

1. **Create an AMD account** at [https://www.amd.com/en/registration/create-account.html](https://www.amd.com/en/registration/create-account.html) (free).
2. **Download** the installer from the [AMD Vitis download page](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vitis.html).  
   Select **Vitis Unified Software Platform 2025.2** and download the Linux self-extracting installer (`Xilinx_Unified_2025.2_*.run`).
3. **Install**
   ```bash
   chmod +x Xilinx_Unified_2025.2_*.run
   ./Xilinx_Unified_2025.2_*.run
   ```
   When prompted, make sure to include the **Vitis HLS** component.  
   The default install root is `/tools/Xilinx/` or `/opt/Xilinx/`.

4. **Source the environment** after installation:
   ```bash
   source /tools/Xilinx/Vitis/2025.2/settings64.sh
   ```
   Add this line to `~/.bashrc` to avoid re-running it every session.

> **License note**: C-simulation and HLS synthesis (`vitis-run --mode hls`) work without a seat license.  
> A device license is required only if you proceed to RTL synthesis and implementation in Vivado.

Verify that `vitis-run` is on your `PATH`:

```bash
which vitis-run
```
