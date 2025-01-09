import re
# normal 2D (PsHet)
filepath1 = 'C:/Users/Hajo/sciebo/Phd/python/SNOM/testdata/2023-08-31 173204 AC approach_curve_new_round_mirror_calibrated/2023-08-31 173204 AC approach_curve_new_round_mirror_calibrated.txt'
# normal Approach Curve
filepath2 = 'C:/Users/Hajo/sciebo/Phd/python/SNOM/testdata/2020-01-08 1337 PH denmark_skurve_02_synchronize/2020-01-08 1337 PH denmark_skurve_02_synchronize.txt'
# header = 27
# header = 6

def _find_header_size(filepath):
    beginning_symb = '#'
    inside_header = True
    header = 0
    max_number = 100 # to avoid endless loop if beginning symbol changes
    with open(filepath, 'r') as file:
        while inside_header and header < max_number:
            line = file.readline()
            if line[0:1] == beginning_symb:
                header += 1
            else: inside_header = False
    return header



def remove_empty_spaces(line):
    # print('starting to replace empty spaces')
    try:
        line = line.replace(u'\xa0', '')
    except: pass
    try:
        line = line.replace(u'\t\t', '\t') # neaspec formatting sucks thus sometimes a simple \t is formatted as \t\xa0\t
    except:
        pass
    # seems like all lines have additional \t in front, so lets get rid of that
    try:
        line = line.replace(u'\t', '', 1)
    except: pass
    return line


def simplify_line(line):
    # replace # in the beginning, might be different for different sofrware versions
    # print(line)
    line = line.replace('# ', '')
    # print(line)
    line = line.replace(':', 'split-here', 1) # only replace first occurence
    # print(line)
    line = line.split('split-here')
    # print(line)
    # only remove empty spaces only from second element, keep only the important empty spaces in second one as it is used as a separator for mutliple values
    line[1] = remove_empty_spaces(line[1])
    # print(line)
    line[1] = line[1].replace(u'\n', '')
    # print(line)
    # split second element into list if possible:
    try:
        line[1] = line[1].split(u'\t')
    except: pass
    # sometimes an empty element will be created, get rid of that too:
    if type(line[1]) is list and '' in line[1]:
        line[1].remove('')
    key = line[0]
    value = line[1]

    return key, value

def convert_header_to_dict():
    content = read_parameters_txt(filepath1)
    parameters_dict = {}
    for i in range(len(content)):
        if i == 0:
            # first line is just the website adress
            pass
        else:
            key, value = simplify_line(content[i])
            # sort dictornary entries correctly:
            # key: [value1, value2, ... , '[unit]'] but only if value contains a list with len > 1 and if value[0] is a string that cannot be converted to a number
            new_value = value.copy()
            if type(value) == list:
                # print('encountered a list', value)
                if len(value) > 1:
                    # print('len(list)', len(value))
                    try: float(value[0])
                    except: exception = True
                    else: exeption = False
                    # print('exception: ', exception)
                    if exception:
                        # print('exception found')
                        for i in range(len(value)-1):
                            new_value[i] = value[i+1]
                        new_value[-1] = value[0]
                        # print('old value: ', value, '\nnew value: ', new_value)


            
            # parameters_dict[key] = value
            parameters_dict[key] = new_value
    for key in parameters_dict:
        print(f'{key}: {parameters_dict[key]}')
    return parameters_dict

def read_parameters_txt(filepath):
    content = []
    # get length of header, header lines should beginn with a '#'
    header = _find_header_size(filepath)
    with open(filepath, 'r', encoding='UTF-8') as file:
        for i in range(header):
            line = file.readline()
            content.append(line)
    return content

def get_parameter_values(parameters_dict, parameter):
    value = None
    if parameter in parameters_dict:
        value = parameters_dict[parameter]
    else:
        print('Parameter not in Parameter dict!')
    return value

def main():
    parameter_dict = convert_header_to_dict()
    print('Scan type: ', get_parameter_values(parameter_dict, 'Scan'))


if __name__ == '__main__':
    main()

# with open(filepath1, 'r') as file:
#     content1 = file.readlines(header)
# content1 = read_parameters_txt(filepath1)
# print('Content of file1:')
# print(content1)

# with open(filepath1, 'r') as file:
#     content2 = file.readlines(header)
# print('Content of file2:')
# print(content2)



