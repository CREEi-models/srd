from srd import add_params_as_attr
import os
from srd.oas import template

module_dir = os.path.dirname(os.path.dirname(__file__))


# wrapper to pick correct year
def program(year, federal):
    """
    Fonction qui permet de sélectionner le programme par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2022)
    federal: {srd.federal.form_2016, ..., srd.federal.form_2022}
        instance de la classe srd.federal.form_xxxx (pour l'année xxxx) du module *federal*
    Returns
    -------
    class instance
        Une instance de la classe de l'année sélectionnée.
    """
    if year == 2016:
        p = program_2016(federal)
    if year == 2017:
        p = program_2017(federal)
    if year == 2018:
        p = program_2018(federal)
    if year == 2019:
        p = program_2019(federal)
    if year == 2020:
        p = program_2020(federal)
    if year == 2021:
        p = program_2021(federal)
    if year == 2022:
        p = program_2022(federal)
    return p


# program for 2016, derived from template, only requires modify
# functions that change
class program_2016(template):
    """
    Version du programme de 2016.

    Parameters
    ----------
    federal: srd.federal.form_2016
        instance de la classe srd.federal.form_2016 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2016.csv")
        self.federal = federal


# program for 2017, derived from template, only requires modify
# functions that change
class program_2017(program_2016):
    """
    Version du programme de 2017.

    Parameters
    ----------
    federal: srd.federal.form_2017
        instance de la classe srd.federal.form_2017 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2017.csv")
        self.federal = federal


# program for 2018, derived from template, only requires modify
# functions that change
class program_2018(program_2017):
    """
    Version du programme de 2018.

    Parameters
    ----------
    federal: srd.federal.form_2018
        instance de la classe srd.federal.form_2018 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2018.csv")
        self.federal = federal


# program for 2019, derived from template, only requires modify
# functions that change
class program_2019(program_2018):
    """
    Version du programme de 2019.

    Parameters
    ----------
    federal: srd.federal.form_2019
        instance de la classe srd.federal.form_2019 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2019.csv")
        self.federal = federal


# program for 2020, derived from template, only requires modify
# functions that change
class program_2020(program_2019):

    """
    Version du programme de 2020.

    Parameters
    ----------
    federal: srd.federal.form_2020
        instance de la classe srd.federal.form_2020 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2020.csv")
        self.federal = federal

    def compute_net_inc_exemption(self, hh):
        """
        Fonction qui remplace dans le gabarit (classe *srd.oas.template*) la fonction du même nom, et calcule le revenu net incluant l'exemption sur les revenus du travail salarié.

        À partir de 2020-2021, les revenus de travail autonome bénéficient également de l'exemption. Les revenus du travail entre 5 000 $ et 10 000 $ bénéficient d'une nouvelle exemption partielle de 50%.

        Parameters
        ----------
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Revenu net de l'exemption sur les revenus du travail.
        """
        net_inc_exempt = 0
        for p in hh.sp:
            exempted_inc = min(p.inc_work, self.work_exempt)
            if p.inc_work > self.work_exempt:
                exempted_inc += 0.5 * (
                    min(p.inc_work, self.max_work_exempt) - self.work_exempt
                )
            payroll = p.payroll['cpp'] + p.payroll['cpp_supp'] + p.payroll['ei'] + p.payroll['qpip']
            net_inc_exempt += max(
                0, p.fed_return["gross_income"] - exempted_inc - payroll
            )
        return net_inc_exempt


class program_2021(program_2020):
    """
    Version du programme de 2021.

    Parameters
    ----------
    federal: srd.federal.form_2021
        instance de la classe srd.federal.form_2021 du module *federal*
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2021.csv")
        self.federal = federal

    def compute_pension(self, p, hh):
        """
        Fonction qui calcule la prestation de PSV.

        Parameters
        ----------

        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la PSV.
        """
        p.oas_65 = min(1, p.years_can / self.max_years_can) * self.oas_full
        p.oas = p.oas_65 * (1 + self.postpone_oas_bonus * p.oas_years_post)

        if p.age >= self.min_age_covid_bonus:
            p.oas += self.oas_covid_bonus
        return self.pension_clawback(p, hh)

    def gis(self, p, hh, income, low_high):
        """
        Fonction qui calcule la prestation de Supplément de revenu garanti.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        income: float
            revenu aux fins du calcul de la récupération du SRG
        low_high: string
            'low'/'high' pour calcul du bonus de SRG pour très faible revenu

        Returns
        -------
        float
            Montant du SRG (après récupération).
        """
        if low_high == 'low':
            gis_full, gis_bonus = self.gis_full_low, self.gis_bonus_low
        else:
            gis_full, gis_bonus = self.gis_full_high, self.gis_bonus_high

        if hh.couple:
            bonus_exempt = self.bonus_exempt_couple
        else:
            bonus_exempt = self.bonus_exempt_single

        gis = (gis_full + self.oas_full - p.oas_65) * p.sq_factor
        claw_gis = self.gis_claw_rate * income / (1+hh.couple)
        bonus = gis_bonus * p.sq_factor
        claw_bonus = self.bonus_claw_rate * max(0, hh.net_inc_exempt - bonus_exempt) / (1+hh.couple)
        return max(0, gis - claw_gis) + max(0, bonus - claw_bonus)

class program_2022(program_2021):
    """
    Version du programme de 2022.

    Parameters
    ----------
    federal: srd.federal.form_2022
        instance de la classe srd.federal.form_2022 du module Federal
    """

    def __init__(self, federal):
        add_params_as_attr(self, module_dir + "/oas/params/old_age_sec_2022.csv")
        self.federal = federal

    def compute_pension(self, p, hh):
        """
        Fonction qui calcule la prestation de PSV.

        Parameters
        ----------

        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant de la PSV.
        """
        p.oas_65 = min(1, p.years_can / self.max_years_can) * self.oas_full
        p.oas = p.oas_65 * (1 + self.postpone_oas_bonus * p.oas_years_post)

        if p.age >= self.min_age_oas_increase:
            p.oas += p.oas * self.rate_oas_increase
        return self.pension_clawback(p, hh)