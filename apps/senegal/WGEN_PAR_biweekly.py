#Author: Eunjin Han
#Institute: IRI-Columbia University
#Date: 11/25/2018
#Objective: Make a program to estimate parameters for Gamma rainfall model and two-state first-order Markov chain
#Procedures:
##1) Compute transition probability of Markov chain for each month
##2) Compute alpha (shape) and beba (scale paramter) of Gamma distribution rainfall model for each month

##* Make a Python program to generate (a) [A] and [B] matrix, (b) compute auto-/cross-correlation for M0 and M1 matrix
##1) Long-term daily weather data (*.data)
##2) Compute long-term daily mean and stdev => compute daily 'residuals'
##   In addition, check if the residuals are normally distribute on which first-order linear autoregressive model works
##3) Compute auto- and serial-correlations between variables
##4) Compute [A] and [B]
##5) Write the elements of [A] and [B] into a text files which is an input of WGEN.
##5-1) Compute MONTHLY mean and stdev of each variable as a reference before shift (CDF matching) based on SCF
##==============
##NOTE: here I assume that *.WTD file has data from doy = 1 to doy = 365
##==============
import numpy as np
# import matplotlib.pyplot as plt
# import math
# import calendar
from scipy import stats
from scipy.stats import kurtosis, skew
from numpy.linalg import inv
from scipy.stats import gamma
import pandas as pd
from scipy.optimize import curve_fit
from optparse import OptionParser
import sys
import os
from os import path # path
from apps.ethiopia.exp_mixture_model import EMM, EMMs  
from exp_mixture_model import EMM, EMMs  
from exp_mixture_model import generate_emm 

def progressbar(it, prefix="", size=60, file=sys.stdout):
    #https://stackoverflow.com/questions/3160699/python-progress-bar
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

#Fourier series with one harmonic
def func1(x, Ubar, C, T):
    # y=[]
    # for i in range(x.shape[0]):
    #     #y.append(Ubar + C*math.cos(0.0172*x[i]-0.0172*T))
    #     y.append(Ubar + C*math.cos(0.0172*x[i]+T))
    #     y_array = np.asarray(y)
    # return y_array
  #return C*math.cos(0.0172*(x-T))+Ubar
    tau = 2*np.pi/365 #tau = 0.0172      T = 365/(2*pi)
    return Ubar + C*np.cos(1*tau*x + T) 
#=================================================================
#Fourier series with two harmonics
def func2(x, Ubar, C1, T1, C2, T2):
    tau = 2*np.pi/365 #tau = 0.0172      T = 365/(2*pi)
    return Ubar + C1*np.cos(1*tau*x + T1)+ C2*np.cos(2*tau*x + T2)

#=================================================================
#=================================================================
# #rainfall transition model - second-order Markov chain 
def MC_transition2(PnP, nyear, nday):
#credit: Jie Chen https://www.mathworks.com/matlabcentral/fileexchange/29136-stochastic-weather-generator-weagets
# % This function calculates the transition matrix [a] from a time series of daily precipitation.  
# The output matrix has a dimension a(8,nday), where nday is the number of days analyzed in a calendar year (usually 365).  
# % The elements of the matrices are as follow
# %    a(1,:) correspond to a000
# %    a(2,:) correspond to a001
# %    a(3,:) correspond to a010
# %    a(4,:) correspond to a011
# %    a(5,:) correspond to a100
# %    a(6,:) correspond to a101
# %    a(7,:) correspond to a110
# %    a(8,:) correspond to a111
# %
# % to calculate the transitions from state i on day n-2 and n-1 to state j on day n
# % a matrix PnPp is produced from PnP by shifting the columns to the right
# % and a matrix PnPpp is produced from PnPp by shifting the columns to the right.
# % rsults will be accurate if D is equal to 365.  There is a lost in accuracy
# % if D is smaller than 365
    PnPp = np.copy(PnP)
    PnPpp = np.copy(PnP)
    PnPp[:,1:nday] = PnP[:,0:nday-1]
    PnPp[1:nyear,0] = PnP[0:nyear-1,nday-1]

    PnPpp[:,1:nday] = PnPp[:,0:nday-1]
    PnPpp[1:nyear,0] = PnPp[0:nyear-1,nday-1]

    a000=np.zeros((nyear,nday)) 
    a001=np.zeros((nyear,nday))
    a010=np.zeros((nyear,nday))
    a011=np.zeros((nyear,nday))
    a100=np.zeros((nyear,nday))
    a101=np.zeros((nyear,nday))
    a110=np.zeros((nyear,nday))
    a111=np.zeros((nyear,nday))

    a000[(PnP==0) & (PnPp==0) & (PnPpp==0)]=1
    a001[(PnP==1) & (PnPp==0) & (PnPpp==0)]=1
    a010[(PnP==0) & (PnPp==1) & (PnPpp==0)]=1
    a011[(PnP==1) & (PnPp==1) & (PnPpp==0)]=1
    a100[(PnP==0) & (PnPp==0) & (PnPpp==1)]=1
    a101[(PnP==1) & (PnPp==0) & (PnPpp==1)]=1
    a110[(PnP==0) & (PnPp==1) & (PnPpp==1)]=1
    a111[(PnP==1) & (PnPp==1) & (PnPpp==1)]=1

    a = np.empty((8,nday,)) * np.nan
    a[0,:] = np.sum(a000, axis=0)
    a[1,:] = np.sum(a001, axis=0)
    a[2,:] = np.sum(a010, axis=0)
    a[3,:] = np.sum(a011, axis=0)
    a[4,:] = np.sum(a100, axis=0)
    a[5,:] = np.sum(a101, axis=0)
    a[6,:] = np.sum(a110, axis=0)
    a[7,:] = np.sum(a111, axis=0)
    return a

