def renormalize(x,a1,a2):
    """
    x is either a list or numpy array
    a1 , a2 are minimum and maximum value between which one has to normalize.
    """
    import numpy as np
    x = np.array(x)
    s = x.shape
    y = x.ravel()
    m1 = np.min(y)
    m2 = np.max(y)
    b1 = (a2-a1)/(m2-m1)
    b2 = (a1*m2-a2*m1)/(m2-m1)
    z = y*b1+b2
    z = z.reshape(s)
    return z


if __name__=="__main__":
    import numpy as np
    x = np.linspace(1,6,6).reshape((2,3))
    z = renormalize(x,0,1)
    print(z)