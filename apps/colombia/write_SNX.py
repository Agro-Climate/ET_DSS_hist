import numpy as np
import pandas as pd
from os import path # path
import os
import subprocess  #to run executable
from datetime import date
import datetime    #to convert date to doy or vice versa
import calendar


def writeSNX_clim(DSSAT_PATH,station,planting_date,crop,cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                       planting_density,scenario,fert_app, df_fert,
                       irrig_app, irrig_method, df_irrig, ir_depth,ir_threshold, ir_eff):   
    WSTA = station
    # ============
    # find the first year in *.WTD & compute how many years are available
    # => then determine IDATE, PDATE and NYERS
    WTD_fname = path.join(DSSAT_PATH, WSTA + ".WTD")
    # 1) read observed weather *.WTD (skip 1st row - heading)
    data1 = np.loadtxt(WTD_fname, skiprows=1)
    # convert numpy array to dataframe
    WTD_df = pd.DataFrame({'YEAR': data1[:, 0].astype(int) // 1000,  # python 3.6: / --> //
                            'DOY': data1[:, 0].astype(int) % 1000,
                            'SRAD': data1[:, 1],
                            'TMAX': data1[:, 2],
                            'TMIN': data1[:, 3],
                            'RAIN': data1[:, 4]})
    # convert year-month-date to DOY
    plt_year = planting_date[:4] #self._Setting.DSSATSetup1.plt_year.getvalue()
    if planting_date is not None:
        date_object = datetime.datetime.strptime(planting_date, '%Y-%m-%d').date()
        plt_doy = date_object.timetuple().tm_yday

    if plt_doy == 1:
        if calendar.isleap(WTD_df.YEAR.values[0]):
            IC_date = WTD_df.YEAR.values[0] * 1000 + 366  # YYYYDOY integer
        else:
            IC_date = WTD_df.YEAR.values[0] * 1000 + 365  # YYYYDOY integer
        first_year = WTD_df.YEAR.values[0]
        PDATE = repr(first_year + 1)[2:] + repr(plt_doy).zfill(3)
    else:
        first_year = WTD_df.YEAR[WTD_df["DOY"] == (plt_doy - 1)].values[0]
        IC_date = first_year * 1000 + (plt_doy - 1)
        PDATE = repr(first_year)[2:] + repr(plt_doy).zfill(3)
    ICDAT = repr(IC_date)[2:]
    hv_doy = plt_doy + 210  # tentative harvest date => long enough considering delayed growth
    # adjust hv_date if harvest moves to a next year
    if hv_doy > 365:
        hv_doy = hv_doy - 365
    last_year = WTD_df.YEAR[WTD_df["DOY"] == (hv_doy)].values[-1]
    NYERS = repr(last_year - first_year + 1)
    # ============
    # NYERS = repr(int(end_year) - int(start_year) + 1)
    # plt_year = start_year
    # if planting_date is not None:
    #     date_object = datetime.datetime.strptime(planting_date, '%Y-%m-%d').date()
    #     plt_doy = date_object.timetuple().tm_yday
    # PDATE = plt_year[2:] + repr(plt_doy).zfill(3)
    #     #   IC_date = first_year * 1000 + (plt_doy - 1)
    #     #   PDATE = repr(first_year)[2:] + repr(plt_doy).zfill(3)
    #     # ICDAT = repr(IC_date)[2:]
    # ICDAT = plt_year[2:] + repr(plt_doy-1).zfill(3)  #Initial condition => 1 day before planting
    SDATE = ICDAT
    INGENO = cultivar[0:6]  
    CNAME = cultivar[7:]  
    ID_SOIL = soil_type[0:10]  
    PPOP = planting_density  #planting density
    i_NO3 = initial_soil_no3_content  # self.label_04.cget("text")[0:1]  #self.NO3_soil.getvalue()[0][0:1] #"H" #or "L"
    IC_w_ratio = float(initial_soil_moisture)
    if irrig_app == "repr_irrig":  #on reported dates
        IRRIG = 'D' # days after planting     'R'
        # IMETH = irrig_method
    elif irrig_app == 'auto_irrig':  # automatic when required
        IRRIG = 'A'  # automatic, or 'N' (no irrigation)
        # IMDEP = ir_depth
        # ITHRL = ir_threshold
        # IREFF = ir_eff
    else:
        IRRIG = 'N'  # automatic, or 'N' (no irrigation)
    if fert_app == "Fert":  # fertilizer applied
        FERTI = 'D'  # 'D'= Days after planting, 'R'=on report date, or 'N' (no fertilizer)
    else:
        FERTI = 'N'

    #1) make SNX
    # temp_snx = path.join(DSSAT_PATH, f"TEMP_ET{crop}.SNX")
    temp_snx = path.join(DSSAT_PATH, f"CO{crop}TEMP.SNX")
    snx_name = f"CL{crop}"+scenario[:4]+".SNX"  #EJ(7/27/2021) climatology run in comparison with forecast run

    SNX_fname = path.join(DSSAT_PATH, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    if irrig_app == "repr_irrig": #on reported dates
        MI = "1"
    else:   #no irrigation or automatic irrigation
        MI = "0"
    if fert_app == "Fert":
        MF = "1"
    else:
        MF = "0"
    # MF = "1"
    SA = "0"
    IC = "1"
    MP = "1"
    MR = "0"
    MC = "0"
    MT = "0"
    ME = "0"
    MH = "0"
    SM = "1"
    temp_str = fr.readline()
    FL = "1"
    fw.write("{0:3s}{1:31s}{2:3s}{3:3s}{4:3s}{5:3s}{6:3s}{7:3s}{8:3s}{9:3s}{10:3s}{11:3s}{12:3s}{13:3s}".format(
        FL.rjust(3), "1 0 0 CC-SIMAGRI                 1",
        FL.rjust(3), SA.rjust(3), IC.rjust(3), MP.rjust(3), MI.rjust(3), MF.rjust(3), MR.rjust(3), MC.rjust(3),
        MT.rjust(3), ME.rjust(3), MH.rjust(3), SM.rjust(3)))
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *CULTIVARS
    temp_str = fr.readline()
    new_str = temp_str[0:3] + crop + temp_str[5:6] + INGENO + temp_str[12:13] + CNAME
    fw.write(new_str)
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)
    # ================write *FIELDS
    # Get soil info from *.SOL
    SOL_file = path.join(DSSAT_PATH, "CC.SOL")
    # soil_depth, wp, fc, nlayer = get_soil_IC(SOL_file, ID_SOIL)
    soil_depth, wp, fc, nlayer, SLTX = get_soil_IC(SOL_file, ID_SOIL)
    SLDP = repr(soil_depth[-1])
    ID_FIELD = WSTA + "0001"
    WSTA_ID =  WSTA
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write(
        "{0:2s} {1:8s}{2:5s}{3:3s}{4:6s}{5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID.rjust(5),
                                                                        "       -99   -99   -99   -99   -99   -99 ",
                                                                        SLTX.ljust(6), SLDP.rjust(4), ID_SOIL,
                                                                        " -99"))
    fw.write(" \n")
    temp_str = fr.readline()  # 1 -99      CCER       -99   -99 DR000   -99   -99
    temp_str = fr.readline()  # @L ...........XCRD ...........YCRD .....ELEV
    fw.write(temp_str)
    temp_str = fr.readline()  # 1             -99             -99       -99   ==> skip
    # ================write *FIELDS - second section
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write("{0:2s} {1:89s}".format(FL.rjust(2),
                                    "            -99             -99       -99               -99   -99   -99   -99   -99   -99"))
    fw.write(" \n")
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *INITIAL CONDITIONS
    temp_str = fr.readline()
    new_str = temp_str[0:9] + ICDAT + temp_str[14:]
    fw.write(new_str)
    temp_str = fr.readline()  # @C  ICBL  SH2O  SNH4  SNO3
    fw.write(temp_str)
    temp_str = fr.readline()
    for nline in range(0, nlayer):
        if nline == 0:  # first layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "15"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # i_NO3 == "L":
                SNO3 = "5"  # **EJ(5/27/2015)
        elif nline == 1:  # second layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "2"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # elif i_NO3 == "L":
                SNO3 = ".5"  # **EJ(4/29/2020) used one constant number regardless of soil types
        else:
            temp_SH2O = fc[nline]  # float
            SNO3 = "0"  # **EJ(5/27/2015)
        SH2O = repr(temp_SH2O)[0:5]  # convert float to string
        new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + " " + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
        fw.write(new_str)
    fw.write("  \n")
    for nline in range(0, 10):
        temp_str = fr.readline()
        if temp_str[0:9] == "*PLANTING":
            break

    fw.write(temp_str)  # *PLANTING DETAILS
    temp_str = fr.readline()  # @P PDATE EDATE
    fw.write(temp_str)
    # write *PLANTING DETAILS
    temp_str = fr.readline()
    PPOE = PPOP #planting density 
    new_str = temp_str[0:3] + PDATE + "   -99" + PPOP.rjust(6) + PPOE.rjust(6) + temp_str[26:]
    fw.write(new_str)
    fw.write("  \n")
    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    if irrig_app == 'repr_irrig':
        fw.write('*IRRIGATION AND WATER MANAGEMENT'+ "\n")
        fw.write('@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME'+ "\n")
        fw.write(' 1     1    30    50   100 GS000 IR001    10 -99'+ "\n")
        fw.write('@I IDATE  IROP IRVAL'+ "\n")
        IROP = irrig_method  #irrigation method
        df_irrig = df_irrig.astype(float)
        df_filtered = df_irrig[(df_irrig["DAP"] >= 0) & (df_irrig["WAmount"] >= 0)]
        irrig_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        IDATE = df_filtered.DAP.values
        IRVAL = df_filtered.WAmount.values
        if irrig_count > 0:   # irrigation applied
            for i in range(irrig_count):
                # new_str = ' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + IRVAL.rjust(5)
                fw.write(' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + repr(IRVAL[i]).rjust(5)+ "\n")
            # fw.write(" \n")

            # df_irrig, ir_depth,ir_threshold, ir_eff
        #end of writing irrigation application

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:12] == "*FERTILIZERS":
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD 
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == "Fert":
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0) & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = "AP001"  #Broadcast, not incorporated    
        FDEP = "5"   #5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = "-99"
        FAMK = "-99"

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + FAMP.rjust(5) + " " + FAMK.rjust(5) + temp_str[44:]
                fw.write(new_str)
            fw.write(" \n")
