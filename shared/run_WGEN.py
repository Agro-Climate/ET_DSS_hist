import numpy as np
import pandas as pd
from os import path
from datetime import date
import datetime    #to convert date to doy or vice versa
import calendar
import sys

import time #just for checking processign time => delete later 
from shared.WGEN_generator import WGEN_generator   #EJ(7/27/2021)
from shared.WGEN_PAR_biweekly import WGEN_PAR_biweekly  
from shared.low_freq_correction import low_freq_correction  
from shared.season_bias_corr import season_bias_corr  #EJ(7/12/2021) bias correction for seasonal total rainfall

# Start the stopwatch / counter  
start_time = time.process_time() 

def run_WGEN(df_tab, tri_doylist, Wdir_path):   
    WSTA =df_tab.stn_name.values[0] 
    WTD_fname = path.join(Wdir_path, WSTA+".WTD")
    trimester1 = df_tab.Trimester1.values[0]  #"JJA followed by SON"
    planting_date = df_tab.PltDate.values[0]
    plt_year = planting_date[:4] 
    #================== MAIN PROGRAM ======================================
    target_year = int(plt_year)  #2016
    nsample = 200 #===> number of years sampled to generate parameters for WGEN
    nrealiz = 100 #number of years to generate (output of WGEN)
    print( '==START WEATHER GENERATION PROCEDURES')

    # === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
    WTD_df_orig, df_obs = read_WTD(WTD_fname)

    sdoy1 = tri_doylist[0] # starting doy of the target trimester #1  => 152 in case of JJA
    edoy1 = tri_doylist[1]  #ending doy of the target trimester #1  => 243 in case of JJA
    sdoy2 = tri_doylist[2] # starting doy of the target trimester #2
    edoy2 = tri_doylist[3]  #ending doy of the target trimester #2

    df_sorted1 = get_ind_sorted_yr(df_obs, sdoy1, edoy1)  #get indices of the sorted years based on SCF1
    df_sorted2 = get_ind_sorted_yr(df_obs, sdoy2, edoy2) #get indices of the sorted years based on SCF2
    #write dataframe into CSV file for debugging => delete later!
    df_sorted1.to_csv(Wdir_path + 'season_rain_sorted'+str(sdoy1) + '.csv', index=False)
    df_sorted2.to_csv(Wdir_path + 'season_rain_sorted'+str(sdoy2) + '.csv', index=False)

    #====1) resampling years for SCF1 period
    BN = df_tab.BN1.values[0]
    AN = df_tab.AN1.values[0]
    SCF1_yr_list = resample_years(df_sorted1,AN,BN,nsample)
    #====2) resampling years for SCF2 period
    BN2 = df_tab.BN2.values[0]
    AN2 = df_tab.AN2.values[0]
    SCF2_yr_list = resample_years(df_sorted2,AN2,BN2,nsample)
    #====3) resampling years for climatology
    # nyears = len(df_obs.YEAR.unique())
    year1 = df_obs.YEAR.iloc[0].astype(int)  #the first obs year
    year2 = df_obs.YEAR.iloc[-1].astype(int) #the last obs year
    clim_yr_list = np.random.randint(year1, year2+1, nsample)

    #========================================================
    print ("0) Resampling histrical years before WGEN-PAR. Please wait....")
    #====4) Aggregate daily weather data based on the resampled year list 
    rain_resampled = np.empty((nsample,365,))*np.NAN 
    srad_resampled = np.empty((nsample,365,))*np.NAN 
    tmin_resampled = np.empty((nsample,365,))*np.NAN 
    tmax_resampled = np.empty((nsample,365,))*np.NAN 

    #see case lists:https://docs.google.com/spreadsheets/d/1XnBcHzbTDtDJpHl9U9SX0AfNgDjy4Vci/edit#gid=801540749
    #=========================================================
    #case #1: both SCF1 and SCF2 are in YR1
    #case #2: both SCF1 and SCF2 are in YR1 but SCF2 is for OND. Therefore, Year 2 is fully based on climatology
    #=========================================================
    if trimester1 == "FMA" or trimester1 == "MAM" or trimester1 == "AMJ" or trimester1 == "MJJ" or trimester1 == "JJA" or trimester1 == "JAS": 
        for i in range(nsample):
            #a)climatology
            rain_resampled[i,0:sdoy1-1] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] < sdoy1)].values
            srad_resampled[i,0:sdoy1-1] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] < sdoy1)].values
            tmin_resampled[i,0:sdoy1-1] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] < sdoy1)].values
            tmax_resampled[i,0:sdoy1-1] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] < sdoy1)].values
            #b)SCF1
            rain_resampled[i,sdoy1-1:edoy1] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            srad_resampled[i,sdoy1-1:edoy1] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmin_resampled[i,sdoy1-1:edoy1] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmax_resampled[i,sdoy1-1:edoy1] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            #c)SCF2
            rain_resampled[i,sdoy2-1:edoy2] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            srad_resampled[i,sdoy2-1:edoy2] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmin_resampled[i,sdoy2-1:edoy2] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmax_resampled[i,sdoy2-1:edoy2] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            #d)climatology
            rain_resampled[i,edoy2:] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2)].values
            srad_resampled[i,edoy2:] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2)].values
            tmin_resampled[i,edoy2:] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2)].values
            tmax_resampled[i,edoy2:] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2)].values 
    #=========================================================
    # #Case #3: SCF1 is for ASO or SON
    #=========================================================
    elif trimester1 == "ASO" or trimester1 == "SON":
        for i in range(nsample):
            #a) second part of SCF2
            rain_resampled[i,0:edoy2] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            srad_resampled[i,0:edoy2] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            tmin_resampled[i,0:edoy2] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            tmax_resampled[i,0:edoy2] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            #b)climatology
            rain_resampled[i,edoy2:sdoy1-1] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            srad_resampled[i,edoy2:sdoy1-1] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmin_resampled[i,edoy2:sdoy1-1] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmax_resampled[i,edoy2:sdoy1-1] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            #c)SCF1
            rain_resampled[i,sdoy1-1:edoy1] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            srad_resampled[i,sdoy1-1:edoy1] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmin_resampled[i,sdoy1-1:edoy1] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmax_resampled[i,sdoy1-1:edoy1] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            #d)first part of SCF2
            rain_resampled[i,edoy1:] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= 365)].values
            srad_resampled[i,edoy1:] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= 365)].values
            tmin_resampled[i,edoy1:] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= 365)].values
            tmax_resampled[i,edoy1:] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= 365)].values
    #=========================================================
    # Case #4:SCF1 is for OND, SCF2 is for JFM in next year
    #=========================================================
    elif trimester1 == "OND":
        for i in range(nsample):
            #a) SCF2
            rain_resampled[i,0:edoy2] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            srad_resampled[i,0:edoy2] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            tmin_resampled[i,0:edoy2] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            tmax_resampled[i,0:edoy2] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy2)].values
            #b)climatology
            rain_resampled[i,edoy2:sdoy1-1] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            srad_resampled[i,edoy2:sdoy1-1] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmin_resampled[i,edoy2:sdoy1-1] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmax_resampled[i,edoy2:sdoy1-1] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            #b)SCF1
            rain_resampled[i,sdoy1-1:edoy1] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            srad_resampled[i,sdoy1-1:edoy1] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmin_resampled[i,sdoy1-1:edoy1] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values
            tmax_resampled[i,sdoy1-1:edoy1] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= edoy1)].values

    #=========================================================
    # Case #5:SCF1 is for NDJ or DJF (SCF2 is for FMA or MAM in next year)
    #=========================================================
    elif trimester1 == "NDJ" or trimester1 == "DJF":
        for i in range(nsample):
            #a) 2nd part of SCF1
            rain_resampled[i,0:edoy1] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            srad_resampled[i,0:edoy1] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            tmin_resampled[i,0:edoy1] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            tmax_resampled[i,0:edoy1] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            #b) SCF2
            rain_resampled[i,edoy1:edoy2] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            srad_resampled[i,edoy1:edoy2] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmin_resampled[i,edoy1:edoy2] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmax_resampled[i,edoy1:edoy2] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            #c)climatology
            rain_resampled[i,edoy2:sdoy1-1] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            srad_resampled[i,edoy2:sdoy1-1] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmin_resampled[i,edoy2:sdoy1-1] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            tmax_resampled[i,edoy2:sdoy1-1] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] < sdoy1)].values
            #d) 1st part of SCF1
            rain_resampled[i,sdoy1-1:] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= 365)].values
            srad_resampled[i,sdoy1-1:] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= 365)].values
            tmin_resampled[i,sdoy1-1:] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= 365)].values
            tmax_resampled[i,sdoy1-1:] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy1) & (df_obs["DOY"] <= 365)].values
    #=========================================================
    # Case #6: SCF1 starts from January in year 2
    #=========================================================
    elif trimester1 == "JFM":
        for i in range(nsample):
            #a) SCF1
            rain_resampled[i,0:edoy1] = df_obs.RAIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            srad_resampled[i,0:edoy1] = df_obs.SRAD[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            tmin_resampled[i,0:edoy1] = df_obs.TMIN[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            tmax_resampled[i,0:edoy1] = df_obs.TMAX[(df_obs["YEAR"] == SCF2_yr_list[i])& (df_obs["DOY"] >= 1) & (df_obs["DOY"] <= edoy1)].values
            #b) SCF2
            rain_resampled[i,edoy1:edoy2] = df_obs.RAIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            srad_resampled[i,edoy1:edoy2] = df_obs.SRAD[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmin_resampled[i,edoy1:edoy2] = df_obs.TMIN[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            tmax_resampled[i,edoy1:edoy2] = df_obs.TMAX[(df_obs["YEAR"] == SCF1_yr_list[i])& (df_obs["DOY"] >= sdoy2) & (df_obs["DOY"] <= edoy2)].values
            #c)climatology
            rain_resampled[i,edoy2:] = df_obs.RAIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] <= 365)].values
            srad_resampled[i,edoy2:] = df_obs.SRAD[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] <= 365)].values
            tmin_resampled[i,edoy2:] = df_obs.TMIN[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] <= 365)].values
            tmax_resampled[i,edoy2:] = df_obs.TMAX[(df_obs["YEAR"] == clim_yr_list[i])& (df_obs["DOY"] > edoy2) & (df_obs["DOY"] <= 365)].values

    #===========================================================================================
    #===========================================================================================
    # ======================END of making resampled matrix for all cases
    #=====save resampled dataframe into a csv for bias correction later on
    Compute_resampled_monthly(target_year, rain_resampled, tmin_resampled, tmax_resampled, srad_resampled,Wdir_path)
    print ("1)Estimate rainfall parameters (running WGEN_PAR_biweekly). Please wait....")
    #Estimate parameters for rainfall models and Fourier coefficients for Tmin/Tmax/Srad
    WGEN_PAR_biweekly(target_year, rain_resampled, tmin_resampled, tmax_resampled, srad_resampled, Wdir_path)
    print("It took {0:5.1f}, sec to estimate biweekly weather parameters, WGEN_PAR_biweekly". format(time.process_time() - start_time)) 
    print ("2) Gnerating weather realization (running WGEN_generator). Please wait....")
    #Generate daily weather realizations based on the estimated parameters
    df_gen = WGEN_generator(target_year,nrealiz, Wdir_path)
    #Correct low frequency (inter-annual variability of monthly weather data)
    print ("3) Correcting low-frequency bias (running low_freq_correction). Please wait....")
    # df_gen_lf = low_freq_correction(df_obs, df_gen, target_year, Wdir_path)
    df_gen_lf = low_freq_correction(df_gen, target_year, Wdir_path)
    print("It took {0:5.1f}, sec to finish calling MONTHLY low frequency correction". format(time.process_time() - start_time)) 
    print ("4) Correcting seasonal bias (running season_bias_corr). Please wait....")
    df_WGEN_corr = season_bias_corr(df_gen_lf, target_year, trimester1,Wdir_path)
    print("It took {0:5.1f}, sec to finish calling SEASONAL bias correction". format(time.process_time() - start_time))
    return df_WGEN_corr



