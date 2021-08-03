#Author: Eunjin Han
#Institute: IRI-Columbia University
#Date: 10/14/2020
#Purpose: to correct low frequency issue in monthly weather variables
# 1) compute monthly total rainfall and monthly mean of Tmin/Tmax/SRad
# 2) apply CDF matching to correct (typically underestimated) variance of WGEN generated output
#===========================================================================================
import numpy as np
import matplotlib.pyplot as plt
import calendar
import pandas as pd
import time
import sys
import os
from os import path # path

#========================================================================
def season_bias_corr(df_gen, target_year, season,Wdir_path):
#=================================================================
    # fname_gen = 'WGEN_corr_out_'+str(target_year)+'.csv'  #LOW-FREQUNCY CORRECTED BASED ON "MONTHLY" RAINFALL
    # # print(os.getcwd())
    # if not os.path.exists(fname_gen):
    #     print( '**Error!!- WGEN_out.csv.csv does not exist!')
    #     os.system('pause')
    # df_gen = pd.read_csv(fname_gen)

    #====================================================================
    #1) Compute monthly weather variables from the generated & LF corrected data
    #====================================================================
    m_doys_list = [1,32,60,91,121,152,182,213,244,274,305,335]
    m_doye_list = [31,59,90,120,151,181,212,243,273,304,334,365]
    numday_list = [31,28,31,30,31,30,31,31,30,31,30,31]

    #====================================================================
    #2) Compute monthly weather variables from the WGEN generated output
    #====================================================================
    #a) rainfall
    # target_year = int(df_gen.YEAR[0])
    gen_yrs = int(df_gen.iyear.values[-1])

    if calendar.isleap(target_year):
        rain_WTD = df_gen.RAIN.values
        year_WTD = df_gen.YEAR.values
        doy_WTD = df_gen.DOY.values
        #remove Feb 29th if created target year is a leap year
        #Exclude Feb. 29th in leapyears
        temp_indx = [1 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 29) else 0 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
        # Get the index of elements with value 15  result = np.where(arr == 15)
        rain_array = rain_WTD[np.where(np.asarray(temp_indx) == 0)]
        rain_array = np.reshape(rain_array, (gen_yrs,365))
        del rain_WTD
    else:
        rain_array = np.reshape(df_gen.RAIN.values, (gen_yrs,365))

    df_rain2 = pd.DataFrame(np.zeros((gen_yrs, 13)))
    df_rain2.columns = ['iyear','1','2','3','4','5','6','7','8','9','10','11','12']
    df_rain2.name = 'Generated_monthly_RAIN_'+str(target_year)
    df_rain2.iyear.iloc[:]= np.unique(df_gen.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_rain2.iloc[:,i+1] = np.sum(rain_array[:,t1:t2], axis=1)

    #make a new df to save daily correction factor
    columns = ['1','2','3','4','5','6','7','8','9','10','11','12']
    data = [[1.0 for j in columns] for i in range(0, gen_yrs)] # create a list of lists of 1.0 s for our dataframe
    df_rain_cf = pd.DataFrame(data, columns=columns)  #100 yrs x 12 months #CHECK!!!!!   all defaul correction factors are "1"

    ## read resampled monthly rainfall
    fname = path.join(Wdir_path, 'Resampled_monthly_RAIN'+repr(target_year)+'.csv')  
    df_rain_res = pd.read_csv(fname)

    #====================================================================
    #3) Compute seasonal total raifnall (e.g., JJAS)
    #====================================================================
    month_list = 'JFMAMJJASOND'  
    m_index = month_list.find(season)  #index of the first character=> m_index = 5 for JJAS
    for ii in range(len(season)):
        if ii == 0:
            srain_gen = df_rain2[repr(m_index + 1)]  #"6" for JJAS
            srain_res = df_rain_res[repr(m_index + 1)]  #"6" for JJAS
            m_index = m_index + 1
        else:
            srain_gen = srain_gen + df_rain2[repr(m_index + 1)]
            srain_res = srain_res + df_rain_res[repr(m_index + 1)]
            m_index = m_index + 1
            # print(srain_gen)

    #====================================================================
    #4) Apply CDF matching
    #====================================================================
    #a) compute CDF curve from the resampled (target cdf to correct)
    sorted_rain_res = np.sort(srain_res.values) #sort monthly rain from smallest to largest
    pdf = np.zeros(len(sorted_rain_res))+ (1/len(sorted_rain_res)) #1/100years
    cdf = np.cumsum(pdf)  #compute CDF
    #b) compute CDF curve from the WGEN-generated
    sorted_rain_gen = np.sort(srain_gen.values) #sort monthly rain from smallest to largest
    index_rain_gen = np.argsort(srain_gen.values) #** argsort - returns the original indexes of the sorted array
    pdf2 = np.zeros(len(sorted_rain_gen))+ (1/len(sorted_rain_gen)) #1/100years
    cdf2 = np.cumsum(pdf2)
    #c) CDF matching for bias correction
    # corrected_rain=np.interp(cdf2,cdf,sorted_rain_res,left=0.0)# 100 WGEN outputs to CDF of 500 resampled based on SCF
    corrected_rain=np.interp(cdf2,cdf,sorted_rain_res,left=0.1)# EJ(6/25/2021) lower limit is 0.1 not 0 to avoid 0 monthly correction factor.


    # ====================================================================
    # # # # ===========       comment out later!!!!  check
    # # #a) compute CDF curve from the climatology
    # fname_obs = 'WTD_observed_365.csv'
    # # print(os.getcwd())
    # if not os.path.exists(fname_obs):
    #     print( '**Error!!- WTD_observed_365.csv does not exist!')
    #     os.system('pause')
    # df_obs = pd.read_csv(fname_obs)
    # obs_yrs = np.unique(df_obs.YEAR.values).shape[0]
    # #a) rainfall
    # df_rain = pd.DataFrame(np.zeros((obs_yrs, 13)))
    # df_rain.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    # df_rain.name = 'Historical_monthly_RAIN'
    # df_rain.Year.iloc[:]= np.unique(df_obs.YEAR.values)
    # rain_array = np.reshape(df_obs.RAIN.values, (obs_yrs,365))
    # for i in range(12):
    #     t1 = m_doys_list[i] -1
    #     t2 = m_doye_list[i]
    #     df_rain.iloc[:,i+1] = np.sum(rain_array[:,t1:t2], axis=1)
    # del rain_array

    # m_index = month_list.find(season)  #index of the first character=> m_index = 5 for JJAS
    # for ii in range(len(season)):
    #     if ii == 0:
    #         srain_obs = df_rain[repr(m_index + 1)]  #"6" for JJAS
    #         m_index = m_index + 1
    #     else:
    #         srain_obs = srain_obs + df_rain[repr(m_index + 1)]
    #         m_index = m_index + 1
    #         print(srain_obs)

    # sorted_rain_obs = np.sort(srain_obs.values) #sort monthly rain from smallest to largest
    # pdf_obs = np.zeros(len(sorted_rain_obs))+ (1/len(sorted_rain_obs)) #1/100years
    # cdf_obs = np.cumsum(pdf_obs)  #compute CDF

    # fig = plt.figure()
    # fig.suptitle('Bias correction of seasonal total rainfall {}'.format(i+1))
    # ax = fig.add_subplot(111)
    # ax.set_xlabel('Seasonal total rain [mm]') #,fontsize=14)
    # ax.set_ylabel('CDF',fontsize=14)
    # ax.plot(sorted_rain_gen,cdf2, 'g--*',label='gen')
    # ax.plot(corrected_rain,cdf2, 'r--o',label='BC_cor')
    # ax.plot(sorted_rain_res,cdf, 'b--^',label='res')
    # ax.plot(sorted_rain_obs,cdf_obs, 'k--^',label='climatology')
    # legend = ax.legend(loc='lower right', shadow=True, fontsize='large')
    # plt.show()

    #=================================================================
    #====================================================================
    # 5) compute correction factor for the target season
    # and then apply it for each month within the target season
    #====================================================================
    # month_list = ['JFMAMJJASOND']  
    ind1 = month_list.find(season)  #+1 #5+1 if season == 'JJAS'
    #save monthly correction factors to dataframe
    sorted_rain_gen[sorted_rain_gen == 0.0] = 0.1  #replace 0 with 0.1 to avoid dividing by zero
    # corrected_rain[corrected_rain == 0.0] = 0.1  ## EJ(6/25/2021) lower limit is 0.1 not 0 to avoid 0 monthly correction factor.
    for i in range(len(season)):
        df_rain_cf.iloc[index_rain_gen, ind1] = np.divide(corrected_rain,sorted_rain_gen)  #CHECK!!!!!
        ind1 = ind1+1

    #==================
    #6)Write the bias-corrected daily output into a dataframe
    #==================
    #===================================================
    #save the corrected generated data into a csv file
    if calendar.isleap(target_year):
        Gndays = 366
        numday_list = [31,29,31,30,31,30,31,31,30,31,30,31]  #number of days in a given month
    else:
        Gndays = 365
        numday_list = [31,28,31,30,31,30,31,31,30,31,30,31]

    #make array into 1D
    for j in range(gen_yrs):
        for i in range(12):
            numday = numday_list[i]  #number of days in a given month
            if i ==0 and j == 0:
                # rain_d_cf = np.tile(df_rain_cf.iloc[j,i+1],(numday,1))  #np.tile(a, 2)
                rain_d_cf = np.tile(df_rain_cf.iloc[j,i],(numday,1))  #np.tile(a, 2)
            else:
                # rain_d_cf = np.concatenate((rain_d_cf, np.tile(df_rain_cf.iloc[j,i+1],(numday,1))),axis=0)
                rain_d_cf = np.concatenate((rain_d_cf, np.tile(df_rain_cf.iloc[j,i],(numday,1))),axis=0)

    df_cor = pd.DataFrame(np.zeros((gen_yrs*Gndays, 7)))   #4 matrix [3 by 3]
    df_cor.columns = ['iyear', 'YEAR','DOY','SRAD','TMAX','TMIN','RAIN']  #iyear => ith year
    df_cor.name = 'WGEN_season_corr_out_'+str(target_year)
    #save the corrected generated data into a dataframe
    df_cor.iyear.iloc[:] = df_gen.iyear.iloc[:]
    df_cor.YEAR.iloc[:] = df_gen.YEAR.iloc[:]
    df_cor.DOY.iloc[:] = df_gen.DOY.iloc[:]
    df_cor.RAIN.iloc[:] = np.multiply(df_gen.RAIN.values, rain_d_cf.flatten())
    df_cor.SRAD.iloc[:] = df_gen.SRAD.iloc[:]
    df_cor.TMAX.iloc[:] = df_gen.TMAX.iloc[:]
    df_cor.TMIN.iloc[:] = df_gen.TMIN.iloc[:]

    #write dataframe into CSV file
    fname = path.join(Wdir_path, df_cor.name + '.csv')  
    df_cor.to_csv(fname, index=False)   #delete later on
    del rain_d_cf
    return df_cor