#-------------------------------------------
    # else: #if no fertilzier applied
    #     temp_str = fr.readline()  #  1     0 FE005 AP002 
    #     fw.write(temp_str)
    #     temp_str = fr.readline()  #  1    45 FE005 AP002
    #     fw.write(temp_str)

    fw.write("  \n")
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:11] == "*SIMULATION":
            break
    fw.write(temp_str)  # *SIMULATION CONTROLS
    temp_str = fr.readline()
    fw.write(temp_str)  # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME
    # write *SIMULATION CONTROLS
    temp_str = fr.readline()
    new_str = temp_str[0:18] + NYERS.rjust(2) + temp_str[20:33] + SDATE + temp_str[38:]
    fw.write(new_str)
    temp_str = fr.readline()  # @N OPTIONS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OP
    fw.write(" 1 OP              Y     Y     Y     N     N     N     N     N     D"+ "\n")
    temp_str = fr.readline()  # @N METHODS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 ME
    fw.write(temp_str)
    temp_str = fr.readline()  # @N MANAGEMENT
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 MA
    new_str = temp_str[0:25] + IRRIG + temp_str[26:31] + FERTI + temp_str[32:]
    fw.write(new_str)
    # fw.write(temp_str)
    temp_str = fr.readline()  # @N OUTPUTS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OU
    fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 5):
        temp_str = fr.readline()
        fw.write(temp_str)
    # irrigation method
    temp_str = fr.readline()  # 1 IR
    if irrig_app == 'auto_irrig':  # automatic when required
        IMDEP = ir_depth
        ITHRL = ir_threshold
        IREFF = ir_eff
        fw.write(' 1 IR          ' + repr(IMDEP).rjust(5) + repr(ITHRL).rjust(6) + '   100 GS000 IR001    10'+ repr(IREFF).rjust(6)+ "\n")
    else:
        # new_str = temp_str[0:39] + IMETH + temp_str[44:]
        fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 7):
        temp_str = fr.readline()
        fw.write(temp_str)

    fr.close()
    fw.close()
    return
