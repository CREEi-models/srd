
class quebec:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
        self.qccap_val = 0.0
        self.qccap_max = 0.0
        self.rtcred_val=0.0
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
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
            if (i >= b):
                t += r * (b - g)
                g = b
            else:
                t += r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_rate*self.rules.base
        cred_amount = 0
        cred_amount += self.get_agecred()
        cred_amount += self.get_singlecred()
        cred_amount += self.get_pencred()
        cred_amount = max(cred_amount - self.ntcred_clawback(), 0)
        cred_amount += self.get_disacred()
        self.ntcred += cred_amount * self.rules.nrtc_rate

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        amount = 0.0
        if p.age >= self.rules.nrtc_age:
            amount += self.rules.nrtc_age_max
        return amount

    def get_singlecred(self):
        amount = 0
        if self.hhold.couple is False:
            amount += self.rules.nrtc_single
        return amount

    def get_pencred(self):
        return min(self.hhold.sp[self.who].inc_rpp,
                   self.rules.nrtc_pension_max)

    def get_disacred(self):
        disa = 0
        amount = 0
        for i, j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if disa > 0:
            amount = self.rules.nrtc_disabled
        return amount

    def ntcred_clawback(self):
        incfam = self.taxinc
        if self.hhold.couple:
            p2 = self.hhold.sp[1-self.who]
            incfam += p2.pro_net_income 
        nbas = self.rules.nrtc_age_base
        clawrate = self.rules.nrtc_age_rate
        return max(clawrate * (incfam - nbas), 0)

    def calc_rtcred(self):
        self.rtcred += self.qccap()
        self.rtcred += self.qcchcare()
        self.rtcred += self.get_wp()
        self.rtcred_val=self.rtcred
        return

    def get_inc_deduc(self, get_for_spouse=0):
        p = self.hhold.sp[self.who]
        if get_for_spouse == 1:
            ind_spouse = 0
            if self.who == 0:
                ind_spouse = 1
                p = self.hhold.sp[ind_spouse]
            else:
                p = self.hhold.sp[ind_spouse]
        elig = False
        inc = p.inc_earn + p.selfemp_earn
        dmax = self.rules.qc_w_inc_deduc_max
        rate = self.rules.qc_w_inc_deduc_rate
        inc_deduc = 0.0
        if inc > 0:
            elig = True

        if elig:
            inc_deduc = min(dmax, inc * rate)
        return inc_deduc

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp - self.get_inc_deduc()
        p.pro_net_income = self.net_inc
        return

    def qccap(self):
        max1c = self.rules.cap_max_1ch
        max2c = self.rules.cap_max_2ndch
        max3c = self.rules.cap_max_3rdch
        max4c = self.rules.cap_max_4thchplus
        sup1p = self.rules.cap_monosupp
        min1c = self.rules.cap_min_1ch
        min2c = self.rules.cap_min_2ndchplus
        min1p = self.rules.cap_min_mono
        rsing = self.rules.cap_red_single
        rcoup = self.rules.cap_red_couple
        rrate = self.rules.cap_redrate
        nkids = self.hhold.nkids0_17
        qccap = 0.0
        amount = 0.0
        elig = False
        if (nkids > 0 and self.hhold.prov == 'qc'):
            elig = True
        if elig:
            self.calc_totinc()
            hinc = self.hhold.sp[self.who].inc_earn - self.get_inc_deduc()
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += (self.hhold.sp[who2].inc_earn
                         - self.get_inc_deduc())
                amount = (hinc - rcoup)
                if amount < 0:
                    amount = 0
                else:
                    amount = amount*rrate
                if nkids == 1:
                    self.qccap_max = max1c
                    qccap = max(min1c, max1c - amount)
                if nkids == 2:
                    self.qccap_max = max1c + max2c
                    qccap = max(min1c + min2c, max1c + max2c - amount)
                if nkids == 3:
                    self.qccap_max = max1c + max2c + max3c
                    qccap = max(min1c + 2*min2c, max1c + max2c + max3c
                                - amount)
                if nkids >= 4:
                    self.qccap_max = max1c + max2c + max3c + (nkids-3)*max4c
                    qccap = max(min1c + (nkids - 1)*min2c, max1c + max2c
                                + max3c + (nkids-3)*max4c - amount)

            else:
                amount = (hinc - rsing)
                if amount < 0:
                    amount = 0
                else:
                    amount = amount*rrate
                if nkids == 1:
                    self.qccap_max = max1c +sup1p
                    qccap = max(min1c + min1p, max1c + sup1p - amount)
                if nkids == 2:
                    self.qccap_max = max1c + max2c +sup1p
                    qccap = max(min1c + min2c + min1p, max1c + max2c + sup1p
                                - amount)
                if nkids == 3:
                    self.qccap_max = max1c + max2c + max3c +sup1p
                    qccap = max(min1c + 2*min2c + min1p, max1c + max2c + max3c
                                + sup1p - amount)
                if nkids >= 4:
                    self.qccap_max = (max1c + max2c + max3c + (nkids-3)*max4c
                                     + sup1p)
                    qccap = max(min1c + (nkids - 1)*min2c + min1p,
                                max1c + max2c + max3c + (nkids-3)*max4c
                                + sup1p - amount)
        self.qccap_val = qccap
        return qccap

    def qcchcare(self, dc_exp0_7=0.0, dc_exp8_16=0.0, dc_exp7d=0.0):
            self.qcchcare_val=0.0
            maxm7 = self.rules.chcare_max_minus7
            maxm16 = self.rules.chcare_max_minus16
            nbrack = len(self.rules.chcare_brack)
            hinc = 0.0
            qcchcare = 0.0
            self.calc_totinc()
            hinc = self.hhold.sp[self.who].inc_earn - self.get_inc_deduc()
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += (self.hhold.sp[who2].inc_earn
                         - self.get_inc_deduc())
            if(hinc >= self.rules.chcare_brack[nbrack-2]):
                dc7 = (max(0, (dc_exp0_7 - dc_exp7d))
                       * self.rules.chcare_rate[nbrack-1])
                dc_nkids7 = (self.hhold.nkids0_7 * maxm7
                             * self.rules.chcare_rate[nbrack-1])
                chcare1 = min(dc7, dc_nkids7)
                dc16 = dc_exp8_16 * self.rules.chcare_rate[nbrack-1]
                dc_nkids16 = (self.hhold.nkids8_16 * maxm16
                              * self.rules.chcare_rate[nbrack-1])
                chcare2 = min(dc16, dc_nkids16)
                qcchcare = chcare1 + chcare2
            else:
                for i in range(nbrack - 2):
                    if(hinc <= self.rules.chcare_brack[i]):
                        dc7 = (max(0, (dc_exp0_7 - dc_exp7d))
                               * self.rules.chcare_rate[i])
                        dc_nkids7 = (self.hhold.nkids0_7 * maxm7
                                     * self.rules.chcare_rate[i])
                        chcare1 = min(dc7, dc_nkids7)
                        dc16 = dc_exp8_16 * self.rules.chcare_rate[i]
                        dc_nkids16 = (self.hhold.nkids8_16 * maxm16
                                      * self.rules.chcare_rate[i])
                        chcare2 = min(dc16, dc_nkids16)
                        qcchcare = chcare1 + chcare2
                        self.qcchcare_val=qcchcare
            return qcchcare

    def get_wp(self):
        self.wp_val=0.0
        wp = 0.0
        hnet = 0.0
        hwork = 0.0
        invalid = False
        for i, j in enumerate(self.hhold.sp):
            hwork += self.hhold.sp[i].inc_earn + self.hhold.sp[i].selfemp_earn
            hnet += self.hhold.sp[i].pro_net_income
            if self.hhold.sp[i].disabled:
                invalid = True
        if invalid:
            if self.hhold.couple:
                vmax = (self.rules.awp_rate_couple
                        * (min(hwork, self.rules.awp_stop_couple)
                           - self.rules.awp_start_couple))
                red = (self.rules.awp_redrate_couple
                       * max(0.0, hnet - self.rules.awp_red_couple))
                wp = max(0.0, vmax - red)
            else:
                vmax = (self.rules.awp_rate_single
                        * (min(hwork, self.rules.awp_stop_single)
                           - self.rules.awp_start_single))
                red = (self.rules.awp_redrate_single
                       * max(0.0, hnet - self.rules.awp_red_single))
                wp = max(0.0, vmax - red)
        else:
            if self.hhold.couple:
                if self.hhold.nkids0_21 > 0:
                    rate = self.rules.wp_rate_couple_child
                else:
                    rate = self.rules.wp_rate_couple
                vmax = (rate * (min(hwork, self.rules.wp_stop_couple)
                                - self.rules.wp_start_couple))
                red = (self.rules.wp_redrate_couple
                       * max(0.0, hnet - self.rules.wp_red_couple))
                wp = max(0.0, vmax - red)
            else:
                if self.hhold.nkids0_21 > 0:
                    rate = self.rules.wp_rate_single_child
                else:
                    rate = self.rules.wp_rate_single
                vmax = (rate * (min(hwork, self.rules.wp_stop_single)
                                - self.rules.wp_start_single))
                red = (self.rules.wp_redrate_single
                       * max(0.0, hnet - self.rules.wp_red_single))
                wp = max(0.0, vmax - red)
        self.wp_val=wp
        return wp


