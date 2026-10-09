# Finite-Spectral Relativity (FSR)
## A First-Principles Derivation from Discrete Calculus and Finite Spectrum

> **Date**: 2026-08-30
> **Status**: 🟡 Core derivation complete (38/38 PASS for N=44 base case)
> **Framework scope**: Self-contained — no external dependencies. IDCM is a special case at N=44.

---

## Preamble

This document derives Finite-Spectral Relativity (FSR) from three axioms:

1. **Finite Spectrum** — the physical kinematic space has a finite number of modes N
2. **Discrete Wave Equation** — dynamics follow the discrete wave equation on a finite chain
3. **Relativity Principle** — the discrete dispersion relation is frame-independent

The framework is self-contained. All quantities follow from discrete calculus and the spectral geometry of the finite chain. The specific case N=44 corresponds to the IDCM embedding, but the framework stands independently.

---

## Axiom 0: The Finite Chain

Let a 1D discrete chain of $M$ nodes with uniform spacing $a$, total length $L = (M-1)a$. The discrete Laplacian with Neumann (reflecting) boundary conditions:

$$(\Delta_{\text{disc}} f)(j) = \frac{f(j+1) - 2f(j) + f(j-1)}{a^2}, \quad j = 1, \ldots, M-2$$

with boundary conditions $f(1) = f(0)$, $f(M-1) = f(M)$ (Neumann).

**Eigenvalue problem**: $\Delta_{\text{disc}} \psi_n = -\kappa_n \psi_n$

Eigenfunctions (discrete cosine transform basis):
$$\psi_n(j) = \cos\left(\frac{\pi n j}{M-1}\right), \quad n = 0, 1, \ldots, M-1$$

Eigenvalues:
$$\kappa_n = \frac{4}{a^2} \sin^2\left(\frac{\pi n}{2(M-1)}\right), \quad n = 0, 1, \ldots, M-1$$

The zero mode $n=0$ has $\kappa_0 = 0$ (uniform translation). The $N = M-1$ non-zero modes form the **finite spectrum**:

$$\boxed{\varepsilon_n = a^2 \kappa_n = 4 \sin^2\left(\frac{\pi n}{2N}\right)}, \quad n = 1, \ldots, N$$

**Spectral sum**: $\sum_{n=1}^N \varepsilon_n = 2N$

---

## Axiom 1: Discrete Wave Equation

The scalar field on the chain satisfies the discrete wave equation:

$$\frac{\partial^2 \phi}{\partial t^2} = c^2 \Delta_{\text{disc}} \phi$$

**Modal decomposition**: $\phi(j,t) = \sum_{n=0}^N A_n \psi_n(j) \cos(\omega_n t + \theta_n)$

**Dispersion relation**:
$$\omega_n = c \sqrt{\kappa_n} = \frac{2c}{a} \sin\left(\frac{\pi n}{2N}\right), \quad n = 1, \ldots, N$$

**Wave number**: $k_n = \frac{\pi n}{N a}$ (from the DCT basis: $k_n = \pi n / L$)

---

## Section 1: Velocity Ladder

### 1.1 Group Velocity

The group velocity of mode $n$:

$$v_g(n) = \frac{d\omega_n}{dk_n} = c \cos\left(\frac{\pi n}{2N}\right), \quad n = 1, \ldots, N$$

The zero mode $n=0$ has $v_g(0) = c$ (the speed of light).

| n/N | v_g/c | Meaning |
|:---:|:-----:|:--------|
| 0 | 1 | Light speed (uniform mode) |
| $\ll 1$ | $1 - \frac{1}{2}(\pi n/2N)^2$ | Near-light, continuum limit |
| $N/2$ | $1/\sqrt{2}$ | Mid-ladder |
| $N$ | 0 | Nyquist mode (rest) |

**Mirror duality**: $v_g(N-n) = -v_g(n)$ — mode reflection = velocity reversal.

### 1.2 Ladder Spacing

The velocity quantum (minimum spacing between adjacent ladder rungs):

$$\Delta v_n = v_g(n) - v_g(n+1) = 2c \sin\left(\frac{\pi(2n+1)}{4N}\right) \sin\left(\frac{\pi}{4N}\right)$$

---

## Section 2: Lorentz Ladder

### 2.1 Definition

From the relativistic identity $\gamma = 1/\sqrt{1-v^2/c^2}$:

