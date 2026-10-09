# FSR vs Standard SR/GR: Complete Derivation and Comparison

> **Date**: 2026-08-30
> **Status**: Derivation from FSR axioms; verification in scripts/03_sr_gr_comparison.py

---

## Part I: Special Relativity from FSR

### 1.1 Lorentz Transformation

**Standard SR** (continuous, boost along x):
$$t' = \gamma\left(t - \frac{vx}{c^2}\right), \quad x' = \gamma(x - vt), \quad \gamma = \frac{1}{\sqrt{1-v^2/c^2}}$$

**FSR derivation**: On the finite ladder, a boost by mode $m$ maps mode $n$ to mode $n'$ where the rapidity shifts:
$$\eta_{n'} = \eta_n + \eta_m, \quad \eta_n = \ln\cot\frac{\pi n}{4N}$$

The Lorentz factor for mode $n$:
$$\gamma_n = \frac{1}{\sqrt{1 - v_n^2/c^2}} = \csc\frac{\pi n}{2N} = \cosh\eta_n$$

The Lorentz transformation matrix for mode $n$:
$$\begin{pmatrix} ct' \\ x' \end{pmatrix} = \begin{pmatrix} \gamma_n & -\gamma_n\beta_n \\ -\gamma_n\beta_n & \gamma_n \end{pmatrix} \begin{pmatrix} ct \\ x \end{pmatrix}$$

**This is the exact SR matrix** — the entries are $\gamma_n$ and $\beta_n\gamma_n$ with $\beta_n = v_n/c = \cos(\pi n/2N)$.

**Continuum limit** ($N \to \infty$, $\ell \to \infty$): The mode index $n$ becomes continuous, $v_n$ becomes continuous in $[0,c]$, and the Lorentz transformation matrix is the standard SR matrix with continuous $\beta$.

**Difference**: At finite $N$, the boost parameter $\beta$ is restricted to the discrete set $\{\cos(\pi n/2N)\}$. This is a quantization of the boost parameter, not a modification of the transformation.

### 1.2 Velocity Addition

**Standard SR**: $u = \frac{u' + v}{1 + u'v/c^2}$

**FSR derivation**: In rapidity form, $\eta_u = \eta_{u'} + \eta_v$. On the FSR ladder:
$$\eta_u = \eta_{n_a} + \eta_{n_b} = \ln\cot\frac{\pi n_a}{4N} + \ln\cot\frac{\pi n_b}{4N}$$

The resulting velocity $u = c\tanh\eta_u$ is generally not on the discrete ladder $\{c\cos(\pi n/2N)\}$. The composed velocity is realized at a finer scale level $\ell'$ where the ladder is dense enough.

**At scale $\ell$**: The refined ladder has $N_\ell = N\cdot4^\ell$ modes. The composition $\eta_a + \eta_b$ lands within $\Delta\eta/2$ of some ladder rung, where $\Delta\eta = \ln\cot(\pi/4N_\ell)$ is the rapidity spacing.

**Continuum limit** ($\ell \to \infty$): $\Delta\eta \to 0$, the ladder becomes dense, and the standard SR velocity addition formula is recovered exactly.

**Key difference**: At finite $\ell$, velocity addition has a quantization error of at most $\Delta v/c \approx \pi/2N_\ell$.

### 1.3 Time Dilation

**Standard SR**: $\Delta t' = \gamma\,\Delta t$

**FSR**: For a clock in mode $n$:
$$\Delta t' = \gamma_n\,\Delta t = \csc\frac{\pi n}{2N}\,\Delta t$$

**Exact identity**: The SR time dilation formula holds **exactly** on the FSR ladder. The only difference is that $\gamma$ is restricted to the discrete set $\{\csc(\pi n/2N)\}$.

**Scale refinement**: For a particle at energy $E = \gamma mc^2$, the mode index $n$ satisfies $\gamma_n = \csc(\pi n/2N_\ell) \approx 2N_\ell/\pi n$, giving $n \approx 2N_\ell/\pi\gamma$. The time dilation is the standard SR value.

### 1.4 Length Contraction

**Standard SR**: $L' = L/\gamma$

**FSR**: For a rod of proper length $L_0$ in its rest frame, moving at $v_n$:
$$L' = \frac{L_0}{\gamma_n} = L_0\sin\frac{\pi n}{2N}$$

**Exact identity**: The SR length contraction formula holds exactly on the FSR ladder.

### 1.5 Relativistic Doppler

**Standard SR**: $f' = f\sqrt{\frac{1-\beta}{1+\beta}}$ (receding source)

**FSR**: $f'_n = f\cot\frac{\pi n}{4N} = f e^{-\eta_n} = f\sqrt{\frac{1-\beta_n}{1+\beta_n}}$

**Exact identity**: The SR Doppler formula holds exactly. $D_n = \cot(\pi n/4N)$ is the exact Doppler factor.

### 1.6 Energy-Momentum

**Standard SR**: $E = \gamma mc^2$, $p = \gamma mv$, $E^2 = p^2c^2 + m^2c^4$

**FSR**:
$$E_n = \gamma_n mc^2 = mc^2\csc\frac{\pi n}{2N}, \quad p_n = \gamma_n m v_n = mc\cot\frac{\pi n}{2N}$$
$$E_n^2 - p_n^2c^2 = m^2c^4 \quad \text{(exact)}$$

**Exact identity**: The mass shell is preserved exactly. The only difference: $(E_n, p_n)$ are discrete points on the hyperbola.

### 1.7 Relativistic Kinetic Energy

**Standard SR**: $K = (\gamma-1)mc^2$

**FSR**: $K_n = (\gamma_n - 1)mc^2 = \left(\csc\frac{\pi n}{2N} - 1\right)mc^2$

**Low-energy limit** ($n \ll N$):
$$K_n \approx \frac{1}{2}\left(\frac{\pi n}{2N}\right)^2 mc^2 = \frac{1}{2}m v_n^2 \quad \text{(Newtonian)}$$

The standard non-relativistic limit is recovered.

---

## Part II: General Relativity from FSR

### 2.1 From Spectral Triple to Einstein-Hilbert Action

**FSR geometry**: The finite chain forms a spectral triple $(\mathcal{A}, \mathcal{H}, D)$:
- $\mathcal{A} = C(\text{Chain})$: algebra of functions on the $N$ sites
- $\mathcal{H} = \mathbb{C}^N$: Hilbert space of modes
- $D = \text{diag}(\varepsilon_n) = \text{diag}(4\sin^2(\pi n/2N))$: Dirac operator (or $D = \text{diag}(\gamma_n)$ for the Lorentz version)

**Spectral action principle** (Connes, Chamseddine): The physical action is
$$S = \text{Tr}(f(D/\Lambda))$$
where $f$ is a cutoff function and $\Lambda$ is the energy scale.

**Expansion for large $\Lambda$** (heat kernel expansion):
$$S = \sum_{k=0}^\infty f_{2k} \Lambda^{d-2k} a_{2k}(D^2)$$
where $a_{2k}$ are the Seeley-deWitt coefficients and $d$ is the dimension.

**For the 1D chain** ($d=1$):
$$S = f_0\Lambda a_0(D^2) + f_2\Lambda^{-1} a_2(D^2) + \cdots$$
$$a_0(D^2) = \text{Tr}(\mathbb{I}) = N_\ell = N\cdot4^\ell \quad \text{(volume term)}$$
$$a_2(D^2) = \text{Tr}(-D^2) = -\sum_n \varepsilon_n = -(2N_\ell + 2) \quad \text{(curvature term)}$$

**Interpretation**: The spectral action on the chain gives:
- A cosmological constant term $\propto N_\ell$ (the volume/number of sites)
- A curvature term $\propto \sum\varepsilon_n$ (the spectral curvature)
- Higher-order corrections $\propto \sum\varepsilon_n^{-k}$ for $k \ge 1$

### 2.2 The 4D Continuum Limit

**Scale refinement**: The refined chain $N_\ell = N\cdot4^\ell$ with spacing $a_\ell = a/4^\ell$. In the limit $\ell \to \infty$, the chain becomes a continuous 1D interval $[0, L]$.

**To 4D**: The spectral triple of the refined chain, when tensored with itself (or with a finite noncommutative geometry), gives a 4D spectral triple. The spectral action expansion gives:

$$S_{4D} = \frac{1}{16\pi G}\int d^4x\sqrt{-g}\left(R - 2\Lambda\right) + \mathcal{O}(R^2)$$

**The Einstein-Hilbert action emerges as the $\ell \to \infty$ limit of the spectral action on the refined FSR chain.**

### 2.3 Einstein Field Equations

**Standard GR**: $G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$

**FSR derivation**: Varying the spectral action with respect to the metric (encoded in $D$):

$$\frac{\delta S}{\delta g_{\mu\nu}} = 0 \quad \Rightarrow \quad \text{Field equations}$$

For the 1D chain, the variation gives the discrete wave equation:
$$\frac{\partial^2\phi}{\partial t^2} = c^2 \Delta_{\text{disc}}\phi$$

In the 4D continuum limit, this becomes the Einstein equations with:
- The Einstein tensor $G_{\mu\nu}$ from the spectral curvature
- The cosmological constant $\Lambda$ from the volume term
- The stress-energy tensor $T_{\mu\nu}$ from matter fields coupled to the spectral triple

### 2.4 Geodesic Equation

**Standard GR**: $\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\nu\rho}\frac{dx^\nu}{d\tau}\frac{dx^\rho}{d\tau} = 0$

**FSR derivation**: On the chain, the geodesic is the path that extremizes the discrete action:
$$S = \sum_j \sqrt{-\Delta t^2 + \Delta x_j^2/c^2}$$

For a chain with uniform spacing $a$, the minimal path is the straight line (no curvature at the base level). At refined levels, the discrete geodesic approaches the continuous geodesic with corrections $\mathcal{O}(a_\ell^2)$.

### 2.5 Schwarzschild Solution

**Standard GR**: $ds^2 = -\left(1-\frac{2GM}{rc^2}\right)c^2dt^2 + \left(1-\frac{2GM}{rc^2}\right)^{-1}dr^2 + r^2d\Omega^2$

**FSR derivation**: The Schwarzschild metric in FSR is the discrete solution to the spectral action with a point mass source. The discrete radial coordinate is $r_j = j a_\ell$ for $j = 1, \ldots, N_\ell$. The metric coefficients are:
$$g_{00}(r_j) = -\left(1 - \frac{2GM}{r_j c^2}\right), \quad g_{rr}(r_j) = \left(1 - \frac{2GM}{r_j c^2}\right)^{-1}$$

**Corrections**: At the discrete level, the metric is exact at the lattice points. The finite resolution introduces a cutoff at $r = a_\ell$ — the Schwarzschild singularity is replaced by a finite core of size $a_\ell$.

### 2.6 Friedmann Equations (Cosmology)

**Standard GR**:
$$H^2 = \frac{8\pi G}{3}\rho + \frac{\Lambda c^2}{3} - \frac{kc^2}{a^2}$$
$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}$$

