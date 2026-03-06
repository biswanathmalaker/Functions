## useless module

def FFT(y):
    from scipy.fft import fft, fftfreq
    import numpy as np

    N = len(y)
    yf = fft(y)
    yf = 2.0/N * np.abs(yf[0:N//2])
    xf = fftfreq(N, 1/N)[:N//2]
    return xf,yf


from numpy.fft import fft , fftfreq

import matplotlib.pyplot as plt
import numpy as np

N = 600
# T = 1/N
x = np.linspace(0.0, N, N, endpoint=False)
T = 1100/12      # in bs
T2 = 550/12     # in bs

f = 1/T
f2 = 1/T2

# f = 1/T  # 3mHz = 3/1000Hz


y = np.sin(2.0*np.pi*x*f)+np.sin(f2*2.0*np.pi*f2)# + np.sin(80.0 * 2.0*np.pi*x)#+0.7*np.sin(10.0 * 2.0*np.pi*x)

# xf,yf = FFT(y)
xf = fftfreq(N)
yf = fft(y)

fig1 = plt.figure()
ax1 = fig1.add_subplot(1,1,1)
ax1.plot(xf,yf)

x1 = np.linspace(1,len(y),len(y))
fig2 = plt.figure()
ax2 = fig2.add_subplot(1,1,1)

ax2.plot(x1, y)

plt.grid()
plt.show()



# if __name__=="__main__":
#     import matplotlib.pyplot as plt
#     import numpy as np

#     N = 1200
#     # T = 1/N
#     x = np.linspace(0.0, N, N, endpoint=False)
#     T = 1100/12      # in bs
#     T2 = 550/12     # in bs

#     f = 91.6
#     f2 = 45.8

#     f = 1/T  # 3mHz = 3/1000Hz


#     y = np.sin(f*2.0*np.pi*x)+np.sin(f2*2.0*np.pi*x)# + np.sin(80.0 * 2.0*np.pi*x)#+0.7*np.sin(10.0 * 2.0*np.pi*x)

#     xf,yf = FFT(y)
    
#     fig1 = plt.figure()
#     ax1 = fig1.add_subplot(1,1,1)
#     ax1.plot(xf,yf)

#     x1 = np.linspace(1,len(y),len(y))
#     fig2 = plt.figure()
#     ax2 = fig2.add_subplot(1,1,1)

#     ax2.plot(x1, y)

#     plt.grid()
#     plt.show()



