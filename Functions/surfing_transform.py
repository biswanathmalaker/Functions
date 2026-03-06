import numpy as np
import matplotlib.pyplot as plt
from skimage import io, img_as_float, img_as_ubyte
from skimage.util import random_noise
from scipy.ndimage import gaussian_filter



def brownian_noise(shape):
    # Generate random increments
    increments = np.random.normal(0, 1, shape)
    
    # Cumulative sum of increments gives Brownian motion
    brownian = np.cumsum(increments, axis=0)
    brownian = np.cumsum(brownian, axis=1)
    
    # Normalize to [0, 1] range
    brownian = (brownian - brownian.min()) / (brownian.max() - brownian.min())
    
    return brownian

def add_brownian_noise_snr(image, snr):
    # Convert image to float
    image_float = img_as_float(image)
    
    # Generate Brownian noise
    noise = brownian_noise(image.shape)
    
    # Calculate signal power
    signal_power = np.mean(image_float ** 2)
    
    # Calculate noise power based on desired SNR
    snr_linear = 10 ** (snr / 10)
    noise_power = signal_power / snr_linear
    
    # Scale noise to achieve desired SNR
    noise_scaled = np.sqrt(noise_power) * noise
    
    # Add noise to image
    noisy_image = image_float + noise_scaled
    
    # Clip values to [0, 1] range
    noisy_image = np.clip(noisy_image, 0, 1)
    
    return noisy_image

### Create a xt plot

def A(x,t,nu,v):

    a0 = 10
    TT,XX = np.meshgrid(t,x)

    omega = nu*2*np.pi
    k = omega/v

    for ki,omegai in zip(k,omega):
        try:
            a =a+ a0*np.cos(ki*XX-omegai*TT)
        except:
            a = a0*np.cos(ki*XX-omegai*TT)


    return a


x = np.linspace(0,80,80)
t = np.linspace(0,120,120)


nu = np.array([5.0,3.33,3.33])
v = np.array([-100.0,50,120])
a = A(x,t,nu,v)
# a = gaussian_filter(a,1)

snr_db = 10 * np.log10(0.1)    # 5% noise
a1 = add_brownian_noise_snr(a, snr_db)


fig = plt.figure()
ax = fig.add_subplot(1,1,1)
im = ax.imshow(a,origin='lower',cmap='Greys_r')

plt.colorbar(im)

# fig1 = plt.figure()
# ax = fig1.add_subplot(1,1,1)
# ax.plot(np.linspace(1,len(a1[20]),len(a1[20])),a1[20])



plt.show()


# x = np.array([2,4])
# t = np.array([0,4])
# TT,XX = np.meshgrid(t,x)

# print(TT)
# print(XX)

# def f(x,t):
#     TT,XX = np.meshgrid(t,x)    
#     return XX**2+TT


# print(f(x,t))






