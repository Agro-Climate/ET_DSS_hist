#Author: Eunjin Han
#Institute: IRI-Columbia University
#Date: 10/6/2020
#Objective: Generate daily weather (rain, Tmax, Tmin, Srad) based on the parameters estimated by WGEN_PAR_biweekly.py
#Procedures:
##1) 
##==============
##NOTE: 
##==============
import numpy as np
import calendar
import pandas as pd
import os
from os import path 
# from apps.ethiopia.exp_mixture_model import EMM, EMMs  
# from apps.ethiopia.exp_mixture_model import generate_emm
# from exp_mixture_model import EMM, EMMs
# from exp_mixture_model import generate_emm
from exp_mixture_model import EMM, EMMs  
from exp_mixture_model import generate_emm 

#=================================================================
#Fourier series with two harmonics
def func2(x, Ubar, C1, T1, C2, T2):
    tau = 2*np.pi/365 #tau = 0.0172      T = 365/(2*pi)
    return Ubar + C1*np.cos(1*tau*x + T1)+ C2*np.cos(2*tau*x + T2)


#========================================================================
def WGEN_generator(target_year,Gnyears,Wdir_path):  #Gnyears = number of years to generate
#=================================================================
    col_namelist = ['index','bw1','bw2','bw3','bw4','bw5','bw6','bw7','bw8','bw9','bw10','bw11','bw12','bw13','bw14','bw15','bw16','bw17','bw18','bw19','bw20','bw21','bw22','bw23','bw24','bw25','bw26']
    fname = path.join(Wdir_path,'Rain_param_W2_'+str(target_year)+'.csv') 
    if not os.path.exists(fname):
        print( '**Error!!- Rain_param_W2.csv does not exist!')
        os.system('pause')
    df_rain = pd.read_csv(fname, names=col_namelist, index_col='index', header=None,skiprows=[0])

    if calendar.isleap(target_year):
        Gndays = 366
    else:
        Gndays = 365

    p000 = df_rain.iloc[0].to_numpy()  #series to numpy array
    p010 = df_rain.iloc[2].to_numpy()
    p100 = df_rain.iloc[4].to_numpy()
    p110 = df_rain.iloc[6].to_numpy()

    n14=int(np.floor(365/14))  #number of biweeks in a year
    nday14 = 14 #days per bi-week
    #% extend the parameter value to every day (the length of simulated series)
    # # # p000_mat = [np.tile(p000[i],(Gnyears, 14)) for i in range(n14)]  xx
    # # # p000_mat = [np.concatenate((p000_mat[i],p000_mat[i+1]), axis=1) for i in range(n14)]  xx
    #initial : the first two-week
    p000_mat = np.tile(p000[0],(Gnyears, nday14))  ##np.tile => Construct an array by repeating A the number of times given by reps.
    p010_mat = np.tile(p010[0],(Gnyears, nday14))
    p100_mat = np.tile(p100[0],(Gnyears, nday14))
    p110_mat = np.tile(p110[0],(Gnyears, nday14))

    for i in range(1,n14):
        p000_mat = np.concatenate((p000_mat, np.tile(p000[i],(Gnyears, nday14))),axis=1)
        p010_mat = np.concatenate((p010_mat, np.tile(p010[i],(Gnyears, nday14))),axis=1)
        p100_mat = np.concatenate((p100_mat, np.tile(p100[i],(Gnyears, nday14))),axis=1)
        p110_mat = np.concatenate((p110_mat, np.tile(p110[i],(Gnyears, nday14))),axis=1)

    #fill DOY=365 with the value of DOY=364
    p000_mat = np.pad(p000_mat, [(0, 0), (0, 1)], 'edge')  #pad only right end
    p010_mat = np.pad(p010_mat, [(0, 0), (0, 1)], 'edge')
    p100_mat = np.pad(p100_mat, [(0, 0), (0, 1)], 'edge')
    p110_mat = np.pad(p110_mat, [(0, 0), (0, 1)], 'edge')

    if calendar.isleap(target_year):
        p000_mat = np.insert(p000_mat, [28], p000_mat[0,27], axis=1)  #replace value on DOY=29 with value on DOY=28
        p010_mat = np.insert(p010_mat, [28], p010_mat[0,27], axis=1)
        p100_mat = np.insert(p100_mat, [28], p100_mat[0,27], axis=1)
        p110_mat = np.insert(p110_mat, [28], p110_mat[0,27], axis=1)

    p000_1D = p000_mat.flatten()
    p010_1D = p010_mat.flatten()
    p100_1D = p100_mat.flatten()
    p110_1D = p110_mat.flatten()

    del p000_mat; del p010_mat; del p100_mat; del p110_mat

    # % generate time series of dry (X=0) and wet (X=1) days
    # % pn is the marginal distribution of X on day n
    # % assume that day 0 is dry.  state=0 when day is dry,  state=1 when day is wet
    # % loop to generate time series

    markov=np.zeros((len(p000_1D),), dtype=int) 
    markov[0]=0  #    % start by assuming two consecutive dry days
    markov[1]=0 #
    for i in range(0, (len(p000_1D)-3)):
        Ru = np.random.uniform(0,1,1)  #numpy.random.uniform(low=0.0, high=1.0, size=None), Draw samples from a uniform distribution.
        if markov[i] ==0 and markov[i+1] == 0:
            Pr = p000_1D[i+2]
        elif markov[i] ==0 and markov[i+1] > 0:
            Pr = p010_1D[i+2]
        elif markov[i] > 0 and markov[i+1] == 0:
            Pr = p100_1D[i+2]
        elif markov[i] > 0 and markov[i+1] > 0:
            Pr = p110_1D[i+2]

        # % establish if day i is dry or wet
        if Ru <= Pr:   #% dry day
            markov[i+2] = 0
        else:  #% wet day
            markov[i+2] = 1
    markov[-1]=0 #assume last element = dry
        
    del p000_1D; del p010_1D; del p100_1D; del p110_1D

    #=======================================================
    #======================================================
    #% extend the parameter value for rain amount simuatoin to every day (the length of simulated series)
    alpha1 = df_rain.iloc[8].to_numpy()  #mixing weight (1)
    beta1 = df_rain.iloc[10].to_numpy()  # mean of the jth exponential distribution(1)
    beta2 = df_rain.iloc[11].to_numpy()  # mean of the jth exponential distribution(2)
    alpha1_mat = np.tile(alpha1[0],(Gnyears, nday14))
    beta1_mat = np.tile(beta1[0],(Gnyears, nday14))
    beta2_mat = np.tile(beta2[0],(Gnyears, nday14))

    for i in range(1,n14):
        alpha1_mat = np.concatenate((alpha1_mat, np.tile(alpha1[i],(Gnyears, nday14))),axis=1)
        beta1_mat = np.concatenate((beta1_mat, np.tile(beta1[i],(Gnyears, nday14))),axis=1)
        beta2_mat = np.concatenate((beta2_mat, np.tile(beta2[i],(Gnyears, nday14))),axis=1)
    #fill DOY=365 with the value of DOY=364
    alpha1_mat = np.pad(alpha1_mat, [(0, 0), (0, 1)], 'edge')
    beta1_mat = np.pad(beta1_mat, [(0, 0), (0, 1)], 'edge')
    beta2_mat = np.pad(beta2_mat, [(0, 0), (0, 1)], 'edge')

    if calendar.isleap(target_year):
        alpha1_mat = np.insert(alpha1_mat, [28], alpha1_mat[0,27], axis=1) #replace value on DOY=29 with value on DOY=28
        beta1_mat = np.insert(beta1_mat, [28], beta1_mat[0,27], axis=1)
        beta2_mat = np.insert(beta2_mat, [28], beta2_mat[0,27], axis=1)

    alpha1_1D = alpha1_mat.flatten()
    beta1_1D = beta1_mat.flatten()
    beta2_1D = beta2_mat.flatten()

    del alpha1_mat; del beta1_mat; del beta2_mat

    nw = np.sum(markov)  #number of wet days 
    wd_index = np.where(markov == 1)[0]
    rain_gen = np.zeros((len(markov),), dtype=float) 

    #% generate time series of precipitation amounts
    emm = EMM(2)    #emm = EMM(options.k)  Call exp_mixture_model(EMM)
    #source: https://pypi.org/project/exp-mixture-model/#description
    #Maximum likelihood estimation and model selection of EMMs
    # Maximum likelihood estimation and model selection for the exponential mixture model (i.e., mixture of exponential distributions)
    # When you use this code, please cite the following paper:
    # Makoto Okada, Kenji Yamanishi, Naoki Masuda. Long-tailed distributions of inter-event times as mixtures of exponential distributions. arXiv:19xx.xxxxx
    #original script from C:\Users\Eunjin\IRI\Hybrid_WGEN\exp_mixture_model-1.0.0\emmfit.py

    for i in range(nw):
        if alpha1_1D[wd_index[i]] == 1:
            pi = alpha1_1D[wd_index[i]]
            mu = beta1_1D[wd_index[i]]
            rain_gen[wd_index[i]] = generate_emm(1, 1, [pi], [mu])  #pi: mixing weight, mu = mean of the jth exponential distribution
        elif alpha1_1D[wd_index[i]] < 0: #in case rainfall parameter could not be estimated due to strongly dry season in Senegal
            #use numbers from another biweek in the same dry season
            pi = 1.0
            mu = 0.1
            rain_gen[wd_index[i]] = generate_emm(1, 1, [pi], [mu])  #pi: mixing weight, mu = mean of the jth exponential distribution      
        else:
            pi = np.array([alpha1_1D[wd_index[i]], 1-alpha1_1D[wd_index[i]]])  #mixing weights
            mu = np.array([beta1_1D[wd_index[i]], beta2_1D[wd_index[i]]])
            # print('nw {0:d}: pi[0] {1:.3f},pi[1]= {2:.3f},mu[0]= {3:.3f},mu[1]= {4:.3f}'.format(i+1, pi[0],pi[1],mu[0],mu[1]))
            rain_gen[wd_index[i]] = emm.generate(1, pi, mu)  #generated data
         
    # rain_gen = np.reshape(rain_gen, (Gnyears,Gndays))  #========!!!!!!!!!!!!!!!!!!!!!!!!!
    # print (time.process_time() - start_time, "sec elapsed until generating rainfall amount")

    #====================================================================
    # GENERATE TEMPERATURE AND SOLAR RADIATION
    #====================================================================
    #1)Generate the fourier estimates of average and standard deviations of the time series
    #====================================================================
    col_namelist2 = ['index','mean_M','amp_M1', 'pos_M1','amp_M2', 'pos_M2','mean_STD','amp_STD1', 'pos_STD1','amp_STD2', 'pos_STD2']
    fname = path.join(Wdir_path,'T_Srad_Fourier_param_'+str(target_year)+'.csv') 
    if not os.path.exists(fname):
        print( '**Error!!- T_Srad_Fourier_param.csv does not exist!')
        os.system('pause')
    df_Fourier = pd.read_csv(fname, names=col_namelist2, index_col='index', header=None,skiprows=[0])

    col_namelist3 = ['index','C1','C2','C3']

    fname = path.join(Wdir_path,'A_B_autocorr_'+str(target_year)+'.csv') 
    if not os.path.exists(fname):
        print( '**Error!!- A_B_autocorr.csv does not exist!')
        os.system('pause')
    df_AB = pd.read_csv(fname, names=col_namelist3, index_col='index', header=None,skiprows=[0])
    A = df_AB.iloc[6:9].values
    B = df_AB.iloc[9:].values

    popt_TXDa = df_Fourier.iloc[0][0:5].values #row 0 => for Tmax-Dry avg, col 0:5 => Tmax-Dry std
    popt_TXDsd = df_Fourier.iloc[0][5:].values 
    popt_TXWa = df_Fourier.iloc[1][0:5].values #row 1 => for Tmax-wet avg, col 0:5 => Tmax-Wet std
    popt_TXWsd = df_Fourier.iloc[1][5:].values 
    popt_TMDa = df_Fourier.iloc[2][0:5].values #row 2 => for Tmin-Dry avg, col 0:5 => Tmin-Dry std
    popt_TMDsd = df_Fourier.iloc[2][5:].values 
    popt_TMWa = df_Fourier.iloc[3][0:5].values #row 3 => for Tmin-Wet avg, col 0:5 => Tmin-wet std
    popt_TMWsd = df_Fourier.iloc[3][5:].values 
    popt_SDa = df_Fourier.iloc[4][0:5].values #row 4 => for Srad-Dry avg, col 0:5 => Srad-Dry std
    popt_SDsd = df_Fourier.iloc[4][5:].values 
    popt_SWa = df_Fourier.iloc[5][0:5].values #row 5 => for Srad-Wet avg, col 0:5 => Srad-Wet std
    popt_SWsd = df_Fourier.iloc[5][5:].values 

    xdata = np.asarray(range(1,Gndays+1))  
    TmaxD_a = func2(xdata, *popt_TXDa )
    TmaxD_sd = func2(xdata, *popt_TXDsd)
    TmaxW_a = func2(xdata, *popt_TXWa)
    TmaxW_sd = func2(xdata, *popt_TXWsd)
    TminD_a = func2(xdata, *popt_TMDa)
    TminD_sd = func2(xdata, *popt_TMDsd)
    TminW_a = func2(xdata, *popt_TMWa)
    TminW_sd = func2(xdata, *popt_TMWsd)
    SradD_a = func2(xdata, *popt_SDa)
    SradD_sd = func2(xdata, *popt_SDsd)
    SradW_a = func2(xdata, *popt_SWa)
    SradW_sd = func2(xdata, *popt_SWsd)

    k=0
    for i in range(Gnyears):
        # % the means and standard deviations obtained by Fourier time series are conditioned
        # % on the wet or dry status of the day determined by using the Markov chain model
        #one matrix for Tmax, Tmin and Srad for Average
        temp_a = np.empty((3,Gndays,)) * np.nan
        temp_sd = np.empty((3,Gndays,)) * np.nan
        w_days = markov[k:Gndays*(i+1)] #dry=0 and wet = 1
        d_days = 1-w_days  #dry=1 and wet = 0
        #combine both wet and dry days
        temp_a[0,:] = np.multiply(w_days,TmaxW_a) + np.multiply(d_days,TmaxD_a)
        temp_a[1,:] = np.multiply(w_days,TminW_a) + np.multiply(d_days,TminD_a)
        temp_a[2,:] = np.multiply(w_days,SradW_a) + np.multiply(d_days,SradD_a)
        # #one matrix for Tmax, Tmin and Srad for STDEV
        temp_sd[0,:] = np.multiply(w_days,TmaxW_sd) + np.multiply(d_days,TmaxD_sd)
        temp_sd[1,:] = np.multiply(w_days,TminW_sd) + np.multiply(d_days,TminD_sd)
        temp_sd[2,:] = np.multiply(w_days,SradW_sd) + np.multiply(d_days,SradD_sd)
        k=k+Gndays
        if i == 0:
            TTS_a = temp_a
            TTS_sd = temp_sd
        else:
            TTS_a = np.hstack((TTS_a,temp_a))
            TTS_sd = np.hstack((TTS_sd,temp_sd))

    del TmaxW_a; del TmaxD_a; del TminW_a; del TminD_a; del SradW_a; del SradD_a
    del TmaxW_sd; del TmaxD_sd; del TminW_sd; del TminD_sd; del SradW_sd; del SradD_sd
    del markov

    #====================================================================
    #2) Generate time series of residuals (x-mean)/stdev
    # %  Procedure is started by assuming that the residuals are equal to 0
    # %  random component eps is normally distributed N(0,1)
    #====================================================================
    res=np.zeros((3, 1)) #initial residual for three variables
    ksi=np.zeros((3, Gnyears*Gndays))   #residual matrix for all three variables to save

    for i in range (Gnyears*Gndays):
        eps=np.random.standard_normal(size=(3, 1))
        res = np.matmul(A, res) + np.matmul(B, eps)  #matrix product [3 by 3] * [3 by 1]
        ksi[:,i] = np.reshape(res, (3,))

    #====================================================================
    #3) Convert residual to noral Tmax, Tmin and Srad values
    # % The daily values of the three weather variables are found by multiplying the
    # % residuals by the standard deviation and adding the mean
    #====================================================================
    TTS = np.multiply(ksi,TTS_sd) + TTS_a  #[3 by ndays]  #========!!!!!!!!!!!!!!!!!!!!!!!!!
    del TTS_a; del TTS_sd
    #  % insure that Tmin is always smaller than Tmax (diff arbitrarily set up at 1)
    Tmax_gen = TTS[0,:]
    Tmin_gen = TTS[1,:]
    Tmax_gen = [Tmin_gen[i] if Tmax_gen[i] < Tmin_gen[i] else Tmax_gen[i] for i in range(Gnyears*Gndays)] #[f(x) if condition else g(x) for x in sequence]
    Tmin_gen = [Tmax_gen[i] if Tmax_gen[i] < Tmin_gen[i] else Tmin_gen[i] for i in range(Gnyears*Gndays)]
    Srad_gen = TTS[2,:]

    rain_gen = np.reshape(rain_gen, (Gnyears,Gndays))  #========!!!!!!!!!!!!!!!!!!!!!!!!!
    Tmax_gen = np.reshape(Tmax_gen, (Gnyears,Gndays))  #========!!!!!!!!!!!!!!!!!!!!!!!!!
    Tmin_gen = np.reshape(Tmin_gen, (Gnyears,Gndays))  #========!!!!!!!!!!!!!!!!!!!!!!!!!
    Srad_gen = np.reshape(Srad_gen, (Gnyears,Gndays))  #========!!!!!!!!!!!!!!!!!!!!!!!!!

    #save dataframe into a csv file
    df_out = pd.DataFrame(np.zeros((Gnyears*Gndays, 7)))   #4 matrix [3 by 3]
    df_out.columns = ['iyear', 'YEAR','DOY','SRAD','TMAX','TMIN','RAIN']  #iyear => ith year
    df_out.name = 'WGEN_out_'+str(target_year)
    k = 0
    for i in range(Gnyears):
        df_out.iyear.iloc[k:Gndays*(i+1)] = np.tile(i+1,(Gndays,))
        df_out.YEAR.iloc[k:Gndays*(i+1)] = np.tile(target_year,(Gndays,))
        df_out.DOY.iloc[k:Gndays*(i+1)]= np.asarray(range(1,Gndays+1))
        df_out.SRAD.iloc[k:Gndays*(i+1)]= np.transpose(Srad_gen[i,:])
        df_out.TMAX.iloc[k:Gndays*(i+1)]= np.transpose(Tmax_gen[i,:])
        df_out.TMIN.iloc[k:Gndays*(i+1)]= np.transpose(Tmin_gen[i,:])
        df_out.RAIN.iloc[k:Gndays*(i+1)]= np.transpose(rain_gen[i,:])
        k=k+Gndays
    # #write dataframe into CSV file
    # df_out.to_csv(df_out.name + '.csv', index=False)
    del rain_gen; del Tmax_gen; del Tmin_gen; del Srad_gen
    return df_out
