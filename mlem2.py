#Name: Hunter Crisp
#KUID: 2544296
#mlem2.py

inputName = raw_input("Enter the name of the input file: ")
outputName = raw_input("Enter the name of the output file: ")

#Read the file values
while True:
	try:
		inputFile = open(inputName, "r")
		break
	except IOError as e:
		print("File not found. Try again")
		inputName = raw_input("Enter the name of the input file: ")


#skip first line
inputFile.readline()

#Store values
labels = inputFile.readline()
labels = labels.split(" ")

labels = labels[1:len(labels) - 1]
if(labels[len(labels) - 1] == ''):
	labels.pop()

dataArray = []
for x in inputFile:
	if(x == '\n'):
		continue
	x = x.split(" ")
	if(x[len(x) - 1]  == "\n"):
		x.remove("\n")
	elif('\n' in x[len(x) - 1]):
		x[len(x) - 1] = x[len(x) - 1].replace('\n', '')
	dataArray.append(x)

#Close file
inputFile.close()

#print("number of rows: ", len(dataArray))

#determine if any attribute values are numeric
isNum = []
for i in range(len(labels) - 1):
	if(not dataArray[0][i].isalpha() and ".." not in dataArray[0][i] and "-" not in dataArray[0][i]):
		isNum.append(i)

#print("cols that are numeric: ", isNum)

decisions = []
for d in range(len(dataArray)):
	decision = dataArray[d][len(labels) - 1]
	if(decision not in decisions):
		decisions.append(decision)

decisionBlock = []
for d in range(len(decisions)):
	temp = []
	for r in range(len(dataArray)):
		if(dataArray[r][len(labels) - 1] == decisions[d]):
			temp.append(r)
	decisionBlock.append([decisions[d], temp])

#print("decisions: ", decisionBlock)

cutGroups = []
#create cutpoints
for i in isNum:
	values = []
	#for each attribute, determine non repeating set of values in ascending order
	for j in range(len(dataArray)):
		if(dataArray[j][i] not in values):
			values.append(dataArray[j][i])
	
	values.sort(key=float)

	cuts = []
	for k in range(len(values)):
		if(k < len(values) - 1):
			cutPoint = (float(values[k]) + float(values[k+1]))
			cutPoint = format(cutPoint / 2, '.3g')
			#print(cutPoint)

			#find blocks
			block1 = []
			block2 = []
			for m in range(len(dataArray)):
				temp = float(dataArray[m][i])
				if(temp >= float(values[0]) and temp <= float(cutPoint)):
					block1.append(m)
				elif(temp >= float(cutPoint) and temp <= float(values[len(values) - 1])):
					block2.append(m)

			cuts.append([values[0] +".."+ str(cutPoint), block1])
			cuts.append([str(cutPoint) +".."+ values[len(values) - 1], block2])

	cutGroups.append([labels[i], cuts])


#print(cutGroups)

#get symbolic values
avPairs = []
for c in range(len(labels) - 1):
	if(c not in isNum):
		colValues = []
		for r in range(len(dataArray)):
			if(dataArray[r][c] not in colValues):
				colValues.append(dataArray[r][c])
		colValues.sort()

		#find blocks
		block1 = []
		for k in colValues:
			block2 = []
			for l in range(len(dataArray)):
				if(k == dataArray[l][c]):
					block2.append(l)
			block1.append([k, block2])		

		avPairs.append([labels[c], block1])

#combine both and sort
avPairs = avPairs + cutGroups
avPairs.sort()
#print(avPairs)

rules = []

