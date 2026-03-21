def normalize_array(arr , lower , upper):
    """
    Normalize array values between lower and upper
    arr ---> list or numpy array\n
    lower ---> lower value\n
    upper ---> upper value
    """
    import numpy as np

    arr = np.array(arr)
    norm = (arr-np.min(arr))/(np.max(arr)-np.min(arr))
    norm_rescaled_shifted = lower+norm*(upper-lower)
    return norm_rescaled_shifted


def rescale_and_translate(l0,m0,l1,m1,x):
    """
    x is a point between l0 and m0 scale.\n
    That scale is rescaled between l1 and m1.\n
    return the value of x in l1m1 scale.\n

    formula : xp = x*M+C\n
    M = (m1-l1)/(m0-l0)\n
    C = (m0*l1-l0*m1)/(m0-l0)\n
    """
    M = (m1-l1)/(m0-l0)
    C = (m0*l1-l0*m1)/(m0-l0)
    xp = x*M+C

    return xp

if __name__=="__main__":
    import numpy as np
    arr = np.array(range(10))
    n_arr = normalize_array(arr , 0 , 1)
    print(arr)
    print(n_arr)






