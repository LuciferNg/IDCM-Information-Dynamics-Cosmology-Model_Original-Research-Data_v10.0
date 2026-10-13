Keywords: Phased arrays, planar arrays, imaging arrays,
frame theory, astronomical telescopes, therahertz instruments,
millimetre-wave instruments, optical modes, coherence

# Theoretical Analysis of Astronomical Phased Arrays

Stafford Withington
George Saklatavala
Michael P. Hobson
Affiliation: Cavendish Laboratory, JJ Thompson Avenue, Cambridge CB3
OHE, UK
Email: [stafford@mrao.cam.ac.uk](mailto:stafford@mrao.cam.ac.uk)

###### Abstract

Low-noise phased arrays are essential for the next
generation of microwave and submillimetre wave astronomy. We analyze
their behaviour from a functional perspective, and show
that their operation is intimately related to the mathematical theory
of frames. No assumptions are made about the orthogonality or linear
independence of the synthesised beams. Frame theory allows an unambiguous
assessment of whether the outputs of an array can be used to
observe a field or brightness distribution within a given class.
Image reconstruction is carried out using dual beams. We identify the
natural modes of phased arrays, and carry out an analysis of noise. The
scheme allows the expectation values, the mean-square fluctuations, and
the correlations between fluctuations at the output ports of a phased
array to be determined for a source in any state of spatial coherence.
Both classical and photon-counting statistics are included. Our model
is conceptually powerful, and suggests many simulation and image recovery
techniques.

## 1 Introduction

Recently, there has been a surge of interest in
developing phased arrays for radio astronomy. Projects include the
Square Kilometer Array (SKA), the Low Frequency Array (LOFAR), the
Electronic Multibeam Radio Astronomy Concept (EMBRACE), the Karoo
Array Telescope (KAT) \[ [1](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib1 ""), [2](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib2 ""), [3](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib3 ""), [4](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib4 "")\], and a number of instruments
for enhancing the performance of single-dish telescopes. Most
of the current projects are aimed constructing phased arrays for
microwave astronomy, but as technological capability improves,
phased arrays will also be constructed for far infrared and
submillimetre wave astronomy \[ [5](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib5 ""), [6](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib6 "")\].

Two types of phased array are of interest: (i) imaging phased
arrays, where an array of passive antennas, or coherent receivers,
is connected to a beam-forming network such that synthesised beams
can be created and swept across the sky; (ii) interferometric phased
arrays, where the individual antennas of an aperture synthesis
interferometer are equipped with phased arrays such that fringes
are formed within the synthesised beams. In this way it is
possible to extend the field of view, to observe completely
different regions of the sky simultaneously, to steer the field of
view electronically, and to observe spatial frequencies that are
not available because the baselines of an interferometer cannot be
packed more tightly than the diameters of the individual telescopes.

It is important to appreciate that the synthesised beams of a
phased array need not, mathematically speaking, be orthogonal and
may even be linearly dependent. Non-orthogonality may be built
into a system intentionally as a way of increasing the fidelity
with which an image can be reconstructed, or it may arise
inadvertently as a consequence of RF coupling and post-processing
cross-talk. In some situations, say in the case of interacting
planar antennas, it may not even be clear how to distinguish one
antenna from another, even before the beam-forming network has
been connected.

Despite the considerable importance of phased arrays for astronomy,
there is still a lack of information about the principles of operation
when the synthesised beams are non-orthogonal, or even
linearly dependent, and when noise is included. In this paper we
describe the operation of low-noise imaging phased arrays from a
functional perspective, and show that information throughput and image
recovery are intimately related to the mathematical theory of frames. We
also show that it is only necessary to know the synthesised beams in order
to calculate the average powers, the correlations between the complex
travelling wave amplitudes, the fluctuations in power, and the
correlations between the fluctuations in power (the Hanbury Brown-Twiss
effect) at the output ports of an array.

The paper provides a powerful conceptual framework for understanding
the operation of phased arrays.
A key feature of the analysis is that we do not fill the half space
between the aperture plane and the sky with a complete set of plane
waves, but limit our attention to the natural optical modes of the
system. In this way, issues relating to information throughput,
sensitivity, noise, correlations, and quantum statistics can be dealt
with in a straightforward manner. Indeed, the quantum statistical
properties of the incoming radiation field can be taken into
account, for a source in any state of spatial coherence, and the
transition from fully bunched to photon-counting statistics included
as the wavelength of operation moves from the microwave range
through into the far infrared.

## 2 Basic Principles

In general an imaging phased array comprises a sequence of optical
components, an array of single-mode receivers, each of which has
a primary beam pattern, and an electrical beam-forming
network such that each output port corresponds to a
synthesised reception pattern on the sky. The synthesised
reception patterns may be static and designed to give optimum
sampling on a given class of object, or they may be controlled
electrically and swept across the field of view. In the case of
radio astronomy, the optical system would be a telescope, the
single-mode receivers would be horns or planar antennas coupled to
HEMT amplifiers or SIS mixers, and the beam-forming network would
be a system of microwave or digital electronics.

The following analysis is based on a generic system comprising
an array of MM horns and a beam-forming network having PP output
ports. Each of the PP ports is associated with a synthesised
reception pattern. For convenience, 𝒜{\\cal A} denotes the input
reference surface, which is a far-field region of the sky,
ℬ{\\cal B} the output ports of the horns, and 𝒞{\\cal C} the output
ports of the beam-forming network.

When a fully coherent field is incident on the system, a set of
travelling waves appears at ℬ{\\cal B}, and we shall denote their
complex amplitudes by {ym:m∈1,⋯,M}\\{y\_{m}:m\\in 1,\\cdots,M\\}; also, a set
of travelling waves appears at 𝒞{\\cal C}, and we shall denote
their complex amplitudes by {zp:p∈1,⋯,P}\\{z\_{p}:p\\in 1,\\cdots,P\\}. Because
MM and PP are finite, the complex amplitudes can be assembled
into column vectors 𝐲∈ℂM{\\bf y}\\in{\\mathbb{C}}^{M} and 𝐳∈ℂP{\\bf z}\\in{\\mathbb{C}}^{P}. If 𝐄⁡(𝛀^){\\bf E}(\\hat{\\boldsymbol{\\Omega}})
is the plane-wave spectrum of the incident electric field,
and 𝛀^\\hat{\\boldsymbol{\\Omega}} a unit radial vector in the aperture
plane pointing towards the sky, then it can be shown that because
the synthesised reception patterns and incoming field are
square-integrable functions, which can be represented by
vectors in the Hilbert space of square integral functions over 𝒜\\cal A,
the complex amplitude of the travelling wave at port pp can be written

|     |     |     |     |
| --- | --- | --- | --- |
|  | zp=∫𝒜𝐭p∗​(𝛀^)⋅𝐄⁡(𝛀^)​𝑑𝛀​,z\_{p}=\\int\_{\\cal A}{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf E}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{,} |  | (1) |

where 𝐭p​(𝛀^){\\bf t}\_{p}(\\hat{\\boldsymbol{\\Omega}}) is the complex
synthesised reception pattern of port pp. It would be naive to assume,
however, that if the array is illuminated by a field having the form
𝐄​(𝛀^)=𝐭p​(𝛀^){\\bf E}(\\hat{\\boldsymbol{\\Omega}})={\\bf t}\_{p}(\\hat{\\boldsymbol{\\Omega}}), a travelling wave only appears at pp.

It is instructive to derive a relationship between the synthesised beams
and the beams of the primary antennas. If the beam patterns of the primary
antennas are denoted by 𝐡m​(𝛀^){\\bf h}\_{m}(\\hat{\\boldsymbol{\\Omega}}) then the
outputs of the antennas, ymy\_{m}, are given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | ym=∫𝒜𝐡m∗​(𝛀^)⋅𝐄⁡(𝛀^)​𝑑𝛀​,y\_{m}=\\int\_{\\cal A}{\\bf h}^{\\ast}\_{m}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf E}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{,} |  | (2) |

but the beam-forming network can be described by scattering matrix
𝚽{\\boldsymbol{\\Phi}}, having elements ϕp​m\\phi\_{pm}, where

|     |     |     |     |
| --- | --- | --- | --- |
|  | zp=∑mϕp​m​ym​,z\_{p}=\\sum\_{m}\\phi\_{pm}y\_{m}\\mbox{,} |  | (3) |