**FSR derivation** (from O76): The FSR "Hubble parameter" (angular frequency of the chain) is:
$$\omega_{\text{ring}} = \frac{2\pi}{T_{\text{ring}}} = \frac{c}{R_{\text{world}}}$$

The angular diameter distance at scale level $\ell$:
$$D_A(\ell) = R_{\text{world}}(1 - 4^{-\ell})(1 + 2\varphi^{-1}\ell + \delta(\ell))$$

The luminosity distance:
$$D_L = (1+z)^{1-n/p} D_A, \quad \frac{n}{p} = \frac{\gamma_7}{\gamma_{20}} = 0.14262$$

The "Friedmann equation" of FSR:
$$H_{\text{FSR}}^2(z) = \omega_{\text{ring}}^2 \cdot \left(\frac{dD_A}{dz}\right)^{-2}$$

**Comparison with ΛCDM**:
- FSR has no expansion — $z$ is a scale level index, not a Doppler shift from expansion
- The Etherington relation is modified: $D_L/D_A = (1+z)^{0.857}$ vs $(1+z)^2$
- Time dilation is identical: $\Delta t \propto (1+z)$
- The distance-redshift relation matches Pantheon+ data: $\chi^2 = 2006.8$ vs ΛCDM $2002.1$ ($\Delta\chi^2 = +4.7$, zero parameters)

