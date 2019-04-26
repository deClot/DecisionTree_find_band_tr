import subprocess

def clear_res_file(file_name):
    ''' Clear initial RES file from parameters and matrix lines. Takes into account of possible permutations in energies'''
    
    def func (v, list1,str3,list2,no,E2):
        E2 = float (E2)

        list1.append(str3)
        k=[E2,no]
        list2.append(k)
        
        return list1,list2

    def sort_col(i):
        return i[0]

    file_res = open(file_name, 'r').readlines()
    file_res = file_res[:-2]
    l = len(file_res)
    count = 0
    
    for i in range(l):
        line = file_res[i]
        if line.find('matrix') == -1:
            continue
        else:
            count = i
            break
    
    list1, list2, file_out = [], [], []

    for i in range(count, l):
        line2 = file_res[i][0:56]
        if len(line2)==0:
            break

        if line2.find('matrix')!=-1: #sodershit matrix
            if len(list2) == 0:
                continue
            list2.sort(key=sort_col)
            for i in range(len(list2)):
                file_out.append('{:>5} V={:>2} J={:>2}{:>3}{:>3}'.format(list2[i][1],\
                        list1[i][0],list1[i][1],list1[i][2],list1[i][3]))
                file_out.append('{:>34}\n'.format(list2[i][0]))
            list1, list2 = [], []
            continue
    
        line2 = line2.replace ('J=','').split()
        no,_,v,J,Ka,Kc, *_ = line2
        E2 = line2[-1]
        str3 = v,J,Ka,Kc
        v = int(v)
        list1,list2=func(v,list1,str3,list2,no,E2)   
    
    with open(file_name,'w') as F:
        F.writelines(file_out)


from keras.models import Model, Sequential
from keras.layers import Dense, Input, GRU, LSTM
from keras.optimizers import Adam

def model_GRU(input_shape, Ty, hidden_size):
    i = Input(shape=input_shape, dtype='float32')
    X = GRU(hidden_size, return_sequences=False)(i)
    
    X = Dense(Ty, activation='sigmoid')(X)
    model = Model(inputs=[i], outputs=X)
    
    return model
  
def model_LSTM(hidden_size):  
    model = Sequential()
    model.add(LSTM(hidden_size, return_sequences=False))
    model.add(Dense(units=1, activation='sigmoid'))
  
    return model

import os

def calculate_RES_for_band_centers(band_centers):
    '''Change value of band center ind DAT file and wait for running TRANS.EXE. After, change name of RES file for corresponding band center'''
    
    for center in band_centers:
        file_dat = open('TRANS.DAT', 'r')
        lines = file_dat.readlines()
        file_dat.close()
        
        line1 = lines[1].split()
        line1[0] = '  ' + center
        lines[1] = '  '.join(line1)+'\n'

        file_dat =  open('TRANS.DAT', 'w')
        file_dat.write(''.join(lines))
        file_dat.close()
        
        print(center)
        a = input()
        
        os.rename('TRANS.RES', 'TRANS_'+band_centers_ini[band_centers.index(center)]+'.RES')
    
def make_asym_search(peak_file, quan_num, max_counter):
    '''Create correct ASYM file and run ASYM and SEARCh exes to get search''' 

    file_asym = open('ASYM', 'r')

    line = ''
    for i in range(5):
        if i == 1:
            file_asym.readline()
            line += peak_file + '\n'
            continue
        line += file_asym.readline()

    file_asym.close()

    file_asym = open('ASYM', 'w')
    file_asym.write(line)

    make_asym(file_asym, *quan_num, max_counter = max_counter)
    file_asym.close()

    #!wine ASYM.EXE
    #!wine SEARCH.exe
    subprocess.run(["wine", "ASYM.EXE"])
    subprocess.run(["wine", "SEARCH.EXE"])
    
def make_asym(file_asym, J, Ka, Kc,max_counter=6, v=1):
    '''Write (in already opened ASYM file) seria from max_counter elements for giver quantum nubers
    file_asym, J, Ka, Kc,max_counter=6, v=1'''
    file_res = open('TRANS.RES', 'r')

    counter = 0
    max_counter = max_counter

    for line in file_res:
        line_split = list(map(int, line.replace ('J=','').split()[2:6])) # v, J, Ka, Kc

        if line_split[0] == v and line_split[1] == J and line_split[2] == Ka \
               and line_split[3] == Kc:
            counter += 1
            if counter > max_counter:
                break

            file_asym.write ('%s' %(line))
            J = J + 1
            Kc = Kc + 1

    file_res.close()
    file_asym.close()


def deltas_in_search(file_name = 'search'):
    file_search = open(file_name, 'r')

    count = 0
    for line in file_search:
        count +=1
        if count == 5:
            break
        continue

    deltas = {}

    for line in file_search:
        if line.find('Searching') != -1:
            J0 = int(line.split()[1])
            deltas[J0] = []
            E0 = float(line.split()[-1])
            continue

        if line.find('No') != -1 or \
           len(line.split()) == 0 or \
           int(line.split()[0]) != int(J0) - 1:
            continue

        try:
            E = float(line.split()[-1])
            delta = round(E - E0, 3)
            deltas[J0].append(delta)
        except ValueError:
            break
            
    return deltas


def find_upper(J0, Ka0, Kc0, path, band_name):
    file_res = open(path+'res_'+band_name+'.res')
    
    for line in file_res:
        line = line.replace('J=', '').split()
        
        if [J0,Ka0,Kc0] == line[3:6]:
            E = float(line[-1])
            file_res.close()
            return E

def make_sequences_y1(file_name, path, band_name):
    file = open(path + file_name, 'r')
    
    sequence = []
    data_1 = []
    flag = False

    for line in file: 
        if line.find('New') != -1:
            if len(sequence) != 0:
                #print(sequence)
                data_1.append(sequence)
            sequence = []
            continue
        if line.find('Searching') != -1:
            flag = False
            J0, Ka0, Kc0, = line.split()[1], line.split()[2], line.split()[3]
            E0 = find_upper(J0, Ka0, Kc0, path, band_name)
            continue

        if flag == True or line.find('No') != -1 or len(line.split()) == 0:
            continue

        try:
            E = float(line[:78].split()[-1])
            delta = E - E0
            flag = True
            sequence.append(delta)
        except ValueError:
            break
    return data_1

import numpy as np

def get_sequence_sample(sequence, window_size=1):
    values = sequence.copy()
    
    for i in range(window_size-1):
        column = np.roll(sequence, -(i + 1), axis=0)
        values = np.hstack((values, column))
    values = values[:-window_size]
    
    return values

def get_x(data, window_size=1):
    X = np.zeros((1, window_size))
    for i in range(len(data)):
      sequences_1 = np.asarray(data[i])
      sequences_1 = np.expand_dims(sequences_1, axis=1)

      X_i = get_sequence_sample(sequences_1, window_size=window_size)
      X = np.vstack((X, X_i))
      
    #labels = np.ones((X.shape[0], 1))
    #X = np.hstack((X, labels))
    return X[1:]
