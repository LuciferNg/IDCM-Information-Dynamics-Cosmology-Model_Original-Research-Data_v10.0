# FSR: Finiteness Analysis — UV Divergences and Gravitational Singularities

> **Date**: 2026-08-30
> **Question**: Does the FSR finite spectrum resolve UV divergences and gravitational singularities, or do they re-emerge in the continuum limit?

---

## 1. The Core Question

Standard physics has two fundamental infinities:

1. **UV divergences in QFT**: Loop integrals $\int^\infty d^4k$ diverge at high momentum. Renormalization absorbs infinities into counterterms but does not eliminate them — the theory is mathematically ill-defined without a cutoff.

2. **Gravitational singularities in GR**: The Schwarzschild $r=0$ and the Big Bang $t=0$ have infinite curvature. Classical GR predicts its own breakdown.

FSR replaces the continuous spectrum with a finite set $\{\varepsilon_n = 4\sin^2(\pi n/2N_\ell)\}$ at scale level $\ell$, with $N_\ell = N\cdot4^\ell$ modes. Does this resolution survive the $\ell \to \infty$ limit?

---

## 2. UV Divergences in QFT

### 2.1 Standard QFT (Continuum)

A typical 1-loop integral in $\phi^4$ theory:
$$\Sigma(p^2) = \int \frac{d^4k}{(2\pi)^4} \frac{1}{k^2 - m^2 + i\epsilon} \quad \text{(divergent as } \Lambda \to \infty\text{)}$$

The divergence is polynomial in the cutoff $\Lambda$:
$$\Sigma \sim \Lambda^2 + m^2\log(\Lambda^2/m^2) + \text{finite}$$

### 2.2 FSR (Finite Spectrum)

The FSR momentum space is compact: $p \in [0, \hbar\pi/a_\ell]$, with $N_\ell$ discrete modes. The loop integral is replaced by a finite sum:

$$\Sigma_{\text{FSR}} = \sum_{n=1}^{N_\ell} \frac{1}{\omega_n^2 - m^2 + i\epsilon} \cdot \Delta k_n$$

where $\omega_n = (2c/a_\ell)\sin(\pi n/2N_\ell)$ and $\Delta k_n = \pi/(N_\ell a_\ell)$.

**The sum is manifestly finite for any finite $N_\ell$.** The maximum momentum is $p_{\max} = \hbar\pi/a_\ell$, giving a maximum loop momentum.

### 2.3 The $\ell \to \infty$ Limit

As $\ell \to \infty$, $N_\ell \to \infty$, $a_\ell \to 0$, $p_{\max} \to \infty$, and the sum approaches the divergent integral:

$$\lim_{\ell\to\infty} \Sigma_{\text{FSR}} = \int \frac{d^4k}{(2\pi)^4} \frac{1}{k^2 - m^2} \quad \text{(divergent)}$$

**The continuum divergence re-emerges in the $\ell \to \infty$ limit.**

### 2.4 Physical Resolution

**The key**: Physical processes at finite energy $E$ live at finite scale level $\ell$. The level is determined by the energy:

$$\ell \approx \log_4\left(\frac{E a}{2\hbar c}\right)$$

For any finite $E$, $\ell$ is finite. The UV cutoff is:
$$p_{\max}(\ell) = \frac{\hbar\pi}{a_\ell} = \frac{\hbar\pi}{a} \cdot 4^\ell \approx \frac{E}{2\sin(\pi/2N_\ell)}$$

The loop integral is finite at the physical $\ell$. The $\ell \to \infty$ limit is a mathematical idealization that corresponds to infinite energy, which is physically inaccessible.

**Analogy**: In statistical mechanics, the thermodynamic limit $N \to \infty$ gives infinities (phase transitions, singularities). But finite systems are always finite. The infinities are properties of the idealization, not of physical systems.

---

## 3. Gravitational Singularities

### 3.1 Standard GR (Schwarzschild)

The Schwarzschild metric:
$$ds^2 = -\left(1 - \frac{2GM}{rc^2}\right)c^2dt^2 + \left(1 - \frac{2GM}{rc^2}\right)^{-1}dr^2 + r^2 d\Omega^2$$

The Kretschmann scalar (curvature invariant):
$$R^{\mu\nu\rho\sigma}R_{\mu\nu\rho\sigma} = \frac{48 G^2 M^2}{c^4 r^6} \to \infty \quad \text{as } r \to 0$$

### 3.2 FSR (Discrete Chain)

In FSR, the radial coordinate is discrete: $r_j = j \cdot a_\ell$ for $j = 1, \ldots, N_\ell$. The minimal radius is $r_{\min} = a_\ell$. The Schwarzschild metric is defined at the lattice points:

