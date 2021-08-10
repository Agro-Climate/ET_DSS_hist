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
from os import path 
#========================================================================
# def low_freq_correction(df_obs, df_gen, target_year, Wdir_path): 
def low_freq_correction(df_gen, target_year, Wdir_path): 
#=================================================================
    # # #=================================================================
    # # # Start the stopwatch / counter  
    # # start_time = time.process_time() 
    # # #====================================================================

    # # # def low_freq_correction(fname_obs, fname_gen):
    # # fname_obs = 'WTD_observed_SANJ.csv'
    # # df_obs = pd.read_csv(fname_obs)
    # # fname_gen = 'WGEN_out_SANJ.csv'
    # # df_gen = pd.read_csv(fname_gen)

    # # fname_obs = 'WTD_observed_365.csv'
    # # # print(os.getcwd())
    # # if not os.path.exists(fname_obs):
    # #     print( '**Error!!- WTD_observed_365.csv does not exist!')
    # #     os.system('pause')
    # # df_obs = pd.read_csv(fname_obs)

    # # fname_gen = 'WGEN_out_'+str(target_year)+'.csv'
    # # # print(os.getcwd())
    # # if not os.path.exists(fname_gen):
    # #     print( '**Error!!- WGEN_out.csv.csv does not exist!')
    # #     os.system('pause')
    # # df_gen = pd.read_csv(fname_gen)

    # obs_yrs = np.unique(df_obs.YEAR.values).shape[0]
    #====================================================================
    #1) Compute monthly weather variables from the historical observation
    #====================================================================
    m_doys_list = [1,32,60,91,121,152,182,213,244,274,305,335]
    m_doye_list = [31,59,90,120,151,181,212,243,273,304,334,365]
    numday_list = [31,28,31,30,31,30,31,31,30,31,30,31]
    # m_doys_list_leap = [1,32,61,92,122,153,183,214,245,275,306,336]  #starting date of each month for leap years
    # m_doye_list_leap = [31,60,91,121,152,182,213,244,274,305,335,366] #ending date of each month for leap years
    # numday_list_leap = [31,29,31,30,31,30,31,31,30,31,30,31]


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
    # #write dataframe into CSV file
    # df_rain.to_csv(df_rain.name + '.csv')

    # #b) Srad
    # df_srad = pd.DataFrame(np.zeros((obs_yrs, 13))) 
    # df_srad.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    # df_srad.name = 'Historical_monthly_SRAD'
    # df_srad.Year.iloc[:]= np.unique(df_obs.YEAR.values)
    # srad_array = np.reshape(df_obs.SRAD.values, (obs_yrs,365))

    # for i in range(12):
    #     t1 = m_doys_list[i] -1
    #     t2 = m_doye_list[i]
    #     df_srad.iloc[:,i+1] = np.mean(srad_array[:,t1:t2], axis=1)
    # #write dataframe into CSV file
    # df_srad.to_csv(df_srad.name + '.csv')

    # #c) Tmax
    # df_tmax = pd.DataFrame(np.zeros((obs_yrs, 13))) 
    # df_tmax.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    # df_tmax.name = 'Historical_monthly_TMAX'
    # df_tmax.Year.iloc[:]= np.unique(df_obs.YEAR.values)
    # tmax_array = np.reshape(df_obs.TMAX.values, (obs_yrs,365))

    # for i in range(12):
    #     t1 = m_doys_list[i] -1
    #     t2 = m_doye_list[i]
    #     df_tmax.iloc[:,i+1] = np.mean(tmax_array[:,t1:t2], axis=1)
    # #write dataframe into CSV file
    # df_tmax.to_csv(df_tmax.name + '.csv')

    # #d) Tmin
    # df_tmin = pd.DataFrame(np.zeros((obs_yrs, 13))) 
    # df_tmin.columns = ['Year','1','2','3','4','5','6','7','8','9','10','11','12']
    # df_tmin.name = 'Historical_monthly_TMIN'
    # df_tmin.Year.iloc[:]= np.unique(df_obs.YEAR.values)
    # tmin_array = np.reshape(df_obs.TMIN.values, (obs_yrs,365))

    # for i in range(12):
    #     t1 = m_doys_list[i] -1
    #     t2 = m_doye_list[i]
    #     df_tmin.iloc[:,i+1] = np.mean(tmin_array[:,t1:t2], axis=1)
    # #write dataframe into CSV file
    # df_tmin.to_csv(df_tmin.name + '.csv')

    # del rain_array; del srad_array; del tmax_array; del tmin_array
    #====================================================================
    #2) Compute monthly weather variables from the WGEN generated output
    #====================================================================
    #a) rainfall
    # target_year = int(df_gen.YEAR[0])
    gen_yrs = int(df_gen.iyear.values[-1])

    if calendar.isleap(target_year):
        rain_WTD = df_gen.RAIN.values
        srad_WTD = df_gen.SRAD.values
        Tmax_WTD = df_gen.TMAX.values
        Tmin_WTD = df_gen.TMIN.values
        year_WTD = df_gen.YEAR.values
        doy_WTD = df_gen.DOY.values
        #remove Feb 29th if created target year is a leap year
        #Exclude Feb. 29th in leapyears
        temp_indx = [1 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 29) else 0 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
        # Get the index of elements with value 15  result = np.where(arr == 15)
        rain_array = rain_WTD[np.where(np.asarray(temp_indx) == 0)]
        rain_array = np.reshape(rain_array, (gen_yrs,365))
        srad_array = srad_WTD[np.where(np.asarray(temp_indx) == 0)]
        srad_array = np.reshape(srad_array, (gen_yrs,365))
        tmax_array = Tmax_WTD[np.where(np.asarray(temp_indx) == 0)]
        tmax_array = np.reshape(tmax_array, (gen_yrs,365))
        tmin_array = Tmin_WTD[np.where(np.asarray(temp_indx) == 0)]
        tmin_array = np.reshape(tmin_array, (gen_yrs,365))
        del rain_WTD; del srad_WTD; del Tmax_WTD; del Tmin_WTD; del year_WTD; del doy_WTD
    else:
        rain_array = np.reshape(df_gen.RAIN.values, (gen_yrs,365))
        srad_array = np.reshape(df_gen.SRAD.values, (gen_yrs,365))
        tmax_array = np.reshape(df_gen.TMAX.values, (gen_yrs,365))
        tmin_array = np.reshape(df_gen.TMIN.values, (gen_yrs,365))

    df_rain2 = pd.DataFrame(np.zeros((gen_yrs, 13))) 
    df_rain2.columns = ['iyear','1','2','3','4','5','6','7','8','9','10','11','12']
    df_rain2.name = 'Generated_monthly_RAIN_'+str(target_year)
    df_rain2.iyear.iloc[:]= np.unique(df_gen.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_rain2.iloc[:,i+1] = np.sum(rain_array[:,t1:t2], axis=1)
    #write dataframe into CSV file
    fname = path.join(Wdir_path,df_rain2.name + '.csv')  
    df_rain2.to_csv(fname)
    df_rain_cf = df_rain2.copy() #df to save monthly rainfall correction factor

    #b) Srad
    df_srad2 = pd.DataFrame(np.zeros((gen_yrs, 13))) 
    df_srad2.columns = ['iyear','1','2','3','4','5','6','7','8','9','10','11','12']
    df_srad2.name = 'Generated_monthly_SRAD_'+str(target_year)
    df_srad2.iyear.iloc[:]= np.unique(df_gen.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_srad2.iloc[:,i+1] = np.mean(srad_array[:,t1:t2], axis=1)
    #write dataframe into CSV file
    fname = path.join(Wdir_path,df_srad2.name + '.csv')  
    df_srad2.to_csv(fname)
    df_srad_cf = df_srad2.copy() #df to save monthly rainfall correction factor

    #c) Tmax
    df_tmax2 = pd.DataFrame(np.zeros((gen_yrs, 13))) 
    df_tmax2.columns = ['iyear','1','2','3','4','5','6','7','8','9','10','11','12']
    df_tmax2.name = 'Generated_monthly_TMAX_'+str(target_year)
    df_tmax2.iyear.iloc[:]= np.unique(df_gen.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_tmax2.iloc[:,i+1] = np.mean(tmax_array[:,t1:t2], axis=1)
    #write dataframe into CSV file
    fname = path.join(Wdir_path, df_tmax2.name + '.csv')  
    df_tmax2.to_csv(fname)
    df_tmax_cf = df_tmax2.copy() #df to save monthly rainfall correction factor

    #d) Tmin
    df_tmin2 = pd.DataFrame(np.zeros((gen_yrs, 13))) 
    df_tmin2.columns = ['iyear','1','2','3','4','5','6','7','8','9','10','11','12']
    df_tmin2.name = 'Generated_monthly_TMIN_'+str(target_year)
    df_tmin2.iyear.iloc[:]= np.unique(df_gen.iyear.values)
    for i in range(12):
        t1 = m_doys_list[i] -1
        t2 = m_doye_list[i]
        df_tmin2.iloc[:,i+1] = np.mean(tmin_array[:,t1:t2], axis=1)
    #write dataframe into CSV file
    fname = path.join(Wdir_path, df_tmin2.name + '.csv') 
    df_tmin2.to_csv(fname)
    
    df_tmin_cf = df_tmin2.copy() #df to save monthly rainfall correction factor

    # print (time.process_time() - start_time, "sec elapsed until computing monthly variables")

    #====================================================================
    #3) Apply CDF matching to correct (typically underestimated) variance of WGEN generated output
    #====================================================================
    #==================================================================================
    #=====EJ(12/30/2020) CDF matching based on resampled distribution (not observed)
    df_rain_res = pd.read_csv(path.join(Wdir_path,'Resampled_monthly_RAIN'+repr(target_year)+'.csv')) #'Resampled_monthly_RAIN'+repr(target_year)+'.csv')
    df_tmin_res = pd.read_csv(path.join(Wdir_path,'Resampled_monthly_TMIN'+repr(target_year)+'.csv'))
    df_tmax_res = pd.read_csv(path.join(Wdir_path,'Resampled_monthly_TMAX'+repr(target_year)+'.csv'))
    df_srad_res = pd.read_csv(path.join(Wdir_path,'Resampled_monthly_SRAD'+repr(target_year)+'.csv'))
    #=====end of EJ(12/30/2020) 
    #==================================================================================
    # for i in progressbar(range(12), "CDF matching for low freq correction: ", 40):
    for i in range(0,12):  #12 months
        #=== 1) Rainfall
        #a) compute CDF curve from the resampled (target cdf to correct)
        sorted_rain_res = np.sort(df_rain_res.iloc[:,i+2].values) #sort monthly rain from smallest to largest
        pdf = np.zeros(len(sorted_rain_res))+ (1/len(sorted_rain_res)) #1/100years
        cdf = np.cumsum(pdf)  #compute CDF
        #b) compute CDF curve from the WGEN-generated
        sorted_rain_gen = np.sort(df_rain2.iloc[:,i+1].values) #sort monthly rain from smallest to largest
        index_rain_gen = np.argsort(df_rain2.iloc[:,i+1].values) #** argsort - returns the original indexes of the sorted array
        pdf2 = np.zeros(len(sorted_rain_gen))+ (1/len(sorted_rain_gen)) #1/100years
        cdf2 = np.cumsum(pdf2)
        #c) CDF matching for bias correction
        # corrected_rain=np.interp(cdf2,cdf,sorted_rain_res,left=0.0)# 100 WGEN outputs to CDF of 500 resampled based on SCF
        corrected_rain=np.interp(cdf2,cdf,sorted_rain_res,left=0.1)# EJ(6/25/2021) lower limit is 0.1 not 0 to avoid 0 monthly correction factor.
        # ====================================================================
        # # # ===========       comment out later!!!!  check
        # #a) compute CDF curve from the climatology
        # if i > 4 and i < 9:
        #     sorted_rain_obs = np.sort(df_rain.iloc[:,i+1].values) #sort monthly rain from smallest to largest
        #     pdf_obs = np.zeros(len(sorted_rain_obs))+ (1/len(sorted_rain_obs)) #1/100years
        #     cdf_obs = np.cumsum(pdf_obs)  #compute CDF

        #     fig = plt.figure()
        #     fig.suptitle('Bias correction of monthly rain for month {}'.format(i+1))
        #     ax = fig.add_subplot(111)
        #     ax.set_xlabel('Monthly total rain [mm]') #,fontsize=14)
        #     ax.set_ylabel('CDF',fontsize=14)
        #     ax.plot(sorted_rain_gen,cdf2, 'g--*',label='gen')
        #     ax.plot(corrected_rain,cdf2, 'r--o',label='LF_cor')
        #     ax.plot(sorted_rain_res,cdf, 'b--^',label='res')
        #     ax.plot(sorted_rain_obs,cdf_obs, 'k--^',label='climatology')
        #     legend = ax.legend(loc='lower right', shadow=True, fontsize='large')
        #     plt.show()
        #=================================================================
        #=== 2) Tmin
        sorted_tmin_res = np.sort(df_tmin_res.iloc[:,i+2].values)
        pdf = np.zeros(len(sorted_tmin_res))+ (1/len(sorted_tmin_res)) 
        cdf = np.cumsum(pdf)  #compute CDF
        #b) compute CDF curve from the WGEN-generated
        sorted_tmin_gen = np.sort(df_tmin2.iloc[:,i+1].values)
        index_tmin_gen = np.argsort(df_tmin2.iloc[:,i+1].values) #** argsort - returns the original indexes of the sorted array
        pdf2 = np.zeros(len(sorted_tmin_gen))+ (1/len(sorted_tmin_gen)) 
        cdf2 = np.cumsum(pdf2)  #compute CDF
        #c) CDF matching for bias correction
        corrected_tmin=np.interp(cdf2,cdf,sorted_tmin_res) 

        # ====================================================================
        # # ===========       comment out later!!!!  check
        # #a) compute CDF curve from the climatology
        # sorted_tmin_obs = np.sort(df_tmin.iloc[:,i+2].values) #sort monthly rain from smallest to largest
        # pdf = np.zeros(len(sorted_tmin_obs))+ (1/len(sorted_tmin_obs)) #1/100years
        # cdf_obs = np.cumsum(pdf)  #compute CDF

        # fig = plt.figure()
        # fig.suptitle('Bias correction of monthly Tmin for month {}'.format(i+1))
        # ax = fig.add_subplot(111)
        # ax.set_xlabel('Monthly Avg. Tmin') #,fontsize=14)
        # ax.set_ylabel('CDF',fontsize=14)
        # ax.plot(sorted_tmin_gen,cdf2, 'g--*',label='gen')
        # ax.plot(corrected_tmin,cdf2, 'r--o',label='LF_cor')
        # ax.plot(sorted_tmin_res,cdf, 'b--^',label='resampling')
        # ax.plot(sorted_tmin_obs,cdf_obs, 'k--^',label='climatology')
        # legend = ax.legend(loc='lower right', shadow=True, fontsize='large')
        # plt.show()
        #=================================================================
        #=== 3) Tmax
        sorted_tmax_res = np.sort(df_tmax_res.iloc[:,i+2].values)
        pdf = np.zeros(len(sorted_tmax_res))+ (1/len(sorted_tmax_res)) 
        cdf = np.cumsum(pdf)  #compute CDF
        #b) compute CDF curve from the WGEN-generated
        sorted_tmax_gen = np.sort(df_tmax2.iloc[:,i+1].values)
        index_tmax_gen = np.argsort(df_tmax2.iloc[:,i+1].values) #** argsort - returns the original indexes of the sorted array
        pdf2 = np.zeros(len(sorted_tmax_gen))+ (1/len(sorted_tmax_gen)) 
        cdf2 = np.cumsum(pdf2)  #compute CDF
        #c) CDF matching for bias correction
        corrected_tmax=np.interp(cdf2,cdf,sorted_tmax_res) 
        
        # # ====================================================================
        # # # ===========       comment out later!!!!  check
        # fig = plt.figure()
        # fig.suptitle('Bias correction of monthly Tmax for month {}'.format(i+1))
        # ax = fig.add_subplot(111)
        # ax.set_xlabel('Monthly Avg. Tmax') #,fontsize=14)
        # ax.set_ylabel('CDF',fontsize=14)
        # ax.plot(sorted_tmax_gen,cdf2, 'g--*',label='gen')
        # ax.plot(corrected_tmax,cdf2, 'r--o',label='LF_cor')
        # ax.plot(sorted_tmax_res,cdf, 'b--^',label='obs')
        # legend = ax.legend(loc='lower right', shadow=True, fontsize='large')
        # plt.show()
        #=================================================================
        #=== 4) SRad
        sorted_srad_res = np.sort(df_srad_res.iloc[:,i+2].values)
        pdf = np.zeros(len(sorted_srad_res))+ (1/len(sorted_srad_res)) 
        cdf = np.cumsum(pdf)  #compute CDF
        #b) compute CDF curve from the WGEN-generated
        sorted_srad_gen = np.sort(df_srad2.iloc[:,i+1].values)
        index_srad_gen = np.argsort(df_srad2.iloc[:,i+1].values) #** argsort - returns the original indexes of the sorted array
        pdf2 = np.zeros(len(sorted_srad_gen))+ (1/len(sorted_srad_gen)) 
        cdf2 = np.cumsum(pdf2)  #compute CDF
        #c) CDF matching for bias correction
        corrected_srad=np.interp(cdf2,cdf,sorted_srad_res) 

        # ====================================================================
        # # ===========       comment out later!!!!  check
        # fig = plt.figure()
        # fig.suptitle('Bias correction of monthly srad for month {}'.format(i+1))
        # ax = fig.add_subplot(111)
        # ax.set_xlabel('Monthly Avg. srad') #,fontsize=14)
        # ax.set_ylabel('CDF',fontsize=14)
        # ax.plot(sorted_srad_gen,cdf2, 'g--*',label='gen')
        # ax.plot(corrected_srad,cdf2, 'r--o',label='LF_cor')
        # ax.plot(sorted_srad_res,cdf, 'b--^',label='obs')
        # legend = ax.legend(loc='lower right', shadow=True, fontsize='large')
        # plt.show()
        #=================================================================
        #save monthly correction factors to dataframe
        sorted_rain_gen[sorted_rain_gen == 0.0] = 0.1  #replace 0 with 0.1 to avoid dividing by zero
        # corrected_rain[corrected_rain == 0.0] = 0.1  ## EJ(6/25/2021) lower limit is 0.1 not 0 to avoid 0 monthly correction factor.
        df_rain_cf.iloc[index_rain_gen,i+1] = np.divide(corrected_rain,sorted_rain_gen)  #100 by 12
        df_srad_cf.iloc[index_srad_gen,i+1] = np.subtract(corrected_srad,sorted_srad_gen)
        df_tmin_cf.iloc[index_tmin_gen,i+1] = np.subtract(corrected_tmin,sorted_tmin_gen)
        df_tmax_cf.iloc[index_tmax_gen,i+1] = np.subtract(corrected_tmax,sorted_tmax_gen)

    # print (time.process_time() - start_time, "sec elapsed until monthly correction")
    #5)Write the bias-corrected daily output into a dataframe
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
                rain_d_cf = np.tile(df_rain_cf.iloc[j,i+1],(numday,1))  #np.tile(a, 2)  
                srad_d_cf = np.tile(df_srad_cf.iloc[j,i+1],(numday,1))  
                tmin_d_cf = np.tile(df_tmin_cf.iloc[j,i+1],(numday,1)) 
                tmax_d_cf = np.tile(df_tmax_cf.iloc[j,i+1],(numday,1)) 
            else:
                rain_d_cf = np.concatenate((rain_d_cf, np.tile(df_rain_cf.iloc[j,i+1],(numday,1))),axis=0) 
                srad_d_cf = np.concatenate((srad_d_cf, np.tile(df_srad_cf.iloc[j,i+1],(numday,1))),axis=0)
                tmin_d_cf = np.concatenate((tmin_d_cf, np.tile(df_tmin_cf.iloc[j,i+1],(numday,1))),axis=0)
                tmax_d_cf = np.concatenate((tmax_d_cf, np.tile(df_tmax_cf.iloc[j,i+1],(numday,1))),axis=0)
    # print (time.process_time() - start_time, "sec elapsed until making 1-dim corrction factor")

    df_cor = pd.DataFrame(np.zeros((gen_yrs*Gndays, 7)))   #4 matrix [3 by 3]
    df_cor.columns = ['iyear', 'YEAR','DOY','SRAD','TMAX','TMIN','RAIN']  #iyear => ith year
    df_cor.name = 'WGEN_LFcorr_out_'+str(target_year)
    #save the corrected generated data into a dataframe 
    df_cor.iyear.iloc[:] = df_gen.iyear.iloc[:]
    df_cor.YEAR.iloc[:] = df_gen.YEAR.iloc[:]
    df_cor.DOY.iloc[:] = df_gen.DOY.iloc[:]
    df_cor.RAIN.iloc[:] = np.multiply(df_gen.RAIN.values, rain_d_cf.flatten())
    df_cor.SRAD.iloc[:] = np.add(df_gen.SRAD.values, srad_d_cf.flatten())
    df_cor.TMAX.iloc[:] = np.add(df_gen.TMAX.values, tmax_d_cf.flatten())
    df_cor.TMIN.iloc[:] = np.add(df_gen.TMIN.values, tmin_d_cf.flatten())

    #write dataframe into CSV file
    fname = path.join(Wdir_path, df_cor.name + '.csv') 
    df_cor.to_csv(fname, index=False)
    del rain_d_cf; del srad_d_cf; del tmin_d_cf; del tmax_d_cf
    return df_cor
    # print (time.process_time() - start_time, "sec elapsed until finishing Tmax,Tmin, Srad generation")