---

## Part III: Comparison Table

### 3.1 Special Relativity

| Equation | Standard SR | FSR (exact) | FSR ($\ell \to \infty$) | Difference |
|:---------|:-----------|:------------|:----------------------|:-----------|
| Lorentz factor | $\gamma = 1/\sqrt{1-\beta^2}$ | $\gamma_n = \csc(\pi n/2N_\ell)$ | $\gamma = 1/\sqrt{1-\beta^2}$ | **None** — exact on ladder |
| Lorentz transform | Matrix with $\gamma, \beta\gamma$ | Same matrix, $\beta_n$ discrete | Same matrix, continuous $\beta$ | Quantized $\beta$ |
| Velocity addition | $u = (u'+v)/(1+u'v/c^2)$ | $\eta = \eta_a + \eta_b$, $v = c\tanh\eta$ | Same | Rapidity ladder not closed |
| Time dilation | $\Delta t' = \gamma\Delta t$ | $\Delta t' = \gamma_n\Delta t$ | Same | $\gamma$ quantized |
| Length contraction | $L' = L/\gamma$ | $L' = L/\gamma_n$ | Same | $\gamma$ quantized |
| Doppler | $f' = f\sqrt{(1-\beta)/(1+\beta)}$ | $f' = f\cot(\pi n/4N_\ell)$ | Same | $\beta$ quantized |
| Mass shell | $E^2 = p^2c^2 + m^2c^4$ | $E_n^2 = p_n^2c^2 + m^2c^4$ | Same | **None** — exact |
| Kinetic energy | $K = (\gamma-1)mc^2$ | $K_n = (\gamma_n-1)mc^2$ | Same | $\gamma$ quantized |

