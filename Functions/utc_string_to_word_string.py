import datetime

def utc_string_to_word(utc_string,format='%Y-%m-%dT%H:%M:%S.%f'):
    """
    e.g. utc_string = '2019-07-01T02:59:21.347'
    format = '%Y-%d-%mT%H:%M:%S.%f'
    """
    t = datetime.datetime.strptime(utc_string,format)
    # t = t.strftime("%b-%d,%Y %H:%M:%S UT")
    t = t.strftime("%Y-%m-%d %H:%M:%S UT")
    return t

if __name__=="__main__":
    utc_string = '2019-07-01T02:59:21.347'
    format = '%Y-%d-%mT%H:%M:%S.%f'
    t = utc_string_to_word(utc_string,format)
    print(t)