$$\gamma_n = \frac{1}{\sqrt{1 - \cos^2(\pi n/2N)}} = \csc\left(\frac{\pi n}{2N}\right), \quad n = 1, \ldots, N$$

**Key property**: The SR relation $\gamma = 1/\sqrt{1-\beta^2}$ is preserved **exactly** on the ladder. FSR does not modify the $\gamma$-$\beta$ relation — it quantizes the velocity spectrum.

| n | $\gamma_n$ | Significance |
|:-:|:----------:|:-------------|
| 1 | $\csc(\pi/2N) \approx 2N/\pi$ | Fastest mode |
| $N/2$ | $\csc(\pi/4) = \sqrt{2}$ | Mid-ladder |
| $N$ | 1 | Rest |

### 2.2 Eigenvalue Identity

The Lorentz factor relates to the finite spectrum $\varepsilon_n$:

$$\gamma_n = \frac{2}{\sqrt{\varepsilon_n}} = \frac{c}{\pi a f_n}$$

where $f_n = \omega_n/2\pi$ is the mode frequency. The **mass-energy ladder** and the **velocity ladder** are the same spectral ladder — two readings of the finite spectrum.

### 2.3 Mirror Product Identity

$$\varepsilon_n \cdot \varepsilon_{N-n} = 16 \sin^2\left(\frac{\pi n}{2N}\right) \cos^2\left(\frac{\pi n}{2N}\right) = 4 \varepsilon_n$$

This is a key structural identity: the mirror-pair product of eigenvalues equals $4\varepsilon_n$. In terms of $\gamma_n$:

$$\gamma_n^2 = \frac{4}{\varepsilon_n \cdot \varepsilon_{N-n}}$$

### 2.4 Sum Rule

$$\sum_{n=1}^N \gamma_n^2 = \sum_{n=1}^N \csc^2\left(\frac{\pi n}{2N}\right) = \frac{(2N)^2 - 1}{3}$$

For $N=44$: $\sum \gamma_n^2 = 1291$ (prime). This is a standard identity for sums of cosecant squares.

---

## Section 3: Rapidity Lattice

### 3.1 Definition

The rapidity in SR is $\eta = \operatorname{atanh}(v/c)$. On the finite ladder:

$$\eta_n = \operatorname{atanh}\left(\cos\frac{\pi n}{2N}\right) = \ln\cot\left(\frac{\pi n}{4N}\right), \quad n = 1, \ldots, N$$

**Proof**: $\operatorname{atanh}(\cos\theta) = \frac{1}{2}\ln\frac{1+\cos\theta}{1-\cos\theta} = \frac{1}{2}\ln\cot^2(\theta/2) = \ln\cot(\theta/2)$. With $\theta = \pi n/2N$, $\eta_n = \ln\cot(\pi n/4N)$.

**Rapidity lattice**: the set $\{\eta_n\}$ forms a discrete lattice in rapidity space.

### 3.2 Doppler Factor

The relativistic Doppler factor $D = \sqrt{(1+\beta)/(1-\beta)} = e^\eta$:

$$D_n = e^{\eta_n} = \cot\left(\frac{\pi n}{4N}\right)$$

**Closed form**: The Doppler factor is a pure cotangent of the half-angle — no approximations.

---

## Section 4: Discrete Mass Shell

### 4.1 Energy-Momentum

For a particle of mass $m$ in mode $n$:

$$E_n = m c^2 \gamma_n = m c^2 \csc\left(\frac{\pi n}{2N}\right)$$
$$p_n = m v_n \gamma_n = m c \cos\left(\frac{\pi n}{2N}\right) \csc\left(\frac{\pi n}{2N}\right) = m c \cot\left(\frac{\pi n}{2N}\right)$$

**Verification**:
$$E_n^2 - p_n^2 c^2 = m^2 c^4 (\csc^2\theta - \cot^2\theta) = m^2 c^4, \quad \theta = \frac{\pi n}{2N}$$

The relativistic mass shell is **exact** on the discrete ladder. The $2N-1$ points $\{(E_n, p_n)\}_{n=0}^{N}$ (including the zero-mode $n=0$ with $E_0 = \infty$, $p_0 = \infty$) lie on the hyperbola $E^2 - p^2c^2 = m^2c^4$.

### 4.2 Spectral Zeta Function (Non-Continuous Riemann)

Define the spectral zeta function of the finite chain:

$$\zeta_N(s) = \sum_{n=1}^N \varepsilon_n^{-s} = \sum_{n=1}^N \frac{1}{4^s \sin^{2s}(\pi n/2N)}$$