#===============================================================
#===============================================================
# === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
def read_WTD(fname):
    #1) Read daily observations into a matrix (note: Feb 29th was skipped)
    # WTD_fname = r'C:\Users\Eunjin\IRI\Hybrid_WGEN\CNRA.WTD'
    #1) read observed weather *.WTD (skip 1st row - heading)
    data1 = np.loadtxt(fname,skiprows=1)
    #convert numpy array to dataframe
    WTD_df = pd.DataFrame({'YEAR':data1[:,0].astype(int)//1000,    #python 3.6: / --> //
                    'DOY':data1[:,0].astype(int)%1000,
                    'SRAD':data1[:,1],
                    'TMAX':data1[:,2],
                    'TMIN':data1[:,3],
                    'RAIN':data1[:,4]})
    #make a copy of original WTD dataframe 
    WTD_df_orig = WTD_df.copy()
    #=== Extract only years with full 365/366 days:  by checking last obs year if it is incomplete or not
    WTD_last_year = WTD_df.YEAR.values[-1] 
    WTD_last_doy = WTD_df.DOY[WTD_df["YEAR"] == WTD_last_year].values[-1]
    if calendar.isleap(WTD_last_year):
        if WTD_last_doy < 366:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_last_year].index
            WTD_df.drop(indexNames , inplace=True) # Delete these row indexes from dataFrame
    else:
        if WTD_last_doy < 365:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_last_year].index
            WTD_df.drop(indexNames , inplace=True)    
    #=== Extract only years with full 365/366 days:  by checking first obs year if it is incomplete or not
    WTD_first_year = WTD_df.YEAR.values[0] 
    WTD_first_date = WTD_df.DOY[WTD_df["YEAR"] == WTD_first_year].values[0]
    if WTD_first_date > 1:
        if calendar.isleap(WTD_first_year):
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_first_year].index
            WTD_df.drop(indexNames , inplace=True)
        else:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_first_year].index
            WTD_df.drop(indexNames , inplace=True) 
    #========================
    rain_WTD = WTD_df.RAIN.values
    srad_WTD = WTD_df.SRAD.values
    Tmax_WTD = WTD_df.TMAX.values
    Tmin_WTD = WTD_df.TMIN.values
    year_WTD = WTD_df.YEAR.values
    doy_WTD = WTD_df.DOY.values
    obs_yrs = np.unique(year_WTD).shape[0]
    #Exclude Feb. 29th in leapyears
    temp_indx = [1 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 29) else 0 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
    # Get the index of elements with value 15  result = np.where(arr == 15)
    rain_array = rain_WTD[np.where(np.asarray(temp_indx) == 0)]
    rain_array = np.reshape(rain_array, (obs_yrs,365))
    srad_array = srad_WTD[np.where(np.asarray(temp_indx) == 0)]
    srad_array = np.reshape(srad_array, (obs_yrs,365))
    Tmax_array = Tmax_WTD[np.where(np.asarray(temp_indx) == 0)]
    Tmax_array = np.reshape(Tmax_array, (obs_yrs,365))
    Tmin_array = Tmin_WTD[np.where(np.asarray(temp_indx) == 0)]
    Tmin_array = np.reshape(Tmin_array, (obs_yrs,365))

    #save dataframe into a csv file [Note: Feb 29th was excluded]
    df_obs = pd.DataFrame(np.zeros((obs_yrs*365, 6)))   
    df_obs.columns = ['YEAR','DOY','SRAD','TMAX','TMIN','RAIN']  #iyear => ith year
    df_obs.name = 'WTD_observed_365'
    k = 0
    for i in range(obs_yrs):
        iyear = np.unique(year_WTD)[i]
        df_obs.YEAR.iloc[k:365*(i+1)] = np.tile(iyear,(365,))
        df_obs.DOY.iloc[k:365*(i+1)]= np.asarray(range(1,366))
        df_obs.SRAD.iloc[k:365*(i+1)]= np.transpose(srad_array[i,:])
        df_obs.TMAX.iloc[k:365*(i+1)]= np.transpose(Tmax_array[i,:])
        df_obs.TMIN.iloc[k:365*(i+1)]= np.transpose(Tmin_array[i,:])
        df_obs.RAIN.iloc[k:365*(i+1)]= np.transpose(rain_array[i,:])
        k=k+365
    # #write dataframe into CSV file
    # df_obs.to_csv(wdir +'//'+ df_obs.name + '.csv', index=False)
    del rain_WTD; del srad_WTD; del Tmax_WTD; del Tmin_WTD; del year_WTD; del doy_WTD
    del rain_array; del srad_array; del Tmax_array; del Tmin_array
    return WTD_df_orig, df_obs