class alberta:
    def __init__(self, hhold, who, rules,fed):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
        self.fedforms = fed
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
            if (i >= b):
                t += r*(b-g)
                g = b
            else:
                t += r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
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
        # for single
        sing = self.rules.nrtc_single
        if not self.hhold.couple:
            elig = True
        else:
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount < 0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
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
        self.rtcred += self.get_abcb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp
        return

    def get_abcb(self):
        self.abcb_val=0.0
        abcb = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            elig = True
        if elig:
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += (self.hhold.sp[who2].inc_earn
                         - self.hhold.sp[who2].con_rrsp)
            if nkids0_17 == 1:
                vmax = self.rules.abcb_base_1ch
                red = (max(0.0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_1ch))
                abcb = max(0.0, vmax-red)
            elif nkids0_17 == 2:
                vmax = self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                red = (max(0.0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_2ch))
                abcb = max(0.0, vmax-red)
            elif nkids0_17 == 3:
                vmax = (self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                        + self.rules.abcb_base_3ch)
                red = (max(0.0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_3ch))
                abcb = max(0.0, vmax-red)
            elif nkids0_17 > 3:
                vmax = (self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                        + self.rules.abcb_base_3ch + self.rules.abcb_base_4ch)
                red = (max(0.0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_4ch))
                abcb = max(0.0, vmax-red)
        self.abcb_val=abcb
        return abcb