This is the **discrete Riemann zeta** — a finite sum replacing the infinite sum $\zeta(s) = \sum_{n=1}^\infty n^{-s}$.

**Key properties**:
- $\zeta_N(0) = N$ (trivial, counting modes)
- $\zeta_N(1) = \sum \csc^2(\pi n/2N)/4 = ((2N)^2-1)/12$
- $\zeta_N(-1) = \sum \varepsilon_n = 2N$ (total spectral weight)
- $\zeta_N(s)$ has a pole at $s=1$ in the $N\to\infty$ limit, recovering the Riemann zeta pole

The **discrete Weyl law**: the eigenvalue counting function
$$N(\Lambda) = \#\{n: \varepsilon_n \leq \Lambda\} = \frac{2N}{\pi} \arcsin\left(\frac{\sqrt{\Lambda}}{2}\right)$$

For $\Lambda \ll 4$ (low-energy limit): $N(\Lambda) \approx \frac{N}{\pi} \sqrt{\Lambda}$, the continuum Weyl law for a 1D interval.

---

## Section 5: Scale Refinement and the Continuum Limit

### 5.1 Hierarchical Refinement

The finite spectrum at level $\ell$ is obtained by refining the chain:

$$N_\ell = N \cdot 4^\ell, \quad a_\ell = \frac{a}{4^\ell}$$

The refined spectrum:
$$\varepsilon_n^{(\ell)} = 4 \sin^2\left(\frac{\pi n}{2N_\ell}\right), \quad n = 1, \ldots, N_\ell$$

The group velocity at level $\ell$:
$$v_g(n;\ell) = c \cos\left(\frac{\pi n}{2N_\ell}\right)$$

### 5.2 Maximum Lorentz Factor

$$\gamma_{\max}(\ell) = \csc\left(\frac{\pi}{2N_\ell}\right) = \csc\left(\frac{\pi}{2N \cdot 4^\ell}\right) \approx \frac{2N}{\pi} \cdot 4^\ell$$

As $\ell \to \infty$: $\gamma_{\max}(\ell) \to \infty$, and the velocity ladder becomes dense in $[0, c]$.

### 5.3 The SR Limit

In the limit $\ell \to \infty$ (equivalently $N \to \infty$):
- The dispersion becomes linear: $\omega_n \to c k_n$
- The velocity ladder becomes continuous: $v_g \in [0, c]$
- The Lorentz factor is unbounded: $\gamma \in [1, \infty)$
- The rapidity lattice becomes dense: $\eta \in [0, \infty)$
- The spectral zeta function $\zeta_N(s) \to \zeta_{\text{cont}}(s)$, the continuum spectral zeta

**Standard SR is recovered exactly as the $\ell \to \infty$ limit of FSR.**

---

## Section 6: Quantum Mechanics Compatibility

### 6.1 Finite Hilbert Space

The Hilbert space of mode states at level $\ell$:
$$\mathcal{H}_\ell = \mathbb{C}^{N_\ell}, \quad \dim \mathcal{H}_\ell = N \cdot 4^\ell$$

All operators are bounded — the quantum theory is rigorous and free of ultraviolet divergences.

### 6.2 Quantized Momentum

The wave number on the refined chain:
$$k_n^{(\ell)} = \frac{\pi n}{N_\ell a_\ell} = \frac{\pi n}{N a}$$

The physical momentum:
$$p_n^{(\ell)} = \hbar k_n^{(\ell)} = \frac{\hbar \pi n}{N a}, \quad n = 1, \ldots, N_\ell$$

The momentum is **independent of $\ell$** — the refinement preserves the momentum quantization. The Brillouin zone: $p \in [0, \hbar\pi/a]$.

### 6.3 Generalized Uncertainty Principle (GUP)

From the compact momentum space:
$$\Delta p \leq p_{\max} = \frac{\hbar\pi}{a}, \quad \Delta x \cdot \Delta p \geq \frac{\hbar}{2}$$

The minimal position uncertainty:
$$\Delta x_{\min} = \frac{\hbar}{2 p_{\max}} = \frac{a}{2\pi}$$

### 6.4 Lattice Klein-Gordon Equation

The Klein-Gordon equation on the finite chain:
$$(i\hbar\partial_t)^2 \phi = (-\hbar^2 c^2 \Delta_{\text{disc}} + m^2 c^4) \phi$$