#====================================================================
# End of reading observations (WTD file) into a matrix 
#====================================================================
def resample_years(df_sorted,AN,BN,nsample):
    nyears = len(df_sorted.YEAR.values)

    gnum_BN = int(nsample * (BN/100.0))  #generated numbers for BN
    gnum_AN = int(nsample * (AN/100.0))
    gnum_NN = nsample - gnum_BN - gnum_AN

    nsample_BN = nyears//3  
    nsample_AN = nyears//3
    nsample_NN = nyears - 2*nsample_BN

    BN_index = np.random.randint(0, nsample_BN, gnum_BN)   #0~9
    #e.g., d1 = np.random.randint(1, 7, 1000) => Random integers of type np.int_ between 1 and 7 (7 is not iuncluded)
    NN_index = nsample_BN + np.random.randint(0, nsample_NN, gnum_NN) #10~19
    AN_index = nsample_BN + nsample_NN + np.random.randint(0, nsample_AN, gnum_AN)  #20~29 for 30 yrs of observations

    BN_yr_list = np.asarray([df_sorted.YEAR.iloc[BN_index[i]] for i in range(gnum_BN)]) #[f(x) if condition else g(x) for x in sequence]
    NN_yr_list = np.asarray([df_sorted.YEAR.iloc[NN_index[i]] for i in range(gnum_NN)])
    AN_yr_list = np.asarray([df_sorted.YEAR.iloc[AN_index[i]] for i in range(gnum_AN)])

    SCF_yr_list = np.concatenate((BN_yr_list.astype(int), NN_yr_list.astype(int)), axis=0)
    SCF_yr_list = np.concatenate((SCF_yr_list, AN_yr_list.astype(int)), axis=0)

    return SCF_yr_list