and therefore substituting ( [2](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E2 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) in ( [3](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E3 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")),

|     |     |     |     |
| --- | --- | --- | --- |
|  | zp=∫𝒜∑mϕp​m​𝐡m∗​(𝛀^)⋅𝐄⁡(𝛀^)​𝑑𝛀​,z\_{p}=\\int\_{\\cal A}\\sum\_{m}\\phi\_{pm}{\\bf h}^{\\ast}\_{m}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf E}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{,} |  | (4) |

which can be cast into the form of ( [1](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E1 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) by defining

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐭p​(𝛀^)=∑mϕp​m∗​𝐡m​(𝛀^)​.{\\bf t}\_{p}(\\hat{\\boldsymbol{\\Omega}})=\\sum\_{m}\\phi\_{pm}^{\\ast}{\\bf h}\_{m}(\\hat{\\boldsymbol{\\Omega}})\\mbox{.} |  | (5) |

As expected, the synthesised reception patterns are
weighted linear combinations of the primary antenna patterns.

Even when the primary beams are orthogonal, and identical, the
synthesised beams do not have to be orthogonal, because

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∫𝒜𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​𝑑𝛀=k​∑mϕp​m​ϕp′​m∗​,\\int\_{\\cal A}{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}=k\\sum\_{m}\\phi\_{pm}\\phi\_{p^{\\prime}m}^{\\ast}\\mbox{,} |  | (6) |

where ( [5](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E5 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) has been used, kk is a constant that derives from
the inner products of the primary antenna patterns,

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∫𝒜𝐡m∗​(𝛀^)⋅𝐡m′​(𝛀^)​𝑑𝛀=k​δm​m′​,\\int\_{\\cal A}{\\bf h}\_{m}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf h}\_{m^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}=k\\,\\delta\_{mm^{\\prime}}\\mbox{,} |  | (7) |

and there is no restriction on the orthogonality of the ϕp​m\\phi\_{pm}.
( [6](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E6 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) can be written in the form of a matrix equation:

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∫𝒜𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​𝑑𝛀=k​\[𝚽​𝚽†\]p​p′​.\\int\_{\\cal A}{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}=k\\left\[{\\boldsymbol{\\Phi}}{\\boldsymbol{\\Phi}}^{\\dagger}\\right\]\_{p\\,p^{\\prime}}\\mbox{.} |  | (8) |

If MM of the columns of 𝚽†:ℂP→ℂM{\\boldsymbol{\\Phi}}^{\\dagger}:{\\mathbb{C}}^{P}\\rightarrow{\\mathbb{C}}^{M} are linearly independent, and P>MP>M, then
the complete set of columns constitutes an over-complete basis, in the sense
that there are PP vectors in an MM-dimensional space. In this case,
except trivially when certain ports are not connected, the synthesised
reception patterns are not orthogonal, because
𝚽​𝚽†≠𝐃{\\boldsymbol{\\Phi}}{\\boldsymbol{\\Phi}}^{\\dagger}\\neq{\\bf D}, where
𝐃{\\bf D} is a diagonal matrix of dimension PP; indeed, the
synthesised reception patterns are linearly dependent. Contrariwise, the
columns of 𝚽†{\\boldsymbol{\\Phi}}^{\\dagger} comprise an under-complete basis
if P<MP<M, and again we may have 𝚽​𝚽†≠𝐃{\\boldsymbol{\\Phi}}{\\boldsymbol{\\Phi}}^{\\dagger}\\neq{\\bf D}. In the case where 𝚽{\\boldsymbol{\\Phi}} is
unitary, 𝚽​𝚽†=𝐈P{\\boldsymbol{\\Phi}}{\\boldsymbol{\\Phi}}^{\\dagger}={\\bf I}\_{P},
where 𝐈P{\\bf I}\_{P} is the identity matrix of dimension PP,
and the primary beam patterns are orthogonal, the synthesised reception
patterns are orthogonal. We conclude that, except in the simplest of
scenarios, the synthesised reception patterns are unlikely to be orthogonal,

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∫𝒜𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​𝑑𝛀≠k​Dp,p′​,\\int\_{\\cal A}{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\neq kD\_{p,p^{\\prime}}\\mbox{,} |  | (9) |

and may even be linearly dependent. According to ( [1](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E1 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) and
( [9](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E9 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), travelling waves will generally appear at more than
one port even when the incident field has the form of one of the
synthesised reception patterns: 𝐄​(𝛀^)=𝐭p′​(𝛀^){\\bf E}(\\hat{\\bf\\Omega})={\\bf t}\_{p^{\\prime}}(\\hat{\\bf\\Omega}).

( [5](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E5 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) indicates that the synthesised beams are weighted linear
combinations of the primary antenna patterns; or conversely, that
there must be sufficient antennas of the correct form, such that
all of the required synthesised reception patterns, are spanned,
mathematically speaking, by the primary antenna patterns.
In the case of real systems, the primary beams 𝐡m​(𝛀^):m∈{1,⋯,M}{\\bf h}\_{m}(\\hat{\\bf\\Omega}):m\\in\\{1,\\cdots,M\\}, which are the
individual beams in the presence of all of the antennas, including
scattering, are likely to be different to one another; for
example, the antennas at the edge of an array will have different
beam patterns to those in the middle. In addition, the primary
beams may have far-out sidelobes, which can couple to warm
radiating objects such as the ground. Ideally, it must be possible
to span all possible synthesised beams, as the source moves across
the sky, including the requirement that the synthesised beams must
be near zero outside of some field of view. If nulling is not
achieved, high noise temperatures, which may be a strong function of
𝚽{\\bf\\Phi}, may result. Low noise temperatures can only be achieved
by ensuring that the reception patterns of the primary antennas can
only couple to low-noise regions of the sky, or, formally
speaking, that there are many more degrees of freedom in the
system than are needed to simply create the main lobes of
the synthesised beams.

In astronomical applications, phased arrays are used to image
incoherent or, in the case of celestial masers, partially coherent
fields. It is convenient, therefore, to introduce correlation
dyadics. Define the correlation dyadic of the incident field
according to

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)=⟨𝐄⁡(𝛀^𝟏)​𝐄^∗​(𝛀^𝟐)⟩​,\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})=\\langle{\\bf E}(\\hat{\\boldsymbol{\\Omega}}\_{1})\\hat{\\bf E}^{\\ast}(\\hat{\\boldsymbol{\\Omega}}\_{2})\\rangle\\mbox{,} |  | (10) |

where 𝐄⁡(𝛀^){\\bf E}(\\hat{\\boldsymbol{\\Omega}}) is
the complex analytic representation of the quasi-monochromatic
electric field, and ⟨⟩\\langle\\,\\,\\rangle denotes the ensemble
average. The final result can be integrated with respect to
frequency to calculate broadband behaviour, but we do not show
frequency dependence explicitly. We shall assume throughout
that the electric-field is normalized to the square root of the
impedance of free space so that the elements of
𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2}) have the units of
Wm-2Sr-2Hz-1.
The rank 2 tensor 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2}) contains complete
information about the correlations between all pairs of transverse
vector field components for any two points on the sky.
Once the correlation dyadic is known, all classical measures of
coherence follow.

The correlation between the travelling wave
amplitudes at any two output ports is given by
⟨zp​zp′∗⟩\\langle z\_{p}z\_{p^{\\prime}}^{\\ast}\\rangle, or in matrix form 𝐙=⟨𝐳𝐳†⟩∈ℂP×P{\\bf Z}=\\langle{\\bf z}{\\bf z}^{\\dagger}\\rangle\\in{\\mathbb{C}}^{P\\times P}. The elements of 𝐙{\\bf Z} can be
found by using ( [1](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E1 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) and ( [10](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E10 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")):

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=∫𝒜∫𝒜𝐭p∗​(𝛀^1)⋅𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)⋅𝐭𝐩′​(𝛀𝟐)​𝐝​𝛀𝟏​𝐝​𝛀𝟐​,Z\_{pp^{\\prime}}=\\int\_{\\cal A}\\int\_{\\cal A}{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}}\_{1})\\cdot\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})\\cdot{\\bf t}\_{p^{\\prime}}({\\boldsymbol{\\Omega}}\_{2})\\,d{\\boldsymbol{\\Omega}}\_{1}\\,d{\\boldsymbol{\\Omega}}\_{2}\\mbox{,} |  | (11) |

and because the the travelling wave amplitudes are normalized to
the square root of impedance, the elements of 𝐙{\\bf Z} have the
units WHz-1. According to ( [11](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E11 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) the correlations
at the outputs are merely the matrix elements of the source
coherence tensor with respect to the synthesised beams.

In the case of spatially incoherent, but not necessarily
unpolarized sources,

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)=𝐁¯¯​(𝛀^𝟏)​δ​(𝛀^𝟏−𝛀^𝟐)​,\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})=\\overline{\\overline{\\bf B}}(\\hat{\\boldsymbol{\\Omega}}\_{1})\\delta(\\hat{\\boldsymbol{\\Omega}}\_{1}-\\hat{\\boldsymbol{\\Omega}}\_{2})\\mbox{,} |  | (12) |

where 𝐁¯¯​(𝛀^𝟏)\\overline{\\overline{\\bf B}}(\\hat{\\boldsymbol{\\Omega}}\_{1})
contains information about the polarisation of the source, which
can be projected onto Pauli-spin matrices or spin-weighted spherical
harmonics. 𝐁¯¯​(𝛀^𝟏)\\overline{\\overline{\\bf B}}(\\hat{\\boldsymbol{\\Omega}}\_{1})
is a brightness tensor because it has units Wm-2Sr-1Hz-1.
In the case of incoherent and unpolarised sources,
( [12](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E12 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) becomes

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)=𝐁⁡(𝛀^𝟏)​𝐈¯¯​δ​(𝛀^𝟏−𝛀^𝟐)​,\\overline{\\overline{\\bf E}}(\\hat{\\bf\\Omega}\_{1},\\hat{\\bf\\Omega}\_{2})=B(\\hat{\\bf\\Omega}\_{1})\\,\\overline{\\overline{\\bf I}}\\,\\delta(\\hat{\\bf\\Omega}\_{1}-\\hat{\\bf\\Omega}\_{2})\\mbox{,} |  | (13) |

where 𝐈¯¯\\overline{\\overline{\\bf I}} is the unit dyad, and
B⁡(𝛀^1)B(\\hat{\\bf\\Omega}\_{1}) the brightness of each polarisation
in the direction of 𝛀^1\\hat{\\bf\\Omega}\_{1}.

( [13](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E13 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) can be expressed in terms of a brightness
temperature, Tb​(𝛀^)T\_{b}(\\hat{\\bf\\Omega}), through

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)=𝐡​ν𝟑𝐜𝟐​𝟏exp⁡\[𝐡​ν/𝐤𝐓𝐛​(𝛀^𝟏)\]−𝟏​𝐈¯¯​δ​(𝛀^𝟏−𝛀^𝟐)​.\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})=\\frac{h\\nu^{3}}{c^{2}}\\frac{1}{\\exp\[h\\nu/kT\_{b}(\\hat{\\boldsymbol{\\Omega}}\_{1})\]-1}\\overline{\\overline{\\bf I}}\\,\\delta(\\hat{\\boldsymbol{\\Omega}}\_{1}-\\hat{\\boldsymbol{\\Omega}}\_{2})\\mbox{.} |  | (14) |