class british_columbia:
    def __init__(self, hhold, who, rules, fed):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
        self.fedforms = fed
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
            if (i >= b):
                t += r*(b-g)
                g = b
            else:
                t += r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
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
        # for single
        sing = self.rules.nrtc_single
        if not self.hhold.couple:
            elig = True
        else:
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount < 0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
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

        self.rtcred += self.get_bcfb()
        self.rtcred += self.get_bcectb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp
        p.pro_net_income = self.net_inc
        return

    def get_bcfb(self):
        self.bcfb_val=0.0
        amount = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            elig = True
        if elig:
            ncbs = self.fedforms[self.who].ncbs()
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                #pro_form2 = british_columbia(self.hhold, who2, self.rules)
                hinc += (self.hhold.sp[who2].inc_earn
                         - self.hhold.sp[who2].con_rrsp)
            if nkids0_17 == 1:
                vmax = self.rules.bcfb_amount - ncbs
                red = (self.rules.bcfb_reducrate_1dep
                       * (hinc - self.rules.bcfb_reducstart))
                amount = vmax - red
            if nkids0_17 >= 0:
                vmax = self.rules.bcfb_amount*nkids0_17 - ncbs
                red = (self.rules.bcfb_reducrate_2dep
                       * (hinc - self.rules.bcfb_reducstart))
                amount = vmax - red
            if amount < 0:
                amount = 0
        self.bcfb_val=amount
        return amount

    def get_bcectb(self):
        self.bcectb_val=0.0
        amount = 0.0
        elig = False
        nkids0_5 = self.hhold.nkids0_5
        if nkids0_5 > 0:
            elig = True
        if elig:
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += (self.hhold.sp[who2].inc_earn
                         - self.hhold.sp[who2].con_rrsp)
            vmax = self.rules.bcectb_base*nkids0_5
            red = (max(0, (hinc - self.rules.bcectb_redstart))
                   * nkids0_5 * self.rules.bcectb_redrate)
            amount = vmax - red
            if amount < 0:
                amount = 0
        self.bcectb_val=amount
        return amount

    def get_bceib(self):
        self.bceib_val=0.0
        bceib = 0.0
        hwork = 0.0
        hnet = 0.0
        for i, j in enumerate(self.hhold.sp):
            hwork += self.hhold.sp[i].inc_earn + self.hhold.sp[i].selfemp_earn
            hnet += self.hhold.sp[i].pro_net_income
        if self.hhold.nkids0_17 == 1:
            vmax = (self.rules.bceib_base_1stch
                    * (min(self.rules.bceib_min, hwork)
                       - self.rules.bceib_phasein) / self.rules.bceib_div)
            red = max(0.0, self.rules.bceib_redrate_1dep
                      * (hnet - self.rules.bceib_redstart))
        if self.hhold.nkids0_17 == 2:
            vmax = ((self.rules.bceib_base_1stch
                     + self.rules.bceib_base_2ndch)
                    * (min(self.rules.bceib_min, hwork)
                       - self.rules.bceib_phasein)
                    / self.rules.bceib_div)
            red = (max(0.0, self.rules.bceib_redrate_2dep
                       * (hnet - self.rules.bceib_redstart)))
        if self.hhold.nkids0_17 > 2:
            vmax = ((self.rules.bceib_base_1stch + self.rules.bceib_base_2ndch
                     + self.rules.bceib_base_3rdchplus
                     * (self.hhold.nkids0_17-2))
                    * (min(self.rules.bceib_min, hwork)
                       - self.rules.bceib_phasein) / self.rules.bceib_div)
            red = (max(0.0, self.rules.bceib_redrate_3dep
                       * (hnet - self.rules.bceib_redstart)))
        bceib = max(0.0, vmax-red)
        self.bceib_val=bceib
        return bceib