### 3.2 General Relativity

| Equation | Standard GR | FSR (spectral) | Continuum limit | Difference |
|:---------|:-----------|:---------------|:----------------|:-----------|
| Field eqs | $G_{\mu\nu} + \Lambda g_{\mu\nu} = 8\pi G T_{\mu\nu}$ | $\delta S_{\text{spec}}/\delta g = 0$ | Standard GR | O($1/N_\ell^2$) corrections |
| Action | $S_{\text{EH}} = \int (R-2\Lambda)\sqrt{-g}$ | $S = \text{Tr}(f(D/\Lambda))$ | $S_{\text{EH}} + \mathcal{O}(R^2)$ | Higher-order terms at finite $\Lambda$ |
| Geodesic | $\ddot{x} + \Gamma\dot{x}\dot{x} = 0$ | Discrete action extremum | Standard geodesic | $\mathcal{O}(a_\ell^2)$ corrections |
| Schwarzschild | $g_{00} = -(1-2GM/rc^2)$ | Same at lattice points | Standard metric | $\mathcal{O}(a_\ell^2)$ corrections at horizon |
| Friedmann | $H^2 = 8\pi G\rho/3 + \Lambda/3$ | $D_A(\ell)$, $D_L = (1+z)^{0.857}D_A$ | $H^2$ relation | **Different**: no expansion, Etherington modified |
| Etherington | $D_L/D_A = (1+z)^2$ | $D_L/D_A = (1+z)^{0.857}$ | N/A | **Structurally different** |
| Time dilation | $\Delta t \propto (1+z)$ | $\Delta t \propto (1+z)$ | Same | **None** — identical |

### 3.3 Summary of Differences

**Identical (SR sector):**
- $\gamma = 1/\sqrt{1-\beta^2}$ relation
- Lorentz transformation matrix
- Mass shell $E^2 - p^2c^2 = m^2c^4$
- Doppler factor
- Time dilation, length contraction
- Energy-momentum relation

**Quantized (FSR-specific):**
- $\beta$ takes discrete values $\{\cos(\pi n/2N_\ell)\}$
- $\gamma$ takes discrete values $\{\csc(\pi n/2N_\ell)\}$
- Velocity addition not closed on the ladder (resolved by scale refinement)

**Structurally different (cosmology):**
- Etherington relation: $D_L/D_A = (1+z)^{0.857}$ vs $(1+z)^2$
- No expansion: $z$ is scale level, not Doppler shift
- The Friedmann equation is replaced by the $D_A(\ell)$ formula

---

## Part IV: Verification

See `scripts/03_sr_gr_comparison.py` for numerical verification of all equations above.

Key results:
1. FSR Lorentz factor vs SR: exact match on the ladder (all 44 modes)
2. FSR mass shell vs SR: exact match (all 44 modes)
3. FSR Doppler vs SR: exact match (all 44 modes)
4. FSR vs ΛCDM cosmology: Pantheon+ $\chi^2$ comparison (O76: $2006.8$ vs $2002.1$)
5. FSR discrete corrections: scale as $1/N_\ell^2$, unobservable at $\ell \ge 6$

---

## References

- Connes, "Noncommutative Geometry" (1994) — spectral action principle
- Chamseddine & Connes, "The Spectral Action Principle" (1997)
- O76: $z$ redshift translation, $D_A(\ell)$, $D_L/D_A = (1+z)^{0.857}$
- O140: FSR first-principles derivation (docs/03)
- FSR verification scripts: scripts/01 (N=44), 02 (generic N)