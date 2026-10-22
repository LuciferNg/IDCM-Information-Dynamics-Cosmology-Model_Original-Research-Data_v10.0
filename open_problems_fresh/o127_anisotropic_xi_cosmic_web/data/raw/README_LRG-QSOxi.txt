Materials for eBOSS LRG and QSO configuration space clustering analysis
=========================================================

Reference
---------

LRG
Bautista et al. 2020 https://arxiv.org/abs/2007.08993

QSO
Hou et al. 2020 https://arxiv.org/abs/2007.02656

Units
-----

Distances are always in Mpc/h

Redshift Cuts
-------------

eBOSS LRG data is selected within the redshift cut 0.6 < z < 1.0
The final DR16 eBOSS LRG catalogue contains both old CMASS BOSS LRG observations at 0.6<z<1.0 and the new eBOSS LRG observations within the same redshift range. Both LRG samples are treated as a unique one. This new combined LRG sample is considered independent of the two lowest BOSS DR12 redshift samples: 0.2<z<0.5 and 0.4<z<0.6. 
In order to obtain the full information from the LRG we recommend to use these three samples: 0.2<z<0.5, 0.4<z<0.6, 0.6<z<1.0. The first two are overlapping and therefore correlated (as described in the BOSS DR12 paper). The last sample is considered fully independent of the other two. 

eBOSS QSO data is selected within the redshift cut 0.8<z<2.2. Although there is an overlap with the LRG sample in the 0.8<z<1.0 range, due to the low density of both samples, we consider them independent. 



BAO fits
--------

LRG-BAO fits are performed on post-reconstructed catalogues. These fits are considered independent (although correlated) to the LRG-FS fits which are performed on the pre-reconstructed catalogues. Both results can be appropriately confined into a single one through their covariance (see LRG paper(s) for more details).

QSO-BAO fits are performed on pre-reconstructed catalogues. These fits are not independent from the QSO-FS fits, also performed on the same catalogues. Therefore both FS and BAO results can't be simultaneously used, as they are highly correlated (and almost not independent). 


Post-reconstruction LRG correlation function measurement is:
Data_LRGxi_{NGC,SGC}_0.6z1.0_postrecon.txt

Pre-reconstruction QSO correlation function measurement is:
Data_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt (exactly the same as for QSO-FS)


Covariance matrix can be extracted from:
Covariance_LRGxi_{NGC,SGC}_0.6z1.0_postrecon.txt for LRGs
Covariance_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt for QSOs (exactly the same as for QSO-FS)

The inverse covariance matrix is:
invCovariance_LRGxi_{NGC,SGC}_0.6z1.0_postrecon.txt for LRGs
invCovariance_QSOxi_{NGC,SGC}_0.8z2.2_prerecon_forBAO.txt for QSOs

The best fit BAO-model is:
Model_BAO_LRGxi_{NGC,SGC}_0.6z1.0_postrecon.txt for LRGs
Model_BAO_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt for QSOs


FS fits
--------------

Both FS-LRG and FS-QSO fits are performed on pre-reconstructed catalogues. 

The LRG-FS fits are considered independent (although correlated) to the LRG-BAO fits which are performed on the post-reconstructed catalogues. Both results can be appropriately confined into a single one through their covariance (see LRG paper(s) for more details).

QSO-FS fits are not independent from the QSO-BAO fits, also performed on the same catalogues. Therefore both FS and BAO results can't be simultaneously used, as they are highly correlated (and almost not independent). 


Pre-reconstruction correlation function measurement is:
Data_LRGxi_{NGC,SGC}_0.6z1.0_prerecon.txt for LRGs
Data_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt for QSOs (exactly the same as for QSO-BAO)


Covariance matrix is:
Covariance_LRGxi_{NGC,SGC}_0.6z1.0_prerecon.txt for LRGs
Covariance_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt for QSOs (exactly the same as for QSO-BAO)

The inverse covariance matrix is:
invCovariance_LRGxi_{PTTNS,GSCLPT}model_{NGC,SGC}_0.6z1.0_prerecon.txt for LRGs
invCovariance_QSOxi_{NGC,SGC}_0.8z2.2_prerecon_forFS.txt for QSOs

The best fit model is:
Model_FS_LRGxi_{PTTNS,GSCLPT}model_{NGC,SGC}_0.6z1.0_prerecon.txt for LRGs
Model_FS_QSOxi_{NGC,SGC}_0.8z2.2_prerecon.txt for QSOs

Note that for the LRG sample two models are fitted to the FS type of analysis: Perturbation Theory + TNS scheme for redshift space distortions (PTTNS); and Gaussian streaming model (GSCLPT).

Note that for Model_FS_LRGxi_PTTNSmodel_NGCSGC_0.6z1.0_prerecon.txt the model for the hexadecapole corresponding to the smallest s-bin is not used in the analysis. We have noted this as NaN for xi4 on that specific bin. 

Pair Counts
----------------

The pair counts are also provided for the Data-Data (DD), Data-Random (DR) and Random-Random (RR) type of pairs,

{DD,DR,RR}counts_{QSO,LRG}xi_{NGC,SGC}_{redshift range}_{prerecon,postrecon}.txt



