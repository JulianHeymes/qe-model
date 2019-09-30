import requests
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

ENERGYRANGES = {'low': 'L', 'high': 'U'}
URLBASE = "https://physics.nist.gov/cgi-bin/ffast/ffast.pl?"

def empty_params():
    return {'Formula=': None,
            'gtype=': None,
            'range=': None,
            'frames=': None,
            'htmltable=': None}

def form_url(formula, energy_range):
    url = URLBASE
    params = empty_params()
    params['gtype='] = '3'
    params['frames='] = 'no'
    params['htmltable='] = '1'
    params['Formula='] = formula
    params['range='] = ENERGYRANGES[energy_range]
    for key, value in params.items():
        url += key
        url += value
        url += "&"
    return url

def get_data(formula, energy_range):
    url = form_url(formula, energy_range)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    table, row = ([], [])
    for val in soup.find_all("td"):
        tmp = float(val.contents[0])
        row.append(tmp)
        if len(row) == 2:
            table.append(np.array(row))
            row = []
    return np.array(table)


def get_full_data(formula):
    lowedata = get_data(formula, 'low')
    highedata = get_data(formula, 'high')
    return np.concatenate((lowedata, highedata))

class XrayData(object):
    """Grabs x-ray mass attenuation factors from the nist website, or from cached database"""
    def __init__(self, db_directory):
        self.material_db = {}
        self.db_dir = db_directory
        self._check_database()
        self._load_database()

    def _check_database(self):
        if not os.path.isdir(self.db_dir):
            os.makedirs(self.db_dir)

    def _load_database(self):
        for fn in glob.glob(self.db_dir + "/*.dat"):
            material = os.path.basename(fn)[:-4]
            data = np.loadtxt(fn)
            self.material_db[material] = data

    def get_material_data(self, formula):
        if formula not in self.material_db:
            print(f"{formula} not found in database, fetching from web...")
            data = get_full_data(formula)
            np.savetxt(self.db_dir + "/" + formula + ".dat", data)
            self.material_db[formula] = data[np.argsort(data[:,0]), :]
        return self.material_db[formula]

    def add(self, formula):
        self.get_material_data(formula)

    def get_database(self):
        return self.material_db
        
        