class newfoundland:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred+= self.get_nlcb()

    def calc_net_inc(self):
         p = self.hhold.sp[self.who]
         self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
         return
    def get_nlcb(self):
        self.nlcb=0.0
        nlcb = 0.0
        nlmbns = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig=True
        if elig:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
            if nkids0_17==1:
                red = max(0.0, self.rules.nlcb_redrate_1dep * (hinc - self.rules.nlcb_redstart))
                nlcb = max(0.0, self.rules.nlcb_base_1stch - red)
            elif nkids0_17 ==2:
                red = max(0.0, self.rules.nlcb_redrate_2dep * (hinc - self.rules.nlcb_redstart))
                nlcb = max(0.0, self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch - red)
            elif nkids0_17 ==3:
                red = max(0.0, self.rules.nlcb_redrate_3dep * (hinc - self.rules.nlcb_redstart))
                nlcb = max(0.0, self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch +
                           self.rules.nlcb_base_3rdch- red)
            elif nkids0_17 >=4:
                red_rate = self.rules.nlcb_redrate_4depplus * (nkids0_17-3)
                red = max(0.0,  red_rate * (hinc - self.rules.nlcb_redstart))
                nlcb = max(0.0, self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch +
                           self.rules.nlcb_base_3rdch + self.rules.nlcb_base_4thch- red)
            if (self.hhold.nkids0_1>0 and hinc < self.rules.nlcb_stop):
                nlmbns = max(0.0, (self.rules.nlmbns_amount * self.hhold.nkids0_1) + self.rules.nlmbns_bonus)
            nlcb+= nlmbns
        self.nlcb=nlcb
        return nlcb

class pei:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        pass

    def calc_net_inc(self):
         p = self.hhold.sp[self.who]
         self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
         return
class new_brunswick:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_nbctb()


    def calc_net_inc(self):
         p = self.hhold.sp[self.who]
         self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
         return
    def get_nbctb(self):
         self.nbctb_val=0.0
         nbctb = 0.0
         nbss = 0.0
         elig = False
         nkids0_17 = self.hhold.nkids0_17
         nkids5_17 = self.hhold.nkids5_17
         if nkids0_17 >0:
             elig=True
         if elig:
             hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
             if self.hhold.couple:
                 if self.who == 1:
                     who2 = 0
                 if self.who == 0:
                     who2 = 1
                 hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
             vmax = self.rules.nbctb_amount * nkids0_17
             red = max(0.0, self.rules.nbwis_redrate * (hinc - self.rules.nbctb_redstart))
             max_wis = max(0.0,self.rules.nbwis_rate* (min(hinc, self.rules.nbwis_stop) - self.rules.nbwis_phasein))
             red_wis = max(0.0, self.rules.nbwis_redrate * (hinc - self.rules.nbwis_redstart))
             nbctb = max(0.0, vmax - red) + max_wis - red_wis
             if (nkids5_17 >0 and hinc <= self.rules.nbss_stop):
                 nbss = self.rules.nbss_amount * nkids5_17
                 nbctb += nbss
         self.nbctb_val=nbctb
         return nbctb


