class tax:
    def __init__(self,year=2016, prov='qc'):
        self.year = year
        self.prov = prov
        self.loadoas()
        self.loadgis()
        self.loadcqpp()
        pros = []
        provs = ['qc','ab','bc','mb','nb','nl','ns','nt','nu','on','pe','sk','yt']
        pros = [qcpars(year)]
        pros.append(abpars(year))
        pros.append(bcpars(year))
        pros.append(mbpars(year))
        pros.append(nbpars(year))
        pros.append(nlpars(year))
        pros.append(nspars(year))
        pros.append(ntpars(year))
        pros.append(nupars(year))
        pros.append(onpars(year))
        pros.append(pepars(year))
        pros.append(skpars(year))
        pros.append(ytpars(year))
        for p in pros:
            p.loadpars()
        self.pros = dict(zip(provs,pros))
        sass = []
        fed = []
        ssol = []
        for p in provs:
            sass.append(socasspars(self.year, prov=p))
            ssol.append(socsolpars(self.year, prov=p))
            fed.append(fedpars(self.year,prov=p))
        for s in sass:
            s.loadpars()
        for s in ssol:
            s.loadpars()
        for f in fed:
            f.loadpars()
        self.socassps = dict(zip(provs,sass))
        self.socsolps = dict(zip(provs,ssol))
        self.fedps = dict(zip(provs,fed))
        self.loadcontrib()
        return
    def loadcontrib(self):
        self.contribp = contribpars(self.year)
        self.contribp.loadpars()
    def loadfederal(self):
        self.fed = fedpars(self.year, prov=self.prov)
        self.fed.loadpars()
        return
    def loadoas(self):
        self.oasp = oaspars(self.year)
        self.oasp.loadpars()
        return
    def loadgis(self):
        self.gisp = gispars(self.year)
        self.gisp.loadpars()
        return
    def loadcqpp(self):
        self.qpp_rules = cpp.rules(qpp=True)
        self.cpp_rules = cpp.rules(qpp=False)
        return
    def file(self,hhold):
        self.prov = hhold.prov
        # load provincial tax params
        self.pro = self.pros[self.prov]
        # load social assistance and solidarity parameters
        self.socassp = self.socassps[self.prov]
        self.socsolp = self.socsolps[self.prov]
        self.fed = self.fedps[self.prov]
        # get oas
        self.fileoas(hhold)
        # get postponed OAS
        self.filepostponed(hhold)
        # get gis
        self.filegis(hhold)
        # contributions
        self.filecontrib(hhold)
        # federal taxes (to compute some credits that go into social assistance)
        self.filefed(hhold)
        # provincial taxes
        self.filepro(hhold)
        # social assistance
        self.filesocass(hhold)
        self.filesocsol(hhold)
        # federal taxes
        self.filefed(hhold)
        # provincial taxes
        self.filepro(hhold)
        # child transfers
        #self.filechild(hhold)
        return

    def fileoas(self,hhold):
        for i,s in enumerate(hhold.sp):
            form = oas(hhold,i,self.oasp)
            form.file()
            hhold.sp[i].inc_oas = form.oasinc
        return
    def filepostponed(self,hhold):
        for i,s in enumerate(hhold.sp):
            if hhold.sp[i].nb_y_rep_oas !=0:
                form = postponed_oas(hhold,i,self.oasp)
                form.file()
                hhold.sp[i].inc_oas *= form.oassupp
        return
    def filecontrib(self, hhold):
        cqpprules = None
        if hhold.prov=='qc':
            cqpprules = self.qpp_rules
        else:
            cqpprules = self.cpp_rules
        for i,s in enumerate(hhold.sp):
            form = contrib(hhold,i,rules=self.contribp,cqpprules=cqpprules,year=self.year)
            form.file()
            hhold.sp[i].eic  = form.ei_contr
            hhold.sp[i].rapc = form.rap_contr
            hhold.sp[i].cqppc = form.cpp_contr
        return
    def filegis(self,hhold):
        for i,s in enumerate(hhold.sp):
            form = gis(hhold,i,self.gisp)
            form.file()
            hhold.sp[i].inc_gis = form.gisinc
        return
    def filefed(self,hhold):
        self.fedforms = []
        for i,sp in enumerate(hhold.sp):
            self.fedforms.append(federal(hhold,i,self.fed))
            self.fedforms[i].file()
        return
    def filepro(self,hhold):
        if (self.prov=='qc'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(quebec(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='ab'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(alberta(hhold,i,self.pro,self.fedforms))
                self.proforms[i].file()
        if (self.prov=='bc'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(british_columbia(hhold,i,self.pro,self.fedforms))
                self.proforms[i].file()
        if (self.prov=='nl'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(newfoundland(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='pe'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(pei(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='nb'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(new_brunswick(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='ns'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(nova_scotia(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='on'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(ontario(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='mb'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(manitoba(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='sk'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(saskatchewan(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='nt'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(nw_territories(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='yt'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(yukon(hhold,i,self.pro))
                self.proforms[i].file()
        if (self.prov=='nu'):
            self.proforms = []
            for i,sp in enumerate(hhold.sp):
                self.proforms.append(nuvavut(hhold,i,self.pro))
                self.proforms[i].file()
        return
    def filesocass(self, hhold):
        who=0
        if hhold.couple:
            if hhold.sp[0].tinc>=hhold.sp[1].tinc:
                who=0
            else:
                who=1
        form = socass(hhold,who,self.socassp)
        form.file(self.fedforms,self.proforms)
        hhold.sp[who].shelter = form.shelter
        hhold.sp[who].social_ass  = form.social_ass
        return

    def filesocsol(self, hhold):
        who=0
        if hhold.couple:
            if hhold.sp[0].tinc>=hhold.sp[1].tinc:
                who=0
            else:
                who=1
        form = socsol(hhold,who,self.socsolp)
        form.file()
        hhold.sp[who].social_sol  = form.socsol
        return

    def paftertax(self,hhold,who):
        inc_disp = 0.0
        inc_disp += self.fedforms[who].totinc
        inc_disp -= self.fedforms[who].liab
        inc_disp -= self.proforms[who].liab
        inc_disp += self.fedforms[who].rtcred
        inc_disp += self.proforms[who].rtcred
        inc_disp += hhold.sp[who].social_ass
        inc_disp -= hhold.sp[who].cqppc
        inc_disp -= hhold.sp[who].eic
        inc_disp -= hhold.sp[who].rapc
        return inc_disp
    def haftertax(self,hhold):
        hh = 0.0
        for i,p in enumerate(hhold.sp):
            hh += self.paftertax(hhold,i)
        return hh

    def pinc(self,hhold,who):
        return self.fedforms[who].totinc

    def hinc(self,hhold):
        hh = 0.0
        for i,p in enumerate(hhold.sp):
            hh += self.pinc(hhold,i)
        return hh

    def patr(self,hhold,who):
        bf = self.pinc(hhold,who)
        if bf>0.0:
            rate = 1.0-self.paftertax(hhold,who)/bf
        else :
            rate = 0.0
        return rate

    def pmtr(self,hhold,who,incre):
        self.file(hhold)
        inc   = self.paftertax(hhold,who)
        hholdp = hhold
        hholdp.sp[who].inc_earn += incre
        self.file(hholdp)
        incp    = self.paftertax(hhold,who)
        rate = 1.0 - (incp - inc)/incre
        return rate

    def hatr(self,hhold):
        bf = self.hinc(hhold)
        if bf>0.0:
            rate = 1.0-self.haftertax(hhold)/bf
        else :
            rate = 0.0
        return rate

    def hmtr(self,hhold,who,incre):
        self.file(hhold)
        inc   = self.haftertax(hhold)
        hholdp = hhold
        hholdp.sp[who].inc_earn += incre
        self.file(hholdp)
        incp    = self.haftertax(hhold)
        rate = 1.0 - (incp - inc)/incre
        return rate
