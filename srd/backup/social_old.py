class oas:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.p = self.hhold.sp[self.who]
        self.elig = False
        self.oasinc = 0.0
        self.rules = rules
        return

    def oaselig(self):
        if self.p.age>=self.rules.ageoas:
            self.elig = True
        return

    def file(self):
        self.oasinc = 0.0
        self.oaselig()
        if (self.elig):
            full = self.rules.oas_full
            tmin = self.rules.oas_immig_mintime

            if(self.p.immig==False):
                self.oasinc = full
            else:
                immig_elig = self.p.t_immig- (self.p.age - self.rules.ageoas)
                if(immig_elig >= tmin):
                    self.oasinc = full * min(40, immig_elig)/40
                elif (immig_elig < tmin and self.p.t_immig >= tmin):
                    self.oasinc = full * tmin/40
                else:
                    self.oasinc = 0.0
        self.clawback()
        return

    def clawback(self):
        inc = self.p.inc_earn + self.p.inc_rpp + self.p.inc_cpp + self.p.inc_othtax + self.p.inc_rrsp
        claw = max(self.rules.oas_clawback_rate*(inc-self.rules.oas_clawback),0.0)
        if (claw > self.oasinc):
            self.oasinc = 0.0
        else :
            self.oasinc -= claw
        return

class gis:
    def __init__(self,hhold,who,rules):
        self.hhold = hhold
        self.who = who
        self.p  = self.hhold.sp[self.who]
        if self.hhold.couple:
            self.p2 = self.hhold.sp[1-self.who]
        self.elig = False
        self.gisinc = 0.0
        self.rules = rules
        return

    def giselig(self):
        if self.p.age >= self.rules.agegis:
            self.elig = True
        if self.hhold.couple:
            if (self.p.age >=self.rules.allow_age and self.p2.age >= self.rules.agegis):
                self.elig = True
        return

    def file(self):
        self.giselig()
        if (self.elig):
            if self.hhold.couple :
                self.gisinc = self.rules.gis_full_couple
            else :
                self.gisinc = self.rules.gis_full_single
            self.clawback()
            self.gisinc += self.get_bonus()
            self.allowsurv()
            #self.allowcouple()
        return

    def clawback(self):
        wexp = self.rules.gis_work_exemption
        if (hasattr('self.rules','gis_partial_exemption_low') &
            hasattr('self.rules','gis_partial_exemption_high')):
            wexps_low = self.rules.gis_partial_exemption_low
            wexps_high = self.rules.gis_partial_exemption_high
        else :
            wexps_low = 0
            wexps_high = 0
        wexps_len = wexps_high -  wexps_low 
        alag = self.rules.allow_age
        claw = 0.0
        comp = 0.0
        if self.hhold.couple:
            rate = self.rules.gis_reduct_rate_couple
            gisa =  self.rules.agegis
            tinc = 0.0
            for sp in self.hhold.sp:
                tinc += sp.inc_earn + sp.inc_rpp + sp.inc_cpp + sp.inc_othtax + sp.inc_rrsp
            winc = self.p.inc_earn + self.p2.inc_earn
            nwinc = tinc -winc
            wexps1 = min(max(self.p.inc_earn-wexps_low,0.0),wexps_len)*.5
            wexps2 = min(max(self.p2.inc_earn-wexps_low,0.0),wexps_len)*.5
            if(self.p.age >= gisa and self.p2.age >= gisa and self.p.inc_oas >0 and self.p2.inc_oas>0):
                comp =self.rules.complement_rate *(2 * self.rules.oas_full - self.p.inc_oas - self.p2.inc_oas)
                claw = rate*(nwinc +max(self.p.inc_earn-wexp-wexps1,0)+ max(self.p2.inc_earn - wexp-wexps2,0))
            elif (self.p.age >= gisa and self.p.inc_oas >0):
                self.gisinc = self.rules.gis_full_single
                rate = self.rules.gis_reduct_rate_single
                comp =self.rules.complement_rate *(self.rules.oas_full - self.p.inc_oas)
                claw = rate*(nwinc +max(self.p.inc_earn-wexp-wexps1,0)+max(self.p2.inc_earn - wexp-wexps2,0))
            elif (self.p2.age >= gisa and self.p2.inc_oas>0 and self.p.age < gisa and self.p.age >= alag):
                self.gisinc = self.allowcouple()
            else:
                self.gisinc = 0.0
        else:
            rate = self.rules.gis_reduct_rate_single
            comp =self.rules.complement_rate *(self.rules.oas_full - self.p.inc_oas)
            inc =  self.p.inc_rpp + self.p.inc_cpp + self.p.inc_othtax
            wexps1 = min(max(self.p.inc_earn-wexps_low,0.0),wexps_len)*.5
            claw = rate*(inc +max(self.p.inc_earn-wexp-wexps1,0))
        if (claw > self.gisinc + comp):
            self.gisinc = 0.0
        else:
            self.gisinc -= claw
        return

    def get_bonus(self):
        amount = 0.0
        if self.hhold.couple==False:
            amount += self.rules.gis_bonus_single
            rate = self.rules.gis_bonus_reduct_single
            inc = self.p.inc_rpp + self.p.inc_cpp + self.p.inc_othtax
            claw = rate*(inc +max(self.p.inc_earn-self.rules.gis_bonus_exemption_single,0))  
            amount -= claw
            if (amount <0.0):
                amount = 0.0
        if self.hhold.couple ==True:
            amount = self.rules.gis_bonus_couple
            rate = self.rules.gis_bonus_reduct_couple
            wexp = self.rules.gis_bonus_exemption_couple
            tinc = 0.0
            for sp in self.hhold.sp:
                tinc += sp.inc_earn + sp.inc_rpp + sp.inc_cpp + sp.inc_othtax + sp.inc_rrsp
            winc = self.p.inc_earn + self.p2.inc_earn
            nwinc = tinc -winc 
            claw = rate*(nwinc +max(self.p.inc_earn-wexp,0) +max(self.p2.inc_earn-wexp,0))
            amount -= claw
            if (amount <0.0):
                amount = 0.0
        return amount

    def allowsurv(self):
        agis = self.rules.agegis
        foas = self.rules.allowsurv_full_oas
        fgis = self.rules.allowsurv_full_gis
        redr = self.rules.allowsurv_reduct_rate
        wexp = self.rules.allowsurv_work_exemption
        boni = self.rules.allowsurv_bonus
        redb = self.rules.allowsurv_bonus_reduct
        bexp = self.rules.allowsurv_bonus_exemption
        rehi = self.rules.allowsurv_reduct_high_inc
        rthi = self.rules.allowsurv_rate_test_high_inc
        alag = self.rules.allow_age
        elig = False
        allowsurv = 0.0
        if(self.p.age >= alag and self.p.age < agis and self.p.ind_widow):
            elig = True
        factor = 0.0
        if elig:
            tinc = 0.0
            for sp in self.hhold.sp:
                tinc += sp.inc_earn + sp.inc_rpp + sp.inc_cpp + sp.inc_othtax + sp.inc_rrsp
            winc = self.p.inc_earn
            nwinc = tinc - winc
            if(self.p.t_immig < self.rules.oas_immig_mintime and self.p.immig == True):
                factor = self.p.t_immig/self.rules.oas_immig_mintime
            else:
                factor = 1.0
            if (tinc < (rthi * foas * factor)):
                gis_factor = max(0.0, fgis * factor)
                work_exemp = max(0.0, winc - wexp)
                oas_factor = max(0.0, foas * factor - redr * (nwinc + work_exemp))
                allowsurv = gis_factor + oas_factor
                bonus_factor = boni *factor
                bonus_exemp = redb * max(0.0, tinc - bexp)
                allowsurv += max(0.0, bonus_factor - bonus_exemp)
            else:
                gis_factor = max(0.0, fgis * factor)
                high_inc_factor = rehi * max(0.0, tinc - (rthi * factor * foas))
                allowsurv = max(0.0, gis_factor - high_inc_factor)
        self.gisinc += allowsurv

        return allowsurv

    def allowcouple(self):
        agis = self.rules.agegis
        alag = self.rules.allow_age
        foas = self.rules.allowcouple_full_oas
        fgis = self.rules.allowcouple_full_gis
        redr = self.rules.allowcouple_reduct_rate
        wexp = self.rules.allowcouple_work_exemption
        boni = self.rules.allowcouple_bonus
        redb = self.rules.allowcouple_bonus_reduct
        bexp = self.rules.allowcouple_bonus_exemption
        rehi = self.rules.allowcouple_reduct_high_inc
        rthi = self.rules.allowcouple_rate_test_high_inc
        surv_wexp = self.rules.allowsurv_work_exemption
        allowcouple = 0.0
        elig = True
        if self.hhold.couple:
            p2 = self.hhold.sp[int(self.who==0)]
            if(self.p.age>=agis and self.p.inc_oas >0):
                if(p2.age >= alag and p2.age < agis):
                    elig = True
        if elig:
            tinc = 0.0
            for sp in self.hhold.sp:
                tinc += sp.inc_earn + sp.inc_rpp + sp.inc_cpp + sp.inc_othtax + sp.inc_rrsp
            winc = self.p.inc_earn + p2.inc_earn
            nwinc = tinc -winc
            if(self.p.t_immig < self.rules.oas_immig_mintime and self.p.immig == True):
                factor = self.p.t_immig/self.rules.oas_immig_mintime
            else:
                factor = 1.0
            if(tinc < (rthi * factor * foas)):
                gis_factor = fgis * factor
                oas_factor = foas * factor
                pwexemp = max(0.0, self.p.inc_earn - surv_wexp)
                p2wexemp = max(0.0, p2.inc_earn - wexp)
                allowcouple = max(0.0, gis_factor +oas_factor - redr * (nwinc + pwexemp + p2wexemp))
                boni_factor = boni * factor
                boni_reduct = redb * max(0.0, tinc - bexp)
                allowcouple += max(0.0, boni_factor - boni_reduct)
            else:
                gis_factor = fgis * factor
                high_factor = rehi * max(0.0, tinc - (rthi * factor * foas))
                allowcouple = max(0.0, gis_factor - high_factor)
        return allowcouple

