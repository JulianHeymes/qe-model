import glob
import os
import json
import numpy as np
import xray_grabber as xrg

class Detector(object):
    def __init__(self, name, materials, bins=np.logspace(-1, 2, 1000)):
        self.name = name
        self.layers = []
        self.beam = None
        self.qe = None
        self.materials = materials
        self.materials = resize_data(self.materials, bins)
        self.bins = bins

    def new_layer(self, material_name, thickness, sensitivity=None):
        """Add a new layer to the bottom of the detector"""
        layer = new_layer(self.materials, material_name, thickness, sensitivity)
        self.layers.append(layer)

    def add_layer(self, layer):
        """Add an already constructed layer to the detector"""
        self.layers.append(layer)

    def add_layers(self, layers):
        """Add a list of layers, in order, to the detector"""
        for l in layers:
            self.layers.append(l)

    def replace_layer(self, index, layer):
        """Replace an existing layer in the detector"""
        self.layers[index] = layer

    def change_thickness(self, index, thickness):
        """Change the thickness of a layer at position index in the detector"""
        old_layer = self.layers[index]
        material = old_layer['material']
        sensitivity = old_layer['sensitivity']
        newl = new_layer(self.materials, material, thickness, sensitivity)
        self.layers[index] = newl

    def transmit(self, beam=None):
        """Uses the transmit function to progress the beam through the detector"""
        if not beam:
            beam = new_beam(self.bins)
        for layer in self.layers:
            beam = transmit(beam, layer)
        return beam

    def calculate_qe(self):
        """Returns energy bins and QE values"""
        beam = self.transmit()
        self.qe = beam['detected']
        return self.bins, beam['detected']

    def get_qe(self):
        """Returns a tuple of the energy bins and QE values for the detector"""
        if not self.qe:
            self.calculate_qe()
        return self.bins, self.qe

    def save(self, filename=None):
        """save the detector to a json file"""
        if not filename:
            filename = self.name + ".json"
        detector = {self.name: [layer_properties(l) for l in self.layers]}
        with open(filename, 'w') as f:
            json.dump(detector, f)

    def load(self, filename):
        """Delete current detector and load one from json file"""
        self.reset()
        with open(filename) as f:
            det = json.load(f)
        self.name = det.keys()[0]
        for l in det[self.name]:
            self.new_layer(l['material'], l['thickness'], l['sensitivity'])

    def reset(self):
        """Reset the detector, delete all layers and QE values"""
        self.name = None
        self.layers = []
        self.beam = None
        self.qe = None


def resize_data(materials, bins):
    """Resize the x-ray data in materials to all use the same bins,
    uses a linear interpolation"""
    new_materials = {}
    for m in materials.keys():
        data = materials[m]
        new_materials[m] = np.array(list(zip(bins, np.interp(bins, data[:,0], data[:, 1]))))
    return new_materials

def get_bins(materials):
    mat = materials.itervalues().next()
    return mat[:, 0]



def load_materials(material_list, base):
    """Creates the material database. Loads from files or grabs from net.
    material_list = dictionary of material, density pairs"""
    print("Loading requested materials...")
    db = xrg.XrayData(base)
    for material in material_list:
        db.add(material)
    db = db.get_database()
    for material, density in material_list.items():
        db[material][:,1] = db[material][:,1]*density
    print("Materials loaded!")
    return db
    
    
def new_layer(materials, material, thickness, sensitivity=None):
    """Generate a new default layer in the detector.
    sensitivity may be a value or a function, it defines what fraction
    of the energy absorbed is actually detected. The function should take
    an energy and an absorption depth"""
    mat_data = materials[material]
    mat_data = np.array(list(mat_data))

    transmission = np.exp(-thickness*mat_data[:,1]*1e-4)
    absorption = np.ones_like(transmission) - transmission
    
    if(callable(sensitivity)):
        sens = sensitivity(mat_data[:,0], mat_data[:,1])
    elif(sensitivity is None):
        sens = np.zeros_like(mat_data[:,0])
    elif(isinstance(sensitivity, int)):
        sens = np.ones_like(mat_data[:,0])
    elif(isinstance(sensitivity, float)):
        sens = np.ones_like(mat_data[:,0])*sensitivity
    elif(len(sensitivity) > 1):
        sens = sensitivity

    return {"material": material,
            'thickness': thickness,
            'transmission': transmission,
            'absorption': absorption,
            'sensitivity': sens}

def layer_properties(layer):
    props = {prop: layer[prop] for prop in ['material', 'thickness', 'sensitivity']}
    props['sensitivity'] = list(props['sensitivity'])
    return props

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
