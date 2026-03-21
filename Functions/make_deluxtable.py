
def unit_names_print(units):
    unit_names = ''
    for i,unit in enumerate(units):
        unit_names+='\\colhead'+'{'+f'{unit}'+'}'
        if i!=len(units)-1:
            unit_names+='   &   '
    return unit_names

def cols_names_print(cols_name):
    header = ''
    for i,col_name in enumerate(cols_name):
        header+='\\colhead'+'{'+f'{col_name}'+'}'
        if i!=len(cols_name)-1:
            header+='   &   '
    
    return header


def data_print1d(data):
    """
    data is 1d array
    """
    string = ''
    for i,d in enumerate(data):
        string+=str(d)

        if i!=len(data)-1:
            string+="   &   "
    string +="\\\\"
    return string

def data_print_2d(data):
    """
    data is 1d array
    """
    string = ''
    for i,d in enumerate(data):

        if i!=len(data)-1:
            string += data_print1d(d)+'\n'
        else:
            string+=data_print1d(d)
    return string


def make_deluxetable(cols_name,data,caption,label,cols_units=None,table_width_pt = 0,comment=None):
    """
    example :
                    cols = ["A","B","C"]
                    units = ['unitA','unitB','unitC']
                    data = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
                    make_deluxetable(cols,data,'my caption','my_label',units,comment='My comment')

    """
    dec1 =''
    for n in range(len(cols_name)):
        dec1+="c"

    start_line = '\\begin{deluxetable}'+'{'+f"{dec1}"+'}'+'[H]'
    end_line = '\\end{deluxetable}'

    line1 = '\\tabletypesize'+'{'+'\\footnotesize'+'}'
    line2 = '\\tablewidth'+'{'+f'{table_width_pt}'+'pt}'
    captions = '\\tablecaption{'+f' {caption} '+'\\label'+'{tab:'+f'{label}'+'}}'
    
    table_head1 = '\\tablehead{'


    print(start_line)

    print(line1)
    print(line2)

    print(captions)

    if cols_units!=None:
        print(table_head1)
        print(cols_names_print(cols_name)+"\\\\")
        print(unit_names_print(cols_units))
        print('}')
    else:
        print(table_head1)
        print(cols_names_print(cols_name))
        print('}')


    print('\\startdata')
    print(data_print_2d(data))
    print('\\enddata')

    if comment !=None:
        comments = "\\tablecomments"+'{'+f'{comment}'+'}'
        print(comments)

    print(end_line)



if __name__=="__main__":
    cols = ["A","B","C"]
    units = ['unitA','unitB','unitC']
    data = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
    make_deluxetable(cols,data,'my caption','my_label',units,comment='My comment')