#========================================================================
def WGEN_PAR_biweekly(target_year,rain_array, Tmin_array, Tmax_array, srad_array,Wdir_path): 
    #=================================================================
    #====================================================================
    #1) Read daily observations into a matrix (note: Feb 29th was skipped)
    #====================================================================
    #====================================================================
    #2) Compute transition probability of Markov chain for each month
    #====================================================================
    n14=int(np.floor(365/14))  #number of biweeks in a year
    #make an dataframe to save the estimated parameters for each month
    #rows for monthly rainfall parameters (p000,p001..., (8) alpha, beta1, beta2(3)), cols for months
    df = pd.DataFrame(np.zeros((12, n14)))   #26 bi-weeks
    df.columns = ['bw1','bw2','bw3','bw4','bw5','bw6','bw7','bw8','bw9','bw10','bw11','bw12','bw13','bw14','bw15','bw16','bw17','bw18','bw19','bw20','bw21','bw22','bw23','bw24','bw25','bw26']
    df.index =  ['P000','P001', 'P010','P011','P100', 'P101','P110', 'P111', 'alpha1', 'alpha2','beta1','beta2']
    df.name = 'Rain_param_W2_'+str(target_year)

    #======= generate matrix of precip - no precip (PnP)
    P_threshold = 1 # EJ(7/11/2011)   0.1 #mm/day
    PnP = np.copy(rain_array) 
    PnP[rain_array < P_threshold] = 0 #dry day
    PnP[rain_array >= P_threshold] = 1 #wet day

    # % adjust precipitation to threshold: substract threshold to precipitation
    # % values so to be able to use the 1-parameter exponential funtion of
    # % 2-parameter gamma funtion.  The threshold will be added back by the generator
    rain_mat = np.copy(rain_array) 
    rain_mat[(rain_array < P_threshold) & (rain_array > 0.0)] = 0 #dry day
    ##rain_mat=np.subtract(rain_mat, P_threshold)  #EJ(7/13/2021) no need => it makes more rain < 1mm and more numbers of input for EMM => more time required.
    rain_mat[rain_mat < 0] = 0 #replace -P_threshold by 0

    # % put NaN for missing values instead of -999
    PnP[rain_array < 0]=np.nan

    #==Compute 2nd order Marcov chain transition
    a = MC_transition2(PnP, rain_array.shape[0], rain_array.shape[1]) # def MC_transition2(PnP, nyear, nday):  => 8 by 365 days

    # % calculate average p00 and p10 using maximum likelihood estimator
    # % on 14-days periods (Woolhiser and Pegram, 1979)
    # %
    #    A000(i)=sum(a(1,14*(i-1)+1:14*i));
    #    A001(i)=sum(a(2,14*(i-1)+1:14*i));
    #    A010(i)=sum(a(3,14*(i-1)+1:14*i));
    #    A011(i)=sum(a(4,14*(i-1)+1:14*i));
    #    A100(i)=sum(a(5,14*(i-1)+1:14*i));
    #    A101(i)=sum(a(6,14*(i-1)+1:14*i));
    #    A110(i)=sum(a(7,14*(i-1)+1:14*i));
    #    A111(i)=sum(a(8,14*(i-1)+1:14*i));
    # ap000=A000./(A001+A000);
    # ap001=1-ap000;
    # ap010=A010./(A010+A011);
    # ap011=1-ap010;
    # ap100=A100./(A101+A100);
    # ap101=1-ap100;
    # ap110=A110./(A110+A111);
    # ap111=1-ap110;
    index1 = [i *14  for i in range(n14)]
    index2 = [(i+1) *14  for i in range(n14)]
    #index for biweekly sum of rainfall transition
    index_w2 = [index1[i // 2] if (i % 2) == 0 else index2[i // 2] for i in range(n14*2)] #[f(x) if condition else g(x) for x in sequence]
    # print(index_w2)  #check  [0,14,   14,28,   28,42,   42,56,   56,70,   70,84,
    A_mat = np.add.reduceat(a, index_w2, axis = 1)[:,::2] #ufunc.reduceat(a, indices, axis=0, dtype=None, out=None)
    # print(A_mat)  #[8 by 26]
    # print(A_mat.shape)

    ap000=A_mat[0,:]/(A_mat[1,:]+A_mat[0,:])         #A000./(A001+A000);
    ap001=1-ap000   #dry -> dry -> wet
    ap010=A_mat[2,:]/(A_mat[2,:]+A_mat[3,:])          #A010./(A010+A011);
    ap011=1-ap010
    ap100=A_mat[4,:]/(A_mat[5,:]+A_mat[4,:])          #A100./(A101+A100);
    ap101=1-ap100
    ap110=A_mat[6,:]/(A_mat[6,:]+A_mat[7,:])          #A110./(A110+A111);
    ap111=1-ap110

    #save transition probability into a dataframe
    ap000[np.isnan(ap000)]=0.001  #replace nan with 0.001 => nan resulted due to dry season !check!!!
    ap001[np.isnan(ap001)]=0.001 
    ap010[np.isnan(ap010)]=0.001 
    ap011[np.isnan(ap011)]=0.001 
    ap100[np.isnan(ap100)]=0.001 
    ap101[np.isnan(ap101)]=0.001 
    ap110[np.isnan(ap110)]=0.001 
    ap111[np.isnan(ap111)]=0.001 

    df.iloc[0] = ap000        #A000./(A001+A000);    iloc => implicit indexing
    df.iloc[1] = ap001   #dry -> dry -> wet
    df.iloc[2] = ap010          #A010./(A010+A011);
    df.iloc[3] = ap011
    df.iloc[4] = ap100         #A100./(A101+A100);
    df.iloc[5] = ap101
    df.iloc[6] = ap110       #A110./(A110+A111);
    df.iloc[7] = ap111


    #====================================================================
    #3) Compute parameters of mixed exponential distribution for rainfall amount simulation
    #====================================================================
    # %  we now process the precipitation amounts
    # %  an exponential distribution (Richardson, 1981), or a 2-parameter Gamma
    # %  distribution is usede
    # %
    # %  we first create a precipitation matrice containing positive
    # % precipitation amounts when precipitation has been recorded and
    # % zero values (when there is no precipitation or when data is missing)
    # % otherwise.  This requires to replace NaN values in PnP matrice
    # % by 0 values.  Position of NaN values in vector kn
    # % 
    PnP[np.isnan(PnP)]=0   #PnP(kn)=0;  %[kn]=find(P<0);
    PP = np.multiply(rain_mat, PnP)  #PP=P.*PnP;
    # sPtot=np.sum(PP, axis=0)    #sum(PP); %total precipitation amounts on given calendar day for all years analysed
    # stot=np.sum(PnP, axis=0)    # sum(PnP); % # of days with precip. on a given calendar day for all years analysed

    emm = EMM(2)    #emm = EMM(options.k)   check!
        #   if options.criterion not in [None, "marginal_log_likelihood", "joint_log_likelihood",
        #                                "AIC", "BIC", "AIC_LVC", "BIC_LVC", "NML_LVC", "DNML"]:
    # #fitting EMM (Exponential Mixture Model)
    # # emm.fit(x)
    # pi, mu = emm.fit(x)
    # # print results
    # emm.print_result()
    # pi, mu = [emm.fit(PP[:,i*14:(i+1)*14].flatten()) for i in range(n14)] #pi=mixing probaibility, mu = mean of the ith component of a hyperexponential rainfall distribution

    par = np.empty((4,n14,)) * np.nan
    for i in progressbar(range(n14), "Computing parameters of Mixed Exp Dist: ", 40):
    # for i in range(n14):
        x= PP[:,i*14:(i+1)*14]  #0-14, 14-28, ...
        if len(x[np.nonzero(x)]) == 0:  #no rainfall for 14 days through 30 yrs => cannot estimate rainfall amount model  !check!!
            par[:,i]=-999
        else:
            pi, mu = emm.fit(x[np.nonzero(x)])
            if len(pi)==1:  #in case k_final=1
                par[0,i]=pi[0]  #mixing probility 1 = 1
                par[1,i]=0      #mixing probility 2 = 0
                par[2,i]=mu[0]  #mu1
                par[3,i]=-999 #np.nan
            else:
                par[0,i]=pi[0]  #mixing probility 1
                par[1,i]=pi[1]   #mixing probility 2 => (1-pi1)
                par[2,i]=mu[0]  #mu1
                par[3,i]=mu[1]  #mu2
        # print(pi)
        # print(mu)
        # print("Estimating paramers of mixed exp Rainfall distribution for {0:2d}th biweeks.".format(i+1))

    # Save parameters of mixed exponentional dist into a dataframe
    df.iloc[8] = par[0,:]  #iloc =>implicit indexing
    df.iloc[9] = par[1,:]
    df.iloc[10] = par[2,:]
    df.iloc[11] = par[3,:]

    # #test print for  the first row and all column
    # print( 'Pi_1: {}'.format(df.iloc[8,:]))
    # print( 'Pi_2: {}'.format(df.iloc[9,:]))
    # print( 'mu_1: {}'.format(df.iloc[10,:]))
    # print( 'mu_2: {}'.format(df.iloc[11,:]))

    #write dataframe into CSV file
    fname = path.join(Wdir_path, df.name + '.csv')  
    df.to_csv(fname, index=True)

    ### plot the distributions and fits.  to lazy to do iteration today
    ##plt.hist(rain_month1, bins=40, normed=True)
    ##plt.plot(x, g1, 'r-', linewidth=6, alpha=.6)
    ###ax.annotate(s='shape = %.3f\nloc = %.3f\nscale = %.3f' %(shape1, loc1, scale1), xy=(6,.2))
    ###ax.set_title('gamma fit')
    ##plt.title('MOBA-January (37 yrs of obs)')
    ##
    ##plt.show()
    ##for x in np.arange(0, numberOfRows):
    ##    #loc or iloc both work here since the index is natural numbers
    ##    df.loc[x] = [np.random.randint(-1,1) for n in range(3)]

    #====================================================================
    #4) Compute Fourier coefficients for Tmax, Tmin and SRad for wet and dry days 
    #====================================================================
    #make an dataframe to save the estimated parameters for each month
    # +++rows for Tmax(dry),Tmax(Wet),Tmin(Dry),Tmin(Wet),Srad(dry), Srad(wet),
    # +++and cols for Ubar(mean), C(amplitude), T(position) for MEAN and  Ubaar(mean), C(amplitude), T(position) for STDEV
    df2 = pd.DataFrame(np.zeros((6, 10))) 
    df2.columns = ['mean_M','amp_M1', 'pos_M1','amp_M2', 'pos_M2','mean_STD','amp_STD1', 'pos_STD1','amp_STD2', 'pos_STD2']
    df2.index =  ['Tmax_D','Tmax_W', 'Tmin_D','Tmin_W','Srad_D', 'Srad_W']
    df2.name = 'T_Srad_Fourier_param_'+str(target_year)
    #Separate Dry and Wet days
    Tmin_dry = np.copy(Tmin_array)
    Tmin_wet = np.copy(Tmin_array)
    Tmin_wet[rain_array < P_threshold] = np.nan
    Tmin_dry[rain_array >= P_threshold] = np.nan

    Tmax_dry = np.copy(Tmax_array)
    Tmax_wet = np.copy(Tmax_array)
    Tmax_wet[rain_array < P_threshold] = np.nan
    Tmax_dry[rain_array >= P_threshold] = np.nan

    Srad_dry = np.copy(srad_array)
    Srad_wet = np.copy(srad_array)
    Srad_wet[rain_array < P_threshold] = np.nan
    Srad_dry[rain_array >= P_threshold] = np.nan

    #compute mean and stdev of daily weather data
    Tmin_D_avg=np.nanmean(Tmin_dry, axis=0)
    Tmin_W_avg=np.nanmean(Tmin_wet, axis=0)
    Tmin_D_std=np.nanstd(Tmin_dry, axis=0)
    Tmin_W_std=np.nanstd(Tmin_wet, axis=0)

    Tmax_D_avg=np.nanmean(Tmax_dry, axis=0)
    Tmax_W_avg=np.nanmean(Tmax_wet, axis=0)
    Tmax_D_std=np.nanstd(Tmax_dry, axis=0)
    Tmax_W_std=np.nanstd(Tmax_wet, axis=0)

    Srad_D_avg=np.nanmean(Srad_dry, axis=0)
    Srad_W_avg=np.nanmean(Srad_wet, axis=0)
    Srad_D_std=np.nanstd(Srad_dry, axis=0)
    Srad_W_std=np.nanstd(Srad_wet, axis=0)
    # if np.sum(Srad_D_avg[np.isnan]) > 0 or np.sum(Srad_W_avg[np.isnan]) > 0 or np.sum(Srad_D_std[np.isnan]) > 0 or np.sum(Srad_W_std[np.isnan]) > 0: 
    #     print("SRAD avg/std have nan values")
    #     os.system("pause")

    #Tmax: curve-fitting for average
    xdata = np.asarray(range(1,366))
    ydata_D = Tmax_D_avg[~np.isnan(Tmax_D_avg)]
    xdata_D = xdata[~np.isnan(Tmax_D_avg)] 
    ydata_W = Tmax_W_avg[~np.isnan(Tmax_W_avg)]
    xdata_W = xdata[~np.isnan(Tmax_W_avg)]  #For Jan and Feb, there are too little wet days and thus ther are many nan values in Tmax_W_avg
    popt, pcov = curve_fit(func2, xdata_D, ydata_D)
    popt_W, pcov_W = curve_fit(func2, xdata_W, ydata_W)
    # print('Four coeff: Tmax-mean(dry): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt[0],popt[1],popt[2],popt[3],popt[4]))
    # print('Four coeff: Tmax-mean(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_W[0],popt_W[1],popt_W[2],popt_W[3],popt_W[4]))

    #curve fitting for standard dev
    ydata_D = Tmax_D_std[~np.isnan(Tmax_D_std)]
    xdata_D = xdata[~np.isnan(Tmax_D_std)] 
    ydata_W = Tmax_W_std[~np.isnan(Tmax_W_std)]
    xdata_W = xdata[~np.isnan(Tmax_W_std)]  #For Jan and Feb, there are too little wet days and thus ther are many nan values in Tmax_W_avg
    popts, pcovs = curve_fit(func2, xdata_D, ydata_D)
    popt_Ws, pcov_Ws = curve_fit(func2, xdata_W, ydata_W)
    # print('Four coeff: Tmax-std(dry): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popts[0],popts[1],popts[2],popts[3],popts[4]))
    # print('Four coeff: Tmax-std(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_Ws[0],popt_Ws[1],popt_Ws[2],popt_Ws[3],popt_Ws[4]))

    #Tmin: curve-fitting for average
    ydata_D = Tmin_D_avg[~np.isnan(Tmin_D_avg)]
    xdata_D = xdata[~np.isnan(Tmin_D_avg)] 
    ydata_W = Tmin_W_avg[~np.isnan(Tmin_W_avg)]
    xdata_W = xdata[~np.isnan(Tmin_W_avg)] 
    #return C*math.cos(0.0172*(x-T))+Ubar
    popt2, pcov2 = curve_fit(func2, xdata_D, ydata_D)
    popt_W2, pcov_W2 = curve_fit(func2, xdata_W, ydata_W)
    #print Fourier coefficients
    # print('Four coeff: Tmin-mean(dry): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt2[0],popt2[1],popt2[2],popt2[3],popt2[4]))
    # print('Four coeff: Tmin-mean(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_W2[0],popt_W2[1],popt_W2[2],popt_W2[3],popt_W2[4]))
    #curve fitting for standard dev
    ydata_D = Tmin_D_std[~np.isnan(Tmin_D_std)]
    xdata_D = xdata[~np.isnan(Tmin_D_std)] 
    ydata_W = Tmin_W_std[~np.isnan(Tmin_W_std)]
    xdata_W = xdata[~np.isnan(Tmin_W_std)] 
    popt3, pcov3 = curve_fit(func2, xdata_D, ydata_D)
    popt_W3, pcov_W3 = curve_fit(func2, xdata_W, ydata_W)
    #print Fourier coefficients
    # print('Four coeff: Tmin-std(dry): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt3[0],popt3[1],popt3[2],popt3[3],popt3[4]))
    # print('Four coeff: Tmin-std(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_W3[0],popt_W3[1],popt_W3[2],popt_W3[3],popt_W3[4]))

    #Srad: curve-fitting for average
    ydata_D = Srad_D_avg[~np.isnan(Srad_D_avg)]
    xdata_D = xdata[~np.isnan(Srad_D_avg)]
    ydata_W = Srad_W_avg[~np.isnan(Srad_W_avg)]
    xdata_W = xdata[~np.isnan(Srad_W_avg)]
    #return C*math.cos(0.0172*(x-T))+Ubar
    popt4, pcov4 = curve_fit(func2, xdata_D, ydata_D)
    popt_W4, pcov_W4 = curve_fit(func2, xdata_W, ydata_W)
    #print Fourier coefficients
    # print('Four coeff: Srad-mean(dry): UUbar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt4[0],popt4[1],popt4[2],popt4[3],popt4[4]))
    # print('Four coeff: Srad-mean(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_W4[0],popt_W4[1],popt_W4[2],popt_W4[3],popt_W4[4]))
    #curve fitting for standard dev
    ydata_D = Srad_D_std[~np.isnan(Srad_D_std)]
    xdata_D = xdata[~np.isnan(Srad_D_std)]
    ydata_W = Srad_W_std[~np.isnan(Srad_W_std)]
    xdata_W = xdata[~np.isnan(Srad_W_std)]
    popt5, pcov5 = curve_fit(func2, xdata_D, ydata_D)
    popt_W5, pcov_W5 = curve_fit(func2, xdata_W, ydata_W)
    #print Fourier coefficients
    # print('Four coeff: Srad-std(dry): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt5[0],popt5[1],popt5[2],popt5[3],popt5[4]))
    # print('Four coeff: Srad-std(wet): Ubar ={0:5.3f}, C1 = {1:5.3f}, T1 = {2:5.3f}, C2 = {3:5.3f}, T2 = {4:5.3f}'.format(popt_W5[0],popt_W5[1],popt_W5[2],popt_W5[3],popt_W5[4]))

    #allocate estimated parameters to dataframe
    #Tmax - dry
    df2.mean_M.iloc[[0]] = popt[0]
    df2.amp_M1.iloc[[0]] = popt[1]
    df2.pos_M1.iloc[[0]] = popt[2]
    df2.amp_M2.iloc[[0]] = popt[3]
    df2.pos_M2.iloc[[0]] = popt[4]
    df2.mean_STD.iloc[[0]] = popts[0]
    df2.amp_STD1.iloc[[0]] = popts[1]
    df2.pos_STD1.iloc[[0]] = popts[2]
    df2.amp_STD2.iloc[[0]] = popts[3]
    df2.pos_STD2.iloc[[0]] = popts[4]
    #Tmax - wet
    df2.mean_M.iloc[[1]] = popt_W[0]
    df2.amp_M1.iloc[[1]] = popt_W[1]
    df2.pos_M1.iloc[[1]] = popt_W[2]
    df2.amp_M2.iloc[[1]] = popt_W[3]
    df2.pos_M2.iloc[[1]] = popt_W[4]
    df2.mean_STD.iloc[[1]] = popt_Ws[0]
    df2.amp_STD1.iloc[[1]] = popt_Ws[1]
    df2.pos_STD1.iloc[[1]] = popt_Ws[2]
    df2.amp_STD2.iloc[[1]] = popt_Ws[3]
    df2.pos_STD2.iloc[[1]] = popt_Ws[4]
    #Tmin - dry
    df2.mean_M.iloc[[2]] = popt2[0]
    df2.amp_M1.iloc[[2]] = popt2[1]
    df2.pos_M1.iloc[[2]] = popt2[2]
    df2.amp_M2.iloc[[2]] = popt2[3]
    df2.pos_M2.iloc[[2]] = popt2[4]
    df2.mean_STD.iloc[[2]] = popt3[0]
    df2.amp_STD1.iloc[[2]] = popt3[1]
    df2.pos_STD1.iloc[[2]] = popt3[2]
    df2.amp_STD2.iloc[[2]] = popt3[3]
    df2.pos_STD2.iloc[[2]] = popt3[4]
    #Tmin - wet
    df2.mean_M.iloc[[3]] = popt_W2[0]
    df2.amp_M1.iloc[[3]] = popt_W2[1]
    df2.pos_M1.iloc[[3]] = popt_W2[2]
    df2.amp_M2.iloc[[3]] = popt_W2[3]
    df2.pos_M2.iloc[[3]] = popt_W2[4]
    df2.mean_STD.iloc[[3]] = popt_W3[0]
    df2.amp_STD1.iloc[[3]] = popt_W3[1]
    df2.pos_STD1.iloc[[3]] = popt_W3[2]
    df2.amp_STD2.iloc[[3]] = popt_W3[3]
    df2.pos_STD2.iloc[[3]] = popt_W3[4]

    #SRad - dry
    df2.mean_M.iloc[[4]] = popt4[0]
    df2.amp_M1.iloc[[4]] = popt4[1]
    df2.pos_M1.iloc[[4]] = popt4[2]
    df2.amp_M2.iloc[[4]] = popt4[3]
    df2.pos_M2.iloc[[4]] = popt4[4]
    df2.mean_STD.iloc[[4]] = popt5[0]
    df2.amp_STD1.iloc[[4]] = popt5[1]
    df2.pos_STD1.iloc[[4]] = popt5[2]
    df2.amp_STD2.iloc[[4]] = popt5[3]
    df2.pos_STD2.iloc[[4]] = popt5[4]
    #SRad - wet
    df2.mean_M.iloc[[5]] = popt_W4[0]
    df2.amp_M1.iloc[[5]] = popt_W4[1]
    df2.pos_M1.iloc[[5]] = popt_W4[2]
    df2.amp_M2.iloc[[5]] = popt_W4[3]
    df2.pos_M2.iloc[[5]] = popt_W4[4]
    df2.mean_STD.iloc[[5]] = popt_W5[0]
    df2.amp_STD1.iloc[[5]] = popt_W5[1]
    df2.pos_STD1.iloc[[5]] = popt_W5[2]
    df2.amp_STD2.iloc[[5]] = popt_W5[3]
    df2.pos_STD2.iloc[[5]] = popt_W5[4]

    #write dataframe into CSV file
    fname = path.join(Wdir_path, df2.name + '.csv')  
    df2.to_csv(fname, index=True)

    #verify fourier series with two harmonics
    # C:\Users\Eunjin\IRI\Hybrid_WGEN\Fourier_mean_curvefit_rainy.py
    #====================================================================
    #4)Compute auto/cross correlation between Tmin, Tmax and SRad => [A] and [B] matrix
    #====================================================================
    #Separate Dry and Wet days
    srad_dry = np.copy(srad_array)  #Srad_array => row = num years, col = 365 days
    srad_wet = np.copy(srad_array)
    srad_wet[rain_array < P_threshold] = np.nan
    srad_dry[rain_array >= P_threshold] = np.nan
    Tmax_dry = np.copy(Tmax_array)
    Tmax_wet = np.copy(Tmax_array)
    Tmax_wet[rain_array < P_threshold] = np.nan
    Tmax_dry[rain_array >= P_threshold] = np.nan
    Tmin_dry = np.copy(Tmin_array)
    Tmin_wet = np.copy(Tmin_array)
    Tmin_wet[rain_array < P_threshold] = np.nan
    Tmin_dry[rain_array >= P_threshold] = np.nan

    #4-1) compute long-term mean and stdev of daily weather data separately for dry and wet days
    #====================================================================
    srad_D_avg=np.nanmean(srad_dry, axis=0)
    srad_W_avg=np.nanmean(srad_wet, axis=0)
    srad_D_std=np.nanstd(srad_dry, axis=0)
    srad_W_std=np.nanstd(srad_wet, axis=0)
    Tmax_D_avg=np.nanmean(Tmax_dry, axis=0)
    Tmax_W_avg=np.nanmean(Tmax_wet, axis=0)
    Tmax_D_std=np.nanstd(Tmax_dry, axis=0)
    Tmax_W_std=np.nanstd(Tmax_wet, axis=0)
    Tmin_D_avg=np.nanmean(Tmin_dry, axis=0)
    Tmin_W_avg=np.nanmean(Tmin_wet, axis=0)
    Tmin_D_std=np.nanstd(Tmin_dry, axis=0)
    Tmin_W_std=np.nanstd(Tmin_wet, axis=0)

    #4-2) compute daily residuals separately for dry and wet days
    #====================================================================
    temp = np.subtract(srad_array,srad_D_avg) #dry days
    srad_dry_res = np.divide(temp,srad_D_std)
    srad_dry_res[rain_array >= P_threshold] = np.nan
    temp = np.subtract(srad_array,srad_W_avg)#wet days
    srad_wet_res = np.divide(temp,srad_W_std)
    srad_wet_res[rain_array < P_threshold] = np.nan
    #combine two residual matrix from dry and wet
    srad_res = np.nan_to_num(srad_dry_res) + np.nan_to_num(srad_wet_res)
    #----Tmax
    temp = np.subtract(Tmax_array,Tmax_D_avg) #dry days
    Tmax_dry_res = np.divide(temp,Tmax_D_std)
    Tmax_dry_res[rain_array >= P_threshold] = np.nan
    temp = np.subtract(Tmax_array,Tmax_W_avg)#wet days
    Tmax_wet_res = np.divide(temp,Tmax_W_std)
    Tmax_wet_res[rain_array < P_threshold] = np.nan
    #combine two residual matrix from dry and wet
    Tmax_res = np.nan_to_num(Tmax_dry_res) + np.nan_to_num(Tmax_wet_res)
    #----tmin
    temp = np.subtract(Tmin_array,Tmin_D_avg) #dry days
    Tmin_dry_res = np.divide(temp,Tmin_D_std)
    Tmin_dry_res[rain_array >= P_threshold] = np.nan
    temp = np.subtract(Tmin_array,Tmin_W_avg)#wet days
    Tmin_wet_res = np.divide(temp,Tmin_W_std)
    Tmin_wet_res[rain_array < P_threshold] = np.nan
    #combine two residual matrix from dry and wet
    Tmin_res = np.nan_to_num(Tmin_dry_res) + np.nan_to_num(Tmin_wet_res)

    #4-3) Compute auto- and serial-correlations between variables
    #====================================================================
    #4-3-1) lag-0 cross-correlation
    #temp = np.concatenate((Tmax_res_1D, Tmin_res_1D), axis=0)
    #M_matrix = np.concatenate((temp, srad_res_1D), axis=0)
    # Tmax_res_1D = Tmax_res.reshape((obs_yrs-1)*365)  #here!
    # Tmin_res_1D = Tmin_res.reshape((obs_yrs-1)*365)
    # srad_res_1D = srad_res.reshape((obs_yrs-1)*365)
    Tmax_res_1D = Tmax_res.flatten()
    Tmin_res_1D = Tmin_res.flatten()
    srad_res_1D = srad_res.flatten()

    temp = np.vstack((Tmax_res_1D, Tmin_res_1D))
    M0_matrix = np.vstack((temp, srad_res_1D))
    #--**-- lag 0 cross-correation between variables
    M0 = np.corrcoef(M0_matrix) #Each row of x represents a variable, and each column a single observation of all those variables.

    #4-3-2) lag-1 serial correlation for variable j
    M1_matrix = np.empty((3,3))*np.nan #initialize
    temp = np.vstack((Tmax_res_1D[:-1], Tmax_res_1D[1:]))
    M1_matrix[0][0] = np.corrcoef(temp)[0][1]
    temp = np.vstack((Tmin_res_1D[:-1], Tmin_res_1D[1:]))
    M1_matrix[1][1] = np.corrcoef(temp)[0][1]
    temp = np.vstack((srad_res_1D[:-1], srad_res_1D[1:]))
    M1_matrix[2][2] = np.corrcoef(temp)[0][1]

    #4-3-3) lag-1 cross correlation for variable j
    # rho(j,k) is the cross correlation between variable j and k with variable k lagged 1 day with respect to variable j
    temp = np.vstack((Tmax_res_1D[1:], Tmin_res_1D[:-1]))
    M1_matrix[0][1] = np.corrcoef(temp)[0][1]
    temp = np.vstack((Tmax_res_1D[:-1], srad_res_1D[1:]))
    M1_matrix[0][2] = np.corrcoef(temp)[0][1]

    temp = np.vstack((Tmin_res_1D[1:], Tmax_res_1D[:-1]))
    M1_matrix[1][0] = np.corrcoef(temp)[0][1]
    temp = np.vstack((Tmin_res_1D[:-1], srad_res_1D[1:]))
    M1_matrix[1][2] = np.corrcoef(temp)[0][1]

    temp = np.vstack((srad_res_1D[1:], Tmax_res_1D[:-1]))
    M1_matrix[2][0] = np.corrcoef(temp)[0][1]
    temp = np.vstack((srad_res_1D[:-1], Tmin_res_1D[1:]))
    M1_matrix[2][1] = np.corrcoef(temp)[0][1]

    #4-4) Compute [A] and [B]
    #====================================================================
    # print(np.linalg.det(M0))
    invM0=inv(M0)
    A=np.matmul(M1_matrix, invM0)

    temp = np.matmul(A, np.transpose(M1_matrix))
    BBT = M0-temp  #B*B.T
    # print( 'B*B_T: {}'.format(BBT))
    #test Cholesky decomposition
    L = np.linalg.cholesky(BBT)  #=> [B] matrix
    #print np.dot(L, L.T)  ## verify that L * L.T = A
    # print( 'L*L_T{}'.format(np.dot(L, L.T)))

    #save dataframe into a csv file
    df3 = pd.DataFrame(np.zeros((12, 3)))   #4 matrix [3 by 3]
    df3.columns = ['C1','C2','C3']
    df3.index =  ['M0_1','M0_2','M0_3','M1_1','M1_2','M1_3','A_1','A_2','A_3', 'B_1','B_2','B_3']
    df3.name = 'A_B_autocorr_'+str(target_year)
    df3.iloc[0:3,0:3]=M0
    df3.iloc[3:6,0:3]=M1_matrix
    df3.iloc[6:9,0:3]=A
    df3.iloc[9:12,0:3]=L
    #write dataframe into CSV file
    fname = path.join(Wdir_path, df3.name + '.csv')  
    df3.to_csv(fname, index=True)



