



# def running_box_car_average(data , point):
#     '''
#     data --> numpy ndarray or list or ndarray of ndarrays.
#     point --> How many data_points to be averaged over.
#     '''
#     import numpy as np
#     data = np.array(data)
#     i = 0
#     moving_average = []
#     while(i+point<=len(data)):
#         a = np.average(data[i:i+point])
#         i = i+1
#         moving_average.append(a)
#     return moving_average


def running_box_car_average(data , point):
    '''
    data --> numpy ndarray or list or ndarray of ndarrays.
    point --> How many data_points to be averaged over.
    '''
    import numpy as np
    data = np.array(data)
    i = 0
    moving_average = []


    while(i+point<=len(data)):
        a = np.average(data[i:i+point])
        i = i+1
        moving_average.append(a)

    for j in range(point-1):
        sum = 0
        for k in range(j+1):
            sum = sum+data[k]
        av = sum/(j+1)
        moving_average.insert(j,av)

    moving_average = np.array(moving_average)
    if point==0:
        moving_average = data

    return moving_average

def running_box_car_average2d(data , point):
    '''
    data --> numpy ndarray or list or ndarray of ndarrays.
    point --> How many data_points to be averaged over.

    e.g.        data = np.array([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
                n = running_box_car_average2d(x,2)
                print(n)
                [[1.  2.  3. ]
                 [2.5 3.5 4.5]
                 [5.5 6.5 7.5]]
    '''         
    import numpy as np
    data = np.array(data)
    i = 0
    moving_average = []


    while(i+point<=len(data)):
        a = np.mean(data[i:i+point] , axis=0)
        i = i+1
        moving_average.append(a)

    for j in range(point-1):
        sum = 0
        for k in range(j+1):
            sum = sum+data[k]
        av = sum/(j+1)
        moving_average.insert(j,av)
    
    moving_average = np.array([list(m) for m in moving_average ])

    if point==0:
        moving_average = data


    return moving_average



if __name__=="__main__":
    import numpy as np
    data = [5,12,17,18,21,22,25,30]
    data1 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    point = 0
    x = np.array([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
    print(data1)
    m = running_box_car_average(data1 , point)
    print(m)
    print(x)
    n = running_box_car_average2d(x,point)
    print(n)
    print(x)
