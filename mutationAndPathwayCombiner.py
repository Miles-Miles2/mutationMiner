import csv

pathwayDict = {}

with open('pathwayFINAL_OUTPUT.csv') as pathwayCSV:
    pathwayCSVDict = csv.DictReader(pathwayCSV)

    for row in pathwayCSVDict:
        pathwayDict[row['cellLineName']] = row
        for pathway in row:
            print(row[pathway])


finalDict = {}

with open('CCLE_mutations_with_radiosensitivity.csv') as mutationsCSV:
    mutationCSVDict = csv.DictReader(mutationsCSV)

    for row in mutationCSVDict:
        if row['cellLineName'] in pathwayDict.keys():
            finalDict[row['cellLineName']] = row | pathwayDict[row['cellLineName']]
            del finalDict[row['cellLineName']]['cellLineName']
            del finalDict[row['cellLineName']]['radiosensitivity']
            #print(len(finalDict[row['cellLineName']].keys()))

fieldNames = []

for key in finalDict:
    fieldNames = list(finalDict[key].keys())
    break


with open(
    'pathwayCSV_and_mutationCSV_merge.csv',
    'w',
    newline=''
) as outputCSV:

    csvDictWriter = csv.DictWriter(outputCSV, fieldnames=fieldNames)
    csvDictWriter.writeheader()

    for cellLine in finalDict:
        csvDictWriter.writerow(finalDict[cellLine])

dictWithoutRadiosensitivity = finalDict

for cellLine in dictWithoutRadiosensitivity:
    del dictWithoutRadiosensitivity[cellLine]['RSV']

for key in dictWithoutRadiosensitivity:
    fieldNames2 = list(dictWithoutRadiosensitivity[key].keys())
    break

with open(
    'pathwayCSV_and_mutationCSV_merge_radiosensitivityRemoved.csv',
    'w',
    newline=''
) as outputCSV:

    csvDictWriter = csv.DictWriter(outputCSV, fieldnames=fieldNames2)
    csvDictWriter.writeheader()

    for cellLine in dictWithoutRadiosensitivity:
        csvDictWriter.writerow(dictWithoutRadiosensitivity[cellLine])