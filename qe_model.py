import glob
import os
import numpy as np

class Detector(object):
    def __init__(self, materials_dir="data", bins=None):
        self.layers = []
        self.beam = None
        self.qe = None
        self.materials = load_materials(materials_dir)
        if(bins is None):
            self.bins = get_bins(self.materials)
        else:
            self.materials = resize_data(self.materials, bins)
            self.bins = bins

    def new_layer(self, material_name, thickness, sensitivity=None):
        layer = new_layer(self.materials, material_name, thickness, sensitivity)
        self.layers.append(layer)

    def add_layer(self, layer):
        self.layers.append(layer)

    def add_layers(self, layers):
        for l in layers:
            self.layers.append(l)

    def replace_layer(self, index, layer):
        self.layers[index] = layer

    def change_thickness(self, index, thickness):
        old_layer = self.layers[index]
        material = old_layer['material']
        sensitivity = old_layer['sensitivity']
        newl = new_layer(self.materials, material, thickness, sensitivity)
        self.layers[index] = newl

    def transmit(self, beam=None):
        if not beam:
            beam = new_beam(self.bins)
        for layer in self.layers:
            beam = transmit(beam, layer)
        return beam

    def calculate_qe(self):
        beam = self.transmit()
        self.qe = beam['detected']
        return self.bins, beam['detected']

    def get_qe(self):
        return self.bins, self.qe

    def save(self, filename):
        self.serialize_layers()



def resize_data(materials, bins):
    """Resize the x-ray data in materials to all use the same bins,
    uses a linear interpolation"""
    new_materials = {}
    for m in materials.keys():
        data = materials[m]
        new_materials[m] = np.array(zip(bins, np.interp(bins, data[:,0], data[:, 1])))
    return new_materials

def get_bins(materials):
    mat = materials.itervalues().next()
    return mat[:, 0]

def load_materials(base):
    """Load all the materials files with a .dat extension from the given directory.
    Strips the .dat from the filename and uses that as the dictionary key. """
    fns = glob.glob(base + "/*.dat")
    materials = {}
    for fn in fns:
        name = os.path.basename(fn)[:-4]
        data = np.loadtxt(fn)
        materials[name] = data
    return materials

def new_layer(materials, material, thickness, sensitivity=None):
    """Generate a new default layer in the detector.
    sensitivity may be a value or a function, it defines what fraction
    of the energy absorbed is actually detected. The function should take
    an energy and an absorption depth"""
    mat_data = materials[material]
    transmission = np.exp(-thickness/mat_data[:,1])
    absorption = np.ones_like(transmission) - transmission
    if(callable(sensitivity)):
        sens = sensitivity(mat_data)
    elif(sensitivity is None):
        sens = np.zeros_like(mat_data[:,0])
    elif(isinstance(sensitivity, int)):
        sens = np.ones_like(mat_data[:,0])
    elif(len(sensitivity) > 1):
        sens = sensitivity

    return {"material": material,
            'thickness': thickness,
            'transmission': transmission,
            'absorption': absorption,
            'sensitivity': sens}


def new_beam(bins):
    """Returns a fresh beam dictionary.
    keys are beam and detected. detected stores the fraction of the beam
    that would actually be observed in the detector"""
    return {'beam': np.ones_like(bins),
            'detected': np.zeros_like(bins)}

def transmit(beam, layer):
    transmission = layer['transmission']
    absorbed = layer['absorption']
    detected = layer['sensitivity']*absorbed*beam['beam']
    beam['detected'] = beam['detected'] + detected
    beam['beam'] = beam['beam']*transmission
    return beam
