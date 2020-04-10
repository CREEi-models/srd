class federal:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold ##
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.deduc_val=0.0 ##
        self.taxinc = 0.0
        self.taxinc_val=0.0
        self.tax = 0.0 #
        self.ntcred = 0.0 #
        self.liab = 0.0
        self.rtcred = 0.0 #
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.cpp_contrib = 0.0
        self.rules = rules
        self.ncbs_val = 0.0
        self.ccb_val = 0.0
        self.cctb_val = 0.0
        self.uccb_val = 0.0
        self.ncbs_max = 0.0
        self.cctb_max = 0.0
        self.ccb_max = 0.0
        self.agecre_val=0.0
        self.ntcred_val=0.0
        self.witb_val =0.0
        self.witbds_val =0.0
        self.ccb_val = 0.0
        return

    def file(self):
        self.calc_totinc()
        self.calc_deduc()
        self.calc_taxinc()
        self.calc_tax()
        self.calc_ntcred()
        self.liab = self.tax - self.ntcred
        if (self.liab < 0.0):
            self.liab = 0.0
        self.calc_net_inc()
        self.calc_rtcred()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
        p.total_income = self.totinc
        return

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp
        p.fed_net_income = self.net_inc
        return

    def calc_deduc(self):
        p = self.hhold.sp[self.who]
        self.deduc += p.con_rrsp
        return

    def calc_taxinc(self):
        p = self.hhold.sp[self.who]
        self.taxinc = self.totinc
        self.taxinc -= p.inc_gis
        self.taxinc -= self.deduc
        self.taxinc -= p.inc_othntax
        return

    def calc_tax(self):
        brack = self.rules.brack
        rates = self.rules.rates
        i = self.taxinc
        t = 0.0
        g = 0.0
        for b, r in zip(brack, rates):
            if (i > b):
                t += r*(b-g)
                g = b
            else:
                t += r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_rate*self.rules.base
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred_val= self.ntcred
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc
        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age >= nage
        amount = 0.0
        if elig:
            amount += nmax
            if (inc > nbas):
                amount -= rate*(inc-nbas)
                if (amount < 0.0):
                    amount = 0.0
            amount *= self.rules.nrtc_rate
        self.agecre_val =amount
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        amount *= self.rules.nrtc_rate
        return amount

    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i, j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa > 0):
            elig = True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.calc_abatment()
        self.rtcred += self.uccb()
        self.rtcred += self.cctb()
        self.rtcred += self.ncbs()
        self.rtcred += self.canchcare()
        self.rtcred += self.ccb()
        self.rtcred += self.witb()
        self.rtcred += self.witbds()
        return

    def calc_abatment(self):
        amount = 0.0
        if (self.hhold.prov == 'qc'):
            amount += (1.0-self.rules.abatment)*self.liab
            self.calc_abatment = amount
        return amount

    def uccb(self):
        amount = 0.0
        if self.hhold.nkids0_5 >= 1:
            amount = (self.rules.uccb_amount * self.hhold.nkids0_5
                      + self.rules.uccb_6_17 * self.hhold.nkids6_17)
        self.inc_uccb = amount
        self.uccb_val = amount
        return amount

    def cctb(self):
        base = self.rules.cctb_base
        rstart = self.rules.cctb_redstart
        rr1c = self.rules.cctb_redrate_1ch
        rr2p = self.rules.cctb_redrate_2chplus
        su3c = self.rules.cctb_supp3rd
        hinc = 0.0
        for i, j in enumerate(self.hhold.sp):
            hinc += self.hhold.sp[i].inc_earn - self.hhold.sp[i].con_rrsp
        elig = False
        cctb = 0.0
        if self.hhold.prov != "ab":
            if self.hhold.nkids0_17 > 0:
                elig = True
                amount = hinc - rstart
                if amount < 0:
                    amount = 0
            if elig:
                nbase = base * self.hhold.nkids0_17
                if self.hhold.nkids0_17 == 1:
                    cctb = (nbase - (amount*rr1c))/2
                    self.cctb_max = nbase
                if self.hhold.nkids0_17 == 2:
                    cctb = (nbase - amount*rr2p)/2
                    self.cctb_max = nbase
                if self.hhold.nkids0_17 >= 3:
                    cctb = ((nbase + ((self.hhold.nkids0_17-2) * su3c)
                             - amount*rr2p)/2)
                    self.cctb_max = nbase + ((self.hhold.nkids0_17-2) * su3c)
            if cctb < 0:
                cctb = 0
        if self.hhold.prov == "ab":
            if self.hhold.nkids0_17 > 0:
                elig = True
            if elig:
                vmax = (self.rules.cctb_alb_minus7*self.hhold.nkids0_6
                        + self.rules.cctb_alb_7to11*self.hhold.nkids7_11
                        + self.rules.cctb_alb_12to15*self.hhold.nkids12_15
                        + self.rules.cctb_alb_16and17*self.hhold.nkids16_17)
                if self.hhold.nkids0_17 == 1:
                    red = max(0.0, hinc - rstart) * rr1c
                else:
                    red = max(0.0, hinc - rstart) * rr2p
                cctb = (vmax - red) / 2
                self.cctb_max = vmax
        self.cctb_val = cctb
        self.cctb_max /=2
        return cctb

    def ncbs(self):
        base1 = self.rules.ncbs_base_1ch
        base2 = self.rules.ncbs_base_2nd
        base3 = self.rules.ncbs_base_3rdplus
        rr1ch = self.rules.ncbs_redrate_1ch
        rr2ch = self.rules.ncbs_redrate_2ch
        rr3ch = self.rules.ncbs_redrate_3chplus
        redst = self.rules.ncbs_redstart
        hinc = 0.0
        for i, j in enumerate(self.hhold.sp):
            hinc += self.hhold.sp[i].total_income
        #hinc -= self.uccb()
        elig = False
        ncbs = 0
        if self.hhold.nkids0_17 > 0:
            elig = True
            amount = hinc - redst
            if amount < 0:
                amount = 0

        if elig:
            if self.hhold.nkids0_17 == 1:
                ncbs = (base1 - amount*rr1ch)/2
                self.ncbs_max = base1
            if self.hhold.nkids0_17 == 2:
                ncbs = (base1 + base2 - amount*rr2ch)/2
                self.ncbs_max = base1 + base2
            if self.hhold.nkids0_17 >= 3:
                ncbs = (base1 + base2 + base3 * (self.hhold.nkids0_17 - 2)
                        - amount*rr3ch)/2
                self.ncbs_max = (base1 + base2 + base3
                                 * (self.hhold.nkids0_17 - 2))
        if ncbs < 0:
            ncbs = 0
        self.ncbs_val = ncbs
        self.ncbs_max /= 2
        return ncbs

    def canchcare(self, dc_exp0_7=0.0, dc_exp8_16=0.0):
        maxm7 = self.rules.chcdeduc_max_minus7
        maxm16 = self.rules.chcdeduc_max_minus16
        rate = self.rules.chcdeduc_winc_rate
        self.p = self.hhold.sp[self.who]
        inc = self.p.inc_earn
        canchcare = 0.0
        exp = dc_exp0_7 + dc_exp8_16
        maxallow = self.hhold.nkids0_7 * maxm7 + self.hhold.nkids8_16 * maxm16
        incdeduc = inc * rate
        canchcare = min(exp, maxallow, incdeduc)
        if canchcare < 0:
            canchcare = 0.0
        return canchcare

    def ccb(self):
        base1 = self.rules.ccb_base_step_1
        rs11c = self.rules.ccb_rate_step1_1ch
        rs12c = self.rules.ccb_rate_step1_2ch
        rs13c = self.rules.ccb_rate_step1_3ch
        rs14c = self.rules.ccb_rate_step1_4ch_plus
        base2 = self.rules.ccb_base_step_2
        rs21c = self.rules.ccb_rate_step2_1ch
        rs22c = self.rules.ccb_rate_step2_2ch
        rs23c = self.rules.ccb_rate_step2_3ch
        rs24c = self.rules.ccb_rate_step2_4ch_plus
        ccb05 = self.rules.ccb_minus_6
        ccb617 = self.rules.ccb_6_17
        thrs1 = self.rules.ccb_thresh_step1
        nk017 = self.hhold.nkids0_17
        ccb = 0.0
        if nk017 > 0:
            if nk017 > 4:
                nk017 = 4
            l_rs1 = [rs11c, rs12c, rs13c, rs14c]
            l_rs2 = [rs21c, rs22c, rs23c, rs24c]
            hinc = 0.0
            for i, j in enumerate(self.hhold.sp):
                hinc += self.hhold.sp[i].inc_earn
            red_step1 = 0.0
            red_step2 = 0.0
            if nk017 == 1:
                rate_s1 = l_rs1[nk017-1]
                rate_s2 = l_rs2[nk017-1]
            if nk017 == 2:
                rate_s1 = l_rs1[nk017-1]
                rate_s2 = l_rs2[nk017-1]
            if nk017 == 3:
                rate_s1 = l_rs1[nk017-1]
                rate_s2 = l_rs2[nk017-1]
            if nk017 == 4:
                rate_s1 = l_rs1[nk017-1]
                rate_s2 = l_rs2[nk017-1]
            ccb = self.hhold.nkids0_5 * ccb05 + self.hhold.nkids6_17 * ccb617
            self.ccb_max = ccb/2
            if hinc > base1:
                diff = hinc - base1
                if min(diff, thrs1) < 0:
                    red_step1 = 0.0
                else:
                    red_step1 = min(thrs1, diff) * rate_s1
            if hinc > base2:
                diff = hinc - base2
                red_step2 = max(0, diff) * rate_s2
            ccb = max(ccb - red_step1 - red_step2, 0) / 2
        self.ccb_val = ccb
        return ccb

    def witb(self):
        witb = 0.0
        hnet = 0.0
        hwork = 0.0
        vmax = 0.0
        red = 0.0
        for i, j in enumerate(self.hhold.sp):
            hwork += self.hhold.sp[i].inc_earn + self.hhold.sp[i].selfemp_earn
            hnet += self.hhold.sp[i].fed_net_income
        if self.hhold.prov == 'qc':
            if self.hhold.couple:
                if self.hhold.nkids0_17 >= 1:
                    vmax = (self.rules.witb_rate_2adch
                            * (min(hwork, self.rules.witb_stop_couple)
                               - self.rules.witb_start_couple))
                    red = (self.rules.witb_redrate_2ad
                           * max(0.0, hnet - self.rules.witb_red_2adch))
                else:
                    vmax = (self.rules.witb_rate_couple
                            * (min(hwork, self.rules.witb_stop_couple)
                               - self.rules.witb_start_couple))
                    red = (self.rules.witb_redrate_2ad
                           * max(0.0, hnet - self.rules.witb_red_couple))
            else:
                if self.hhold.nkids0_17 >= 1:
                    vmax = (self.rules.witb_rate_1adch
                            * (min(hwork, self.rules.witb_stop_single)
                               - self.rules.witb_start_single))
                    red = (self.rules.witb_redrate_1ad
                           * max(0.0, hnet - self.rules.witb_red_1adch))
                else:
                    vmax = (self.rules.witb_rate_single
                            * (min(hwork, self.rules.witb_stop_single)
                               - self.rules.witb_start_single))
                    red = (self.rules.witb_redrate_1ad
                           * max(0.0, hnet - self.rules.witb_red_single))
        else:
            if self.hhold.couple:
                vmax = (self.rules.witb_rate_fam
                        * (min(hwork, self.rules.witb_stop_fam)
                           - self.rules.witb_start_fam))
                red = (self.rules.witb_redrate_fam
                       * max(0.0, hnet - self.rules.witb_red_fam))
            else:
                if self.hhold.nkids0_17 >= 1:
                    vmax = (self.rules.witb_rate_fam
                            * (min(hwork, self.rules.witb_stop_fam)
                               - self.rules.witb_start_fam))
                    red = (self.rules.witb_redrate_fam
                           * max(0.0, hnet - self.rules.witb_red_fam))
                else:
                    vmax = (self.rules.witb_rate_single
                            * (min(hwork, self.rules.witb_stop_single)
                               - self.rules.witb_start_single))
                    red = (self.rules.witb_redrate_single
                           * max(0.0, hnet - self.rules.witb_red_single))
        witb = max(0.0, vmax - red)
        self.witb_val = witb
        return witb

    def witbds(self):
        witbds = 0.0
        hnet = 0.0
        hwork = 0.0
        vmax = 0.0
        red = 0.0
        invalid = False
        for i, j in enumerate(self.hhold.sp):
            hwork += self.hhold.sp[i].inc_earn + self.hhold.sp[i].selfemp_earn
            hnet += self.hhold.sp[i].fed_net_income
            if self.hhold.sp[i].disabled:
                invalid = True
        if self.hhold.prov == 'qc':
            if invalid:
                if self.hhold.couple:
                    if self.hhold.nkids0_17 >= 1:
                        vmax = (self.rules.awitb_rate_couple
                                * (min(hwork, self.rules.awitb_stop_couple)
                                   - self.rules.awitb_start_couple))
                        red = (self.rules.awitb_redrate_couple
                               * max(0.0, hnet - self.rules.awitb_red_2adch))
                    else:
                        vmax = (self.rules.awitb_rate_couple
                                * (min(hwork, self.rules.awitb_stop_couple)
                                   - self.rules.awitb_start_couple))
                        red = (self.rules.awitb_redrate_couple
                               * max(0.0, hnet - self.rules.awitb_red_couple))
                else:
                    if self.hhold.nkids0_17 >= 1:
                        vmax = (self.rules.awitb_rate_single
                                * (min(hwork, self.rules.awitb_stop_single)
                                   - self.rules.awitb_start_single))
                        red = (self.rules.awitb_redrate_single
                               * max(0.0, hnet - self.rules.awitb_red_1adch))
                    else:
                        vmax = (self.rules.awitb_rate_single
                                * (min(hwork, self.rules.awitb_stop_single)
                                   - self.rules.awitb_start_single))
                        red = (self.rules.awitb_redrate_single
                               * max(0.0, hnet - self.rules.awitb_red_single))
        else:
            if invalid:
                if self.hhold.couple:
                    vmax = (self.rules.awitb_rate_fam
                            * (min(hwork, self.rules.awitb_stop_fam)
                               - self.rules.awitb_start_fam))
                    red = (self.rules.awitb_redrate_fam
                           * max(0.0, hnet - self.rules.awitb_red_fam))
                else:
                    if self.hhold.nkids0_17 >= 1:
                        vmax = (self.rules.awitb_rate_fam
                                * (min(hwork, self.rules.awitb_stop_fam)
                                   - self.rules.awitb_start_fam))
                        red = (self.rules.awitb_redrate_fam
                               * max(0.0, hnet - self.rules.awitb_red_fam))
                    else:
                        vmax = (self.rules.awitb_rate_single
                                * (min(hwork, self.rules.awitb_stop_single)
                                   - self.rules.awitb_start_single))
                        red = (self.rules.awitb_redrate_single
                               * max(0.0, hnet - self.rules.awitb_red_single))
        witbds = max(0.0, vmax - red)
        self.witbds_val = witbds
        return witbds