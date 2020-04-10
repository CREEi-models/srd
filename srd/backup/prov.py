import tax

class Province:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.rules = rules

    def file(self):
        self.calc_totinc()
        self.calc_deduc()
        self.calc_taxinc()
        self.calc_tax()
        self.calc_ntcred()
        self.liab = max(self.tax - self.ntcred, 0)
        self.calc_rtcred()
        self.calc_net_inc()

    def calc_totinc(self):
        p = self.hhold.sp[self.who]
        self.totinc = (p.inc_earn
                       + p.inc_oas
                       + p.inc_gis
                       + p.inc_rpp
                       + p.inc_cpp
                       + p.inc_othtax
                       + p.inc_rrsp
                       + p.inc_uccb)
        p.total_income = self.totinc
    
    def calc_deduc(self):
        self.deduc = self.hhold.sp[self.who].con_rrsp
        
    def calc_taxinc(self):
        p = self.hhold.sp[self.who]
        self.taxinc = self.totinc
        self.taxinc -= p.inc_gis
        self.taxinc -= self.deduc
        self.taxinc -= p.inc_othntax
    
    def calc_tax(self):
        tax = 0
        prev_bracket = 0
        for bracket, rate in zip(self.rules.brack, self.rules.rates):
            if self.taxinc >= bracket:
                tax += rate * (bracket - prev_bracket)
                prev_bracket = bracket
            else:
                tax += rate * (self.taxinc - prev_bracket)
                break
        self.tax = tax

    def calc_ntcred(self):
        self.ntcred = 0
        self.ntcred += self.rules.nrtc_basic
        self.ntcred += self.get_agecred()
        self.ntcred += self.get_singlecred()
        self.ntcred += self.get_pencred()
        self.ntcred += self.get_disacred()
        self.ntcred *= self.rules.nrtc_rate

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
        amount = 0
        if sum([sp.disabled for sp in self.hhold.sp]) > 0:
            amount += self.rules.nrtc_disabled
        return amount

    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        p.pro_net_income = self.net_inc = self.totinc - p.con_rrsp

    def calc_rtcred(self):
        pass

