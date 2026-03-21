

def running_difference(arr,n):
    import numpy as np
    arr = np.array(arr)
    l = len(arr)
    d = np.zeros_like(arr)
    for i in range(n,l):
        d[i] = arr[i]-arr[i-n]

    for j in range(n):
        if j==0:
            d[j] = arr[j]
        else:
            d[j] = arr[j]-arr[0]

    if n==0:
        d = arr
    return d


if __name__=="__main__":
    import numpy as np
    # x = np.array([1,3,4,10,7,6,14,5,2,12,13,15])
    # running_difference(x,3)

    x = np.array([[1,3,4],[10,7,6],[14,5,2],[12,13,15]])
    r = running_difference(x,0)
    print(r)