class nova_scotia:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_nscb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_nscb(self):
        self.nscb_val=0.0
        nscb = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig=True
        if elig:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
            if nkids0_17 == 1:
                vmax = self.rules.nscb_base_1stch
                red = max(0.0, self.rules.nscb_redrate_1dep * (hinc - self.rules.nscb_redstart))
                nscb = vmax - red
            elif nkids0_17 ==2:
                vmax = self.rules.nscb_base_1stch + self.rules.nscb_base_2ndch
                red = max(0.0, self.rules.nscb_redrate_2dep * (hinc - self.rules.nscb_redstart))
                nscb = vmax - red
            elif nkids0_17 >=3:
                vmax = (self.rules.nscb_base_1stch + self.rules.nscb_base_2ndch +
                        self.rules.nscb_base_3rdchplus * (nkids0_17-2))
                red_rate = self.rules.nscb_redrate_2dep + self.rules.nscb_redrate_3depplus * (nkids0_17-2)
                red = max(0.0,   red_rate * (hinc - self.rules.nscb_redstart))
                nscb = vmax - red
        self.nscb_val=nscb
        return nscb

class ontario:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_ocb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_ocb(self):
        self.ocb_val=0.0
        amount = 0.0
        hinc=0.0
        elig = False
        if self.hhold.nkids0_17 >0:
            elig = True
        if elig:
           hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
           if self.hhold.couple:
               if self.who == 1:
                   who2 = 0
               if self.who == 0:
                   who2 = 1
               hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
           max_amount = self.rules.ocb_max * self.hhold.nkids0_17
           reduc      = (hinc - self.rules.ocb_redstart) * self.rules.ocb_redrate
           amount = max(0.0,max_amount - reduc)
        self.ocb_val=amount
        return amount

class manitoba:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount
    def calc_rtcred(self):
        self.rtcred += self.get_mancb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_mancb(self):
        self.mancb_val=0.0
        mancb = 0.0
        hinc=0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig = True
        if elig:
           hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
           if self.hhold.couple:
               if self.who == 1:
                   who2 = 0
               if self.who == 0:
                   who2 = 1
               hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
           if nkids0_17 == 1:
               vmax = self.rules.mancb_base
               red  = max(0.0, (hinc - self.rules.mancb_redstart)*self.rules.mancb_redrate_1ch)
               mancb = max(0.0, vmax-red)
           elif nkids0_17==2:
               vmax = self.rules.mancb_base*nkids0_17
               red  = max(0.0, (hinc - self.rules.mancb_redstart)*self.rules.mancb_redrate_2ch)
               mancb = max(0.0, vmax-red)
           elif nkids0_17>2:
               vmax = self.rules.mancb_base*nkids0_17
               red  = max(0.0, (hinc - self.rules.mancb_redstart)*self.rules.mancb_redrate_3chplus)
               mancb = max(0.0, vmax-red)
        self.mancb_val=mancb
        return mancb
class saskatchewan:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
        return amount

    def get_pencred(self):
        amount = self.hhold.sp[self.who].inc_rpp
        if (amount > self.rules.nrtc_pension_max):
            amount = self.rules.nrtc_pension_max
        return amount
    def get_disacred(self):
        elig = False
        disa = 0
        amount = 0
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        pass

    def calc_net_inc(self):
         p = self.hhold.sp[self.who]
         self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
         return
class nw_territories:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_rate*self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
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
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_ntcb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_ntcb(self):
        self.ntcb_val=0.0
        ntcb = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig=True
        if elig:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            earn = self.hhold.sp[self.who].inc_earn + self.hhold.sp[self.who].selfemp_earn
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
                earn += self.hhold.sp[who2].inc_earn + self.hhold.sp[who2].selfemp_earn
            if nkids0_17 ==1:
                vmax = (self.rules.ntcb_amount + self.rules.nttwb_base_1stch *
                           (min(self.rules.nttwb_min, earn) - self.rules.nttwb_start)/self.rules.nttwb_div)
                red = max(0.0, self.rules.nttwb_redrate_1ch * (hinc - self.rules.nttwb_redstart))
                ntcb = max(0.0, vmax - red)
            elif nkids0_17>1:
                vmax = (self.rules.ntcb_amount*nkids0_17 + self.rules.nttwb_base_2ndchplus *
                           (min(self.rules.nttwb_min, earn) - self.rules.nttwb_start)/self.rules.nttwb_div)
                red = max(0.0, self.rules.nttwb_redrate_2ch * (hinc - self.rules.nttwb_redstart))
                ntcb = max(0.0, vmax - red)
        self.ntcb_val=ntcb
        return ntcb
