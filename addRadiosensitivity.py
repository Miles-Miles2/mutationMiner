import csv
import decimal


import numpy as np



radiosensitivityDict = {}

nameToIDConversion = {}

cellLinesWithRadiosensitivity = {}

with open('radiosensitivityData.csv') as radiosensitivityData:
    rsdDictReader = csv.DictReader(radiosensitivityData)
    for row in rsdDictReader:
        radiosensitivityDict[row['cell_line']] = float(decimal.Decimal(row['2']))


with open('CellLineNameToCCLE_ID.csv') as NameToID:
    NameToIDDictReader = csv.DictReader(NameToID)
    for row in NameToIDDictReader:
        nameToIDConversion[row['DepMap_ID']] = row['stripped_cell_line_name']



with open('mutationsCSV.csv') as mutationsCSV:
    mutationsCSVDictReader = csv.DictReader(mutationsCSV)

    radSensList = list(radiosensitivityDict.values())
    q1 = np.percentile(radSensList, 66)
    q2 = np.percentile(radSensList, 33)



    for row in mutationsCSVDictReader:    
        convertedName = nameToIDConversion[row['cellLineName']]
        
        if convertedName in radiosensitivityDict.keys():
            print(convertedName)
            cellLinesWithRadiosensitivity[convertedName] = row
            #cellLinesWithRadiosensitivity[convertedName]['cellLineName'] what is this??

            cellLinesWithRadiosensitivity[convertedName]['RSV'] = radiosensitivityDict[convertedName]

            #changed so that CSV includes raw radiosensitivity number
            if radiosensitivityDict[convertedName] > q1:
                cellLinesWithRadiosensitivity[convertedName]['radiosensitivity'] = 'radioresistant'
            elif radiosensitivityDict[convertedName] > q2:
                cellLinesWithRadiosensitivity[convertedName]['radiosensitivity'] = 'normal'
            else:
                cellLinesWithRadiosensitivity[convertedName]['radiosensitivity'] = 'radiosensitive'

            





with open(
    'CCLE_mutations_with_radiosensitivity.csv',
    'w',
    newline=''




) as mutationsCSV:
    fieldnames = cellLinesWithRadiosensitivity['HS888T'].keys()
    csvDictWriter = csv.DictWriter(mutationsCSV, fieldnames=fieldnames)
    csvDictWriter.writeheader()

    for cellLines in cellLinesWithRadiosensitivity:
        csvDictWriter.writerow(cellLinesWithRadiosensitivity[cellLines])



print('done')
