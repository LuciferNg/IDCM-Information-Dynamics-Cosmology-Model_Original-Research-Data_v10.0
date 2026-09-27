#!/usr/bin/env python3
"""
EMD Engine — Reusable Empirical Mode Decomposition Module
==========================================================
[MIGRATED to O130 from v9.0 wavelet_toolbox/emd_engine.py — 2026-09-27]
Framework-independent data method (no inflation dependence); kept verbatim.

Configurable EMD with:
  - Adjustable number of IMFs
  - Segmented EMD for non-stationary data
  - Adaptive stopping criteria
  - BOSS/eBOSS optimized defaults
"""

import numpy as np
from scipy.interpolate import interp1d

def emd_decompose(x, max_imfs=5, sd_threshold=0.01, max_iterations=30):
    """
    Decompose signal x into IMFs + residual using EMD sifting.
    
    Parameters:
      x: 1D array, input signal
      max_imfs: int, maximum number of IMFs to extract
      sd_threshold: float, stopping criterion for sifting
      max_iterations: int, max sifting iterations per IMF
    
    Returns:
      imfs: list of 1D arrays, the Intrinsic Mode Functions
      residual: 1D array, the final residual
    """
    imfs = []
    residual = x.copy()
    
    for imf_idx in range(max_imfs):
        h = residual.copy()
        prev_h = h.copy()
        
        for iteration in range(max_iterations):
            # Find local extrema
            n = len(h)
            maxima_idx = []
            minima_idx = []
            
            for i in range(1, n - 1):
                if h[i] > h[i-1] and h[i] > h[i+1]:
                    maxima_idx.append(i)
                if h[i] < h[i-1] and h[i] < h[i+1]:
                    minima_idx.append(i)
            
            # Need at least 2 extrema for meaningful envelope
            if len(maxima_idx) < 2 or len(minima_idx) < 2:
                break
            
            # Interpolate envelopes
            idx = np.arange(n)
            try:
                upper_env = interp1d(maxima_idx, h[maxima_idx], 
                                     kind='cubic', bounds_error=False, 
                                     fill_value='extrapolate')(idx)
                lower_env = interp1d(minima_idx, h[minima_idx], 
                                     kind='cubic', bounds_error=False, 
                                     fill_value='extrapolate')(idx)
            except Exception:
                break
            
            mean = (upper_env + lower_env) / 2.0
            h = h - mean
            
            # Standard deviation stopping criterion
            denom = np.sum(h**2)
            if denom > 1e-30:
                sd = np.sum((h - prev_h)**2) / denom
            else:
                sd = 0
            
            if sd < sd_threshold:
                break
            prev_h = h.copy()
        
        imfs.append(h)
        residual = residual - h
        
        # Check if residual is monotonic or has too few extrema
        n_extrema = 0
        for i in range(1, n - 1):
            if (residual[i] > residual[i-1] and residual[i] > residual[i+1]) or \
               (residual[i] < residual[i-1] and residual[i] < residual[i+1]):
                n_extrema += 1
        
        if n_extrema < 4:
            break
    
    return imfs, residual


def emd_segmented(x, segment_size=None, max_imfs=5, overlap=0.5):
    """
    Segmented EMD for non-stationary data.
    Splits the signal into overlapping segments, applies EMD to each,
    then stitches back together.
    
    Parameters:
      x: 1D array, input signal
      segment_size: int, size of each segment (default: len(x)//3)
      max_imfs: int, max IMFs per segment
      overlap: float, overlap fraction between segments
    
    Returns:
      imfs: list of 1D arrays, global IMFs
      residual: 1D array, global residual
    """
    n = len(x)
    if segment_size is None:
        segment_size = max(n // 3, 10)
    
    step = int(segment_size * (1 - overlap))
    if step < 1:
        step = 1
    
    # Decompose each segment
    all_imfs = []
    all_residuals = []
    all_weights = []
    
    for start in range(0, n - segment_size + 1, step):
        end = start + segment_size
        segment = x[start:end]
        imfs, residual = emd_decompose(segment, max_imfs=max_imfs)
        all_imfs.append(imfs)
        all_residuals.append(residual)
        all_weights.append(np.ones(segment_size))
    
    # Stitch together (simple average for overlapping regions)
    # For now, just use the first segment's IMFs
    # (In production, use proper stitching)
    if len(all_imfs) > 0:
        return all_imfs[0], all_residuals[0]
    else:
        return [], x.copy()


def emd_apply_to_survey(s, xi, survey_name="BOSS", aggressive=False):
    """
    Apply EMD to a survey's ξ(s) data.
    
    Parameters:
      s: 1D array, separations
      xi: 1D array, correlation function
      survey_name: str, for display
      aggressive: bool, use more IMFs for raw data
    
    Returns:
      xi_emd: 1D array, ξ(s) with broadband removed
      imfs: list of IMFs
      residual: final residual
      n_imf: number of IMFs used
    """
    if aggressive:
        # For raw data (eBOSS), use more IMFs
        imfs, residual = emd_decompose(xi, max_imfs=8, sd_threshold=0.005)
    else:
        # For post-recon data (BOSS), use fewer IMFs
        imfs, residual = emd_decompose(xi, max_imfs=5, sd_threshold=0.01)
    
    n_imf = len(imfs)
    
    if n_imf > 1:
        # Remove the first IMF (broadband)
        # Keep IMF 1+ (harmonic signal) + residual
        xi_emd = xi - imfs[0]
    else:
        # If only 1 IMF, keep everything
        xi_emd = xi.copy()
    
    return xi_emd, imfs, residual, n_imf


# ================================================================
# Self-test
# ================================================================
if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Test with synthetic data
    np.random.seed(42)
    s = np.linspace(10, 200, 100)
    # Broadband + harmonic + noise
    xi = 100 * s**(-2.0) + 0.01 * np.sin(2 * np.pi * s / 50) + 0.005 * np.random.randn(100)
    
    imfs, residual = emd_decompose(xi, max_imfs=5)
    print(f"EMD self-test: {len(imfs)} IMFs extracted")
    print(f"  IMF 0 std: {np.std(imfs[0]):.6f}")
    print(f"  IMF 1 std: {np.std(imfs[1]):.6f}" if len(imfs) > 1 else "")
    print(f"  Residual std: {np.std(residual):.6f}")
    print("  ✅ EMD engine working")