#======================================================================
def get_ind_sorted_yr(WTD_df, sdoy, edoy): 
    #sdoy: starting doy of the target period
    #edoy: ending doy of the target period
    #===================================================
    sdoy = int(sdoy) #convert into integer just in case
    edoy = int(edoy)
    #3-1) Extract daily weather data for the target period
    # count how many years are recorded
    year_array = WTD_df.YEAR.unique()
    nyears = year_array.shape[0]

    #Make 2D array and aggregate during the specified season/months (10/15/2020)
    rain_array = np.reshape(WTD_df.RAIN.values, (nyears,365))
    if edoy > sdoy: #all months within the target season is within one year
        season_rain_sum = np.sum(rain_array[:,(sdoy-1):edoy], axis=1)
    else: #seasonal sum goes beyond the first year  #   if edoy < sdoy:
        a= rain_array[:-1,(sdoy-1):]
        b = rain_array[1:,0:edoy]
        rain_array2 = np.concatenate((a,b), axis = 1)
        # season_rain_sum = np.sum(rain_array[:-1,(sdoy-1):(sdoy+edoy)], axis=1)    
        season_rain_sum = np.sum(rain_array2, axis=1) #check !
        nyears = nyears - 1
    #================================================================
    #save dataframe into a csv file [Note: Feb 29th was excluded]
    df_sorted = pd.DataFrame(np.zeros((nyears, 3)))   
    df_sorted.columns = ['YEAR','season_rain', 'sindex']  #iyear => ith year
    df_sorted.name = 'season_rain_sorted'+str(sdoy)
    df_sorted.YEAR.iloc[:]= year_array[0:nyears][np.argsort(season_rain_sum)]
    df_sorted.season_rain.iloc[:]= season_rain_sum[np.argsort(season_rain_sum)]
    df_sorted.sindex.iloc[:]= np.argsort(season_rain_sum)
    # #write dataframe into CSV file
    # df_sorted.to_csv(wdir + '//'+df_sorted.name + '.csv', index=False)

    return df_sorted
    #=================================================