class postponed_oas:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.p = self.hhold.sp[self.who]
        self.rules = rules
        self.oassupp = 0.0

    def calc_port_oas(self):
        ageoas = self.rules.ageoas
        bonus = self.rules.postponeoas_bonus
        if self.p.age >= ageoas + self.p.nb_y_rep_oas:
            self.oassupp = (1 + bonus*self.p.nb_y_rep_oas)

    def file(self):
        self.calc_port_oas()
        return

class contrib:
    def __init__(self,hhold,who,rules,cqpprules,year):
        self.hhold = hhold
        self.who = who
        self.rules = rules
        self.cqpprules = cqpprules
        self.year = year
        self.p = self.hhold.sp[self.who]
        return

    def file(self):
        self.get_ei_contrib()
        self.get_rap_contrib()
        self.get_cqpp_contrib()

    def get_ei_contrib(self):
        #hard coding to fix
        if self.hhold.prov=='qc':
            rate= self.rules.ei_contr_rate
        else: rate = 0.0188
        cmax= self.rules.ei_contr_max
        earn= self.p.inc_earn
        if earn>0:
           elig=True
        else:
           elig=False

        self.ei_contr=0.0
        if elig:
           self.ei_contr = rate * min(earn, cmax)
        return


    def get_rap_contrib(self):
        rate= self.rules.rap_contr_rate
        cmax= self.rules.rap_contr_max
        earn= self.p.inc_earn
        if earn>0:
           elig=True
        else:
           elig=False
        self.rap_contr= 0.0
        if elig:
           self.rap_contr= rate * min(earn, cmax)
        return

    def get_cqpp_contrib(self):
        if self.p.cqppc:
            self.cpp_contr = self.p.cqppc
        elif(self.p.age>=70):
            self.cpp_contr = 0.0
        else:
            by= self.year - self.p.age
            acc = cpp.account(byear=by, rules=self.cqpprules)
            acc.MakeContrib(year=self.year,earn=self.p.inc_earn)
            hist = acc.history[self.p.age-18]
            self.cpp_contr = hist.contrib+hist.contrib_s1+hist.contrib_s2   
        return