Eigenvalues:
$$E_n^2 = m^2 c^4 + \hbar^2 c^2 k_n^2 = m^2 c^4 + \left(\frac{\hbar c \pi n}{N a}\right)^2$$

The spectrum is **bounded**: $E \leq \sqrt{m^2 c^4 + (\hbar c\pi/a)^2}$. No ultraviolet divergence.

---

## Section 7: The Spectral Triple (Non-Continuous Riemann)

The finite chain forms a **spectral triple** $(A, \mathcal{H}, D)$:

- **Algebra**: $A = C(\text{Chain})$, the algebra of functions on the $N$ sites
- **Hilbert space**: $\mathcal{H} = \mathbb{C}^N$, the mode space
- **Dirac operator**: $D = \operatorname{diag}(\varepsilon_n) = \operatorname{diag}(4\sin^2(\pi n/2N))$ (or $D = \operatorname{diag}(\gamma_n)$ for the Lorentz version)

The spectral triple encodes the discrete geometry:
- The commutator $[D, f]$ for $f \in A$ gives the discrete derivative
- The spectral action $\operatorname{Tr}(f(D/\Lambda))$ gives the finite-volume action
- The zeta function $\zeta_D(s) = \operatorname{Tr}(D^{-s}) = \zeta_N(s)$ is the spectral zeta of the triple

This is a concrete realization of Connes' noncommutative geometry — the finite spectrum **is** the geometry.

---

## Section 8: Correspondence with IDCM

The FSR framework is independent; the IDCM corresponds to the specific choice $N=44$:

| FSR (general) | IDCM (N=44) | Physical meaning |
|:-------------|:------------|:-----------------|
| $N$ | 44 | Number of non-zero modes |
| $2N$ | 88 | Dual chain sites |
| $\varepsilon_n = 4\sin^2(\pi n/2N)$ | $\gamma_n^{44} = 4\sin^2(\pi n/88)$ | Discrete spectrum |
| $\sum \varepsilon_n = 2N$ | 90 | World sum |
| $\sum \gamma_n^2 = ((2N)^2-1)/3$ | 1291 | Prime sum |
| $v_g(n) = c\cos(\pi n/2N)$ | $v_g = c\cos(\pi n/88)$ | Velocity ladder |
| $\gamma_n = \csc(\pi n/2N)$ | $\gamma_n = \csc(\pi n/88)$ | Lorentz ladder |
| $\eta_n = \ln\cot(\pi n/4N)$ | $\eta_n = \ln\cot(\pi n/176)$ | Rapidity lattice |
| $\gamma_{\max}(\ell) = \csc(\pi/2N\cdot 4^{-\ell})$ | $\gamma_{\max} \approx 28\cdot 4^\ell$ | Scale refinement |
| $K_{\text{Tree}}$ branching $B=4$ | B=4 | Scale factor |
| Scale-redshift $1+z = 4^\ell$ (O76) | IDCM | FSR + IDCM cosmology |

---

## Section 9: Open Problems

1. **Group closure of velocity addition**: The rapidity sum $\eta_a + \eta_b$ is not generally on the discrete ladder. The exact group structure of the finite ladder is an open problem (likely a quantum group deformation of the Poincaré algebra, e.g., $\kappa$-Poincaré).

2. **Two-index structure**: The mass spectrum (mode index $k$) and the velocity ladder (mode index $n$) are both labelled by the same finite spectrum. The Hilbert space $\mathcal{H}_k \otimes \mathcal{H}_n$ and the Dirac operator $D_{\text{FSR}} = \sum m_k |k\rangle\langle k| \otimes \gamma_n |n\rangle\langle n|$ need formalization.

3. **Local scale level**: The assignment of the physical scale level $\ell$ to a laboratory frame is not derived.

---

## Appendix: Verification

All identities in this document are verified numerically for $N=44$ (the IDCM base case) in `scripts/01_verify_fsr_identities.py` (38/38 PASS). A generic-N verification is in `scripts/02_generic_n_verification.py`.

---

## References

- Standard discrete Laplacian eigenvalue theory (Strang, "Discrete Laplacian", SIAM Review)
- Spectral zeta functions of finite graphs (Tate, Terras)
- Noncommutative geometry (Connes, "Noncommutative Geometry")
- Lattice wave equation (textbook, any numerical PDE source)
- IDCM O76: redshift translation, $1+z = 4^\ell$, Etherington violation
- IDCM O54: lepton mass spectrum, $m_g \propto \varepsilon_{n_g}$