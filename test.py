import qe_model as qm
import numpy as np
import matplotlib.pyplot as plt

def grey_sensitivity(mat_data):
    #potential well is maybe a few nanometers?
    #charge cloud is proportional to sqrt of energy
    #try 1 - exp(-sqrt(e)/well size)
    energies = mat_data[:,0]
    mass_lens = mat_data[:,0]
    sens = np.exp(-np.sqrt(energies)/0.5/mass_lens)
    print(sens)
    return sens

materials = qm.load_materials({'Al': 2.77, 'Si': 2.33, 'SiO2': 2.6}, 'qetestdata')
# for m, v in materials.items():
#     plt.loglog(v[:,0], v[:,1], label=m)
# plt.legend()
# plt.show()
detector = qm.Detector("standard", materials, bins=np.logspace(np.log10(50e-3), np.log10(2), 100))
#detector.new_layer("Al", 0.09)
detector.new_layer("SiO2", 0.004)
detector.new_layer("Si", 0.005)
detector.new_layer("Si", 0.02, sensitivity=grey_sensitivity)
detector.new_layer("Si", 13, sensitivity=1.0)
energy, qe = detector.get_qe()
plt.semilogx(energy, qe)
mdata = np.loadtxt("/mnt/storage/SXRQE/QEAnalysis/15051_7_3_QE.dat")
plt.plot(mdata[:,0]*1e-3, mdata[:,1])
plt.ylim(0,1)
plt.show()