class yukon:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_rate*self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
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
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_yucb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_yucb(self):
        self.yucb=0.0
        yucb = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig=True
        if elig:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
            if nkids0_17 ==1:
                vmax = self.rules.yucb_amount
                red = max(0.0, self.rules.yucb_redrate_1ch *(hinc - self.rules.yucb_redstart))
                yucb = max(0.0, vmax - red)
            elif nkids0_17>1:
                vmax = self.rules.yucb_amount * nkids0_17
                red = max(0.0, self.rules.yucb_redrate_2ch *(hinc - self.rules.yucb_redstart))
                yucb = max(0.0, vmax - red)
        self.yucb=yucb
        return yucb

class nuvavut:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.totinc = 0.0
        self.deduc = 0.0
        self.taxinc = 0.0
        self.tax = 0.0
        self.ntcred = 0.0
        self.liab = 0.0
        self.rtcred = 0.0
        self.taxpay = 0.0
        self.dspinc = 0.0
        self.rules = rules
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
        self.calc_rtcred()
        self.calc_net_inc()
        return

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = 0
        self.totinc += p.inc_earn
        self.totinc += p.inc_oas
        self.totinc += p.inc_gis
        self.totinc += p.inc_rpp
        self.totinc += p.inc_cpp
        self.totinc += p.inc_othtax
        self.totinc += p.inc_othntax
        self.totinc += p.inc_rrsp
        self.totinc += p.inc_uccb
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
        for b,r in zip(brack,rates):
            if (i>=b):
                t+=r*(b-g)
                g=b
            else :
                t+=r*(i-g)
                break
        self.tax = t
        return

    def calc_ntcred(self):
        self.ntcred += self.rules.nrtc_rate*self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        return

    def get_agecred(self):
        p = self.hhold.sp[self.who]
        inc = self.taxinc

        nage = self.rules.nrtc_age
        nmax = self.rules.nrtc_age_max
        nbas = self.rules.nrtc_age_base
        rate = self.rules.nrtc_age_rate
        elig = p.age>=nage
        amount = 0.0
        if elig:
            amount += nmax
        # for single
        sing = self.rules.nrtc_single
        if self.hhold.couple==False:
            elig = True
        else :
            elig = False
        if elig:
            amount += sing
        # claw both
        if (inc > nbas):
            amount -= rate*(inc-nbas)
            if (amount <0.0):
                amount = 0.0
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
        for i,j in enumerate(self.hhold.sp):
            disa += int(self.hhold.sp[i].disabled)
        if (disa>0):
            elig=True
        if(elig):
            amount = self.rules.nrtc_disabled
        return amount

    def calc_rtcred(self):
        self.rtcred += self.get_nucb()

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        self.net_inc = self.totinc - p.con_rrsp #- self.get_inc_deduc()
        return
    def get_nucb(self):
        self.nucb_val=0.0
        nucb = 0.0
        elig = False
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 >0:
            elig=True
        if elig:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            earn = self.hhold.sp[self.who].inc_earn + self.hhold.sp[self.who].selfemp_earn
            if self.hhold.couple:
                if self.who == 1:
                    who2 = 0
                if self.who == 0:
                    who2 = 1
                hinc += self.hhold.sp[who2].inc_earn - self.hhold.sp[who2].con_rrsp
                earn += self.hhold.sp[who2].inc_earn + self.hhold.sp[who2].selfemp_earn
            if nkids0_17 == 1:
                vmax = self.rules.nucb_amount
                wbon = (self.rules.nutwb_base_1stch*(min(self.rules.nutwb_min, earn)-
                                                    self.rules.nutwb_start)/self.rules.nutwb_div)
                red = max(0.0, self.rules.nutwb_redrate_1ch*(hinc - self.rules.nutwb_redstart))
                nucb = max(0.0, vmax+wbon-red)
            elif nkids0_17 >1:
                vmax = self.rules.nucb_amount * nkids0_17
                wbon = (self.rules.nutwb_base_2ndchplus*(min(self.rules.nutwb_min, earn)-
                                                    self.rules.nutwb_start)/self.rules.nutwb_div)
                red = max(0.0, self.rules.nutwb_redrate_2ch*(hinc - self.rules.nutwb_redstart))
                nucb = max(0.0, vmax+wbon-red)
        self.nucb_val=nucb
        return nucb