# ======================================================================================
# ======================================================================================
# ======================================================================================
def writeSNX_frst(DSSAT_PATH,station,planting_date,crop,cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                       planting_density,scenario,fert_app, df_fert,
                       irrig_app, irrig_method, df_irrig, ir_depth,ir_threshold, ir_eff):    

    plt_year = planting_date[:4] #self._Setting.DSSATSetup1.plt_year.getvalue()
    if planting_date is not None:
        date_object = datetime.datetime.strptime(planting_date, '%Y-%m-%d').date()
        plt_doy = date_object.timetuple().tm_yday

    if plt_doy == 1:
        PDATE = plt_year + repr(plt_doy).zfill(3)
        PDATE = PDATE[2:]
        ICDAT = PDATE  #EJ(7/27/2021)temporary!!
    else:
        PDATE = plt_year + repr(plt_doy).zfill(3)
        PDATE = PDATE[2:]
        ICDAT = plt_year + repr(plt_doy-1).zfill(3)  #IC date is one day before planting
        ICDAT = ICDAT[2:]

    NYERS = 100  #EJ(7/27/2021) temporary => hard-coded by fixing 100 simulations 
    SDATE = ICDAT
    INGENO = cultivar[0:6]  
    CNAME = cultivar[7:]  
    ID_SOIL = soil_type[0:10]  
    PPOP = planting_density  #planting density
    i_NO3 = initial_soil_no3_content  # self.label_04.cget("text")[0:1]  #self.NO3_soil.getvalue()[0][0:1] #"H" #or "L"
    IC_w_ratio = float(initial_soil_moisture)
    if irrig_app == "repr_irrig":  #on reported dates
        IRRIG = 'D' # days after planting     'R'
        # IMETH = irrig_method
    elif irrig_app == 'auto_irrig':  # automatic when required
        IRRIG = 'A'  # automatic, or 'N' (no irrigation)
        # IMDEP = ir_depth
        # ITHRL = ir_threshold
        # IREFF = ir_eff
    else:
        IRRIG = 'N'  # automatic, or 'N' (no irrigation)
    if fert_app == "Fert":  # fertilizer applied
        FERTI = 'D'  # 'D'= Days after planting, 'R'=on report date, or 'N' (no fertilizer)
    else:
        FERTI = 'N'

    #1) make SNX
    # temp_snx = path.join(DSSAT_PATH, f"TEMP_ET{crop}.SNX")
    temp_snx = path.join(DSSAT_PATH, f"CO{crop}TEMP.SNX")
    snx_name = f"FC{crop}"+scenario[:4]+".SNX"  #EJ(7/27/2021) Forecast mode

    SNX_fname = path.join(DSSAT_PATH, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    if irrig_app == "repr_irrig": #on reported dates
        MI = "1"
    else:   #no irrigation or automatic irrigation
        MI = "0"
    if fert_app == "Fert":
        MF = "1"
    else: 
        MF = "0"
    # MF = "1"
    SA = "0"
    IC = "1"
    MP = "1"
    MR = "0"
    MC = "0"
    MT = "0"
    ME = "0"
    MH = "0"
    SM = "1"
    temp_str = fr.readline()
    FL = "1"
    fw.write("{0:3s}{1:31s}{2:3s}{3:3s}{4:3s}{5:3s}{6:3s}{7:3s}{8:3s}{9:3s}{10:3s}{11:3s}{12:3s}{13:3s}".format(
        FL.rjust(3), "1 0 0 CO-SIMAGRI                 1",
        FL.rjust(3), SA.rjust(3), IC.rjust(3), MP.rjust(3), MI.rjust(3), MF.rjust(3), MR.rjust(3), MC.rjust(3),
        MT.rjust(3), ME.rjust(3), MH.rjust(3), SM.rjust(3)))
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *CULTIVARS
    temp_str = fr.readline()
    new_str = temp_str[0:3] + crop + temp_str[5:6] + INGENO + temp_str[12:13] + CNAME
    fw.write(new_str)
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)
    # ================write *FIELDS
    # Get soil info from *.SOL
    SOL_file = path.join(DSSAT_PATH, "CC.SOL")
    # soil_depth, wp, fc, nlayer = get_soil_IC(SOL_file, ID_SOIL)
    soil_depth, wp, fc, nlayer, SLTX = get_soil_IC(SOL_file, ID_SOIL)
    SLDP = repr(soil_depth[-1])
    ID_FIELD = scenario[:4] + "0001"
    # WSTA_ID =  scenario[:4]+ plt_year[2:] +"99"  #EJ(7/27/2021) generated weather are stored in ONE long WTH file for the next 100 yr simulations
    # # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    # fw.write(
    #     "{0:2s} {1:8s} {2:8s}{3:36s} {4:4s}  {5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID,
    #                                                                     "   -99   -99   -99   -99   -99   -99",
    #                                                                     SLTX.rjust(4), SLDP.rjust(4), ID_SOIL,
    #                                                                     " -99"))
    WSTA_ID = scenario[:4].upper()
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write(
        "{0:2s} {1:8s}{2:5s}{3:3s}{4:6s}{5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID.rjust(5),
                                                                        "       -99   -99   -99   -99   -99   -99 ",
                                                                        SLTX.ljust(6), SLDP.rjust(4), ID_SOIL,
                                                                        " -99"))
    fw.write(" \n")
    temp_str = fr.readline()  # 1 -99      CCER       -99   -99 DR000   -99   -99
    temp_str = fr.readline()  # @L ...........XCRD ...........YCRD .....ELEV
    fw.write(temp_str)
    temp_str = fr.readline()  # 1             -99             -99       -99   ==> skip
    # ================write *FIELDS - second section
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write("{0:2s} {1:89s}".format(FL.rjust(2),
                                    "            -99             -99       -99               -99   -99   -99   -99   -99   -99"))
    fw.write(" \n")
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *INITIAL CONDITIONS
    temp_str = fr.readline()
    new_str = temp_str[0:9] + ICDAT + temp_str[14:]
    fw.write(new_str)
    temp_str = fr.readline()  # @C  ICBL  SH2O  SNH4  SNO3
    fw.write(temp_str)
    temp_str = fr.readline()
    for nline in range(0, nlayer):
        if nline == 0:  # first layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "15"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # i_NO3 == "L":
                SNO3 = "5"  # **EJ(5/27/2015)
        elif nline == 1:  # second layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "2"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # elif i_NO3 == "L":
                SNO3 = ".5"  # **EJ(4/29/2020) used one constant number regardless of soil types
        else:
            temp_SH2O = fc[nline]  # float
            SNO3 = "0"  # **EJ(5/27/2015)
        SH2O = repr(temp_SH2O)[0:5]  # convert float to string
        new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + " " + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
        fw.write(new_str)
    fw.write("  \n")
    for nline in range(0, 10):
        temp_str = fr.readline()
        if temp_str[0:9] == "*PLANTING":
            break

    fw.write(temp_str)  # *PLANTING DETAILS
    temp_str = fr.readline()  # @P PDATE EDATE
    fw.write(temp_str)
    # write *PLANTING DETAILS
    temp_str = fr.readline()
    PPOE = PPOP #planting density 
    new_str = temp_str[0:3] + PDATE + "   -99" + PPOP.rjust(6) + PPOE.rjust(6) + temp_str[26:]
    fw.write(new_str)
    fw.write("  \n")
    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    if irrig_app == 'repr_irrig':
        fw.write('*IRRIGATION AND WATER MANAGEMENT'+ "\n")
        fw.write('@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME'+ "\n")
        fw.write(' 1     1    30    50   100 GS000 IR001    10 -99'+ "\n")
        fw.write('@I IDATE  IROP IRVAL'+ "\n")
        IROP = irrig_method  #irrigation method
        df_irrig = df_irrig.astype(float)
        df_filtered = df_irrig[(df_irrig["DAP"] >= 0) & (df_irrig["WAmount"] >= 0)]
        irrig_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        IDATE = df_filtered.DAP.values
        IRVAL = df_filtered.WAmount.values
        if irrig_count > 0:   # irrigation applied
            for i in range(irrig_count):
                # new_str = ' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + IRVAL.rjust(5)
                fw.write(' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + repr(IRVAL[i]).rjust(5)+ "\n")
            # fw.write(" \n")

            # df_irrig, ir_depth,ir_threshold, ir_eff
        #end of writing irrigation application

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:12] == "*FERTILIZERS":
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD 
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == "Fert":
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0) & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = "AP001"  #Broadcast, not incorporated    
        FDEP = "5"   #5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = "-99"
        FAMK = "-99"

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + FAMP.rjust(5) + " " + FAMK.rjust(5) + temp_str[44:]
                fw.write(new_str)
            fw.write(" \n")
