import os
from srd import add_params_as_attr, add_schedule_as_attr
from srd.quebec import template

module_dir = os.path.dirname(os.path.dirname(__file__))


# wrapper to pick correct year
def form(year):
    """
    Fonction qui permet de sélectionner le formulaire d'impôt provincial par année.

    Parameters
    ----------
    year: int
        année (présentement entre 2016 et 2020)
    Returns
    -------
    class instance
        Une instance du formulaire pour l'année sélectionnée.
    """
    if year == 2016:
        p = form_2016()
    if year == 2017:
        p = form_2017()
    if year == 2018:
        p = form_2018()
    if year == 2019:
        p = form_2019()
    if year == 2020:
        p = form_2020()
    return p


class form_2016(template):
    """
    Formulaire d'impôt de 2016.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2016.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/health_contrib_2016.csv')


class form_2017(form_2016):
    """
    Formulaire d'impôt de 2017.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2017.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2017.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2017.csv')

    def calc_contributions(self, p, hh):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule les contributions.

        Cette fonction fait la somme des contributions du contribuable. La contribution santé est abolie en 2017.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        p.prov_return['contributions'] += self.add_contrib_subsid_chcare(p, hh)

    def get_donations_cred(self, p):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule le crédit d'impôt non-remboursable pour dons.

        Parameters
        ----------
        p: Person
            instance de la classe Person

        Returns
        -------
        float
            Montant du crédit
        """
        tot_donation = p.donation + p.gift

        if tot_donation <= self.nrtc_donation_low_cut:
            return tot_donation * self.nrtc_donation_low_rate
        else:
            extra_donation = tot_donation - self.nrtc_donation_low_cut
            high_inc = max(0, p.fed_return['taxable_income']
                             - self.nrtc_donation_high_cut)
            donation_high_inc = min(extra_donation, high_inc)
            donation_low_inc = extra_donation - donation_high_inc
            return (self.nrtc_donation_low_cut * self.nrtc_donation_low_rate
                    + donation_high_inc * self.nrtc_donation_high_rate
                    + donation_low_inc * self.nrtc_donation_med_rate)


class form_2018(form_2017):
    """
    Formulaire d'impôt de 2018.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2018.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2018.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2018.csv')

    def senior_assist(self, p, hh):
        """
        Fonction qui remplace dans le gabarit (classe *srd.quebec.template*) la fonction du même nom, et calcule le crédit remboursable pour support aux ainés. En vigueur à partir de 2018.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold

        Returns
        -------
        float
            Montant du crédit
        """
        if max([p.age for p in hh.sp]) < self.senior_assist_min_age:
            return 0

        n_elderly = len([p.age for p in hh.sp
                         if p.age >= self.senior_assist_min_age])
        amount = self.senior_assist_amount * n_elderly

        if hh.couple:
            cutoff = self.senior_assist_cutoff_couple
        else:
            cutoff = self.senior_assist_cutoff_single

        clawback = self.senior_assist_claw_rate * max(0, hh.fam_net_inc_prov - cutoff)

        return max(0, amount - clawback) / (1 + hh.couple)


class form_2019(form_2018):
    """
    Formulaire d'impôt de 2019.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2019.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2019.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2019.csv')

    def calc_contributions(self, p, hh):
        """
        Fonction qui remplace la fonction antérieure du même nom, et calcule les contributions.

        Cette fonction fait la somme des contributions du contribuable. La contribution additionnelle pour service de garde éducatifs à l'enfance subventionnés est abolie en 2019.

        Parameters
        ----------
        p: Person
            instance de la classe Person
        hh: Hhold
            instance de la classe Hhold
        """
        pass

class form_2020(form_2019):
    """
    Formulaire d'impôt de 2020.
    """
    def __init__(self):
        add_params_as_attr(self, module_dir + '/quebec/params/measures_2020.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/schedule_2020.csv')
        add_schedule_as_attr(self, module_dir + '/quebec/params/chcare_2020.csv')