class QC(Province):
    def calc_net_inc(self):
        p = self.hhold.sp[self.who]
        net_inc = self.totinc - p.con_rrsp - self.get_inc_deduc()
        p.pro_net_income = self.net_inc = net_inc

    def get_inc_deduc(self, get_for_spouse=0):
        p = self.hhold.sp[self.who]
        if get_for_spouse:
            p = self.hhold.sp[1 - self.who]
        return min(self.rules.qc_w_inc_deduc_rate * p.inc_earn + p.selfemp_earn,
                   self.rules.qc_w_inc_deduc_max)
    
    def calc_ntcred(self):
        self.ntcred = 0
        self.ntcred += self.rules.nrtc_rate*self.rules.base
        cred_amount = 0
        cred_amount += self.get_agecred()
        cred_amount += self.get_singlecred()
        cred_amount += self.get_pencred()
        cred_amount = max(cred_amount - self.ntcred_clawback(), 0)
        cred_amount += self.get_disacred()
        self.ntcred += cred_amount * self.rules.nrtc_rate

    def get_singlecred(self):
        amount = 0
        if self.hhold.couple is False:
            amount += self.rules.nrtc_single
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
        self.rtcred = 0
        self.rtcred += self.qccap()
        self.rtcred += self.qcchcare()
        self.rtcred += self.get_wp()
        self.rtcred_val=self.rtcred
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
        
        if nkids > 0:
            self.calc_totinc() # necessary?
            hinc = self.hhold.sp[self.who].inc_earn - self.get_inc_deduc()

            if self.hhold.couple:
                who2 = 1 -self.who
                qc_form2 = QC(self.hhold, who2, self.rules) # seems strange !!!
                hinc += (qc_form2.hhold.sp[who2].inc_earn 
                         - qc_form2.get_inc_deduc())
                amount = rrate * max(hinc - rcoup, 0)

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
                amount =  rrate * max(hinc - rsing, 0)
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

    def qcchcare(self, dc_exp0_7=0, dc_exp8_16=0, dc_exp7d=0):
            self.qcchcare_val=0.0
            maxm7 = self.rules.chcare_max_minus7
            maxm16 = self.rules.chcare_max_minus16
            nbrack = len(self.rules.chcare_brack)
            hinc, qcchcare = 0, 0
            self.calc_totinc() # necessary
            hinc = self.hhold.sp[self.who].inc_earn - self.get_inc_deduc()

            if self.hhold.couple:  # this part is same as in qccap()
                who2 = 1 - self.who
                qc_form2 = QC(self.hhold, who2, self.rules)
                hinc += (qc_form2.hhold.sp[who2].inc_earn
                         - qc_form2.get_inc_deduc())
            if hinc >= self.rules.chcare_brack[nbrack-2]:
                dc7 = (max(0, dc_exp0_7 - dc_exp7d)
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
                    if hinc <= self.rules.chcare_brack[i]: # this part is same as above
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
        self.wp_val, wp, hnet, hwork = 0, 0, 0, 0
        for p in self.hhold.sp:
            hwork += p.inc_earn + p.selfemp_earn
            hnet += p.pro_net_income

        if sum([p.disabled for p in self.hhold.sp]) > 0:
            if self.hhold.couple:
                vmax = (self.rules.awp_rate_couple
                        * (min(hwork, self.rules.awp_stop_couple)
                           - self.rules.awp_start_couple))
                red = (self.rules.awp_redrate_couple
                       * max(hnet - self.rules.awp_red_couple, 0))
            else:
                vmax = (self.rules.awp_rate_single
                        * (min(hwork, self.rules.awp_stop_single)
                           - self.rules.awp_start_single))
                red = (self.rules.awp_redrate_single
                       * max(hnet - self.rules.awp_red_single), 0)
            
        else:
            if self.hhold.couple:
                if self.hhold.nkids0_21 > 0:
                    rate = self.rules.wp_rate_couple_child
                else:
                    rate = self.rules.wp_rate_couple
                vmax = (rate * (min(hwork, self.rules.wp_stop_couple)
                                - self.rules.wp_start_couple))
                red = (self.rules.wp_redrate_couple
                       * max(hnet - self.rules.wp_red_couple), 0)
            else:
                if self.hhold.nkids0_21 > 0:
                    rate = self.rules.wp_rate_single_child
                else:
                    rate = self.rules.wp_rate_single
                vmax = (rate * (min(hwork, self.rules.wp_stop_single)
                                - self.rules.wp_start_single))
                red = (self.rules.wp_redrate_single
                       * max(hnet - self.rules.wp_red_single), 0)
        wp = max(vmax - red, 0)
        self.wp_val = wp
        return wp
    

class AB(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_abcb()

    def get_abcb(self):
        self.abcb_val, abcb = 0, 0
        if self.hhold.nkids0_17 > 0:
            tx = tax.tax()  # created instance of tax ???
            tx.filefed(self.hhold)
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                who2 = 1 - self.who
                pro_form2 = AB(self.hhold, who2, self.rules)
                hinc += (pro_form2.hhold.sp[who2].inc_earn
                         - pro_form2.hhold.sp[who2].con_rrsp)
            if self.hhold.nkids0_17 == 1:
                vmax = self.rules.abcb_base_1ch
                red = (max(0.0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_1ch))            
            elif self.hhold.nkids0_17 == 2:
                vmax = self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                red = (max(0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_2ch))
            elif self.hhold.nkids0_17 == 3:
                vmax = (self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                        + self.rules.abcb_base_3ch)
                red = (max(0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_3ch))
            elif self.hhold.nkids0_17 > 3:
                vmax = (self.rules.abcb_base_1ch + self.rules.abcb_base_2ch
                        + self.rules.abcb_base_3ch + self.rules.abcb_base_4ch)
                red = (max(0, (hinc - self.rules.abcb_redstart)
                           * self.rules.abcb_redrate_4ch))
            abcb = max(vmax - red, 0)
        self.abcb_val = abcb
        return abcb


class BC(Province):
    def calc_rtcred(self):
        self.rtcred = self.get_bcfb()
        self.rtcred += self.get_bcectb()

    def get_bcfb(self):
        self.bcfb_val, amount = 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if self.hhold.nkids0_17 > 0:
            tx = tax.tax()
            tx.filefed(self.hhold)
            ncbs = tx.fedforms[self.who].ncbs()
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                who2 = 1 - self.who
                pro_form2 = BC(self.hhold, who2, self.rules)
                hinc += (pro_form2.hhold.sp[who2].inc_earn
                         - pro_form2.hhold.sp[who2].con_rrsp)
            if nkids0_17 == 1:
                vmax = self.rules.bcfb_amount - ncbs
                red = (self.rules.bcfb_reducrate_1dep
                       * (hinc - self.rules.bcfb_reducstart))
            if nkids0_17 > 1:  # >= 0 in original code -> error?
                vmax = self.rules.bcfb_amount * nkids0_17 - ncbs
                red = (self.rules.bcfb_reducrate_2dep
                       * (hinc - self.rules.bcfb_reducstart))
            amount = max(vmax - red, 0)
        self.bcfb_val = amount
        return amount

    def get_bcectb(self):
        self.bcectb_val, amount =  0, 0
        amount = 0.0
        nkids0_5 = self.hhold.nkids0_5
        if nkids0_5 > 0:
            hinc = (self.hhold.sp[self.who].inc_earn
                    - self.hhold.sp[self.who].con_rrsp)
            if self.hhold.couple:
                who2 = 1 -self.who
                bc_form2 = BC(self.hhold, who2, self.rules)
                hinc += (bc_form2.hhold.sp[who2].inc_earn
                         - bc_form2.hhold.sp[who2].con_rrsp)
            vmax = self.rules.bcectb_base*nkids0_5
            red = (max(hinc - self.rules.bcectb_redstart, 0)
                   * nkids0_5 * self.rules.bcectb_redrate)
            amount = max(vmax - red, 0)
        self.bcectb_val = amount
        return amount

class NL(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_nlcb()

    def get_nlcb(self):
        self.nlcb, nlcb, nlmbns = 0, 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                who2 = 1 - self.who
                pro_form2 = NL(self.hhold, who2, self.rules)
                hinc += (pro_form2.hhold.sp[who2].inc_earn 
                         - pro_form2.hhold.sp[who2].con_rrsp)
            if nkids0_17== 1:
                red = max(self.rules.nlcb_redrate_1dep * (hinc - self.rules.nlcb_redstart), 0)
                nlcb = max(self.rules.nlcb_base_1stch - red, 0)
            elif nkids0_17 == 2:
                red = max(self.rules.nlcb_redrate_2dep * (hinc - self.rules.nlcb_redstart), 0)
                nlcb = max(self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch - red, 0)
            elif nkids0_17 == 3:
                red = max(self.rules.nlcb_redrate_3dep * (hinc - self.rules.nlcb_redstart), 0)
                nlcb = max(self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch +
                           self.rules.nlcb_base_3rdch- red, 0)
            elif nkids0_17 >= 4:
                red_rate = self.rules.nlcb_redrate_4depplus * (nkids0_17-3)
                red = max( red_rate * (hinc - self.rules.nlcb_redstart), 0)
                nlcb = max(self.rules.nlcb_base_1stch + self.rules.nlcb_base_2ndch +
                           self.rules.nlcb_base_3rdch + self.rules.nlcb_base_4thch- red, 0)
            if (self.hhold.nkids0_1 > 0) and (hinc < self.rules.nlcb_stop):
                nlmbns = max(self.rules.nlmbns_amount * self.hhold.nkids0_1 
                             + self.rules.nlmbns_bonus, 0)
            nlcb += nlmbns
        self.nlcb = nlcb
        return nlcb

class PE(Province):
    pass

class NB(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_nbctb()

    def get_nbctb(self):
         self.nbctb_val, nbctb, nbss = 0, 0, 0
         nkids0_17 = self.hhold.nkids0_17
         nkids5_17 = self.hhold.nkids5_17
         if nkids0_17 > 0:
             hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
             if self.hhold.couple:
                 who2 = 1 - self.who
                 pro_form2 = NB(self.hhold, who2, self.rules)
                 hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
             vmax = self.rules.nbctb_amount * nkids0_17
             red = max(self.rules.nbwis_redrate * 
                       (hinc - self.rules.nbctb_redstart), 0)
             max_wis = max(self.rules.nbwis_rate * 
                           (min(hinc, self.rules.nbwis_stop) - self.rules.nbwis_phasein), 0)
             red_wis = max(self.rules.nbwis_redrate * 
                           (hinc - self.rules.nbwis_redstart), 0)
             nbctb = max(vmax - red, 0) + max_wis - red_wis
             if (nkids5_17 > 0) and (hinc <= self.rules.nbss_stop):
                 nbss = self.rules.nbss_amount * nkids5_17
                 nbctb += nbss
         self.nbctb_val=nbctb
         return nbctb

class NS(Province):
    def calc_rtcred(self):
        self.rtcred = self.get_nscb()
    def get_nscb(self):
        self.nscb_val, nscb, = 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                who2 = 1- self.who
                pro_form2 = NS(self.hhold, who2, self.rules)
                hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
            if nkids0_17 == 1:
                vmax = self.rules.nscb_base_1stch
                red = max(self.rules.nscb_redrate_1dep * 
                          (hinc - self.rules.nscb_redstart), 0)
                nscb = vmax - red
            elif nkids0_17 == 2:
                vmax = self.rules.nscb_base_1stch + self.rules.nscb_base_2ndch
                red = max(self.rules.nscb_redrate_2dep * 
                          (hinc - self.rules.nscb_redstart), 0)
                nscb = vmax - red
            elif nkids0_17 >= 3:
                vmax = (self.rules.nscb_base_1stch + self.rules.nscb_base_2ndch +
                        self.rules.nscb_base_3rdchplus * (nkids0_17-2))
                red_rate = self.rules.nscb_redrate_2dep + self.rules.nscb_redrate_3depplus * (nkids0_17-2)
                red = max(red_rate * (hinc - self.rules.nscb_redstart), 0)
                nscb = vmax - red
        self.nscb_val = nscb
        return nscb

class ON(Province):
    def calc_rtcred(self):
        self.rtcred = self.get_ocb()
    
    def get_ocb(self):
        self.ocb_val, amount, hinc = 0, 0, 0
        if self.hhold.nkids0_17 > 0:
           hinc = self.hhold.sp[self.who].inc_earn - self.hhold.sp[self.who].con_rrsp
           if self.hhold.couple:
               who2 = 1 - self.who
               pro_form2 = ON(self.hhold, who2, self.rules)
               hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
           max_amount = self.rules.ocb_max * self.hhold.nkids0_17
           reduc      = (hinc - self.rules.ocb_redstart) * self.rules.ocb_redrate
           amount = max(max_amount - reduc, 0)
        self.ocb_val = amount
        return amount

class MB(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_mancb()
    
    def get_mancb(self):
        self.mancb_val, mancb, hinc = 0, 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                who2 = 1 - self.who
                pro_form2 = MB(self.hhold, who2, self.rules)
                hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
            if nkids0_17 == 1:
                vmax = self.rules.mancb_base
                red  = max((hinc - self.rules.mancb_redstart) *
                           self.rules.mancb_redrate_1ch, 0)
            elif nkids0_17 == 2:
                vmax = self.rules.mancb_base*nkids0_17
                red  = max((hinc - self.rules.mancb_redstart) *
                           self.rules.mancb_redrate_2ch, 0)
            elif nkids0_17 > 2:
                vmax = self.rules.mancb_base*nkids0_17
                red  = max((hinc - self.rules.mancb_redstart) * 
                           self.rules.mancb_redrate_3chplus, 0)
            mancb = max(vmax-red, 0)
        self.mancb_val = mancb
        return mancb

class SK(Province):
    pass

class NT(Province):
    def calc_rtcred(self):
        self.rtcred = self.get_ntcb()

    def get_ntcb(self):
        self.ntcb_val, ntcb = 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            earn = self.hhold.sp[self.who].inc_earn + self.hhold.sp[self.who].selfemp_earn
            if self.hhold.couple:
                who2 =  1 - self.who
                pro_form2 = NT(self.hhold, who2, self.rules)
                hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
                earn += pro_form2.hhold.sp[who2].inc_earn + pro_form2.hhold.sp[who2].selfemp_earn
            if nkids0_17 == 1:
                vmax = (self.rules.ntcb_amount + self.rules.nttwb_base_1stch *
                        (min(self.rules.nttwb_min, earn) - self.rules.nttwb_start) / 
                        self.rules.nttwb_div)
                red = max(self.rules.nttwb_redrate_1ch * (hinc - self.rules.nttwb_redstart), 0)
                ntcb = max(vmax - red, 0)
            elif nkids0_17 > 1:
                vmax = (self.rules.ntcb_amount*nkids0_17 + self.rules.nttwb_base_2ndchplus *
                        (min(self.rules.nttwb_min, earn) - self.rules.nttwb_start) / 
                        self.rules.nttwb_div)
                red = max(self.rules.nttwb_redrate_2ch * (hinc - self.rules.nttwb_redstart), 0)
                ntcb = max(vmax - red, 0)
        self.ntcb_val=ntcb
        return ntcb

class YT(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_yucb()
    
    def get_yucb(self):
        self.yucb, yucb = 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn - self.hhold.sp[self.who].con_rrsp
            if self.hhold.couple:
                who2 = self.who - 1
                pro_form2 = YT(self.hhold, who2, self.rules)
                hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
            if nkids0_17 == 1:
                vmax = self.rules.yucb_amount
                red = max(self.rules.yucb_redrate_1ch *
                          (hinc - self.rules.yucb_redstart), 0)
            elif nkids0_17 > 1:
                vmax = self.rules.yucb_amount * nkids0_17
                red = max(self.rules.yucb_redrate_2ch *
                          (hinc - self.rules.yucb_redstart), 0)
        yucb = max(vmax - red, 0)
        self.yucb=yucb
        return yucb

class NU(Province):
    def calc_rtcred(self):
        self.rtcred = 0
        self.rtcred += self.get_nucb()
    def get_nucb(self):
        self.nucb_val, nucb = 0, 0
        nkids0_17 = self.hhold.nkids0_17
        if nkids0_17 > 0:
            hinc = self.hhold.sp[self.who].inc_earn- self.hhold.sp[self.who].con_rrsp
            earn = self.hhold.sp[self.who].inc_earn + self.hhold.sp[self.who].selfemp_earn
            if self.hhold.couple:
                who2 = 1 - self.who
                pro_form2 = NU(self.hhold, who2, self.rules)
                hinc += pro_form2.hhold.sp[who2].inc_earn - pro_form2.hhold.sp[who2].con_rrsp
                earn += pro_form2.hhold.sp[who2].inc_earn + pro_form2.hhold.sp[who2].selfemp_earn
            if nkids0_17 == 1:
                vmax = self.rules.nucb_amount
                wbon = (self.rules.nutwb_base_1stch * 
                        (min(self.rules.nutwb_min, earn) - self.rules.nutwb_start) / 
                        self.rules.nutwb_div)
                red = max(self.rules.nutwb_redrate_1ch*(hinc - self.rules.nutwb_redstart), 0)
            elif nkids0_17 > 1: # could just be else
                vmax = self.rules.nucb_amount * nkids0_17
                wbon = (self.rules.nutwb_base_2ndchplus*(min(self.rules.nutwb_min, earn)-
                                                    self.rules.nutwb_start)/self.rules.nutwb_div)
                red = max(self.rules.nutwb_redrate_2ch*(hinc - self.rules.nutwb_redstart), 0)
            nucb = max(vmax + wbon - red, 0)
        self.nucb_val = nucb
        return nucb   