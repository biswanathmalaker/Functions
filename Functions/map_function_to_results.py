
x = [(1,10,100),(2,11,101)]

def map_function_to_results(x):
    import numpy as np
    # y = np.array([[1,2],[10,11],[100,101]]) # that must be

    s0,s1 = len(x[0]),len(x)

    y1 = np.zeros((s0,s1))

    l = [list(j) for j in x]
    l = np.array(l)
    y2 = l.T.tolist()

    for i,j in enumerate(y2):
        y1[i]=j

    return y1

z = map_function_to_results(x)
print(z)


