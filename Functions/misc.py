def write_json(file_path:str,data:dict):
    import json
    json_obj = json.dumps(data,indent=4)

    with open(file_path , 'w+') as json_file:
        json_file.write(json_obj)

    json_file.close()

def update_json(file_path:str,data:dict):
    import json
    with open(file_path , 'r+') as json_file:
        data1 = json.load(json_file)
    data = {**data1,**data}

    write_json(file_path,data)
    json_file.close()

def read_json(file_path):
    import json
    with open(file_path,'r') as json_file:
        data = json.load(json_file)
    
    return data

def get_outside_av(x,av,dx):
    """
    return numpy array of numbers inside x , greater than av+dx and less than av-dx.
    x = np.array([10,9,11,10,10,9,11,10,10,40,40,25,10,10,28,9,10,9])
    dx = 1
    av = 10

    return 
    [ 9 10 11 14] , [40 40 25 28]

    """
    import numpy as np
    b1 = x>=av-dx
    b2 = x<=av+dx
    b = np.logical_and(b1,b2)
    b = np.invert(b)
    I = np.array(list(range(len(x))))

    x_gt_av = np.extract(b,x)
    I_get_av = np.extract(b,I)

    return I_get_av,x_gt_av


def fix_nan(data):
    import numpy as np
    mask = np.isnan(data)
    print(mask)
    data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])
    return data


def fix_zeros(data):
    import numpy as np
    mask = data==0
    data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])
    return data

# def fix_unphysical_vals(data,min_v,max_v):
#     import numpy as np
#     mask = np.logical_or(data<min_v,data>max_v)
#     # print(mask)
#     data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])
#     return data


def contain_vals(data,min_v,max_v):
    import numpy as np
    s = data.shape
    data = data.flatten().copy()
    mask = np.logical_or(data<min_v,data>max_v)

    dm_ = data[~mask]
    ind = np.where(~mask)
    ind1 = np.arange(ind[0][0],ind[0][-1])

    f = np.interp(ind1,ind[0],data[ind[0]])

    data1 = np.zeros_like(data)

    if ind[0][0] !=0:
        data1[0:ind[0][0]] = dm_[0]

    if ind[0][-1] !=len(data)-1:
        data1[ind[0][-1]-len(data):] = dm_[-1]

    data1[ind1] = f

    return data1.reshape(s)


if __name__ == "__main__":
    import numpy as np
    # Generate data...
    x1 = np.array([1,2,3,4,9,5,6,7,8,9],dtype=np.float64)

    y1 = contain_vals(x1,4,7)
    print(y1)

# if __name__ == "__main__":
#     import numpy as np
#     # Generate data...
#     x = np.array([1,2,3,4,5,np.nan,6,7,np.nan,8,9])
#     x1 = np.array([1,2,3,4,9,5,6,7,8,9],dtype=np.float64)
#     # y = fix_nan(x)
#     y1 = fix_unphysical_vals(x1,3,7)
#     print(y1)