#-------------------------------------------
    # else: #if no fertilzier applied
    #     temp_str = fr.readline()  #  1     0 FE005 AP002 
    #     fw.write(temp_str)
    #     temp_str = fr.readline()  #  1    45 FE005 AP002
    #     fw.write(temp_str)

    fw.write("  \n")
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:11] == "*SIMULATION":
            break
    fw.write(temp_str)  # *SIMULATION CONTROLS
    temp_str = fr.readline()
    fw.write(temp_str)  # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME
    # write *SIMULATION CONTROLS
    temp_str = fr.readline()
    new_str = temp_str[0:17] + repr(NYERS).rjust(3) + temp_str[20:33] + SDATE + temp_str[38:]  #EJ(7/27/2021) generated weather are stored in ONE long WTH file for the next 100 yr simulations
    fw.write(new_str)
    temp_str = fr.readline()  # @N OPTIONS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OP
    fw.write(" 1 OP              Y     Y     Y     N     N     N     N     N     D"+ "\n")
    temp_str = fr.readline()  # @N METHODS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 ME
    fw.write(temp_str)
    temp_str = fr.readline()  # @N MANAGEMENT
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 MA
    new_str = temp_str[0:25] + IRRIG + temp_str[26:31] + FERTI + temp_str[32:]
    fw.write(new_str)
    # fw.write(temp_str)
    temp_str = fr.readline()  # @N OUTPUTS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OU
    fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 5):
        temp_str = fr.readline()
        fw.write(temp_str)
    # irrigation method
    temp_str = fr.readline()  # 1 IR
    if irrig_app == 'auto_irrig':  # automatic when required
        IMDEP = ir_depth
        ITHRL = ir_threshold
        IREFF = ir_eff
        fw.write(' 1 IR          ' + repr(IMDEP).rjust(5) + repr(ITHRL).rjust(6) + '   100 GS000 IR001    10'+ repr(IREFF).rjust(6)+ "\n")
    else:
        # new_str = temp_str[0:39] + IMETH + temp_str[44:]
        fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 7):
        temp_str = fr.readline()
        fw.write(temp_str)

    fr.close()
    fw.close()
    return

