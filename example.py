import qe_model as qm
import numpy as np
import matplotlib.pyplot as plt

# You can define a function that gives the sensitivity of the detector
# It should return an array of the same length as energies and attenuation lengths (att_len)
# energy in keV, att length in cm2/g
# In this case, the function just returns 1 for each energy, meaning there is no modelling
# of detector effects
def sensitivity_function(energies, att_len):
    return np.ones_like(energies)

# define the materials
materials = qm.load_materials({'Al': 2.77, # a dictionary defining the materials by chemical
                               'Si': 2.33, # formula, and their densities in g/cm3
                               'SiO2': 2.6,
                               'Si3N4': 3.44,
                               'SiP2': 2.5},
                              'qedata') # The name of the folder to save material data to

# create the detector
detector = qm.Detector("standard", #a name
                       materials, #the materials database
                       bins=np.geomspace(0.1, 10, 1000)) #the energy bins to use

# Add the detector layers
detector.new_layer("Al", 0.09) #90 nm optical filter.
detector.new_layer("SiO2", 0.004)
detector.new_layer("Si", 35, sensitivity=sensitivity_function)

# Calculate the QE
energy, qe = detector.get_qe()

# Save the data and then plot.
np.savetxt("qe.dat", list(zip(energy, qe)))
plt.semilogx(energy, qe)
plt.ylim(0,1)
plt.show()


