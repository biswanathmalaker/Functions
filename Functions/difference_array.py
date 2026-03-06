def difference_arrayNd(a):
    """
    a is the 1d array of elements. Elements(may be ndarray) are subtracted. 
    """
    import numpy as np

    a = np.array(a)
    b = np.delete(a,0,axis=0)
    c = np.delete(a,len(b),axis=0)
    d = b-c
    d = np.insert(d,0,a[0],axis=0)
    return d


if __name__=="__main__":
    import numpy as np
    a = np.linspace(1,36,36).reshape((3,3,4))
    print(a)
    l = difference_arrayNd(a)
    print(l[0].shape)
    print(l)
