from cmath import nan
import os
import numpy as np
import matplotlib.pyplot as plt

#set directory name
directory = 'matrix_list'

#initialize temperature and rate arrays
t9 = np.empty(0)
l_21_eff = np.empty(0)

#main loop. This will read each file in the directory, read in the Transfer matrix data and perform the necessary calculations
#to calculate the effective rate lambda_21

for filename in os.listdir(directory):
    
    #splitting the file name to extract the temperature
    dummy = filename.split('_')[1]
    dummy = dummy.split('.')[0] +'.'+ dummy.split('.')[1]

    #appending the temperature to the array
    t9 = np.append(t9, np.float64(dummy))

    #reading in the data (lambda_ij)
    data = np.genfromtxt(directory + '/' + filename).T

    #initializing rate matrix array lambda_ij. since only 22 levels in example.xml, will create a square matrix 22x22
    lambda_ij = np.zeros((22,22))

    #loop over length of file and set values of matrix accordingly. since python  starts index at 0, a '-1' will be taken into account
    for i in range(len(data[0])):
        lambda_ij[int(data[0][i]) - 1][int(data[1][i]) - 1] = data[2][i]
      
    #transfer matrix F of size (n-2)x(n-2) (20x20)
    #Lambda_k is sum over lambda_ij - diagonal element
    F = np.empty((20,20))
    f1_in = np.empty(20)
    f2_out = np.empty(20)
    Lambda_k = np.zeros(22)    
    
    #while setting up, account for a '+2' since we are starting from the 3rd state
    for i in range(0,22):
        for j in range(0,22):
            if j == i:
                j += 1
                if j > 21:
                    break
            Lambda_k[i] += lambda_ij[i][j]

    for i in range(0,20):
        for j in range(0,20):
            F[i][j] = lambda_ij[i+2][j+2]/Lambda_k[i+2]
    
    for i in range(0,20):
        f1_in[i] = lambda_ij[i+2][0]/Lambda_k[i+2]
        f2_out[i] = lambda_ij[1][i+2]/Lambda_k[1]

    dummy = np.matmul(np.linalg.inv(np.identity(20) - F.T),f2_out)
    dummy = np.matmul(f1_in.T,dummy)
    l_21_eff = np.append(l_21_eff,Lambda_k[1]*dummy) 

    
n = len(t9)

for j in range(n-1,0,-1):
    for i in range(0,j):
        if t9[i] > t9[i+1]:
            dummy = t9[i+1]
            t9[i+1] = t9[i]
            t9[i] = dummy

            dummy = l_21_eff[i+1]
            l_21_eff[i+1] = l_21_eff[i]
            l_21_eff[i] = dummy            




plt.figure(figsize=(12,12))
fontsize = 40
plt.rcParams['font.size'] = fontsize

plt.ylabel(r'$\lambda^{eff}_{21} (s^{-1})$')
plt.xlabel(r'$T_{9}$')

plt.xscale('log')
plt.yscale('log')
plt.xticks(fontsize = 0.65*fontsize)
plt.yticks(fontsize = 0.65*fontsize)

plt.plot(t9,l_21_eff,color = 'black')
plt.ylim([1.e-15,1.e+15])
plt.xlim([1.e-1,10])
plt.axhline(y = 1.e-1,color = 'r',linestyle = ':')
plt.show()

