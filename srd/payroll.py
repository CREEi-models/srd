import os
import srpp
from srd import qpip
from srd import ei
import numpy as np

module_dir = os.path.dirname(os.path.dirname(__file__))


def create_stub():
    lines = ['cpp', 'cpp_supp', 'qpip', 'ei']
    return dict(zip(lines, np.zeros(len(lines))))


class payroll:
    """
    Calcul des cotisations sociales: à l'assurance emploi, au RQAP (Québec), au RRQ (Québec) ainsi qu'au RPC (provinces autres que le Québec).

    Parameters
    ----------
    year: int
        année pour le calcul
    """
    def __init__(self, year):
        self.year = year
        self.qpp_rules = srpp.rules(qpp=True)
        self.cpp_rules = srpp.rules(qpp=False)
        self.qpip_prog = qpip.program(self.year)
        self.ei_prog = ei.program(self.year)

    def compute(self, hh):
        """
        Fonction qui appelle *ei*, *qpip* et la fonction *get_cpp_contrib* afin de calculer respectivement les cotisations à l'assurance-emploi, à l'assurance parentale (RQAP) et au RRQ/RPC.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold
        """
        for p in hh.sp:
            p.payroll = create_stub()
            p.payroll['ei'] = self.ei_prog.contrib(p, hh)
            base, supp = self.get_cpp_contrib(p, hh)
            p.payroll['cpp'] = base
            p.payroll['cpp_supp'] = supp
            p.payroll['qpip'] = self.qpip_prog.contrib(p, hh)

    def get_cpp_contrib(self, p, hh):
        """
        Fonction pour le calcul des cotisations au RPC et au RRQ, qui appelle le module *srpp*.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        liste de floats
            Montants des cotisations aux régimes de base et supplémentaire du RRQ et du RPC.
        """
        rules = self.qpp_rules if hh.prov == 'qc' else self.cpp_rules
        if (p.age < 18) | (p.age > 69):
            p.contrib_cpp, p.contrib_cpp_self = 0, 0
            return 0, 0
        else:
            acc = srpp.account(byear=self.year - p.age, rules=rules)
            acc.MakeContrib(year=self.year, earn=p.inc_earn,
                            earn_aut=p.inc_self_earn)
            hist = acc.history[p.age - 18]
            p.contrib_cpp, p.contrib_cpp_self = hist.contrib, hist.contrib_aut

            return (hist.contrib + hist.contrib_aut,
                    hist.contrib_s1 + hist.contrib_s2 +
                    hist.contrib_aut_s1 + hist.contrib_aut_s2)
