import os
import importlib
from srd import OldAgeSec
from srd import Contrib
importlib.reload(OldAgeSec)
importlib.reload(Contrib)

class Run:
    """
    This class creates calculators, loads parameters 
    and runs households through the calculators:
    OAS, GIS, fed and prov taxes, social assistance and social solidarity.
    """
    def __init__(self, year):
        self.year = year
        self.path_params = (os.path.dirname(os.path.dirname(__file__)) 
                            + f'/params/{self.year}/')
        
    def create_calculators(self):
        """
        Creates calculators.
        """
        self.old_age_sec = OldAgeSec(self.path_params)

        self.contributions = Contrib(self.path_params, self.year)


    def file(self, hh):
        """
        Runs households through calculators.
        """
        self.old_age_sec.file(hh)

        self.contributions.file(hh)