for c in range(len(decisionBlock)):
	intBlocks = []
	#grab necessary blocks
	conceptBlock = decisionBlock[c][1]
	for a in range(len(avPairs)):
		b = []
		for r in range(len(avPairs[a][1])):
			avBlock = avPairs[a][1][r][1]
			#determine intersection, store cardinality with it
			intBlock = [list(set(conceptBlock) & set(avBlock))]
			
			if(len(intBlock) > 0):
				intBlock.append([len(avPairs[a][1][r][1])])
			b.append([avPairs[a][0], avPairs[a][1][r][0], intBlock])
		intBlocks.append(b)
	
	#begin LEM2
	#find max
	satisfiedG = False
	ruleList = []
	while satisfiedG is False:
		
		maximum = []
		mList = []
		tie1 = False
		for i in range(len(intBlocks)):
			for j in range(len(intBlocks[i])):
				temp = intBlocks[i][j][2]
				if(len(temp) > 0):
					if(maximum == []):
						maximum = intBlocks[i][j]
					if(len(temp[0]) > len(maximum[2][0])):
						#replace with new maximum a/v block
						mList = []
						maximum = intBlocks[i][j]
						mList.append(maximum)
					if(len(temp[0]) == len(maximum[2][0])):
						#if it is the same attribute, add it to the list
						if(intBlocks[i][j][0] == maximum[0]):
							mList.append(intBlocks[i][j])
						else:
							tie1 = True
							break
			if(tie1):
				break
		
		if(not tie1):
			#max successfully found
			#find it in avPairs and get av block
			for i in range(len(avPairs)):
				if(avPairs[i][0] == maximum[0]):
					for j in range(len(avPairs[i][1])):
						if(avPairs[i][1][j][0] == maximum[1]):
							ruleList.append([avPairs[i][0], avPairs[i][1][j][0], avPairs[i][1][j][1]])

			#remove rules with same attribute that are also max
			for i in range(len(mList)):
				for j in range(len(intBlocks)):
					if(mList[i] in intBlocks[j]):
						intBlocks[j].remove(mList[i])


		
		#If tie occurs, find minimum cardinality
		tie2 = False
		minimum = []

		if(tie1):
			for i in range(len(intBlocks)):
				for j in range(len(intBlocks[i])):
					temp = intBlocks[i][j][2]
					if(len(temp[0]) > 0):
						if(minimum == []):
							minimum = intBlocks[i][j]
						if(temp[1][0] < minimum[2][1][0]):
							#replace with new minimum
							minimum = intBlocks[i][j]
						if(temp[1][0] == minimum[2][1][0]):
							#different attribute, choose current min
							if(intBlocks[i][j][0] != minimum[0]):
								tie2 = True
								break
				if(tie2):
					break
			
			#minimum was chosen, find av block and add to rule list
			for i in range(len(avPairs)):
				if(avPairs[i][0] == minimum[0]):
					for j in range(len(avPairs[i][1])):
						if(avPairs[i][1][j][0] == minimum[1]):
							ruleList.append([avPairs[i][0], avPairs[i][1][j][0], avPairs[i][1][j][1]])

			#remove minimum from intBlocks
			for i in range(len(intBlocks)):
				if(minimum in intBlocks[i]):
					intBlocks[i].remove(minimum)
		
		#Check if G is satisfied by intersecting all current rules added
		if(len(ruleList) > 0):
			tempList = []
			temp = set(ruleList[0][2])
			if(len(ruleList) == 1):
				if(temp.issubset(set(conceptBlock))):
					rules.append([ruleList[0][0], ruleList[0][1], labels[len(labels) - 1],  decisionBlock[c][0]])
					satisfiedG = True
			else:
				tempList.append([ruleList[0][0], ruleList[0][1]])
				for i in range(1, len(ruleList)):
					tempList.append([ruleList[i][0], ruleList[i][1]])
					temp = temp.intersection(set(ruleList[i][2]))
					if(temp.issubset(set(conceptBlock))):
						rules.append([tempList, labels[len(labels) - 1], decisionBlock[c][0]])
						satisfiedG = True


#Format for printing
rulesFormatted = []
for i in range(len(rules)):
	if(len(rules[i]) == 3):
		attRule = str(rules[i][0])
		attRule = attRule.replace('[', '(')
		attRule = attRule.replace(']', ')')
		decisionLabel = rules[i][1]
		d = rules[i][2]
		f = attRule + " ---> (" + decisionLabel + ", " + d + ")"
		rulesFormatted.append(f)
	if(len(rules[i]) == 4):
		attRule = "(" + rules[i][0] + ", " + rules[i][1] + ")"
		decisionLabel = rules[i][2]
		d = rules[i][3]
		f = attRule + " ---> (" + decisionLabel + ", " + d + ")"
		rulesFormatted.append(f)


outputFile = open(outputName, "w")
#Write rules to file
for i in range(len(rulesFormatted)):
	outputFile.write(rulesFormatted[i])
	outputFile.write("\n\n")

outputFile.close()