$$g_{00}(r_j) = -\left(1 - \frac{2GM}{r_j c^2}\right), \quad j = 1, \ldots, N_\ell$$

The Kretschmann scalar at the innermost point:
$$R^{\mu\nu\rho\sigma}R_{\mu\nu\rho\sigma}(r_{\min}) = \frac{48 G^2 M^2}{c^4 a_\ell^6} \quad \text{(finite for any finite } \ell\text{)}$$

### 3.3 The Big Bang

In standard GR, the Friedmann equation gives $a(t) \propto t^{2/3}$ for matter domination, with $a(t) \to 0$ as $t \to 0$, giving $R \to \infty$.

**In FSR, there is no expansion.** The "Big Bang" is replaced by the recursion from $\{0,1\}$ — a logical emergence, not a geometric singularity. The finite chain has no $t=0$ point.

### 3.4 The $\ell \to \infty$ Limit

As $\ell \to \infty$, $a_\ell \to 0$, $r_{\min} \to 0$, and the Kretschmann scalar diverges:

$$\lim_{\ell\to\infty} R^{\mu\nu\rho\sigma}R_{\mu\nu\rho\sigma}(r_{\min}) = \infty$$

**The singularity re-emerges in the $\ell \to \infty$ limit.**

### 3.5 Physical Resolution

The Schwarzschild singularity is reached only at $r < r_S(1 + 2GM/a_\ell c^2)$... Actually, the more precise statement: the singularity is approached as $r \to 0$. In FSR, $r$ is bounded below by $a_\ell$. The physical question: can a black hole be probed at distances smaller than $a_\ell$?

The Planck scale provides a natural bound: $\ell$ cannot exceed $\ell_{\max}$ where $a_\ell$ reaches the Planck length:

$$\ell_{\max} = \log_4\left(\frac{a}{L_P}\right) = \log_4\left(\frac{R_{\text{world}}}{N \cdot L_P}\right)$$

At $\ell_{\max}$, the minimal radius is $L_P$. The Kretschmann scalar is finite:
$$R^{\mu\nu\rho\sigma}R_{\mu\nu\rho\sigma}(L_P) = \frac{48 G^2 M^2}{c^4 L_P^6} \sim \frac{M^2}{M_P^2} \cdot \frac{1}{L_P^4}$$

For a solar-mass black hole: $M/M_P \sim 10^{38}$, so the curvature at the Planck scale is $\sim 10^{76} / L_P^4$ — large but finite. The singularity is replaced by a Planck-scale core.

---

## 4. Summary: What Finite N Resolves

| Divergence/Singularity | Standard Theory | FSR (finite $\ell$) | Limit $\ell \to \infty$ | Physical resolution |
|:----------------------|:---------------|:-------------------|:----------------------|:--------------------|
| QFT UV divergence | $\int^\infty d^4k$ diverges | Finite sum over $N_\ell$ modes | Re-emerges | Finite energy $\to$ finite $\ell$ |
| Schwarzschild $r=0$ | $R \to \infty$ | $r_{\min} = a_\ell$, finite $R$ | Re-emerges | Planck-scale core at $\ell_{\max}$ |
| Big Bang $t=0$ | $a(t) \to 0$, $R \to \infty$ | No expansion — recursion from $\{0,1\}$ | N/A | Logical emergence, not geometric |
| Renormalization | Need infinite counterterms | Finite theory, no renormalization | Re-emerges | Finite spectrum = UV completion |
| Maximum energy | Unbounded | $E_{\max} = \hbar c\pi/a_\ell$ | $\to \infty$ | $E_{\max}$ finite at any $\ell$ |

### 4.1 The Key Insight

**The finite spectrum does not "remove" infinities in the limit — it makes the physical theory finite at every finite energy scale.** 

The $\ell \to \infty$ limit is a mathematical idealization analogous to the thermodynamic limit in statistical mechanics. Physical processes happen at finite $\ell$, and the continuum divergences are properties of the idealization, not of the physical system.

In this sense, FSR is a **UV-complete** theory: all observables are finite at every finite energy, because the spectrum is finite at every finite scale level.

---

## 5. Verification

See `scripts/04_finiteness_check.py` for numerical verification:
- UV cutoff $p_{\max}(\ell)$ as a function of $\ell$ — finite at every $\ell$
- Maximum loop momentum — finite sum at every $\ell$
- Schwarzschild curvature at $r_{\min}$ — finite at every $\ell$
- Comparison with continuum: divergences scale as $4^\ell$ and vanish only at $\ell \to \infty$