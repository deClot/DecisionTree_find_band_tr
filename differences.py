file = open('search', 'r')
file_res = open('results.RES', 'w')
file_delta = open('deltas', 'w')

count = 0
for line in file:
    count +=1
    if count == 5:
        break
    continue

deltas = {}
for line in file:
    if line.find('Searching') != -1:
        J0 = line.split()[1]
        deltas[J0] = []
        E0 = float(line.split()[-1])
        file_res.write(line)
        continue

    if line.find('No') != -1:
        continue

    if len(line.split()) == 0:
        file_res.write(line)
        continue

    try:
        E = float(line.split()[-1])
        delta = round(E - E0, 3)
        file_res.write(line[:-1]+ "\t"+ str(delta) + "\n")
        deltas[J0].append(delta)
    except ValueError:
        break

for k,v in deltas.items():
    file_delta.write(k + '\t' + '  '.join(map(str,v)) + '\n')
        
        #file_res.write(line[:-1]+ "\t"+ delta + "\n")
        # = round(str(float(line.split()[-1]) - E0)), 3)

    