def Compute_resampled_monthly(target_year, rain_resampled, tmin_resampled, tmax_resampled, srad_resampled, Wdir_path):
   #==================================================================================
   #=====EJ(12/30/2020) save resampled dataframe into a csv for bias correction later on
    #save dataframe into a csv file [Note: Feb 29th was excluded]
    nsample = rain_resampled.shape[0]
    df_resmp = pd.DataFrame(np.zeros((nsample*365, 7)))   
    df_resmp.columns = ['iyear', 'YEAR','DOY','SRAD','TMAX','TMIN','RAIN']  #iyear => ith year
    df_resmp.name = 'WGEN_resampled_'+repr(target_year)
    k = 0
    for i in range(nsample):
        df_resmp.iyear.iloc[k:365*(i+1)]= i+1
        iyear = target_year #np.unique(year_WTD)[i]
        df_resmp.YEAR.iloc[k:365*(i+1)] = np.tile(iyear,(365,))
        df_resmp.DOY.iloc[k:365*(i+1)]= np.asarray(range(1,366))
        df_resmp.SRAD.iloc[k:365*(i+1)]= np.transpose(srad_resampled[i,:])
        df_resmp.TMAX.iloc[k:365*(i+1)]= np.transpose(tmax_resampled[i,:])
        df_resmp.TMIN.iloc[k:365*(i+1)]= np.transpose(tmin_resampled[i,:])
        df_resmp.RAIN.iloc[k:365*(i+1)]= np.transpose(rain_resampled[i,:])
        k=k+365
    #write dataframe into CSV file
    fname = path.join(Wdir_path, df_resmp.name + '.csv') 
    df_resmp.to_csv(fname, index=False)

    #2) Compute monthly weather variables from the historical observation
    m_doys_list = [1,32,60,91,121,152,182,213,244,274,305,335]
    m_doye_list = [31,59,90,120,151,181,212,243,273,304,334,365]
    # numday_list = [31,28,31,30,31,30,31,31,30,31,30,31]
    #a) rainfall
    df_res_rain = pd.DataFrame(np.zeros((nsample, 13))) 
    df_res_rain.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    df_res_rain.name = 'Resampled_monthly_RAIN'+repr(target_year)
    df_res_rain.Year.iloc[:]= np.unique(df_resmp.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_res_rain.iloc[:,i+1] = np.sum(rain_resampled[:,t1:t2], axis=1) 
    fname = path.join(Wdir_path, df_res_rain.name + '.csv') 
    df_res_rain.to_csv(fname) #write dataframe into CSV file

    #b) Srad
    df_res_srad = pd.DataFrame(np.zeros((nsample, 13))) 
    df_res_srad.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    df_res_srad.name = 'Resampled_monthly_SRAD'+repr(target_year)
    df_res_srad.Year.iloc[:]= np.unique(df_resmp.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_res_srad.iloc[:,i+1] = np.mean(srad_resampled[:,t1:t2], axis=1)
    fname = path.join(Wdir_path, df_res_srad.name + '.csv') 
    df_res_srad.to_csv(fname) #write dataframe into CSV file

    #c) Tmax
    df_res_tmax = pd.DataFrame(np.zeros((nsample, 13))) 
    df_res_tmax.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    df_res_tmax.name = 'Resampled_monthly_TMAX'+repr(target_year)
    df_res_tmax.Year.iloc[:]= np.unique(df_resmp.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_res_tmax.iloc[:,i+1] = np.mean(tmax_resampled[:,t1:t2], axis=1)
    fname = path.join(Wdir_path, df_res_tmax.name + '.csv') 
    df_res_tmax.to_csv(fname) #write dataframe into CSV file

    #d) Tmin
    df_res_tmin = pd.DataFrame(np.zeros((nsample, 13))) 
    df_res_tmin.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    df_res_tmin.name = 'Resampled_monthly_TMIN'+repr(target_year)
    df_res_tmin.Year.iloc[:]= np.unique(df_resmp.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_res_tmin.iloc[:,i+1] = np.mean(tmin_resampled[:,t1:t2], axis=1)
    fname = path.join(Wdir_path, df_res_tmin.name + '.csv') 
    df_res_tmin.to_csv(fname) #write dataframe into CSV file
    del df_res_tmin; del df_res_tmax; del df_res_rain; del df_res_srad; del df_resmp



