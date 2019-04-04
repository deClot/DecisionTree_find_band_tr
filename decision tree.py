file = open('deltas', 'r')
file_tree = open('tree', 'w')

deltas = {}
for line in file:
    deltas[line.split()[0]] = line.split()[1:]


def tree (k,v):
    #print(k)
    file_tree.write('({}) {} '.format(k,v))
    for k2, v2 in deltas.items():
        if int(k2) <= int(k):
            continue
        else:
            tree(k2,v2)
    
            
for k,v in deltas.items():
    print('ini', k)
    tree(k,v)
    file_tree.write('\n')
    
