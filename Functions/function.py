from numpy.lib.function_base import average


def group(L,n,add_leftover=True):
    """
    L is a list of more than n elements and group will
    return list of lists with n elements and leftover will be removed
    """
    import numpy as np
    if type(L).__module__ == 'numpy':
        L = L.tolist()

    l = len(L)
    m = l//n
    Gr_list = []
    for i in range(0,len(L),n):
        if i < m*n:
            Gr_list.append(L[i:i+n])

    if add_leftover:
        return np.array(Gr_list) , np.array(L[-m:])
    else:
        return np.array(Gr_list)


def rstrip_word(str, word):
    if str.endswith(word):
        return str[:-len(word)]
    return str

def lstrip_word(str, word):
    if str.startswith(word):
        return str[len(word):]
    return str



def strip_word(str, word):
    return rstrip_word(lstrip_word(str, word), word)



def average_of_n_elments_before_max_x(x , n):
    import numpy as np
    """
    x = [1, 2, 3, 4, 5, 6, 7, 856, 8, 8, 7, 6, 5, 4, 3, 2, 1]
    max(x) = 856 ;
    if n = 3 , function will return average of 5 , 6 and 7
    """

    max_x = np.max(x)
    indx = x.index(max_x)
    y = x[indx-n:indx-len(x)]
    return np.mean(y)



def average_of_n_elments_after_max_x(x , n):
    import numpy as np
    """
    x = [1, 2, 3, 4, 5, 6, 7, 856, 8, 8, 7, 6, 5, 4, 3, 2, 1]
    max(x) = 856 ;
    if n = 3 , function will return average of 8 , 8 and 7
    """

    max_x = np.max(x)
    indx = x.index(max_x)
    y = x[indx+1:indx+n+1]
    print(y)
    return np.mean(y)


if __name__== "__main__" :
    import numpy as np
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = group(x,4,add_leftover=False)  
    print(y)

