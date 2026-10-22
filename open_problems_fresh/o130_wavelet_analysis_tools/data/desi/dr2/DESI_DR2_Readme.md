# DESI DR2 Results II: Supplementary data

## Overview
This repository contains supplementary data supporting the paper [DESI Collaboration et al, 2025](https://ui.adsabs.harvard.edu/abs/2025arXiv250314738D/abstract) "DESI DR2 Results II: Measurement of Baryon Acoustic Oscillations and Cosmological Constraints", Phys. Rev. D in press. The data provided here enables the user to reproduce all figures and numerical results in the paper.

## Documentation
### Directory structure
Directories containing the data and minimal code to reproduce each of Figures 1, 2, 3, 4, 5, 6 and 12 in the paper are provided; these are named ``figure1/``, ``figure2/`` etc. Another zipped directory named ``cosmology_chains/`` contains the data for all MCMC chains and posterior maximization runs used to obtain Figures 7, 8, 9, 10, 11, 13, 14, 15, 16, 17 and 18, and to reproduce all the results provided in Tables V, VI and VII, and in all the inline equations in Sections VI, VII and VIII of the text. Further details are provided below.

#### 1. Data to reproduce figures 1-6 and 12
Each subdirectory `figure<X>/`, for X=1, 2, 3, 4, 5, 6 or 12, contains some data files and a Jupyter notebook named `plot_figure<X>.ipynb` which contains code to read these data files and reproduce the appropriate numbered figure in the paper. The Python code in each notebook requires the packages `numpy` and `matplotlib`, the code to reproduce Figure 2 additionally requires the `astropy` package, and some figures may require an appropriate TeX backend to correctly render fonts exactly as used in the published figures (though this can also be avoided if desired).

#### 2. Posterior information in `cosmology_chains/`
After unzipping, this will contain two sub-directories: `cobaya/` contains results of posterior sampling for various models and combinations of datasets, performed using the [`cobaya`](https://cobaya.readthedocs.io/en/latest/) sampling code, and `iminuit/` contains equivalent results for the maximum of the posterior, determined using the [`iminuit`](https://scikit-hep.org/iminuit/) optimization code.

**Models:**

Within each of these folders, results are arranged in folders named in order to indicate the cosmological model scenario considered in each case. Model naming follows the *Planck* convention: the base $\Lambda$CDM cosmological model is denoted by the root `base` in the folder name, with additional free parameters – when present – indicated by suffixes attached to this root. The naming convention relating suffixes to models is as follows:
* `_mnu`:  Free sum of neutrino masses, $\sum m_\nu$, with only a non-negativity constraint, $\sum m_\nu>0$
* `_omegak`: Free curvature parameter, $\Omega_\mathrm{K}$
* `_w`: A dark energy equation of state parameter $w$ that is freely varied but restricted to be constant in time
* `_w_wa`: A variable dark energy equation of state with two free parameters, $w_0$ and $w_a$
* `_w-binned-3uniform`: A dark energy equation of state that is piecewise-constant in 3 uniform bins of redshift
* `_mnu_binary_3`: Free sum of neutrino masses, $\sum m_\nu$, with additional physical priors on the minimum mass from the [NuFit-6.0](https://ui.adsabs.harvard.edu/abs/2024arXiv241005380E/abstract) flavor-oscillation constraints, incorporating either mass ordering

Suffixes can also be chained together to represent models with more than one free parameter, e.g. the folder `base_omegak_w_wa/` contains results for the model where bae $\Lambda$CDM is extended by allowing free curvature and a time-varying dark energy equation of state.

**Datasets:**

Within each model folder, results are arranged in additional sub-folders named to indicate the combination of datasets used in fitting. As for the case of the models, the folder names are formed by chaining together building blocks representing different individual datasets, separated by `_`, according to the following "dictionary":
* `desi-bao-<X>`: BAO data from DESI DR2; the `<X>` placeholder specifies the subset of DESI data used and can take the following values:
    * `bgs`: BAO measured in Bright Galaxy Sample, at effective redshift $z_\mathrm{eff}=0.295$
    * `lrg-z0`: BAO from the first Luminous Red Galaxy (LRG) redshift bin, at $z_\mathrm{eff}=0.510$
    * `lrg-z1`: BAO from the second LRG redshift bin, at $z_\mathrm{eff}=0.706$
    * `lrg`: the combination of the above two redshift bins (`lrg-z0` and `lrg-z1`)
    * `lrgpluselg`: BAO from the combined LRG and Emission Line Galaxy (ELG) sample at $z_\mathrm{eff}=0.934$
    * `elg`: BAO from higher redshift ELGs, at $z_\mathrm{eff}=1.321$
    * `qso`: BAO from the quasar sample (QSO), at $z_\mathrm{eff}=1.484$
    * `lya`: BAO from the Lyman-$\alpha$ forest (and cross-correlation with quasars) at $z_\mathrm{eff}=2.330$, as described in [DESI Collaboration et al, 2025](https://ui.adsabs.harvard.edu/abs/2025arXiv250314739D/abstract)
    * `all`: the combination of DESI BAO data in all the above redshift bins
* `planck2018-lowl-TT-clik_planck2018-lowl-EE-clik_planck-NPIPE-highl-CamSpec-TTTEEE`: cosmic microwave background (CMB) data from *Planck* PR4 TTTEEE using the `CamSpec` likelihood
* `planck2018-lowl-TT-clik_planck2018-lowl-EE-clik_planck2018-highl-plik-TTTEEE`: CMB data from *Planck* PR3 TTTEEE using the `plik` likelihood
* `planck2018-lowl-TT-clik_planck2020-lollipop-lowlE_planck2020-hillipop-TTTEEE`: CMB data from *Planck* PR4 TTTEEE using the `lollipop` and `hillipop` likelihoods
* `planck-act-dr6-lensing`: CMB lensing data from the combination of *Planck* PR4 NPIPE and ACT DR6 (as provided by the ACT team)
* `CMB-compressed-theta-ombh2-ombch2`: Minimal "early-Universe" CMB prior in lieu of using the full CMB data 
* `planck2018-thetastar-fixed-marg-nnu`: An even more minimal CMB-derived prior on the acoustic angular scale $\theta_\ast$
* `pantheonplus`: SNIa data from the Pantheon+ dataset
* `union3`: SNIa data from the Union3 dataset
* `desy5sn`: SNIa data from the Dark Energy Survey 5-year SN dataset
* `desy5sn-zmin-0.1`: A reduced version the Dark Energy Survey 5-year SN dataset excluding all SNe at $z<0.1$
* `schoneberg2024-bbn`: A BBN prior on the baryon density $\Omega_\mathrm{b}h^2$
* `schoneberg2024-bbn-fixed-nnu`: A more restrictive version of the above BBN prior derived by fixing $N_\mathrm{eff}$ rather than marginalised over it
* `desy3x2pt`: Weak lensing $3\times2$-pt data from the Dark Energy Survey Y3 results

These individual datasets can be combined together in too many ways to exhaustively list here. Combinations can be identified by chaining together the appropriate roots using `_` separators.

All chain data in the `cobaya/` directory is provided in a form that can easily be read and manipulated using the [`getdist`](https://getdist.readthedocs.io/en/latest/) package, but can also be accessed by other chain-processing software (and the chain files themselves are in ASCII format so are human-readable). 

In the `iminuit/` directory, each subfolder contains an ASCII file named `bestfit.minimizer.txt` which provides the posterior value, cosmological and nuisance parameter values, and goodness-of-fit measures for the model at the MAP point determined by the minimizer. The file `bestfit.minimum.npy` provides the same information but in binary format; other YAML files in the directory provide information on conditions under which the minimizer was run.
