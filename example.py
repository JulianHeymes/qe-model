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

materials = qm.load_materials({'Al': 2.77, 'Si': 2.33, 'SiO2': 2.6, 'Si3N4': 3.44, 'SiP2': 2.5}, 'qetestdata')
# for m, v in materials.items():
#     plt.loglog(v[:,0], v[:,1], label=m)
# plt.legend()
# plt.show()
detector = qm.Detector("standard", materials, bins=np.geomspace(0.1, 10, 1000))
#detector.new_layer("Al", 0.09)
#detector.new_layer("Al", 0.09)
#detector.new_layer("Si3N4", 0.02)
detector.new_layer("Al", 0.13)
detector.new_layer("SiO2", 0.05)
detector.new_layer("SiO2", 0.004)
detector.new_layer("Si", 35, sensitivity=True)
energy, qe = detector.get_qe()
plt.semilogx(energy, qe)
np.savetxt("SiO2-50nm-2.6gcm3_Al-130nm-2.77gcm3.dat", list(zip(energy, qe)))
plt.ylim(0,1)
plt.show()