# ====End of WRITE *.SNX
# ======================================================================================
# ======================================================================================
# ======================================================================================
def writeSNX_frst_FR(DSSAT_PATH,station,planting_date,crop,cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                       planting_density,scenario,fert_app, df_fert,
                       irrig_app, irrig_method, df_irrig, ir_depth,ir_threshold, ir_eff):    

    plt_year = planting_date[:4] #self._Setting.DSSATSetup1.plt_year.getvalue()
    if planting_date is not None:
        date_object = datetime.datetime.strptime(planting_date, '%Y-%m-%d').date()
        plt_doy = date_object.timetuple().tm_yday

    if plt_doy == 1:
        PDATE = plt_year + repr(plt_doy).zfill(3)
        PDATE = PDATE[2:]
        ICDAT = PDATE  #EJ(7/27/2021)temporary!!
    else:
        PDATE = plt_year + repr(plt_doy).zfill(3)
        PDATE = PDATE[2:]
        ICDAT = plt_year + repr(plt_doy-1).zfill(3)  #IC date is one day before planting
        ICDAT = ICDAT[2:]

    NYERS = 200  #EJ(8/2/2021) temporary => hard-coded by fixing 300 simulation for FResampler
    SDATE = ICDAT
    INGENO = cultivar[0:6]  
    CNAME = cultivar[7:]  
    ID_SOIL = soil_type[0:10]  
    PPOP = planting_density  #planting density
    i_NO3 = initial_soil_no3_content  # self.label_04.cget("text")[0:1]  #self.NO3_soil.getvalue()[0][0:1] #"H" #or "L"
    IC_w_ratio = float(initial_soil_moisture)
    if irrig_app == "repr_irrig":  #on reported dates
        IRRIG = 'D' # days after planting     'R'
        # IMETH = irrig_method
    elif irrig_app == 'auto_irrig':  # automatic when required
        IRRIG = 'A'  # automatic, or 'N' (no irrigation)
        # IMDEP = ir_depth
        # ITHRL = ir_threshold
        # IREFF = ir_eff
    else:
        IRRIG = 'N'  # automatic, or 'N' (no irrigation)
    if fert_app == "Fert":  # fertilizer applied
        FERTI = 'D'  # 'D'= Days after planting, 'R'=on report date, or 'N' (no fertilizer)
    else:
        FERTI = 'N'

    #1) make SNX
    # temp_snx = path.join(DSSAT_PATH, f"TEMP_ET{crop}.SNX")
    temp_snx = path.join(DSSAT_PATH, f"CO{crop}TEMP.SNX")
    snx_name = f"FC{crop}"+scenario[:4]+".SNX"  #EJ(7/27/2021) Forecast mode

    SNX_fname = path.join(DSSAT_PATH, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    if irrig_app == "repr_irrig": #on reported dates
        MI = "1"
    else:   #no irrigation or automatic irrigation
        MI = "0"
    if fert_app == "Fert":
        MF = "1"
    else: 
        MF = "0"
    # MF = "1"
    SA = "0"
    IC = "1"
    MP = "1"
    MR = "0"
    MC = "0"
    MT = "0"
    ME = "0"
    MH = "0"
    SM = "1"
    temp_str = fr.readline()
    FL = "1"
    fw.write("{0:3s}{1:31s}{2:3s}{3:3s}{4:3s}{5:3s}{6:3s}{7:3s}{8:3s}{9:3s}{10:3s}{11:3s}{12:3s}{13:3s}".format(
        FL.rjust(3), "1 0 0 CO-SIMAGRI                 1",
        FL.rjust(3), SA.rjust(3), IC.rjust(3), MP.rjust(3), MI.rjust(3), MF.rjust(3), MR.rjust(3), MC.rjust(3),
        MT.rjust(3), ME.rjust(3), MH.rjust(3), SM.rjust(3)))
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *CULTIVARS
    temp_str = fr.readline()
    new_str = temp_str[0:3] + crop + temp_str[5:6] + INGENO + temp_str[12:13] + CNAME
    fw.write(new_str)
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)
    # ================write *FIELDS
    # Get soil info from *.SOL
    SOL_file = path.join(DSSAT_PATH, "CC.SOL")
    # soil_depth, wp, fc, nlayer = get_soil_IC(SOL_file, ID_SOIL)
    soil_depth, wp, fc, nlayer, SLTX = get_soil_IC(SOL_file, ID_SOIL)
    SLDP = repr(soil_depth[-1])
    ID_FIELD = scenario[:4] + "0001"
    # WSTA_ID =  scenario[:4]+ plt_year[2:] +"99"  #EJ(7/27/2021) generated weather are stored in ONE long WTH file for the next 100 yr simulations
    # # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    # fw.write(
    #     "{0:2s} {1:8s} {2:8s}{3:36s} {4:4s}  {5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID,
    #                                                                     "   -99   -99   -99   -99   -99   -99",
    #                                                                     SLTX.rjust(4), SLDP.rjust(4), ID_SOIL,
    #                                                                     " -99"))
    WSTA_ID = scenario[:4].upper()
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write(
        "{0:2s} {1:8s}{2:5s}{3:3s}{4:6s}{5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID.rjust(5),
                                                                        "       -99   -99   -99   -99   -99   -99 ",
                                                                        SLTX.ljust(6), SLDP.rjust(4), ID_SOIL,
                                                                        " -99"))
    fw.write(" \n")
    temp_str = fr.readline()  # 1 -99      CCER       -99   -99 DR000   -99   -99
    temp_str = fr.readline()  # @L ...........XCRD ...........YCRD .....ELEV
    fw.write(temp_str)
    temp_str = fr.readline()  # 1             -99             -99       -99   ==> skip
    # ================write *FIELDS - second section
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write("{0:2s} {1:89s}".format(FL.rjust(2),
                                    "            -99             -99       -99               -99   -99   -99   -99   -99   -99"))
    fw.write(" \n")
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *INITIAL CONDITIONS
    temp_str = fr.readline()
    new_str = temp_str[0:9] + ICDAT + temp_str[14:]
    fw.write(new_str)
    temp_str = fr.readline()  # @C  ICBL  SH2O  SNH4  SNO3
    fw.write(temp_str)
    temp_str = fr.readline()
    for nline in range(0, nlayer):
        if nline == 0:  # first layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "15"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # i_NO3 == "L":
                SNO3 = "5"  # **EJ(5/27/2015)
        elif nline == 1:  # second layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "2"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # elif i_NO3 == "L":
                SNO3 = ".5"  # **EJ(4/29/2020) used one constant number regardless of soil types
        else:
            temp_SH2O = fc[nline]  # float
            SNO3 = "0"  # **EJ(5/27/2015)
        SH2O = repr(temp_SH2O)[0:5]  # convert float to string
        new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + " " + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
        fw.write(new_str)
    fw.write("  \n")
    for nline in range(0, 10):
        temp_str = fr.readline()
        if temp_str[0:9] == "*PLANTING":
            break

    fw.write(temp_str)  # *PLANTING DETAILS
    temp_str = fr.readline()  # @P PDATE EDATE
    fw.write(temp_str)
    # write *PLANTING DETAILS
    temp_str = fr.readline()
    PPOE = PPOP #planting density 
    new_str = temp_str[0:3] + PDATE + "   -99" + PPOP.rjust(6) + PPOE.rjust(6) + temp_str[26:]
    fw.write(new_str)
    fw.write("  \n")
    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    if irrig_app == 'repr_irrig':
        fw.write('*IRRIGATION AND WATER MANAGEMENT'+ "\n")
        fw.write('@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME'+ "\n")
        fw.write(' 1     1    30    50   100 GS000 IR001    10 -99'+ "\n")
        fw.write('@I IDATE  IROP IRVAL'+ "\n")
        IROP = irrig_method  #irrigation method
        df_irrig = df_irrig.astype(float)
        df_filtered = df_irrig[(df_irrig["DAP"] >= 0) & (df_irrig["WAmount"] >= 0)]
        irrig_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        IDATE = df_filtered.DAP.values
        IRVAL = df_filtered.WAmount.values
        if irrig_count > 0:   # irrigation applied
            for i in range(irrig_count):
                # new_str = ' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + IRVAL.rjust(5)
                fw.write(' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + repr(IRVAL[i]).rjust(5)+ "\n")
            # fw.write(" \n")

            # df_irrig, ir_depth,ir_threshold, ir_eff
        #end of writing irrigation application

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:12] == "*FERTILIZERS":
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD 
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == "Fert":
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0) & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = "AP001"  #Broadcast, not incorporated    
        FDEP = "5"   #5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = "-99"
        FAMK = "-99"

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + FAMP.rjust(5) + " " + FAMK.rjust(5) + temp_str[44:]
                fw.write(new_str)
            fw.write(" \n")
