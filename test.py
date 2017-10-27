import qe_model as qm
import numpy as np
import matplotlib.pyplot as plt



detector = qm.Detector()
detector.new_layer("Al", 0.09)
detector.new_layer("SiO2", 0.003)
detector.new_layer("Si", 0.01)
detector.new_layer("Si", 13, sensitivity=1)
energy, qe = detector.calculate_qe()
plt.semilogx(energy, qe)
detector.change_thickness(index=0, thickness=0)
energy, qe = detector.calculate_qe()
plt.semilogx(energy, qe)
plt.show()