class socass:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.rules = rules

    def file(self,fedforms,proforms):
        self.calc_shelter()
        self.calc_social_ass(fedforms,proforms)

    def calc_shelter(self):
        self.shelter = 0.0
        if (self.hhold.hh_size == 1):
            self.shelter = self.rules.socass_shelter_1ad0depch
        elif (self.hhold.hh_size == 2):
            self.shelter = self.rules.socass_shelter_1ad1depch
        elif (self.hhold.hh_size == 3):
            self.shelter = self.rules.socass_shelter_1ad2depch
        elif (self.hhold.hh_size == 4):
            self.shelter = self.rules.socass_shelter_1ad3depch
        elif (self.hhold.hh_size == 5):
            self.shelter = self.rules.socass_shelter_1ad4depch
        elif (self.hhold.hh_size == 6):
            self.shelter = self.rules.socass_shelter_1ad5depch
        elif (self.hhold.hh_size >= 6):
            self.shelter = self.rules.socass_shelter_1ad6depch
        return self.shelter
    def calc_social_ass(self, fed, pro):
        self.social_ass = 0.0
        self.assetlimit = 0.0
        tot_inc = 0.0
        amount = 0.0
        asset = 0.0
        ei_contr = 0.0
        cpp_contr = 0.0
        rap_contr = 0.0
        for i, s in enumerate(self.hhold.sp):
            self.hhold.sp[i].calc_totinc()
            tot_inc += self.hhold.sp[i].tinc
            asset += self.hhold.sp[i].asset
            ei_contr += self.hhold.sp[i].eic
            cpp_contr += self.hhold.sp[i].cqppc
            rap_contr += self.hhold.sp[i].rapc

        if self.hhold.prov == 'nl':
            self.assetlimit = 0.0
            if(self.hhold.hh_size == 1):
                self.assetlimit = self.rules.socass_assetlimit_single
            else:
                self.assetlimit = self.rules.socass_assetlimit_couple

            if(self.hhold.couple):
                if(self.hhold.nkids0_17 > 0):
                    amount = (self.rules.socass_base_2ad1depch
                              + self.rules.socass_shelter_1ad1depch)
                    amount += (self.rules.socass_add_supp
                               / self.rules.socass_reductionrate)
                    amount += self.rules.socass_exemption_couple
                    if (tot_inc < amount):
                        amount = (self.rules.socass_base_2ad1depch
                                  + self.rules.socass_shelter_1ad1depch)
                        amount += self.rules.socass_add_supp
                        red = max(0.0, tot_inc
                                  - self.rules.socass_exemption_couple)
                        amount -= self.rules.socass_reductionrate * red
                        self.social_ass = amount
                else:
                    amount = (self.rules.socass_base_couple
                              + self.rules.socass_shelter_1ad1depch)
                    amount += (self.rules.socass_add_supp
                               / self.rules.socass_reductionrate)
                    amount += self.rules.socass_exemption_couple
                    if (tot_inc < amount):
                        amount = (self.rules.socass_base_couple
                                  + self.rules.socass_shelter_1ad1depch)
                        amount += self.rules.socass_add_supp
                        red = max(0.0, tot_inc
                                  - self.rules.socass_exemption_couple)
                        amount -= self.rules.socass_reductionrate * red
                        self.social_ass = amount
            else:
                if(self.hhold.nkids0_17 > 0):
                    amount = (self.rules.socass_base_1ad1depch
                              + self.rules.socass_shelter_1ad1depch)
                    amount += (self.rules.socass_add_supp
                               / self.rules.socass_reductionrate)
                    amount += self.rules.socass_exemption_single
                    if (tot_inc < amount):
                        amount = (self.rules.socass_base_1ad1depch
                                  + self.rules.socass_shelter_1ad1depch)
                        amount += self.rules.socass_add_supp
                        red = max(0.0, tot_inc
                                  - self.rules.socass_exemption_single)
                        amount -= self.rules.socass_reductionrate * red
                        self.social_ass = amount
                else:
                    amount = (self.rules.socass_base_single
                              + self.rules.socass_shelter_1ad0depch)
                    amount += (self.rules.socass_add_supp
                               / self.rules.socass_reductionrate)
                    amount += self.rules.socass_exemption_single
                    if (tot_inc < amount):
                        amount = (self.rules.socass_base_single
                                  + self.rules.socass_shelter_1ad0depch)
                        amount += self.rules.socass_add_supp
                        red = max(0.0, tot_inc
                                  - self.rules.socass_exemption_single)
                        amount -= self.rules.socass_reductionrate * red
                        self.social_ass = amount
            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov == 'pe':
            if self.hhold.couple:
                self.assetlimit = max(2400.0,
                                      self.rules.socass_assetlimit_couple
                                      + self.hhold.nkids0_17
                                      * self.rules.socass_assetlimit_sup)
            else:
                if self.hhold.nkids > 0:
                    self.assetlimit = max(2400.0,
                                          3*self.rules.socass_assetlimit_sup
                                          + self.hhold.nkids0_17
                                          * self.rules.socass_assetlimit_sup)
                else:
                    self.assetlimit = self.rules.socass_assetlimit_single
            self.shelter = 0.0
            socass_base = 0.0
            if (self.hhold.hh_size == 1):
                self.shelter = self.rules.socass_shelter_1
            elif (self.hhold.hh_size == 2):
                self.shelter = self.rules.socass_shelter_2
            elif (self.hhold.hh_size == 3):
                self.shelter = self.rules.socass_shelter_3
            elif (self.hhold.hh_size == 4):
                self.shelter = self.rules.socass_shelter_4
            elif (self.hhold.hh_size == 5):
                self.shelter = self.rules.socass_shelter_5
            elif (self.hhold.hh_size >= 6):
                self.shelter = self.rules.socass_shelter_6
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 1:
                    socass_base = (self.rules.socass_base_2ad1depch
                                   + self.shelter + self.hhold.nkids12_17
                                   * self.rules.social_ch12_18if23
                                   + self.hhold.nkids0_11
                                   * self.rules.social_ch0_12if23)
                elif self.hhold.nkids0_17 > 1:
                    socass_base = (self.rules.socass_base_2ad2depch
                                   + self.shelter
                                   + self.hhold.nkids12_17
                                   * self.rules.social_ch12_18if4
                                   + self.hhold.nkids0_11
                                   * self.rules.social_ch0_12if4)
                else:
                    socass_base = self.rules.socass_base_couple + self.shelter
                amount = (socass_base / self.rules.socass_reductionrate
                          + self.rules.socass_exemption_couple)
                if(tot_inc < amount):
                    red = (self.rules.socass_reductionrate
                           * max(0.0, tot_inc
                                 - self.rules.socass_exemption_couple))
                    self.social_ass = socass_base - red
            else:
                if(self.hhold.nkids0_17 > 0 and self.hhold.nkids0_17 <= 2):
                    socass_base = (self.rules.socass_base_1ad1depch
                                   + self.shelter
                                   + self.hhold.nkids12_17
                                   * self.rules.social_ch12_18if23
                                   + self.hhold.nkids0_11
                                   * self.rules.social_ch0_12if23)
                elif self.hhold.nkids0_17 > 2:
                    socass_base = (self.rules.socass_base_1ad3depch
                                   + self.shelter
                                   + self.hhold.nkids12_17
                                   * self.rules.social_ch12_18if4
                                   + self.hhold.nkids0_11
                                   * self.rules.social_ch0_12if4)
                else:
                    socass_base = self.rules.socass_base_single + self.shelter
                amount = (socass_base / self.rules.socass_reductionrate
                          + self.rules.socass_exemption_single)
                if(tot_inc < amount):
                    red = (self.rules.socass_reductionrate
                           * max(0.0, tot_inc
                                 - self.rules.socass_exemption_single))
                    self.social_ass = socass_base - red
            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov == 'ns':
            if(self.hhold.hh_size == 1):
                self.assetlimit = self.rules.socass_assetlimit_single
            else:
                self.assetlimit = self.rules.socass_assetlimit_couple
            if (self.hhold.hh_size == 1):
                self.shelter = self.rules.socass_shelter_1
            elif (self.hhold.hh_size == 2):
                self.shelter = self.rules.socass_shelter_2
            else:
                self.shelter = self.rules.socass_shelter_3
            if self.hhold.couple:
                socass_base = ((self.rules.socass_base_couple + self.shelter
                                + self.hhold.nkids18_19
                                * self.rules.socass_base_single)
                               / self.rules.socass_reductionrate
                               + self.rules.socass_exemption_couple)
                if (tot_inc < socass_base):
                    self.social_ass = ((self.rules.socass_base_couple
                                        + self.shelter + self.hhold.nkids18_19
                                        * self.rules.socass_base_single)
                                       - self.rules.socass_reductionrate
                                       * max(0.0, tot_inc + ei_contr
                                        - self.rules.socass_exemption_couple))
            else:
                socass_base = (self.rules.socass_base_single + self.shelter
                               + self.hhold.nkids18_19
                               * self.rules.socass_base_single)
                red = (self.rules.socass_reductionrate
                       * max(0.0, tot_inc + ei_contr
                             - self.rules.socass_exemption_single))
                self.social_ass = max(0.0, socass_base - red)
            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov == 'nb':
            if self.hhold.couple:
                if self.hhold.nkids0_18 > 0:
                    socass_base = ((self.rules.socass_base_1ad2depch
                                    + (self.hhold.nkids0_18 - 1)
                                    * self.rules.socass_base_supch)
                                   / self.rules.socass_reductionrate
                                   + self.rules.socass_exemption_couple)
                    if tot_inc < socass_base:
                        vmax = (self.rules.socass_base_1ad2depch
                                + (self.hhold.nkids0_18 - 1)
                                * self.rules.socass_base_supch)
                        red = (self.rules.socass_reductionrate
                               * max(0.0, tot_inc
                                     - self.rules.socass_exemption_couple))
                        self.social_ass = max(0.0, vmax - red)
                else:
                    socass_base = (self.rules.socass_base_couple
                                   / self.rules.socass_reductionrate
                                   + self.rules.socass_exemption_couple)
                    if tot_inc < socass_base:
                        vmax = self.rules.socass_base_couple
                        red = (self.rules.socass_reductionrate
                               * max(0.0, tot_inc
                                     - self.rules.socass_exemption_couple))
                        self.social_ass = max(0.0, vmax - red)
            else:
                if self.hhold.nkids0_18 == 1:
                    socass_base = (self.rules.socass_base_1ad1depch
                                   / self.rules.socass_reductionrate
                                   + self.rules.socass_exemption_single)
                    if tot_inc < socass_base:
                        vmax = self.rules.socass_base_1ad1depch
                        red = (self.rules.socass_reductionrate
                               * max(0.0, tot_inc
                                     - self.rules.socass_exemption_single))
                        self.social_ass = max(0.0, vmax - red)
                elif self.hhold.nkids0_18 > 1:
                    socass_base = ((self.rules.socass_base_1ad2depch
                                    + (self.hhold.nkids0_18 - 1)
                                    * self.rules.socass_base_supch)
                                   / self.rules.socass_reductionrate
                                   + self.rules.socass_exemption_single)
                    if tot_inc < socass_base:
                        vmax = (self.rules.socass_base_1ad2depch
                                + (self.hhold.nkids0_18 - 1)
                                * self.rules.socass_base_supch)
                        red = (self.rules.socass_reductionrate
                               * max(0.0, tot_inc
                                     - self.rules.socass_exemption_single))
                        self.social_ass = max(0.0, vmax - red)
                else:
                    socass_base = (self.rules.socass_base_single
                                   / self.rules.socass_reductionrate
                                   + self.rules.socass_exemption_single)
                    if tot_inc < socass_base:
                        vmax = self.rules.socass_base_single
                        red = (self.rules.socass_reductionrate
                               * max(0.0, tot_inc
                                     - self.rules.socass_exemption_single))
                        self.social_ass = max(0.0, vmax - red)

        elif self.hhold.prov == 'qc':
            ncbs = 0.0
            qccap = 0.0
            chsupp = 0.0
            ncbs = (fed[self.who].ncbs_max
                    + (fed[self.who].ccb_val
                       - fed[self.who].cctb_max
                       - fed[self.who].uccb_val))
            qccap = pro[self.who].qccap_max
            if self.hhold.nkids0_17 == 1:
                if self.hhold.couple:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_couple
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))
                else:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_single
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))

            elif self.hhold.nkids0_17 ==2:
                if self.hhold.couple:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_couple
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp
                                  + self.rules.social_fed_2ndchsupp - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))
                else:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_single
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp
                                    + self.rules.social_fed_2ndchsupp - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))

            elif self.hhold.nkids0_17 >=3:
                if self.hhold.couple:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_couple
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp
                                  + self.rules.social_fed_2ndchsupp
                                  + (self.rules.social_fed_3rdchsupp
                                  * (self.hhold.nkids0_17-2)) - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))
                else:
                    chsupp = max(0.0, self.rules.social_qc_chsupp_single
                                 * self.hhold.nkids0_17 - qccap)
                    chsupp += max(0.0, self.rules.social_fed_1stchsupp
                                    + self.rules.social_fed_2ndchsupp
                                    + (self.rules.social_fed_3rdchsupp
                                    * (self.hhold.nkids0_17-2)) - ncbs)
                    chsupp += (self.rules.social_supp_12plus
                               * min(2, self.hhold.nkids12_17))

            sabc = self.rules.socass_base_couple
            sabs = self.rules.socass_base_single
            sarr = self.rules.socass_reductionrate
            saec = self.rules.socass_exemption_couple
            saes = self.rules.socass_exemption_single
            sass = self.rules.socass_single_supp
            sacs = self.rules.socass_constr_supp_single
            ind_kids = 0
            if self.hhold.nkids0_17 >=1:
                ind_kids =1
            if self.hhold.couple:
                if tot_inc < (sabc + chsupp) / sarr + saec:
                    self.social_ass = sabc + chsupp - (sarr * max(0.0, tot_inc -saec)
                                                       - cpp_contr - rap_contr - ei_contr)
            else:
                if tot_inc < (sabs + chsupp + (ind_kids * sass)) / sarr + saes:
                    if ind_kids:
                        self.social_ass = sabs + chsupp - (sarr * max(0.0, tot_inc -saes)
                                                           - cpp_contr - rap_contr - ei_contr)
                    else:
                        self.social_ass = sabs + sass - (sarr * max(0.0, tot_inc -saes)
                                                           - cpp_contr - rap_contr - ei_contr)
        elif self.hhold.prov == 'on':
            ncbs = fed[self.who].ncbs_val
            uccb = fed[self.who].inc_uccb
            if self.hhold.couple:
                assetlimit = (self.rules.socass_assetlimit_couple
                              + max(0.0, self.rules.socass_assetlimit_sup
                                    * self.hhold.nkids0_17))
            else:
                assetlimit = (self.rules.socass_assetlimit_single
                              + max(0.0, self.rules.socass_assetlimit_sup
                                    * self.hhold.nkids0_17))
            self.shelter = 0.0
            if (self.hhold.hh_size == 1):
                self.shelter = self.rules.socass_shelter_1
            elif (self.hhold.hh_size == 2):
                self.shelter = self.rules.socass_shelter_2
            elif (self.hhold.hh_size == 3):
                self.shelter = self.rules.socass_shelter_3
            elif (self.hhold.hh_size == 4):
                self.shelter = self.rules.socass_shelter_4
            elif (self.hhold.hh_size == 5):
                self.shelter = self.rules.socass_shelter_5
            elif (self.hhold.hh_size >= 6):
                self.shelter = self.rules.socass_shelter_6

            if self.hhold.couple:
                if self.hhold.nkids18_25 == 1:
                    sabo = self.rules.socass_base_2ad1depch + self.shelter
                elif self.hhold.nkids18_25 == 2:
                    sabo = self.rules.socass_base_2ad2depch + self.shelter
                elif self.hhold.nkids18_25 == 3:
                    sabo = self.rules.socass_base_2ad3depch + self.shelter
                elif self.hhold.nkids18_25 > 3:
                    sabo = (self.rules.socass_base_2ad3depch
                            + (self.hhold.nkids18_25 - 3) * self.rules.socass_base_supch)
                else:
                    sabo = self.rules.socass_base_couple + self.shelter
            else:
                if self.hhold.nkids18_25 == 1:
                    sabo = self.rules.socass_base_1ad1depch + self.shelter
                elif self.hhold.nkids18_25 == 2:
                    sabo = self.rules.socass_base_1ad2depch + self.shelter
                elif self.hhold.nkids18_25 == 3:
                    sabo = self.rules.socass_base_1ad3depch + self.shelter
                elif self.hhold.nkids18_25 > 3:
                    sabo = (self.rules.socass_base_1ad3depch
                            + (self.hhold.nkids18_25 - 3) * self.rules.socass_base_supch)
                else:
                    if self.hhold.nkids0_17 > 0:
                        sabo = self.rules.socass_base_1adch + self.shelter
                    else:
                        sabo = self.rules.socass_base_single + self.shelter

            saec = self.rules.socass_exemption_couple
            saes = self.rules.socass_exemption_single
            onfr = self.rules.ont_flat_rate
            dc_exp0_7 = 0.0
            #To fit with the Fortran version, should be revised
            if self.hhold.couple:
                netinc = (tot_inc - cpp_contr - ei_contr + ncbs)
            else:
                netinc = (tot_inc - cpp_contr - ei_contr + ncbs -uccb)
            for i, j in enumerate(self.hhold.sp):
                dc_exp0_7 += self.hhold.sp[i].dc_exp0_7
            if self.hhold.couple:
                amount = (max(0.0, netinc
                          - ((netinc - saec) * onfr
                          + saec + dc_exp0_7)))
                self.social_ass = max(0.0, sabo - amount)
            else:
                amount = (max(0.0, netinc
                          - ((netinc - saes) * onfr
                          + saes + dc_exp0_7)))
                self.social_ass = max(0.0, sabo - amount)


            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov == 'mb':
            if self.hhold.nkids0_18 == 0:
                if self.hhold.couple:
                    self.shelter = self.rules.socass_shelter_2ad0depch
                else:
                    self.shelter = self.rules.socass_shelter_1
            else:
                if self.hhold.hh_size == 2:
                    self.shelter = self.rules.socass_shelter_2ad0depch
                elif self.hhold.hh_size == 3:
                    self.shelter = self.rules.socass_shelter_3
                elif self.hhold.hh_size == 4:
                    self.shelter = self.rules.socass_shelter_4
                elif self.hhold.hh_size == 5:
                    self.shelter = self.rules.socass_shelter_5
                elif self.hhold.hh_size == 6:
                    self.shelter = self.rules.socass_shelter_6
                else:
                    self.shelter = (self.rules.socass_shelter_6
                                    + (self.rules.socass_shelter_sup
                                       * (self.hhold.hh_size - 6)))
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 1:
                    soass_base_mb = (self.rules.socass_base_2ad1depch
                                     + self.rules.socass_ch12_17_fam * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_fam * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_fam * self.hhold.nkids0_6
                                     + self.rules.socass_add_supp)
                elif self.hhold.nkids0_17 == 2:
                    soass_base_mb = (self.rules.socass_base_2ad2depch
                                     + self.rules.socass_ch12_17_fam * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_fam * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_fam * self.hhold.nkids0_6)
                elif self.hhold.nkids0_17 >= 3:
                    soass_base_mb = (self.rules.socass_base_2ad3depch
                                     + self.rules.socass_ch12_17_fam * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_fam * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_fam * self.hhold.nkids0_6)
                else:
                    soass_base_mb = (self.rules.socass_base_couple
                                     + self.rules.socass_add_supp
                                     + 2 * self.rules.socass_single_supp)
            else:
                if self.hhold.nkids0_17 == 1:
                    soass_base_mb = (self.rules.socass_base_1ad1depch
                                     + self.rules.socass_ch12_17_mono * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_mono * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_mono * self.hhold.nkids0_6
                                     + self.rules.socass_add_supp)
                elif self.hhold.nkids0_17 == 2:
                    soass_base_mb = (self.rules.socass_base_1ad2depch
                                     + self.rules.socass_ch12_17_mono * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_mono * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_mono * self.hhold.nkids0_6
                                     + self.rules.socass_add_supp)
                elif self.hhold.nkids0_17 >= 3:
                    soass_base_mb = (self.rules.socass_base_1ad3depch
                                     + self.rules.socass_ch12_17_mono * self.hhold.nkids12_17
                                     + self.rules.socass_ch7_11_mono * self.hhold.nkids7_11
                                     + self.rules.socass_ch0_6_mono * self.hhold.nkids0_6
                                     + self.rules.socass_add_supp)
                elif self.hhold.nkids18_25 >0:
                    soass_base_mb = self.rules.socass_base_1adch
                else:
                    soass_base_mb = (self.rules.socass_base_single
                                     + self.rules.socass_single_supp)
            sarr = self.rules.socass_reductionrate
            saec = self.rules.socass_exemption_couple
            saes = self.rules.socass_exemption_single
            if self.hhold.couple:
                if (tot_inc < (soass_base_mb + self.shelter) / sarr + saec):
                    self.social_ass = (soass_base_mb + self.shelter
                                       - sarr * max(0.0, tot_inc - saec))
            else:
                if (tot_inc < (soass_base_mb + self.shelter) / sarr + saes):
                    self.social_ass = (soass_base_mb + self.shelter
                                       - sarr * max(0.0, tot_inc - saes))

        elif self.hhold.prov == 'sk':
            assetlimit = 0.0
            socass_base = 0.0
            socass_inc = 0.0
            uccb = fed[self.who].inc_uccb
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 0:
                    assetlimit = self.rules.socass_assetlimit_couple
                else:
                    assetlimit = (self.rules.socass_assetlimit_couple
                                  + self.hhold.nkids0_17 * self.rules.socass_assetlimit_sup)
            else:
                if self.hhold.nkids0_17 == 0:
                    assetlimit = self.rules.socass_assetlimit_single
                else:
                    assetlimit = (self.rules.socass_assetlimit_couple
                                  + (self.hhold.nkids0_17 - 1)
                                  * self.rules.socass_assetlimit_sup)
            if self.hhold.couple:
                socass_base = self.rules.socass_base_couple
                if self.hhold.nkids0_17 == 0:
                    self.shelter = self.rules.socass_shelter_2ad0depch
                elif self.hhold.nkids0_17 == 1 or self.hhold.nkids0_17 == 2:
                    self.shelter = self.rules.socass_shelter_2ad1depch
                elif self.hhold.nkids0_17 == 3 or self.hhold.nkids0_17 == 4:
                    self.shelter = self.rules.socass_shelter_2ad3depch
                elif self.hhold.nkids0_17 > 4:
                    self.shelter = self.rules.socass_shelter_2ad5depch
            else:
                socass_base = self.rules.socass_base_single
                if self.hhold.nkids0_17 == 0:
                     self.shelter = self.rules.socass_shelter_1ad0depch
                elif self.hhold.nkids0_17 == 1 or self.hhold.nkids0_17 == 2:
                     self.shelter = self.rules.socass_shelter_1ad1depch
                elif self.hhold.nkids0_17 == 3 or self.hhold.nkids0_17 == 4:
                     self.shelter = self.rules.socass_shelter_1ad3depch
                elif self.hhold.nkids0_17 > 4:
                     self.shelter = self.rules.socass_shelter_1ad5depch

            saec = self.rules.socass_exemption_couple
            saes = self.rules.socass_exemption_single
            sarr = self.rules.socass_reductionrate
            salc = self.rules.socass_limit_exemption_couple
            sals = self.rules.socass_limit_exemption_single
            saef = self.rules.socass_exemption_family
            if self.hhold.couple:
                if self.hhold.nkids0_17 ==0:
                    socass_inc = (max(0.0,tot_inc
                                     - (saec + sarr * max(salc,tot_inc))))
                else:
                    socass_inc = (max(0.0,tot_inc - saef * 2) - uccb)
            else:
                if self.hhold.nkids0_17 ==0:
                    socass_inc = (max(0.0,tot_inc
                                     - (saes + sarr * max(sals,tot_inc))))
                else:
                    socass_inc = (max(0.0,tot_inc - saef))
            self.social_ass = (max(0.0,socass_base + self.shelter -socass_inc))
            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov=='ab':
            socass_base = 0.0
            ncbs = fed[self.who].ncbs_val
            uccb = fed[self.who].inc_uccb
            ccb  = fed[self.who].ccb_val
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 1:
                    self.shelter = self.rules.socass_shelter_2ad1depch
                    socass_base  = self.rules.socass_base_2ad1depch
                elif self.hhold.nkids0_17 == 2:
                    self.shelter = self.rules.socass_shelter_2ad2depch
                    socass_base  = self.rules.socass_base_2ad2depch
                elif self.hhold.nkids0_17 == 3:
                    self.shelter = self.rules.socass_shelter_2ad3depch
                    socass_base  = self.rules.socass_base_2ad3depch
                elif self.hhold.nkids0_17 == 4:
                    self.shelter = self.rules.socass_shelter_2ad4depch
                    socass_base  = self.rules.socass_base_2ad4depch
                elif self.hhold.nkids0_17 == 5:
                    self.shelter = self.rules.socass_shelter_2ad5depch
                    socass_base  = self.rules.socass_base_2ad5depch
                elif self.hhold.nkids0_17 >= 6:
                    self.shelter = (self.rules.socass_shelter_2ad6depch
                                    + ((self.hhold.nkids0_17 - 6)
                                       * self.rules.socass_shelter_supch))
                    socass_base  = (self.rules.socass_base_2ad6depch
                                    + ((self.hhold.nkids0_17 - 6)
                                       * self.socass_base_supch))
            else:
                if self.hhold.nkids0_17 == 1:
                    self.shelter = self.rules.socass_shelter_1ad1depch
                    socass_base  = self.rules.socass_base_1ad1depch
                elif self.hhold.nkids0_17 == 2:
                    self.shelter = self.rules.socass_shelter_1ad2depch
                    socass_base  = self.rules.socass_base_1ad2depch
                elif self.hhold.nkids0_17 == 3:
                    self.shelter = self.rules.socass_shelter_1ad3depch
                    socass_base  = self.rules.socass_base_1ad3depch
                elif self.hhold.nkids0_17 == 4:
                    self.shelter = self.rules.socass_shelter_1ad4depch
                    socass_base  = self.rules.socass_base_1ad4depch
                elif self.hhold.nkids0_17 == 5:
                    self.shelter = self.rules.socass_shelter_1ad5depch
                    socass_base  = self.rules.socass_base_1ad5depch
                elif self.hhold.nkids0_17 >= 6:
                    self.shelter = (self.rules.socass_shelter_1ad6depch
                                    + ((self.hhold.nkids0_17 - 6)
                                       * self.rules.socass_shelter_supch))
                    socass_base  = (self.rules.socass_base_1ad6depch
                                    + ((self.hhold.nkids0_17 - 6)
                                       * self.socass_base_supch))
            socass_inc = 0.0
            saec = self.rules.socass_exemption_couple
            saes = self.rules.socass_exemption_single
            sabc = self.rules.socass_base_couple
            sabs = self.rules.socass_base_single
            sabcc = self.rules.socass_base_2ad1depch
            sabsc = self.rules.socass_base_1ad1depch
            sarr = self.rules.socass_reductionrate
            if self.hhold.couple:
                socass_inc = (max(0.0,tot_inc - saec - cpp_contr - ei_contr
                                  - uccb + ncbs))
                if self.hhold.nkids0_17 == 0:
                    self.social_ass = (max(0.0,sabc - sarr * socass_inc))
                else:
                    self.social_ass = (max(0.0,sabcc + self.shelter
                                           - sarr * socass_inc))
            else:
                socass_inc = (max(0.0,tot_inc - saes - cpp_contr - ei_contr
                                  - uccb + ncbs))
                if self.hhold.nkids0_17 == 0:
                    self.social_ass = (max(0.0,sabs - sarr * socass_inc))
                else:
                    self.social_ass = (max(0.0,sabsc + self.shelter
                                           - sarr * socass_inc))
            assetlimit = (self.social_ass / 12 + max(0.0,ncbs / 12)
                          + max(0.0,ccb / 12))
            if asset > self.assetlimit:
                self.social_ass = 0.0

        elif self.hhold.prov=='bc':
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 0:
                    self.assetlimit = self.rules.socass_assetlimit_single
                else:
                    self.assetlimit = self.rules.socass_assetlimit_family
            else:
                if self.hhold.nkids == 0:
                    self.assetlimit = self.rules.socass_assetlimit_single
                else:
                    self.assetlimit = self.rules.socass_assetlimit_family
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 0:
                    self.shelter = self.rules.socass_shelter_2
                elif self.hhold.nkids0_17 == 1:
                    self.shelter = self.rules.socass_shelter_3
                elif self.hhold.nkids0_17 == 2:
                    self.shelter = self.rules.socass_shelter_4
                elif self.hhold.nkids0_17 == 3:
                    self.shelter = self.rules.socass_shelter_5
                elif self.hhold.nkids0_17 == 4:
                    self.shelter = self.rules.socass_shelter_6
                elif self.hhold.nkids0_17 == 5:
                    self.shelter = self.rules.socass_shelter_7
                elif self.hhold.nkids0_17 == 6:
                    self.shelter = self.rules.socass_shelter_8
                elif self.hhold.nkids0_17 == 7:
                    self.shelter = self.rules.socass_shelter_9
                elif self.hhold.nkids0_17 == 8:
                    self.shelter = self.rules.socass_shelter_10
                else:
                    self.shelter = (self.rules.socass_shelter_10
                                    + (self.hhold.nkids0_17 - 8)
                                    * self.rules.socass_shelter_sup)
            else:
                if self.hhold.nkids0_17 == 0:
                    self.shelter = self.rules.socass_shelter_1
                elif self.hhold.nkids0_17 == 1:
                    self.shelter = self.rules.socass_shelter_2
                elif self.hhold.nkids0_17 == 2:
                    self.shelter = self.rules.socass_shelter_3
                elif self.hhold.nkids0_17 == 3:
                    self.shelter = self.rules.socass_shelter_4
                elif self.hhold.nkids0_17 == 4:
                    self.shelter = self.rules.socass_shelter_5
                elif self.hhold.nkids0_17 == 5:
                    self.shelter = self.rules.socass_shelter_6
                elif self.hhold.nkids0_17 == 6:
                    self.shelter = self.rules.socass_shelter_7
                elif self.hhold.nkids0_17 == 7:
                    self.shelter = self.rules.socass_shelter_8
                elif self.hhold.nkids0_17 == 8:
                    self.shelter = self.rules.socass_shelter_9
                elif self.hhold.nkids0_17 == 9:
                    self.shelter = self.rules.socass_sherter_10
                else:
                    self.shelter = (self.rules.socass_shelter_10
                                    + (self.hhold.nkids0_17 - 9)
                                    * self.rules.socass_shelter_sup)
            uccb = 0.0
            ncbs = 0.0
            uccb = fed[self.who].inc_uccb
            ncbs = fed[self.who].ncbs_val
            socass_base = 0.0
            socass_ex = 0.0
            socass_inc = 0.0
            oas_gis = 0.0
            nb_65plus = 0
            sabc = self.rules.socass_base_couple
            sabs = self.rules.socass_base_single
            sabcc = self.rules.socass_base_couple_ch
            sabsc = self.rules.socass_base_single_ch
            sabc165 = self.rules.socass_base_couple_65plus_one
            sabc165c = self.rules.socass_base_couple_65plus_one_ch
            sabc265 = self.rules.socass_base_couple_65plus_both
            sabc265c = self.rules.socass_base_coupl_65plus_both_ch
            sabs65 = self.rules.socass_base_single_65plus
            sabs65c = self.rules.socass_base_single_65plus_ch
            saes = self.rules.socass_exemption_single
            saef = self.rules.socass_exemption_family
            for i,s in enumerate(self.hhold.sp):
                oas_gis += self.hhold.sp[i].inc_oas + self.hhold.sp[i].inc_gis
                if self.hhold.sp[i].age >=65:
                    nb_65plus += 1
            tot_inc += ncbs + oas_gis - uccb
            if self.hhold.couple:
                if nb_65plus == 0:
                    if self.hhold.nkids0_17 == 0:
                        socass_base = sabc
                        socass_ex = min(saes, tot_inc - oas_gis)
                    else:
                        socass_base = sabcc
                        socass_ex = min(saef, tot_inc - oas_gis)
                elif nb_65plus == 1:
                    if self.hhold.nkids0_17 == 0:
                        socass_base = sabc165
                        socass_ex = min(saes, tot_inc - oas_gis)
                    else:
                        socass_base = sabc165c
                        socass_ex = min(saef, tot_inc - oas_gis)
                elif nb_65plus == 2:
                    if self.hhold.nkids0_17 == 0:
                        socass_base = sabc265
                        socass_ex = min(saes, tot_inc - oas_gis)
                    else:
                        socass_base = sabc265c
                        socass_ex = min(saef, tot_inc - oas_gis)
            else:
                if nb_65plus == 0:
                    if self.hhold.nkids0_17 == 0:
                        socass_base = sabs
                        socass_ex = min(saes, tot_inc - oas_gis)
                    else:
                        socass_base = sabsc
                        socass_ex = min(saef, tot_inc - oas_gis)
                else:
                    if self.hhold.nkids0_17 == 0:
                        socass_base = sabs65
                        socass_ex = min(saes, tot_inc - oas_gis)
                    else:
                        socass_base = sabs65c
                        socass_ex = min(saef, tot_inc - oas_gis)
            if self.hhold.couple:
                if self.hhold.nkids0_17 == 0:
                    socass_inc = oas_gis + max(0.0, tot_inc - oas_gis
                                               - cpp_contr - ei_contr
                                               - socass_ex)
                else:
                    socass_inc = oas_gis + max(0.0, tot_inc - oas_gis
                                               - cpp_contr - ei_contr
                                               - socass_ex)
            else:
                if self.hhold.nkids0_17 == 0:
                    socass_inc = oas_gis + max(0.0, tot_inc - oas_gis
                                               - cpp_contr - ei_contr
                                               - socass_ex)
                else:
                    socass_inc = oas_gis + max(0.0, tot_inc - oas_gis
                                               - cpp_contr - ei_contr
                                               - socass_ex)
            self.social_ass = max(0.0, self.shelter + socass_base - socass_inc)
            if asset > self.assetlimit:
                self.social_ass = 0.0
        return