#-------------------------------------------
    # else: #if no fertilzier applied
    #     temp_str = fr.readline()  #  1     0 FE005 AP002 
    #     fw.write(temp_str)
    #     temp_str = fr.readline()  #  1    45 FE005 AP002
    #     fw.write(temp_str)

    fw.write("  \n")
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:11] == "*SIMULATION":
            break
    fw.write(temp_str)  # *SIMULATION CONTROLS
    temp_str = fr.readline()
    fw.write(temp_str)  # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME
    # write *SIMULATION CONTROLS
    temp_str = fr.readline()
    new_str = temp_str[0:17] + repr(NYERS).rjust(3) + temp_str[20:33] + SDATE + temp_str[38:]  #EJ(7/27/2021) generated weather are stored in ONE long WTH file for the next 100 yr simulations
    fw.write(new_str)
    temp_str = fr.readline()  # @N OPTIONS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OP
    fw.write(" 1 OP              Y     Y     Y     N     N     N     N     N     D"+ "\n")
    temp_str = fr.readline()  # @N METHODS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 ME
    fw.write(temp_str)
    temp_str = fr.readline()  # @N MANAGEMENT
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 MA
    new_str = temp_str[0:25] + IRRIG + temp_str[26:31] + FERTI + temp_str[32:]
    fw.write(new_str)
    # fw.write(temp_str)
    temp_str = fr.readline()  # @N OUTPUTS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OU
    fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 5):
        temp_str = fr.readline()
        fw.write(temp_str)
    # irrigation method
    temp_str = fr.readline()  # 1 IR
    if irrig_app == 'auto_irrig':  # automatic when required
        IMDEP = ir_depth
        ITHRL = ir_threshold
        IREFF = ir_eff
        fw.write(' 1 IR          ' + repr(IMDEP).rjust(5) + repr(ITHRL).rjust(6) + '   100 GS000 IR001    10'+ repr(IREFF).rjust(6)+ "\n")
    else:
        # new_str = temp_str[0:39] + IMETH + temp_str[44:]
        fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 7):
        temp_str = fr.readline()
        fw.write(temp_str)

    fr.close()
    fw.close()
    return

# ====End of WRITE *.SNX
#===============================================================
def get_soil_IC(SOL_file, ID_SOIL):
    # SOL_file=Wdir_path.replace("/","\\") + "\\SN.SOL"
    # initialize
    depth_layer = []
    ll_layer = []
    ul_layer = []
    n_layer = 0
    soil_flag = 0
    count = 0
    fname = open(SOL_file, "r")  # opens *.SOL
    for line in fname:
        if ID_SOIL in line:
            soil_depth = line[33:37]
            s_class = line[25:29]
            soil_flag = 1
        if soil_flag == 1:
            count = count + 1
            if count >= 7:
                depth_layer.append(int(line[0:6]))
                ll_layer.append(float(line[13:18]))
                ul_layer.append(float(line[19:24]))
                n_layer = n_layer + 1
                if line[3:6].strip() == soil_depth.strip():
                    fname.close()
                    break
    return depth_layer, ll_layer, ul_layer, n_layer, s_class
#===============================================================