( [14](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E14 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) predicts an infinite correlation dyadic when 𝛀^1=𝛀^2\\hat{\\boldsymbol{\\Omega}}\_{1}=\\hat{\\boldsymbol{\\Omega}}\_{2}, which occurs because an
infinitely small coherence area requires an infinitely large
number of radiators to be packed into every finite region of the
sky. Nevertheless, ( [14](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E14 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) behaves correctly when integrated
with respect to antenna power patterns, because antenna power
patterns, even in the multimode case, have finite coherence
areas.

Numerous sources can be modelled in this way, for example, a
polarized source can be combined with unpolarized emission from
the atmosphere having brightness temperature TsT\_{s}, to give

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐄¯¯​(𝛀^𝟏,𝛀^𝟐)=\[𝐡​ν𝟑𝐜𝟐​𝟏exp⁡\[𝐡​ν/𝐤𝐓𝐬\]−𝟏​𝐈¯¯+𝐁¯¯​(𝛀^𝟏)\]​δ​(𝛀^𝟏−𝛀^𝟐)​.\\overline{\\overline{\\bf E}}(\\hat{\\boldsymbol{\\Omega}}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})=\\left\[\\frac{h\\nu^{3}}{c^{2}}\\frac{1}{\\exp\[h\\nu/kT\_{s}\]-1}\\,\\overline{\\overline{\\bf I}}+\\overline{\\overline{\\bf B}}(\\hat{\\boldsymbol{\\Omega}}\_{1})\\right\]\\,\\delta(\\hat{\\boldsymbol{\\Omega}}\_{1}-\\hat{\\boldsymbol{\\Omega}}\_{2})\\mbox{.} |  | (15) |

Some care is needed when TsT\_{s} is not uniform because the source
is in the far field of the array whereas the atmosphere is usually in
in the near field; these effects can be taken into account, but we
shall not do so here.

Now illuminate a phased array with an unpolarised, incoherent source.
Substituting ( [13](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E13 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) in ( [11](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E11 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), the elements of the
coherence matrix become

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=∫𝒜B⁡(𝛀^)​𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​𝑑𝛀​,Z\_{pp^{\\prime}}=\\int\_{\\cal A}B(\\hat{\\bf\\Omega})\\,{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{,} |  | (16) |

the diagonal elements of which correspond to coupling the incoming
radiation field to the synthesised power patterns, Kp​(𝛀^)=𝐭p∗​(𝛀^)⋅𝐭p​(𝛀^)K\_{p}(\\hat{\\boldsymbol{\\Omega}})={\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p}(\\hat{\\boldsymbol{\\Omega}}), giving

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p=∫𝒜B⁡(𝛀^)​Kp​(𝛀^)​𝑑𝛀​.Z\_{pp}=\\int\_{\\cal A}B(\\hat{\\boldsymbol{\\Omega}})\\,K\_{p}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{.} |  | (17) |

The functions Kp​(𝛀^)K\_{p}(\\hat{\\boldsymbol{\\Omega}}) are direction-dependent
effective areas, and we could use Kp​(𝛀^)=Ap​Pp​(𝛀^)K\_{p}(\\hat{\\boldsymbol{\\Omega}})=A\_{p}P\_{p}(\\hat{\\boldsymbol{\\Omega}}), where ApA\_{p} is the effective
area of the pp’th synthesised beam in the most receptive direction, and
Pp​(𝛀^)P\_{p}(\\hat{\\boldsymbol{\\Omega}}) is the dimensionless power pattern.
Substituting the Planck formula in ( [17](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E17 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), and assuming
a uniform sky temperature, gives

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|  | Zp​p\\displaystyle Z\_{pp} | =\\displaystyle= | ∫𝒜h​ν3c2​1exp⁡\[h​ν/k​Ts\]−1​Ap​Pp​(𝛀^)​𝑑𝛀\\displaystyle\\int\_{\\cal A}\\frac{h\\nu^{3}}{c^{2}}\\frac{1}{\\exp\[h\\nu/kT\_{s}\]-1}\\,A\_{p}P\_{p}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}} |  | (18) |
|  |  | =\\displaystyle= | Ap​Ωpλ2​h​νexp⁡\[h​ν/k​Ts\]−1\\displaystyle\\frac{A\_{p}\\,\\Omega\_{p}}{\\lambda^{2}}\\frac{h\\nu}{\\exp\[h\\nu/kT\_{s}\]-1} |  |
|  |  | =\\displaystyle= | κp​h​νexp⁡\[h​ν/k​Ts\]−1​,\\displaystyle\\kappa\_{p}\\frac{h\\nu}{\\exp\[h\\nu/kT\_{s}\]-1}\\mbox{,} |  |

where κp=Ap​Ωp/λ2\\kappa\_{p}=A\_{p}\\,\\Omega\_{p}/\\lambda^{2} is a
coupling factor. For orthogonal primary beams, and a unitary
beam-forming network, Ap​Ωp/λ2A\_{p}\\,\\Omega\_{p}/\\lambda^{2} can
be regarded as the number of modes in the beam, which is unity,
and we arrive at the expected spectral power in the travelling
wave. Generally, however, for a phased array,
Ap​Ωp/λ2<1A\_{p}\\,\\Omega\_{p}/\\lambda^{2}<1. Certainly ∑pAp​Ωp/λ2≤M\\sum\_{p}A\_{p}\\,\\Omega\_{p}/\\lambda^{2}\\leq M, because the total
power cannot exceed the modal throughput of the primary
antennas.

( [16](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E16 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) shows that because the synthesised reception patterns are
generally not orthogonal the travelling waves at the output ports are
correlated, even when the sky brightness is uniform. If the source is not
uniform, correlations exist even when the synthesised beams are orthogonal,
which corresponds to the usual case of interferometry. Thus, each port of
a phased array records the incident flux in the usual manner, but because
the beams are not necessarily orthogonal, and may even be linearly
dependent, the travelling waves at the output ports may be
correlated, and the correlations will be more complicated than in the
usual case of interferometry.

## 3 Information Throughput and Image Recovery

Consider information throughput and image recovery. Represent the primary
physical quantities as abstract vectors. Because the incoming field,
𝐄⁡(𝛀^){\\bf E}(\\hat{\\boldsymbol{\\Omega}}), is square integrable over
the appropriate region of the sky, 𝒜\\cal A, it can be
represented by a vector \|𝐄⟩\|{\\bf E}\\rangle in Hilbert space
ℍ{\\mathbb{H}}. Regions having different shapes
and sizes correspond to different Hilbert spaces.
In the case of realizable phased arrays, where the numbers
of ports and primary antennas are finite, the measurable quantities
𝐲{\\bf y} and 𝐳{\\bf z} are finite-dimensional vectors,
𝐲∈ℂM{\\bf y}\\in{\\mathbb{C}}^{M} and 𝐳∈ℂP{\\bf z}\\in{\\mathbb{C}}^{P}, but because we wish to draw attention to
the relationship with frame theory, and to emphasize the role of
convergence, we use the more general
representations \|𝐲⟩∈ℓ2\|{\\bf y}\\rangle\\in{\\ell}^{2} and
\|𝐳⟩∈ℓ2\|{\\bf z}\\rangle\\in{\\ell}^{2}, where ℓ2{\\ell}^{2}
is the space of square-summable complex sequences. These
definitions lead to two operators, one of
which, 𝐇^:ℍ→ℓ2\\hat{\\bf H}:{\\mathbb{H}}\\rightarrow{\\ell}^{2}, maps the
incoming electric field onto the outputs of the horns, and the
other 𝚽^:ℓ2→ℓ2\\hat{\\bf\\Phi}:{\\ell}^{2}\\rightarrow{\\ell}^{2} maps the
outputs of the horns onto the outputs of the beam-forming network.
These individual operators can be combined into a single composite
operator 𝐓^=𝚽^​𝐇^:ℍ→ℓ2\\hat{\\bf T}=\\hat{\\bf\\Phi}\\hat{\\bf H}:{\\mathbb{H}}\\rightarrow{\\ell}^{2}, which describes the system as a whole.

The operation of phased arrays is intimately related to the
mathematical theory of frames. Suppose that we
have some general monochromatic field \|𝐄⟩\|{\\bf E}\\rangle, and that
we determine the inner products with respect to a set of basis
vectors 𝕋={\|𝐭p⟩,p∈1,⋯,P}{\\mathbb{T}}=\\{\|{\\bf t}\_{p}\\rangle,\\,p\\in 1,\\cdots,P\\}: zp=⟨𝐭p\|𝐄⟩z\_{p}=\\langle{\\bf t}\_{p}\|{\\bf E}\\rangle.
PP can extend to infinity, and we do not make any assumptions
about the orthonormality or linear independence of 𝕋{\\mathbb{T}}.
Under what circumstances can the original vector \|𝐄⟩\|{\\bf E}\\rangle, which represents a continuous function, be recovered
unambiguously from a discrete, possibly countable, set of complex
coefficients, and how can this be achieved? In the context
of phased arrays, we are asking under what circumstances can the
form of an incident electric field be recovered unambiguously
from the complex travelling-wave outputs.

Frame theory \[ [7](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib7 ""), [8](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib8 ""), [9](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib9 "")\] proceeds as follows. Evaluate the square
moduli of the inner products between 𝕋{\\mathbb{T}} and any general vector, \|𝐄⟩∈ℍ\|{\\bf E}\\rangle\\in{\\mathbb{H}}, and
sum the results. If there are two non-zero constants AA and BB such
that 0<A<∞0<A<\\infty and 0<B<∞0<B<\\infty, and

|     |     |     |     |
| --- | --- | --- | --- |
|  | A∥𝐄∥2≤∥𝐓^\|𝐄⟩∥2≤B∥𝐄∥2,A\\parallel{\\bf E}\\parallel^{2}\\,\\leq\\,\\parallel\\hat{\\bf T}\|{\\bf E}\\rangle\\parallel^{2}\\,\\leq B\\,\\parallel{\\bf E}\\parallel^{2}\\mbox{,} |  | (19) |

which can also be written

|     |     |     |     |
| --- | --- | --- | --- |
|  | A∥𝐄∥2≤∑p\|⟨𝐭p\|𝐄⟩ℍ\|2≤B∥𝐄∥2,A\\parallel{\\bf E}\\parallel^{2}\\,\\leq\\,\\sum\_{p}\\left\|\\langle{\\bf t}\_{p}\|{\\bf E}\\rangle\_{\\mathbb{H}}\\right\|^{2}\\,\\leq\\,B\\parallel{\\bf E}\\parallel^{2}\\mbox{,} |  | (20) |

∀\|𝐄⟩∈ℍ\\forall\\,\|{\\bf E}\\rangle\\in{\\mathbb{H}}, then the basis set
𝕋{\\mathbb{T}} is called a frame with respect to ℍ{\\mathbb{H}}.

Notice the strict use of inequalities in the allowable values of
AA and BB. In the case where A≈BA\\approx B, the frame is called
a tight frame because the inner products for all \|𝐄⟩∈ℍ\|{\\bf E}\\rangle\\in{\\mathbb{H}} lie within some small range, and the
dynamic range needed for inversion is small. When the original
basis is orthonormal, the frame bounds, AA and BB, are equal, as
can be appreciated by inserting \|𝐄⟩=\|𝐭p′⟩\|{\\bf E}\\rangle=\|{\\bf t}\_{p^{\\prime}}\\rangle in ( [20](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E20 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")). If the frame is normalized, AA is
a measure of the redundancy in the frame. If a basis set
constitutes a frame, then it can be shown through ( [19](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E19 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays"))
alone that the electric field can be recovered unambiguously from
the inner products, and the more tightly bound the frame, the more
tightly bound the inverse, and the more stable the image recovery
process. The frame condition, ( [19](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E19 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")), is completely general,
and applies for any continuous function, even though an infinite
number of possibly linearly dependent basis functions may be used.
Phased arrays have a finite number of ports,
but can nevertheless span spatially band-limited functions having
finite support, and can therefore form frames with respect to
fields carrying finite information.

Because the synthesised beam
patterns of a phased array may be non-orthogonal, and even
linearly dependent, the recovery of the original field, through an
operator we shall call 𝐓^−1\\hat{\\bf T}^{-1}, is best implemented
by the introduction of dual vectors, which correspond to dual
beams. The dual vectors \|𝐭~p⟩\|\\widetilde{\\bf t}\_{p}\\rangle of any
given frame 𝕋{\\mathbb{T}}, with respect to Hilbert space ℍ{\\mathbb{H}}, are given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | \|𝐭~p⟩=𝐒^−1​\|𝐭p⟩​,\|\\widetilde{\\bf t}\_{p}\\rangle=\\hat{\\bf S}^{-1}\|{\\bf t}\_{p}\\rangle\\mbox{,} |  | (21) |

where 𝐒^=𝐓^†​𝐓^\\hat{\\bf S}=\\hat{\\bf T}^{\\dagger}\\hat{\\bf T} is
non-singular, and can therefore be inverted. The dual basis set,
which we shall call 𝕋~={\|𝐭~p⟩,p∈1,⋯,P}\\widetilde{\\mathbb{T}}=\\{\|\\widetilde{\\bf t}\_{p}\\rangle,\\,p\\in 1,\\cdots,P\\}, has the same degree of
completeness as the original frame, 𝕋{\\mathbb{T}}, and therefore
it too constitutes a frame with respect to ℍ{\\mathbb{H}}. Indeed,
two representations of any general \|𝐄⟩\|{\\bf E}\\rangle are possible:

|     |     |     |     |
| --- | --- | --- | --- |
|  | \|𝐄⟩=∑p⟨𝐭p​\|𝐄⟩\|𝐭~p⟩\|𝐄⟩=∑p⟨𝐭~p​\|𝐄⟩\|𝐭p⟩​.\|{\\bf E}\\rangle=\\sum\_{p}\\langle{\\bf t}\_{p}\|{\\bf E}\\rangle\\,\|\\widetilde{\\bf t}\_{p}\\rangle\\hskip 28.45274pt\|{\\bf E}\\rangle=\\sum\_{p}\\langle\\widetilde{\\bf t}\_{p}\|{\\bf E}\\rangle\\,\|{\\bf t}\_{p}\\rangle\\mbox{.} |  | (22) |

( [22](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E22 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")) shows that if one calculates a set of coefficients by
taking the inner products with a frame, then one inverts the
process by reconstructing the field using the dual vectors. In the
case where the basis vectors are perfectly complete with respect
to ℍ{\\mathbb{H}}, but not necessarily orthogonal, the basis is
called a Riesz basis, and the basis set 𝕋{\\mathbb{T}} and dual set
𝕋~\\widetilde{\\mathbb{T}} are biorthogonal: ⟨𝐭~p\|𝐭p′⟩=δp​p′:∀p,p′∈1,⋯,P\\langle\\widetilde{\\bf t}\_{p}\|{\\bf t}\_{p^{\\prime}}\\rangle=\\delta\_{pp^{\\prime}}:\\forall\\,p,p^{\\prime}\\in 1,\\cdots,P.

In the case where the basis vectors do not constitute a frame, but
an attempt is made to reconstruct the original field vector using the
duals,

|     |     |     |     |
| --- | --- | --- | --- |
|  | \|𝐄′⟩=∑p⟨𝐭p​\|𝐄⟩\|𝐭~p⟩​,\|{\\bf E}^{\\prime}\\rangle=\\sum\_{p}\\langle{\\bf t}\_{p}\|{\\bf E}\\rangle\\,\|\\widetilde{\\bf t}\_{p}\\rangle\\mbox{,} |  | (23) |

the reconstructed vector \|𝐄′⟩\|{\\bf E}^{\\prime}\\rangle cannot, for all
vectors in ℍ{\\mathbb{H}}, be the same as the original vector
\|𝐄⟩\|{\\bf E}\\rangle. It can be shown, however, that the error vector
\|𝐄⟩−\|𝐄′⟩\|{\\bf E}\\rangle-\|{\\bf E}^{\\prime}\\rangle is orthogonal to the basis
vectors. Consequently, \|𝐄′⟩\|{\\bf E}^{\\prime}\\rangle is the orthogonal
projection of \|𝐄⟩\|{\\bf E}\\rangle onto 𝕊{\\mathbb{S}}, the subspace
spanned by the under complete set of basis vectors. In other words
the solution is as close as possible to the original field vector
to within the degrees of freedom available.

The relevance to phased arrays is clear; one can measure the
complex outputs of a phased array, and if the synthesised
reception patterns constitute a frame with respect to the Hilbert
space defined by the shape, extent, and illumination of the input
reference surface, then the continuous, coherent, incoming field
can be reconstructed completely from the complex travelling wave
amplitudes at the output ports. If the reception patterns do
not constitute a frame, reconstruction leads to the least square
fit that is consistent with the degrees of freedom to which the
phased array is sensitive. If the field of interest has passed
through an optical system, which can only ever transmit a finite
number of modes, then frames can in principle be formed; if
the input surface corresponds to the sky, frames are not
possible, because the dimensionality of a field, even over a finite
region, is infinite. It is possible, however, to form a frame with
respect to some given class of object, as will be discussed. It is also
possible to synthesize more and more beams to tighten a frame, thereby
increasing the stability of the image recovery process. Central to
this model is the notion of dual beams. Every synthesised beam
has a dual beam, and the concept of dual beams is central to
understanding the optical physics of phased arrays, and the image
recovery process.

To this point it has been assumed that the incoming field is fully
coherent, but in the case of astronomical phased arrays the
incoming field is usually incoherent, and sometimes only the
powers are measured at 𝒞\\cal C. According to ( [16](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E16 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), the
self and cross correlations at the output ports of a phased array,
for an incoherent, unpolarized source are given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=∫𝒜B⁡(𝛀^)​Sp​p′∗​(𝛀^)​𝑑𝛀​,Z\_{pp^{\\prime}}=\\int\_{\\cal A}B(\\hat{\\boldsymbol{\\Omega}})\\,S\_{pp^{\\prime}}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{,} |  | (24) |

where

|     |     |     |     |
| --- | --- | --- | --- |
|  | Sp​p′∗​(𝛀^)=𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​,S\_{pp^{\\prime}}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})={\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\mbox{,} |  | (25) |

but according to ( [24](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E24 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")) the elements of the correlation
matrix are merely the inner products of B⁡(𝛀^)B(\\hat{\\boldsymbol{\\Omega}}) with respect to Sp​p′​(𝛀^)​∀p,p′∈{1,⋯,P}S\_{pp^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,\\,\\forall\\,\\,p,p^{\\prime}\\in\\{1,\\cdots,P\\}. Hence
once again, frame theory can be used to determine the degree to
which B⁡(𝛀^)B(\\hat{\\boldsymbol{\\Omega}}) can be recovered from the
correlations between the travelling waves at 𝒞\\cal C. The case
were only the powers are measured, Zp​p​∀p∈{1,⋯,P}Z\_{pp}\\,\\,\\forall\\,\\,p\\in\\{1,\\cdots,P\\}, is a special case of ( [24](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E24 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")), and
corresponds to determining the degree to which the synthesised
power patterns span the source brightness distributions of interest.
It seems, therefore, that frames can be defined for either fully
coherent fields with correlation measurement, for incoherent fields
with correlation measurement, or for incoherent fields with only power
measurement. We shall call these possibilities field frames,
interferometric frames, and intensity frames respectively.
Note that the term interferometric does not necessarily imply
that an aperture synthesis interferometer is being used, but
merely that the correlations between the travelling waves at the outputs
are measured. Each of these frames can be associated with dual beams of
some kind. In fact, it is straightforward to formulate a more general
theory, and ask whether a set of synthesised beams forms a frame with
respect to the full coherence tensor field of the incoming radiation.
This more general theory has interesting applications, but we shall not
described it here.

Suppose that the goal is to reconstruct the intensity distribution
of an astronomical source, and one needs to know whether the basis
Sp​p′​(𝛀^)​∀p,p′∈{1,⋯,P}S\_{pp^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,\\,\\forall\\,\\,p,p^{\\prime}\\in\\{1,\\cdots,P\\} forms an interferometric frame. There is a problem,
however, because in assuming that the source is spatially
incoherent, we have tacitly assumed that the brightness
distribution is a member of an infinite dimensional space. To
answer the question correctly, we need to ask whether the phased
array is suitable for recovering brightness from the vector space
of the brightness distributions of interest. One approach is to
describe the range of possible brightness distributions as a finite,
weighted linear combination of basis functions, ψn​(𝛀^):n∈{1,⋯,N}\\psi\_{n}(\\hat{\\boldsymbol{\\Omega}}):n\\in\\{1,\\cdots,N\\}. These functions
could, for example, be radial basis functions, or delta functions
at certain sample points. The functions need not correspond to a
single region, but could correspond to different regions of the
sky that need to be imaged simultaneously.

The intensity on the sky, according to our chosen class, can be
written

|     |     |     |     |
| --- | --- | --- | --- |
|  | B⁡(𝛀^)=∑nan​ψn​(𝛀^)​,B(\\hat{\\boldsymbol{\\Omega}})=\\sum\_{n}a\_{n}\\,\\psi\_{n}(\\hat{\\boldsymbol{\\Omega}})\\mbox{,} |  | (26) |

and therefore, according to ( [24](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E24 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")), the correlations between
the travelling waves at the output ports become

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=∑nan​Fp​p′,n​,Z\_{pp^{\\prime}}=\\sum\_{n}a\_{n}\\,F\_{pp^{\\prime},n}\\mbox{,} |  | (27) |

where

|     |     |     |     |
| --- | --- | --- | --- |
|  | Fp​p′,n=∫𝒜Sp​p′∗​(𝛀^)​ψn​(𝛀^)​𝑑𝛀​.F\_{pp^{\\prime},n}=\\int\_{\\cal A}S\_{pp^{\\prime}}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\psi\_{n}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{.} |  | (28) |

Defining the matrix 𝐅{\\bf F} whose elements are Fq,nF\_{q,n}, where
p​p′pp^{\\prime} is now indexed by the single integer qq, the frame
condition ( [19](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E19 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")) becomes

|     |     |     |     |
| --- | --- | --- | --- |
|  | A≤𝐚†​𝐅†​𝐅𝐚≤B∀𝐚∈ℂN​.A\\leq{\\bf a}^{\\dagger}{\\bf F}^{\\dagger}{\\bf F}{\\bf a}\\leq B\\hskip 14.22636pt\\forall\\,{\\bf a}\\in{\\mathbb{C}}^{N}\\mbox{.} |  | (29) |

( [29](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E29 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")) has the Hermitian form, and it is well known that the
stationary values of the Hermitian form occur when the unit
vector 𝐚{\\bf a} points in the same directions as the eigenvectors
of 𝐅†​𝐅{\\bf F}^{\\dagger}{\\bf F}, with the stationary values being
the corresponding eigenvalues. AA and BB, and hence the tightness
of the frame, can be determined by finding the largest and smallest
eigenvalues of the Hermitian operator 𝐅†​𝐅{\\bf F}^{\\dagger}{\\bf F},
which can be found analytically or numerically. Although, the operator
𝐅†​𝐅{\\bf F}^{\\dagger}{\\bf F} maps a finite dimensional space onto itself,
the mapping passes through a space having infinite dimensions and
therefore the integrals in ( [28](https://ar5iv.labs.arxiv.org/html/0707.1580#S3.E28 "In 3 Information Throughput and Image Recovery ‣ Theoretical Analysis of Astronomical Phased Arrays")) should be evaluated analytically
if at all possible. The operator 𝐅†​𝐅{\\bf F}^{\\dagger}{\\bf F} simply maps
the intensity distribution coefficients of the source onto the
measured quantities at the output ports of the array and then back
again onto the coefficients. If the basis functions
Sp​p′​(𝛀^)S\_{pp^{\\prime}}(\\hat{\\boldsymbol{\\Omega}}) do not span all possible intensity
distributions, information is lost when an observation is made,
and it is not possible to recover complete information about the
source.

In the case where the basis functions correspond to sample points
𝛀^n\\hat{\\boldsymbol{\\Omega}}\_{n}, we have ψn​(𝛀^)=δ⁡(𝛀^−𝛀n)\\psi\_{n}(\\hat{\\boldsymbol{\\Omega}})=\\delta(\\hat{\\boldsymbol{\\Omega}}-{\\boldsymbol{\\Omega}}\_{n})
and Fp​p′,n=Sp​p′∗​(𝛀^n)F\_{pp^{\\prime},n}=S\_{pp^{\\prime}}^{\\ast}(\\hat{\\boldsymbol{\\Omega}}\_{n}).
Although, in practice, a frame cannot be formed that reproduces the sky
brightness at every one of an infinite number of points, a
frame can be formed with respect to a finite number of sample points.
Also, shapelets\[ [10](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib10 ""), [11](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib11 ""), [12](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib12 "")\], which are essentially Gaussian Hermite and
Gaussian Laguerre polynomials, are now being used to parameterize the
brightness distributions of astronomical sources, such as galaxies. It
would therefore be possible to check whether an imaging phased
array forms a frame with respect to a set of shapelets, and to recover
the shapelet coefficients directly from observations.

## 4 Natural Modes of Phased Arrays

Superficially speaking, the natural modes of a phased array
are those orthogonal field distributions that can pass through the
horns and beam-forming network with high efficiency. When the
synthesised beams are linearly dependent, or even if they are simply
non-orthogonal, the forms of the natural modes are not directly known.
The natural modes are, however, central to understanding noise and
correlations, to understanding quantum statistical behaviour, which
is important at sub-millimetre wavelengths, and to understanding the
operation of interferometric phased arrays.

Suppose that a telescope is equipped with an imaging phased array.
As described previously, the process of projecting a
coherent field onto the complex travelling wave amplitudes at the
output ports is described by the mapping 𝐓:\|𝐱⟩⟼\|𝐳⟩{\\bf T}:\|{\\bf x}\\rangle\\longmapsto\|{\\bf z}\\rangle as 𝐓:ℍ→ℓ2{\\bf T}:{\\mathbb{H}}\\rightarrow{\\ell}^{2}. The phased array acts as a linear operator between
two Hilbert spaces: the space of square integrable functions over
the input reference surface, and the space of square summable
complex sequences. Because the operator maps between two different
Hilbert spaces, it does not make sense to search for the
eigenfunctions of such an operator in an attempt to find the
natural modes.

For any real system, it is certainly known that every incoming
field carries a finite amount of power, and the associated complex
travelling waves at the output ports carry a finite amount of
power: 𝐓{\\bf T} is therefore bounded. More importantly, a real
system can only transmit a limited amount of information, because
a finite number of primary antennas is used: 𝐓{\\bf T} is
therefore Hilbert-Schmidt. It follows that the integral operator
that maps the incoming field distribution onto the output ports
can be written in the form \[ [13](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib13 "")\]

|     |     |     |     |
| --- | --- | --- | --- |
|  | zp=∫𝒜∑iσi​𝐔ip​𝐕i∗​(𝛀^)⋅𝐄⁡(𝛀^)​𝑑𝛀​.z\_{p}=\\int\_{\\cal A}\\sum\_{i}\\sigma\_{i}\\,{\\bf U}\_{i}^{p}{\\bf V}\_{i}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf E}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{.} |  | (30) |

It is a feature of the Hilbert-Schmidt decomposition that
{𝐕i(𝛀^):i∈1,⋯,P}\\{{\\bf V}\_{i}(\\hat{\\bf\\Omega}):i\\in 1,\\cdots,P\\}
and {𝐔ip:p∈1,⋯,P;i∈1,⋯,P}\\{{\\bf U}\_{i}^{p}:p\\in 1,\\cdots,P\\,;\\,i\\in 1,\\cdots,P\\} are orthogonal
sets and therefore, according to ( [30](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E30 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")), the operation of a phased
array can be regarded as first mapping the incoming field onto the
beams, 𝐕i​(𝛀^){\\bf V}\_{i}(\\hat{\\bf\\Omega}), scaling by the singular
values, σi\\sigma\_{i}, and reconstructing the complex travelling
wave amplitudes at the output ports through the basis vectors
𝐔ip{\\bf U}\_{i}^{p}. Those reception patterns, 𝐕i​(𝛀^){\\bf V}\_{i}(\\hat{\\bf\\Omega}),
associated with non-zero singular values span the field distributions at
the input to which the phased array is sensitive, and those output vectors
𝐔ip{\\bf U}\_{i}^{p}, associated with non-zero singular values span the
vectors at the output to which the phased array can couple. These
are the natural modes of a phased array, and we shall call them the
eigenfields, by analogy with bolometric interferometers \[ [14](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib14 "")\].
In the case of fields that have been discretised for numerical calculation,
𝐕i​(𝛀^){\\bf V}\_{i}(\\hat{\\bf\\Omega}), 𝐔ip{\\bf U}\_{i}^{p}, and σi\\sigma\_{i}
correspond to the singular vectors and singular values of the singular
value decomposition of the phased array’s transmission matrix 𝐓{\\bf T}.

It can be shown, \[ [14](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib14 "")\], although we shall not do so here, that
the eigenfields on the sky are the eigenfunctions of the
Hermitian operator that maps the sky field onto the travelling
waves at the output ports, and then back again onto the sky in a
time reversed manner. The input eigenfields are those field
distributions that remain unchanged in form after this complete
round trip. Likewise, the output eigenfields are the eigenvectors
of the Hermitian operator that maps the travelling waves at the
output ports onto the sky in a time reversed manner, and then
forward again to the output ports. The output eigenfields are
those discrete vectors that can make this round trip unchanged in
form.

The eigenfields have many unique properties. First, they
represent the primary paths by which information can pass from the
sky to the output ports. The input eigenfields on the sky are
mutually orthogonal, even though the synthesised beams may be
non-orthogonal or linearly dependent. The output eigenfields,
which are actually discrete vectors in this case, are also
mutually orthogonal. Secondly, the number of singular values,
σi\\sigma\_{i}, greater than some threshold is the modal throughput
of the system. Thirdly, if two phased arrays are placed
side-by-side, with the intention of creating an aperture synthesis
interferometer, the input eigenfields having non-zero singular values
associated with the different telescopes are mutually orthogonal\[ [14](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib14 "")\],
which makes them ideal for analysing the behaviour of interferometers.

Now consider how the concepts of frames and eigenfields can be
used to construct powerful models of imaging phased arrays. The
correlations at the output ports can be found through
Zp​p′=⟨zp​zp′∗⟩Z\_{pp^{\\prime}}=\\langle z\_{p}z\_{p^{\\prime}}^{\\ast}\\rangle; using ( [30](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E30 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")),

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=∑i∑i′σiσi′𝐔ip𝐔i′p′∗∫𝒜∫𝒜𝐕i∗(𝛀^1)⋅E¯¯(𝛀^1,𝛀^2)⋅𝐕i′(𝛀^2)d𝛀1d𝛀2,Z\_{pp^{\\prime}}=\\sum\_{i}\\sum\_{i^{\\prime}}\\sigma\_{i}\\sigma\_{i^{\\prime}}{\\bf U}\_{i}^{p}{\\bf U}\_{i^{\\prime}}^{p^{\\prime}\\ast}\\int\_{\\cal A}\\int\_{\\cal A}{\\bf V}\_{i}^{\\ast}(\\hat{\\boldsymbol{\\Omega}}\_{1})\\cdot\\overline{\\overline{E}}(\\hat{\\bf\\Omega}\_{1},\\hat{\\boldsymbol{\\Omega}}\_{2})\\cdot{\\bf V}\_{i^{\\prime}}(\\hat{\\boldsymbol{\\Omega}}\_{2})\\,d{\\boldsymbol{\\Omega}}\_{1}\\,d{\\boldsymbol{\\Omega}}\_{2}\\mbox{,} |  | (31) |

which is equivalent to ( [11](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E11 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), but with the array described
in terms of its natural modes. ( [31](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E31 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")) describes the
projection of the coherence tensor of the source onto the input
eigenfields, the eigenfield coefficients are then multiplied by
the singular values, and the correlations at the output ports
assembled through the output eigenfields. It is interesting to
observe that if a phased array is illuminated by an incoherent,
unpolarized, spatially uniform source, then using ( [14](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E14 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays"))
with a uniform temperature TsT\_{s}, and ( [31](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E31 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")), gives

|     |     |     |     |
| --- | --- | --- | --- |
|  | Zp​p′=h​νexp⁡\[h​ν/k​T\]−1∑iσi2𝐔ip𝐔ip′∗,Z\_{pp^{\\prime}}=\\frac{h\\nu}{\\exp\[h\\nu/kT\]-1}\\sum\_{i}\\sigma\_{i}^{2}{\\bf U}\_{i}^{p}{\\bf U}\_{i}^{p^{\\prime}\\ast}\\mbox{,} |  | (32) |

where we have followed a procedure similar to that described by
( [18](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.Ex2 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")). ( [32](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E32 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")) shows that the correlations at the output
are merely those associated with the incoherent excitation of the output
eigenfields. Indeed the total power, WW, becomes

|     |     |     |     |
| --- | --- | --- | --- |
|  | W=∑pZp​p=h​νexp⁡\[h​ν/k​T\]−1​∑iσi2​,W=\\sum\_{p}Z\_{pp}=\\frac{h\\nu}{\\exp\[h\\nu/kT\]-1}\\sum\_{i}\\sigma\_{i}^{2}\\mbox{,} |  | (33) |

where we have used the orthogonality of the output eigenfields.
Comparing with ( [18](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.Ex2 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")),

|     |     |     |     |
| --- | --- | --- | --- |
|  | ∑pAp​Ωp/λ2=∑pσp2≤M​.\\sum\_{p}A\_{p}\\,\\Omega\_{p}/\\lambda^{2}=\\sum\_{p}\\sigma\_{p}^{2}\\,\\leq\\,M\\mbox{.} |  | (34) |

The total throughput is determined by the number of singular values
significantly greater than some threshold, usually determined by the
noise. ( [34](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E34 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")) can be regarded as a statement about the modal
throughput of a complete array; an important performance metric of
phased arrays can therefore be determined from the synthesised beams
alone.

## 5 Noise

Consider the case where the primary antennas and beam forming
network are are made up of passive components, such as a planar
array and microstrip coupling network. What noise sources appear
at the output as a consequence of the losses? Because the signal
is uncorrelated with the internally generated noise, the
correlation matrix at the output can be written 𝐙′=𝐙+𝐙N{\\bf Z}^{\\prime}={\\bf Z}+{\\bf Z}\_{N}, where 𝐙′{\\bf Z}^{\\prime} is the combined output,
𝐙{\\bf Z} the output due to the signal, and 𝐙N{\\bf Z}\_{N}
the output due to the thermal noise from the losses.

If the array is illuminated by a uniform, unpolarized thermal
source, and the losses in the array are at the same temperature as
the source, TsT\_{s}, the travelling waves at the output will be
uncorrelated, and appear to originate from a thermal source having
temperature TsT\_{s}. Under these circumstances, using ( [16](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E16 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays"))

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐙′=h​νexp⁡\[h​ν/k​Ts\]−1​𝐈P=h​ν3c2​1exp⁡\[h​ν/k​Ts\]−1​𝐑+𝐙N​,{\\bf Z}^{\\prime}=\\frac{h\\nu}{\\exp\[h\\nu/kT\_{s}\]-1}{\\bf I}\_{P}=\\frac{h\\nu^{3}}{c^{2}}\\frac{1}{\\exp\[h\\nu/kT\_{s}\]-1}\\,{\\bf R}+{\\bf Z}\_{N}\\mbox{,} |  | (35) |

where 𝐑{\\bf R} has elements

|     |     |     |     |
| --- | --- | --- | --- |
|  | Rp​p′=∫𝒜𝐭p∗​(𝛀^)⋅𝐭p′​(𝛀^)​𝑑𝛀​.R\_{pp^{\\prime}}=\\int\_{\\cal A}\\,{\\bf t}\_{p}^{\\ast}(\\hat{\\boldsymbol{\\Omega}})\\cdot{\\bf t}\_{p^{\\prime}}(\\hat{\\boldsymbol{\\Omega}})\\,d{\\boldsymbol{\\Omega}}\\mbox{.} |  | (36) |

Rearranging,

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐙N=h​νexp⁡\[h​ν/k​Ts\]−1​\[𝐈P−1λ2​𝐑\]​.{\\bf Z}\_{N}=\\frac{h\\nu}{\\exp\[h\\nu/kT\_{s}\]-1}\\left\[{\\bf I}\_{P}-\\frac{1}{\\lambda^{2}}\\,{\\bf R}\\right\]\\mbox{.} |  | (37) |

If the synthesised beam patterns are known, and all of the overlap
integrals calculated, giving 𝐑{\\bf R}, the thermal noise and the
correlations at the output, 𝐙N{\\bf Z}\_{N}, can be found.

Now consider the case where the phased array is not passive, for
example when HEMT amplifiers are used, but the noise temperatures
of the primary receiving antennas are known, and equal. By definition,
the noise temperature of a receiver is the temperature that a matched
source would need to have in order to generate the same output
as a noiseless, but otherwise identical system. Let us call the
associated noise correlation matrix at the output 𝐙N′{\\bf Z}\_{N}^{\\prime}, where
𝐙′=𝐙+𝐙N′{\\bf Z}^{\\prime}={\\bf Z}+{\\bf Z}\_{N}^{\\prime}, then to find 𝐙N′{\\bf Z}\_{N}^{\\prime} we
simply need to calculate the coefficients of a uniform sky having the
same physical temperature as the noise temperatures of the receivers.
Using ( [14](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E14 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) and ( [11](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E11 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")) we get

|     |     |     |     |
| --- | --- | --- | --- |
|  | 𝐙N=h​νexp⁡\[h​ν/k​TN\]−1​1λ2​𝐑​,{\\bf Z}\_{N}=\\frac{h\\nu}{\\exp\[h\\nu/kT\_{N}\]-1}\\,\\frac{1}{\\lambda^{2}}{\\bf R}\\mbox{,} |  | (38) |

where TNT\_{N} is the noise temperature of the individual receivers.
In both cases, if the beams are orthogonal, the noise sources are
uncorrelated. In the case where the primary receiver temperatures
are different, a similar scheme can easily be established.

## 6 Fluctuations and Sensitivity

The last step in the analysis is to determine the fluctuations in
power and the correlations between the fluctuations in power at
the output ports of a phased array once 𝐙{\\bf Z}, or 𝐙′{\\bf Z}^{\\prime},
is known; after all, it is the fluctuations that ultimately determine
the sensitivity of an instrument. Following recent work on multimode
detectors\[ [14](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib14 ""), [15](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib15 "")\], it is straightforward to determine the
fluctuations in any power-related measurement that is made at
the output ports.

If 𝐙{\\bf Z} is the coherence matrix of the complex travelling wave
amplitudes at the output ports, and 𝐖∈ℂP×P{\\bf W}\\in{\\mathbb{C}}^{P\\times P}
is a matrix that characterises the nature of the measurement being made,
the expectation value of the measurement, ⟨P⟩\\langle P\\rangle, is given
by

|     |     |     |     |
| --- | --- | --- | --- |
|  | P¯=⟨P⟩=Δ​ν​Tr​𝐖𝐙​,\\bar{P}=\\langle P\\rangle=\\Delta\\nu\\,\\mbox{Tr}{\\bf W}{\\bf Z}\\mbox{,} |  | (39) |

where Δ​ν\\Delta\\nu is the RF bandwidth. ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) can be appreciated by
remembering that the trace of the product of two matrices constitutes an
inner product in the abstract vector space of matrices. Thus, ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays"))
describes the way in which the state of coherence of the source projects
onto the state of coherence to which the measurement system is sensitive.
The structure of ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) has be explored in detail, and leads to the
coupled-mode theory of power detection\[ [15](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib15 ""), [16](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib16 ""), [17](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib17 "")\].

More significantly, it has also been shown\[ [16](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib16 "")\] that if two measurements
are made, one represented by 𝐖a{\\bf W}^{a} and one by 𝐖b{\\bf W}^{b},
then the covariance of the measurements, Cov​\[Pa,Pb\]=⟨(Pa−P¯a)​(Pb−P¯b)⟩\\mbox{Cov}\\left\[P^{a},P^{b}\\right\]=\\langle(P^{a}-\\bar{P}^{a})(P^{b}-\\bar{P}^{b})\\rangle, is
given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov​\[Pa,Pb\]=Δ​ντ​\[Tr​𝐖a​𝐙𝐖b​𝐙+δa​b​h​ν0​Tr​𝐖a​𝐙\]​,\\mbox{Cov}\\left\[P^{a},P^{b}\\right\]=\\frac{\\Delta\\nu}{\\tau}\\left\[\\mbox{Tr}{\\bf W}^{a}{\\bf Z}{\\bf W}^{b}{\\bf Z}+\\delta\_{ab}h\\nu\_{0}\\mbox{Tr}{\\bf W}^{a}{\\bf Z}\\right\]\\mbox{,} |  | (40) |

where ν0\\nu\_{0} is the central RF frequency, and τ\\tau the time for
which the output is integrated. ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) is valid for thermal sources, and
when the integration time is much longer than either the coherence time of the
source or the intrinsic response time of the detector. It is valid, therefore,
for astronomical phased arrays. The first term in ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) can be
identified with the noise associated with classical waves, whereas the second
term with the noise associated with photon counting. Thus, ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays"))
contains the transition from fully bunched to Poisson statistics as the
wavelength of operation moves from the microwave range through into the far
infrared. ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) contains a considerable amount of detail, including
partition noise, and the randomization of photon arrival times due to
losses and imperfect quantum efficiencies.

We can imagine three principle measurements at the output ports. First
consider a measurement having the matrix elements

|     |     |     |     |
| --- | --- | --- | --- |
|  | Wi​ja=ηa​δi​j​δi​a​,W\_{ij}^{a}=\\eta^{a}\\delta\_{ij}\\delta\_{ia}\\mbox{,} |  | (41) |

where i,j∈{1,⋯,P}i,j\\in\\{1,\\cdots,P\\}, which is diagonal with just one
non-zero element. Substituting ( [41](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E41 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) in ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) gives

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|  | ⟨Pa⟩\\displaystyle\\langle P^{a}\\rangle | =\\displaystyle= | Δ​ν​∑i​jWi​ja​Zj​i\\displaystyle\\Delta\\nu\\,\\sum\_{ij}W\_{ij}^{a}Z\_{ji} |  | (42) |
|  |  | =\\displaystyle= | Δ​ν​ηa​∑i​jδi​j​δi​a​Zj​i\\displaystyle\\Delta\\nu\\,\\eta^{a}\\,\\sum\_{ij}\\delta\_{ij}\\delta\_{ia}Z\_{ji} |  |
|  |  | =\\displaystyle= | Δ​ν​ηa​Za​a​.\\displaystyle\\Delta\\nu\\,\\eta^{a}Z\_{aa}\\mbox{.} |  |

( [41](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E41 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) therefore corresponds to measuring the expectation value of the
power at port aa, using a detector having quantum efficiency ηa\\eta^{a}.
Likewise, a power measurement at port bb is characterised by

|     |     |     |     |
| --- | --- | --- | --- |
|  | Wi​jb=ηb​δi​j​δi​b​.W\_{ij}^{b}=\\eta^{b}\\delta\_{ij}\\delta\_{ib}\\mbox{.} |  | (43) |

In the case of a phased array where only powers are measured,
which would correspond to an ordinary imaging array with the
appropriate synthesised beams, ( [41](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E41 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) and ( [43](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E43 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) can
be substituted into ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) to give

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov​\[Pa,Pb\]=Δ​ντ​\[ηa​ηb​\|Za​b\|2+δa​b​h​ν0​ηa​Za​a\]​.\\mbox{Cov}\\left\[P^{a},P^{b}\\right\]=\\frac{\\Delta\\nu}{\\tau}\\left\[\\eta^{a}\\eta^{b}\|Z\_{ab}\|^{2}+\\delta\_{ab}h\\nu\_{0}\\eta^{a}Z\_{aa}\\right\]\\mbox{.} |  | (44) |

When we are interested in the true fluctuations in the power
at port aa, as distinct from the fluctuations in the
absorbed power, then a=ba=b and ηa=ηb=1\\eta^{a}=\\eta^{b}=1, and the
root mean square fluctuation, Δ​Pa\\Delta P^{a}, is given by

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Pa={Cov​\[Pa,Pa\]}1/2=(Δ​ντ)1/2​\[\|Za​a\|2+h​ν0​Za​a\]1/2​.\\Delta P^{a}=\\left\\{\\mbox{Cov}\\left\[P^{a},P^{a}\\right\]\\right\\}^{1/2}=\\left(\\frac{\\Delta\\nu}{\\tau}\\right)^{1/2}\\left\[\|Z\_{aa}\|^{2}+h\\nu\_{0}Z\_{aa}\\right\]^{1/2}\\mbox{.} |  | (45) |

We can also form the quantity, which is the noise in the measurement
normalised by the signal,

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Pa⟨Pa⟩=1τ1/2​\[1Δ​ν+h​ν0Δ​ν​Za​a\]1/2​.\\frac{\\Delta P^{a}}{\\langle P^{a}\\rangle}=\\frac{1}{\\tau^{1/2}}\\left\[\\frac{1}{\\Delta\\nu}+\\frac{h\\nu\_{0}}{\\Delta\\nu Z\_{aa}}\\right\]^{1/2}\\mbox{.} |  | (46) |

or

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Pa⟨Pa⟩=1(Δ​ν​τ)1/2​\[1+Δ​νn¯\]1/2​,\\frac{\\Delta P^{a}}{\\langle P^{a}\\rangle}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\left\[1+\\frac{\\Delta\\nu}{\\bar{n}}\\right\]^{1/2}\\mbox{,} |  | (47) |

where n¯=Δ​ν​Za​a/h​ν0\\bar{n}=\\Delta\\nu Z\_{aa}/h\\nu\_{0} is
the average photon rate. In the case where the photon rate is
much greater than the bandwidth, or equivalently many
photons arrive in the radiation’s coherence time, the sensitivity
scales according to the radiometer equation; in the case where
very few photons arrive in the coherence time, the sensitivity
scales according to photon counting.

Likewise the root mean square correlation, Δ​Pa​b\\Delta P^{ab}, between
the fluctuations in two different power measurements, a≠ba\\neq b, is
given by ( [44](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E44 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) as

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Pa​b={Cov​\[Pa,Pb\]}1/2=(Δ​ντ)1/2​\|Za​b\|​,\\Delta P^{ab}=\\left\\{\\mbox{Cov}\\left\[P^{a},P^{b}\\right\]\\right\\}^{1/2}=\\left(\\frac{\\Delta\\nu}{\\tau}\\right)^{1/2}\|Z\_{ab}\|\\mbox{,} |  | (48) |

and we also have

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Pa​b⟨Pa⟩1/2​⟨Pb⟩1/2=1(Δ​ν​τ)1/2​\|Za​b\|(Za​a​Zb​b)1/2=1(Δ​ν​τ)1/2​\|Γa​b\|​,\\frac{\\Delta P^{ab}}{\\langle P^{a}\\rangle^{1/2}\\langle P^{b}\\rangle^{1/2}}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\frac{\|Z\_{ab}\|}{(Z\_{aa}Z\_{bb})^{1/2}}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\|\\Gamma^{ab}\|\\mbox{,} |  | (49) |

where \|Γa​b\|\|\\Gamma^{ab}\| is the correlation coefficient. ( [49](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E49 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays"))
is the Hanbury Brown-Twiss effect for phased arrays. It does not show Poisson
noise because the Poisson term corresponds to photon arrival times that are
uncorrelated. In the case where the synthesised beams are orthogonal,
and the source uniform, Za​b=0Z\_{ab}=0, and the fluctuations in the powers
measured at different ports are uncorrelated. In the case of non-orthogonal
beams, or a non-uniform source on the sky, the fluctuations are correlated,
and the correlations must be taken into account when calculating the noise in
the reconstructed image.

Now consider the case where we wish to measure the correlations between
the travelling waves at the output ports, say aa and bb, for the purpose of
recovering an image, as in done in interferometry. In this context, there are
two measurement-system matrices of interest:

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|  | Ri​ja​b\\displaystyle R\_{ij}^{ab} | =\\displaystyle= | ηa​b​12​(δi​a​δj​b+δi​b​δj​a)\\displaystyle\\eta^{ab}\\frac{1}{2}(\\delta\_{ia}\\delta\_{jb}+\\delta\_{ib}\\delta\_{ja}) |  | (50) |
|  | Ii​ja​b\\displaystyle I\_{ij}^{ab} | =\\displaystyle= | ηa​b​i2​(δi​a​δj​b−δi​b​δj​a)​,\\displaystyle\\eta^{ab}\\frac{i}{2}(\\delta\_{ia}\\delta\_{jb}-\\delta\_{ib}\\delta\_{ja})\\mbox{,} |  |

where a≠ba\\neq b, and the ii in the prefactor corresponds to the unit
imaginary, rather than the index, with no confusion. The two
matrices comprising the elements listed in ( [50](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E50 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) are Hermitian,
and characterise realizable measurements.

Substituting ( [50](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E50 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) in ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")),

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|  | ⟨Ra​b⟩\\displaystyle\\langle R^{ab}\\rangle | =\\displaystyle= | Δ​ν​ηa​b​Re​Za​b\\displaystyle\\Delta\\nu\\,\\eta^{ab}\\,\\mbox{Re}Z\_{ab} |  | (51) |
|  | ⟨Ia​b⟩\\displaystyle\\langle I^{ab}\\rangle | =\\displaystyle= | Δ​ν​ηa​b​Im​Za​b​,\\displaystyle\\Delta\\nu\\,\\eta^{ab}\\,\\mbox{Im}Z\_{ab}\\mbox{,} |  |

and the two measurements correspond to finding the real and
imaginary parts of the correlations between ports aa and bb,
which is equivalent to finding the in and out of phase components
of the fringe formed when the signals at aa and bb are
combined. More specifically, the matrices correspond to using
an analogue correlator to measure the cos\\cos and sin\\sin fringes.

We can now substitute ( [50](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E50 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) into ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) to give

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov​\[Ra​b,Ra​b\]=Δ​ντ​\[(ηa​b)2​12​(Za​a​Zb​b+Re​Za​b2)+h​ν0​ηa​b​Re​Za​b\]​,\\mbox{Cov}\\left\[R^{ab},R^{ab}\\right\]=\\frac{\\Delta\\nu}{\\tau}\\left\[(\\eta^{ab})^{2}\\frac{1}{2}(Z\_{aa}Z\_{bb}+\\mbox{Re}Z\_{ab}^{2})+h\\nu\_{0}\\eta^{ab}\\mbox{Re}Z\_{ab}\\right\]\\mbox{,} |  | (52) |

giving a noise to signal ratio of

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ra​b⟨Ra​b⟩=1(Δ​ν​τ)1/2​\[12​(Za​a​Zb​b+Re​Za​b2)+h​ν0​Re​Za​b\]1/2Re​Za​b​,\\frac{\\Delta R^{ab}}{\\langle R^{ab}\\rangle}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\frac{\\left\[\\frac{1}{2}(Z\_{aa}Z\_{bb}+\\mbox{Re}Z\_{ab}^{2})+h\\nu\_{0}\\mbox{Re}Z\_{ab}\\right\]^{1/2}}{\\mbox{Re}Z\_{ab}}\\mbox{,} |  | (53) |

for ηa​b=1\\eta^{ab}=1, which corresponds to the actual power.
For a completely incoherent source, and orthogonal beams,
Za​b=0Z\_{ab}=0, the noise becomes

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ra​b=1(Δ​ν​τ)1/2​12​(⟨Pa​a⟩​⟨Pb​b⟩)1/2\\Delta R^{ab}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\frac{1}{\\sqrt{2}}\\left(\\langle P\_{aa}\\rangle\\langle P\_{bb}\\rangle\\right)^{1/2} |  | (54) |

and the noise is classical, with the fluctuations being proportional to
the geometric means of the two power levels, which is a well known feature
of noise in interferometers.

In the case where the two signals at aa and bb are fully coherent,
Za​a​Zb​b=\|Za​b\|2Z\_{aa}Z\_{bb}=\|Z\_{ab}\|^{2}, we get

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ra​b⟨Ra​b⟩=1τ1/2​\[1Δ​ω+h​ν0Δ​ω\|Za​b\|cos⁡θa​b\]1/2​,\\frac{\\Delta R^{ab}}{\\langle R^{ab}\\rangle}=\\frac{1}{\\tau^{1/2}}\\left\[\\frac{1}{\\Delta\\omega}+\\frac{h\\nu\_{0}}{\\Delta\\omega\|Z\_{ab}\|\\cos\\theta\_{ab}}\\right\]^{1/2}\\mbox{,} |  | (55) |

or

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ra​b⟨Ra​b⟩=1(Δ​ν​τ)1/2​\[1+Δ​νn¯c\]1/2​,\\frac{\\Delta R^{ab}}{\\langle R^{ab}\\rangle}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\left\[1+\\frac{\\Delta\\nu}{\\bar{n}\_{c}}\\right\]^{1/2}\\mbox{,} |  | (56) |

where n¯c\\bar{n}\_{c} is the mean number of photons in the in-phase
correlated power, and θa​b\\theta\_{ab} is the phase of Za​bZ\_{ab}.
Thus, for weak fringes, and even in the nulled region
of a strong fringe, classical noise is swapped for Poisson noise. In
general, the nature of the noise will change throughout the fringe.

Similarly, we have

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov​\[Ia​b,Ia​b\]=Δ​ντ​\[(ηa​b)2​12​(Za​a​Zb​b−Re​Za​b2)+h​ν0​ηa​b​Im​Za​b\]​,\\mbox{Cov}\\left\[I^{ab},I^{ab}\\right\]=\\frac{\\Delta\\nu}{\\tau}\\left\[(\\eta^{ab})^{2}\\frac{1}{2}(Z\_{aa}Z\_{bb}-\\mbox{Re}Z\_{ab}^{2})+h\\nu\_{0}\\eta^{ab}\\mbox{Im}Z\_{ab}\\right\]\\mbox{,} |  | (57) |

giving

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ia​b⟨Ia​b⟩=1(Δ​ν​τ)1/2​\[12​(Za​a​Zb​b−Re​Za​b2)+h​ν0​Im​Za​b\]1/2Im​Za​b​,\\frac{\\Delta I^{ab}}{\\langle I^{ab}\\rangle}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\frac{\\left\[\\frac{1}{2}(Z\_{aa}Z\_{bb}-\\mbox{Re}Z\_{ab}^{2})+h\\nu\_{0}\\mbox{Im}Z\_{ab}\\right\]^{1/2}}{\\mbox{Im}Z\_{ab}}\\mbox{,} |  | (58) |

for ηa​b=1\\eta^{ab}=1.

For incoherent travelling waves, the noise is the same as for the
in-phase measurement, ( [54](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E54 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")). For fully coherent signals,

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ia​b⟨Ia​b⟩=1τ1/2​\[1Δ​ν+h​ν0Δ​ν\|Za​b\|sin⁡θa​b\]1/2​.\\frac{\\Delta I^{ab}}{\\langle I^{ab}\\rangle}=\\frac{1}{\\tau^{1/2}}\\left\[\\frac{1}{\\Delta\\nu}+\\frac{h\\nu\_{0}}{\\Delta\\nu\|Z\_{ab}\|\\sin\\theta\_{ab}}\\right\]^{1/2}\\mbox{.} |  | (59) |

or

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​Ia​b⟨Ia​b⟩=1(Δ​ν​τ)1/2​\[1+Δ​νn¯s\]1/2​,\\frac{\\Delta I^{ab}}{\\langle I^{ab}\\rangle}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\left\[1+\\frac{\\Delta\\nu}{\\bar{n}\_{s}}\\right\]^{1/2}\\mbox{,} |  | (60) |

where n¯s\\bar{n}\_{s} is the mean number of photons in the quadrature
component of the correlated power. Overall, the same behaviour is seen
as for the in-phase component.

Finally, we can correlate the fluctuations in the in-phase and quadrature
measurements, giving

|     |     |     |     |
| --- | --- | --- | --- |
|  | Cov​\[Ra​b,Ia​b\]=Δ​ντ​\[(ηa​b)2​12​Im​Za​b2\]​,\\mbox{Cov}\\left\[R^{ab},I^{ab}\\right\]=\\frac{\\Delta\\nu}{\\tau}\\left\[(\\eta^{ab})^{2}\\frac{1}{2}\\mbox{Im}Z\_{ab}^{2}\\right\]\\mbox{,} |  | (61) |

and

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​R​Ia​b⟨Ra​b⟩1/2​⟨Ia​b⟩1/2=1(Δ​ν​τ)1/2​12​\[Im​Za​b2Re​Za​b​Im​Za​b\]1/2​,\\frac{\\Delta RI^{ab}}{\\langle R^{ab}\\rangle^{1/2}\\langle I^{ab}\\rangle^{1/2}}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\frac{1}{\\sqrt{2}}\\left\[\\frac{\\mbox{Im}Z\_{ab}^{2}}{\\mbox{Re}Z\_{ab}\\,\\mbox{Im}Z\_{ab}}\\right\]^{1/2}\\mbox{,} |  | (62) |

giving

|     |     |     |     |
| --- | --- | --- | --- |
|  | Δ​R​Ia​b⟨Ra​b⟩1/2​⟨Ia​b⟩1/2=1(Δ​ν​τ)1/2​.\\frac{\\Delta RI^{ab}}{\\langle R^{ab}\\rangle^{1/2}\\langle I^{ab}\\rangle^{1/2}}=\\frac{1}{(\\Delta\\nu\\,\\tau)^{1/2}}\\mbox{.} |  | (63) |

It is also possible to calculate the correlations between the fluctuations
in the real and imaginary parts of fringe measurements on two different
pairs of ports.

## 7 Conclusion

We have analyzed the behaviour of phased arrays from a functional
perspective, and shown that their operation is intimately
related to the mathematical theory of frames. In cases where the beams
are non-orthogonal, or even linearly dependent, image reconstruction
can be carried out using dual beams. The theory of frames
allows one to assess, in a straightforward manner, whether the
powers or correlations at the output ports of a phased array contain sufficient
information to allow some class of field or intensity distribution to be
reconstructed precisely. We have also identified the natural modes of phased
arrays, which are important for understanding information throughput and
aperture synthesis interferometry.

In order to calculate the behaviour of an imaging phased array it is only
necessary to know the synthesised reception patterns, which may be
non-orthogonal. It is not necessary to know anything about the internal
construction of the array itself. As a consequence, data can be taken from
experimental measurements or from electromagnetic simulations. The ability
to assess behaviour simply from the synthesised beams separates the
process of choosing the best beams for a given application from the process
of realizing the beams in practice. It also suggests important techniques for
analysing experimental data.

Our model allows the straightforward calculation of quantities
such as the correlations in the fluctuations at the output ports of an
phased array. Indeed, sources can be constructed through expressions
of the kind ( [15](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E15 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), the correlations at the output ports calculated
through ( [11](https://ar5iv.labs.arxiv.org/html/0707.1580#S2.E11 "In 2 Basic Principles ‣ Theoretical Analysis of Astronomical Phased Arrays")), or in the modal case ( [31](https://ar5iv.labs.arxiv.org/html/0707.1580#S4.E31 "In 4 Natural Modes of Phased Arrays ‣ Theoretical Analysis of Astronomical Phased Arrays")), system noise can
be included through ( [37](https://ar5iv.labs.arxiv.org/html/0707.1580#S5.E37 "In 5 Noise ‣ Theoretical Analysis of Astronomical Phased Arrays")) and ( [38](https://ar5iv.labs.arxiv.org/html/0707.1580#S5.E38 "In 5 Noise ‣ Theoretical Analysis of Astronomical Phased Arrays")),
and the expectation values, fluctuations, and correlations between fluctuations
in measurements at the output determined through ( [39](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E39 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")) and ( [40](https://ar5iv.labs.arxiv.org/html/0707.1580#S6.E40 "In 6 Fluctuations and Sensitivity ‣ Theoretical Analysis of Astronomical Phased Arrays")).
The whole procedure only requires simple matrix algebra. The scheme is
conceptually and numerically powerful\[ [18](https://ar5iv.labs.arxiv.org/html/0707.1580#bib.bib18 "")\], and in an upcoming paper
we shall present simulations showing dual beams, natural modes, and image
reconstructions.

References

## References

- \[1\] van Ardenne A, Smolders A and Hampson G 2000
Active adaptive antennas for radio astronomy: Results of
the R & D program towards the square kilometer array
Radio Telescopes ed H R Butcher; Proc. SPIE
4015 420-433

- \[2\] Braun R 1997 The concept of the square kilometer array
interferometer Proc. High Sensitivity Radio Astronomy,
ed N Jackson and R J Davies, (Cambridge Univ. Press, Cambridge, UK)
260-268

- \[3\] Ellingson S W 2003 Efficient multibeam synthesis with
interference nulling for large arrays IEEE Trans. Antennas Propag.51 503-511

- \[4\] Ardenne A, Wilkinson P, Patel P, Vaate J 2004 Electronic
Multi-beam Radio Astronomy Concept: Embrace a demonstrator for the
European SKA program Experimental Astronomy17 65-77

- \[5\] Padman R Optical fundementals for array feeds 1995
Multi-feed Systems for Radio Telescopes ed DT Emerson and
J M Payne (ASP Conf. Series) 75 3-26

- \[6\] Murphy J A and Padman R 1988 Focal plane and aperture
plane heterodyne array receivers for millimeter-wave radio
astronomy-a comparison Int. J. Infrared Millimeter Waves9 667-704

- \[7\] Casazza P G The art of frame theory Taiwanese
J. Mathematics4 129-201

- \[8\] Daubechies I 1990 The wavelet transform, time-frequency
localization and signal analysis IEEE TRans. Inform. Theory
961-1005

- \[9\] Daubechies I, Grossmann A, and Meyer Y 1986 Painless
nonorthogonal expansions J. Math. Phys.27 1271-1283

- \[10\] Massey R and Refregier A 2005 Polar shapelets
Mon. Not. R. Astron. Soc.363, 197-210

- \[11\] Refregier A 2003 Shapelets:I A method for image
analysis Mon. Not. R. Astron. Soc.338 35-47

- \[12\] Berry R H, Hobson M P and Withington S 2004 Modal
decomposition of astronomical images with applications to
shapelets Mon. Not. R. Astron. Soc.354 199-211

- \[13\] Withington S, Hobson M P and Campbell E S 2004
Modal foundations of close-packed optical arrays with particular
application to infrared and millimeter-wave astronomical
interferometry J. Appl. Phys.96 1794-1802

- \[14\] Saklatvala G, Hobson M P and Withington S 2006
Simulations of multimode bolometric interferometers Mon. Not.
R. Astron. Soc.367, 1194-1200

- \[15\] Withington S, Campbell E S and Hobson M P 2005
Quantum statistical analysis of multimode far-infrared and
submillimetre-wave astronomical interferometers J. Opt.
Soc. Am. A22 1937-1946

- \[16\] Saklatvala G, Withington S and Hobson M P 2007
A coupled mode theory of far-infrared and submillimetre-wave
detectors J. Opt. Soc. Am. A24 764-775

- \[17\] Withington S and Yassin G 2001 Power coupled
between partially coherent vector fields in different states of
coherence J. Opt. Soc. Am. A18 3061-3071

- \[18\] Withington S, Saklatvala G and Hobson M P 2006
Partially coherent analysis of imaging and interferometric
phased arrays: noise, correlations, and fluctuations J.
Opt. Soc. Am. A23 1340-1348


[◄](https://ar5iv.labs.arxiv.org/html/0707.1578) [![ar5iv homepage](https://ar5iv.labs.arxiv.org/assets/ar5iv.png)](https://ar5iv.labs.arxiv.org/) [Feeling\\
\\
lucky?](https://ar5iv.labs.arxiv.org/feeling_lucky) [Conversion\\
\\
report](https://ar5iv.labs.arxiv.org/log/0707.1580) [Report\\
\\
an issue](https://github.com/dginev/ar5iv/issues/new?template=improve-article--arxiv-id-.md&title=Improve+article+0707.1580) [View original\\
\\
on arXiv](https://arxiv.org/abs/0707.1580) [►](https://ar5iv.labs.arxiv.org/html/0707.1581)