class socsol:
    def __init__(self, hhold, who, rules):
        self.hhold = hhold
        self.who = who
        self.rules = rules
        self.tot_inc = 0.0
        for i, s in enumerate(self.hhold.sp):
            self.tot_inc += self.hhold.sp[i].tinc
        return

    def file(self):
        self.calc_social_sol()
        return

    def calc_social_sol(self):
        self.socsol = 0.0
        nb_disa = 0
        for i, j in enumerate(self.hhold.sp):
            if self.hhold.sp[i].disabled == True:
                nb_disa +=1
        if self.hhold.prov == 'pe':
            if nb_disa ==2:
                self.socsol = (self.hhold.sp[self.who].social_ass
                               + 2 * self.rules.socsol_add_supp)
            elif nb_disa == 1:
                self.socsol = (self.hhold.sp[self.who].social_ass
                               + self.rules.socsol_add_supp)
        if self.hhold.prov == 'nb':
            if self.hhold.couple:
                pass
        if self.hhold.prov == 'qc':
            if self.hhold.couple:
                ssbc = self.rules.socsol_base_couple
                ssrr = self.rules.socsol_redrate
                ssec = self.rules.socsol_exemption_couple1
                if(self.tot_inc < ssbc / ssrr + ssec):
                    self.socsol = ssbc - ssrr * max(0.0,self.tot_inc - ssec)
            else:
                ssbs = self.rules.socsol_base_single
                ssrr = self.rules.socsol_redrate
                sses = self.rules.socsol_exemption_single
                if(self.tot_inc < ssbs / ssrr + sses):
                    self.socsol = ssbs - ssrr * max(0.0,self.tot_inc - sses)
        if self.hhold.prov == 'on':
            shelter = 0.0
            socsol_base = 0.0
            if self.hhold.hh_size<7:
                name = 'socsol_shelter_'+str(self.hhold.hh_size)
                shelter = getattr(self.rules,name)
            else:
                shelter = self.rules.socsol_shelter_6
            ssbc22 = self.rules.socsol_base_2ad2depch
            ssbc23 = self.rules.socsol_base_2ad3depch
            ss1317 = self.rules.socsol_ch13_17_fam
            ssbsch = self.rules.socsol_base_supch
            ssbc   = self.rules.socsol_base_couple
            ssbc21 = self.rules.socsol_base_2ad1depch
            ssbc11 = self.rules.socsol_base_1ad1depch
            ssbc12 = self.rules.socsol_base_1ad2depch
            ssbc13 = self.rules.socsol_base_1ad3depch
            ssbs   = self.rules.socsol_base_single
            ssrr   = self.rules.socsol_redrate
            ssec   = self.rules.socsol_exemption_couple1
            sses   = self.rules.socsol_exemption_single
            if(self.hhold.couple):
                if(nb_disa==2):
                    if self.hhold.nkids18_25==0:
                        socsol_base = (ssbc22 + shelter + self.hhold.nkids13_17 * ss1317)
                    else:
                        socsol_base = (ssbc23 + shelter + self.hhold.nkids18_25 * ssbsch
                                       + self.hhold.nkids13_17 * ss1317 )
                elif(nb_disa==1):
                    if self.hhold.nkids18_25==0:
                        socsol_base = (ssbc + shelter + self.hhold.nkids13_17 * ss1317)
                    else:
                        socsol_base = (ssbc21 + shelter + self.hhold.nkids18_25 * ssbsch
                                       + self.hhold.nkids13_17 * ss1317)
                else:
                    if (self.hhold.nkids0_17>0 and self.hhold.nkids18_25==0):
                        socsol_base = ssbc11 + shelter + self.hhold.nkids13_17 * ss1317
                    elif self.hhold.nkids18_25==1:
                        socsol_base = ssbc12 + shelter + self.hhold.nkids13_17 * ss1317
                    elif self.hhold.nkids18_25==2:
                        socsol_base = ssbc13 + shelter + self.hhold.nkids13_17 * ss1317
                    elif self.hhold.nkids18_25>2:
                        socsol_base = (ssbc13 + shelter + self.hhold.nkids13_17 * ss1317
                                        + self.hhold.nkids18_25 * ssbsch)
                    else:
                        socsol_base = ssbs + shelter
            if(self.hhold.couple):
                if(self.tot_inc < socsol_base / ssrr + ssec / 2):
                    self.socsol = max(0.0,socsol_base - ssrr * max(0.0,self.tot_inc - ssec))
            else:
                if(self.tot_inc < socsol_base / ssrr + sses):
                    self.socsol = max(0.0,socsol_base - ssrr * max(0.0,self.tot_inc - sses))
        if(self.hhold.prov=='mb'):
            pass
            #To be revised
            #shelter = 0.0
            #socsol_base = 0.0
            #if self.hhold.hh_size<7:
                #name = 'socsol_shelter_'+str(self.hhold.hh_size)
                #shelter = getattr(self.rules,name)
            #else:
                #shelter = self.rules.socsol_shelter_6
        if(self.hhold.prov=='sk'):
            shelter = 0.0
            ssbc = self.rules.socsol_base_couple
            ssbs = self.rules.socsol_base_single
            ssrr = self.rules.socsol_redrate
            ssef = self.rules.socsol_exemption_family
            sses = self.rules.socsol_exemption_single
            ssec = self.rules.socsol_exemption_couple1
            ssls = self.rules.socsol_limit_exemption_single
            sslc = self.rules.socsol_limit_exemption_couple
            if(self.hhold.nkids0_17==1 or self.hhold.nkids0_17==2):
                shelter=self.rules.socsol_shelter_2
            elif(self.hhold.nkids0_17==3 or self.hhold.nkids0_17==4):
                shelter=self.rules.socsol_shelter_4
            elif(self.hhold.nkids0_17>4):
                shelter=self.rules.socsol_shelter_5
            if(self.hhold.couple):
                if(self.hhold.nkids0_17>0):
                    if(self.tot_inc <(ssbc + shelter) / ssrr + ssef):
                        self.socsol = max(0.0, ssbc + shelter - max(0.0, self.tot_inc - ssef))
                else:
                    shelter = self.rules.socsol_shelter_2
                    if(self.tot_inc <(ssbc + shelter) / ssrr + ssec):
                        limit = min(sslc,self.tot_inc)
                        exp   = max(0.0,limit-ssec)
                        self.socsol = max(0.0, ssbc + shelter -ssrr * exp - max(0.0, self.tot_inc - sslc))
            else:
                if(self.hhold.nkids0_17>0):
                    if(self.tot_inc <(ssbs + shelter) / ssrr + ssef):
                        self.socsol = max(0.0, ssbs + shelter - max(0.0, self.tot_inc - ssef))
                else:
                    shelter = self.rules.socsol_shelter_1
                    if(self.tot_inc <(ssbs + shelter) / ssrr + sses):
                        limit = min(ssls,self.tot_inc)
                        exp   = max(0.0,limit-sses)
                        self.socsol = max(0.0, ssbs + shelter -ssrr * exp - max(0.0, self.tot_inc - ssls))
        if(self.hhold.prov=='ab'):
            shelter = 0.0
