from tkinter import *
from tkinter import ttk, filedialog
from pythermo import abr2prop, prop2abr
import pythermo
from pythermo.report import *
import datetime
import os
import threading
import time

nr_components = {
  "any": 0,  
  "pure compound": 1,
  "binary mixture": 2,
  "ternary mixture": 3
}


var0= ''
var1= 'pure compound'
var2= ''
var3= ''
var4= ''
var5= ''
var6= ''

root = Tk()

root.title('ILThermo Database Manager')
root.geometry("480x480")


label0 = Label(root, text="Enter Chemical Name, CAS or Chemical Formula")
label0.pack()

entry = Entry(root, width=30)
entry.pack()

def profit_calculator():
    global var0
    var0 = entry.get()

button_calc = Button(root, text="Insert", command=profit_calculator)
button_calc.pack()

label1 = Label(root, text="Choose number of components")
label1.pack()

def close_window():
    root.destroy()

def comboclick1(event):
    global var1
    var1 = myCombo1.get()    

def comboclick2(event):
    global var2
    var2 = myCombo2.get()

options1 = [
    "pure compound",
    "binary mixture",
    "ternary mixture",
    "any"
    ]

options2 = list(abr2prop.values())

myCombo1 = ttk.Combobox(root, value=options1)
myCombo1.current(0)
myCombo1.bind("<<ComboboxSelected>>", comboclick1)
myCombo1.pack()

label6 = Label(root, text="Choose property")
label6.pack()

myCombo2 = ttk.Combobox(root, value=options2, width=45)
myCombo2.bind("<<ComboboxSelected>>", comboclick2)
myCombo2.pack()

def directory():
    global var3
    var3 = filedialog.askdirectory()
    #var3 = entry2.get()

label2 = Label(root, text="Browse saving directory")
label2.pack()

button_calc2 = Button(root, text="Browse", command=directory)
button_calc2.pack()

def action1():
    global var4
    var4 = entry3.get()

label3 = Label(root, text="Enter publication year")
label3.pack()

entry3 = Entry(root, width=50)
entry3.pack()

button_calc3 = Button(root, text="Save", command=action1)
button_calc3.pack()

def action2():
    global var5
    var5 = entry4.get()

label4 = Label(root, text="Enter author's last name")
label4.pack()

entry4 = Entry(root, width=50)
entry4.pack()

button_calc4 = Button(root, text="Save", command=action2)
button_calc4.pack()

def action3():
    global var6
    var6 = entry5.get()

label5 = Label(root, text="Enter keyword(s) - use comma to add more")
label5.pack()

entry5 = Entry(root, width=50)
entry5.pack()

button_calc5 = Button(root, text="Save", command=action3)
button_calc5.pack()


class Spinner:
    """A class providing a spinning cursor for cli tools."""
    busy = False
    delay = 0.01

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        """Start the spinner."""
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        """Stop the spinner."""
        self.busy = False
        time.sleep(self.delay)

# create a spinner object for some of the following functions
spinner = Spinner()

def metaDataStr(datObj):
    """
    Returns the meta data of an :class:`pyilt2.dataset` object as a *string*, like::

        Property:
          Specific density
        Reference:
          "Densities, isobaric expansivities and isothermal compressibilities [...].",
          Krolikowska, M.; Hofman, T. (2012) Thermochim. Acta 530, 1-6.
        Component(s):
          1) 1-ethyl-3-methylimidazolium thiocyanate
        Method: Vibrating tube method
        Phase(s): Liquid
        Data columns:
          1) Temperature/K
          2) Pressure/kPa
        ...

    :param datObj: dataset object
    :type datObj: :class:`pyilt2.dataset`
    :return: meta data
    :rtype: str
    """
    with open('list_of_unique_compounds.dat') as f:
        cmpds = f.read().splitlines()
    with open('comp_smiles.dat') as g:
        smiles = g.read().splitlines()
    
    dictionary = {}
    for i in range(len(cmpds)):
        dictionary[cmpds[i]] = smiles[i]
    
    out =  'Property:\n  {0:s}\n'.format(datObj.setDict['title'].split(':')[-1].strip())
    out += 'Reference:\n'
    out += '  "{0:s}",\n'.format(datObj.setDict['ref']['title'])
    out += '  {0:s}\n'.format(datObj.setDict['ref']['full'])
    out += 'Component(s):\n'
    for i in range(0, datObj.numOfComp):
        out += '  {0:d}) {1:s}\n'.format(i+1, datObj.listOfComp[i])
    out += 'Smiles:\n'
    # SMILES
    for i in range(0, datObj.numOfComp):
        out += '  {0:d}) {1:s}\n'.format(i+1, dictionary[datObj.listOfComp[i]])
    if datObj.setDict['expmeth']:
        out += 'Method: {0:s}\n'.format(datObj.setDict['expmeth'])
    out += 'Phase(s): {0:s}\n'.format(', '.join(datObj.setDict['phases']))
    if datObj.setDict['solvent']:
        out += 'Solvent: {0:s}\n'.format(datObj.setDict['solvent'])
    out += 'Data columns:\n'
    for i in range(0, len(datObj.headerList)):
        out += '  {0:d}) {1:s}\n'.format(i+1, datObj.headerList[i])
    out += 'Data points: {0:d}\n'.format(datObj.np)
    out += 'ILT2 setid: {0:s}\n'.format(datObj.setid)
    return out

def writeReport(listOfDataSets, reportDir=None, resDOI=False, verbose=False):
    global newReportDir
    dtnow = datetime.datetime.now()
    if not reportDir:
        reportDir = 'ILThermo_' + dtnow.strftime("%Y-%m-%d_%H_%M_%S")
        os.mkdir(reportDir)
        os.mkdir(reportDir+'/data')
    else:
        newReportDir = reportDir + '/' +'ILThermo_' + dtnow.strftime("%Y-%m-%d_%H_%M_%S")
        os.mkdir(newReportDir)
        os.mkdir(newReportDir+'/data')
    if verbose:
        print('\nWrite report to folder: '+newReportDir)
        print(' << report.txt')
    rep = open(newReportDir + '/report.dat', 'w')
    rep.write(dtnow.strftime("%d. %b. %Y (%H_%M_%S)") + '\n')
    rep.write('-' * 24 + '\n')
    file_names=[]
    const=0
    for i in range(0, len(listOfDataSets)):
        dataSet = listOfDataSets[i]
        original_string = str(dataSet.listOfComp)
        characters_to_remove = "["
        new_string = original_string
        for character in characters_to_remove:      
            new_string = new_string.replace(character, "", 1)
        new_string = new_string[:-1]
        file_names.append(new_string)
        
        if i>0:
            for word in file_names[:-1:]:
                if file_names[-1] == word[:]:
                    const = const + 1
                    new_string = new_string + str(const)
        
        dataFile = '{}.txt'.format(new_string)
        # write data file
        dataSet.write(newReportDir + '/' + dataFile)
        if verbose:
            print(' << {0:s} [{1:s}]'.format(dataFile, dataSet.setid))
        # write meta data to report file
        rep.write('\nRef. #{0:d}\n'.format(i, dataSet.setid))
        rep.write('=' * 10 + '\n')
        rep.write( metaDataStr(dataSet) )
        if resDOI:
            if verbose:
                print(' >> resolve DOI ... ', end='')
                spinner.start()
            try:
                (doi, url, score) = citation2doi(dataSet.fullcite)
            except:
                if verbose:
                    spinner.stop()
                e = sys.exc_info()[1]
                print('Error: {0:s}'.format(str(e)))
            else:
                if verbose:
                    spinner.stop()
                    print('\b {0:s} (score: {1:f}) done!'.format(doi, score))
                rep.write('DOI: {0:s} (score: {1:f})\n'.format(doi, score))
                rep.write('URL: {0:s}\n'.format(url))
    rep.close()
    return newReportDir

def pyilt2():
    
    import pythermo
    import pythermo.report
    import subprocess
    
    results = pythermo.report.cliQuery(comp  = entry.get(),
                                 numOfComp = nr_components[myCombo1.get()], 
                                 prop      = myCombo2.get(),
                                 year      = str(var4),
                                 author    = str(var5),
                                 keywords  = str(var6)
                                )
    
    lista=[]
    for ref in results.resDict['res']:
        if nr_components[myCombo1.get()] == 2:
            lista.append(results._makeRefDict(ref)['nm1'])
            lista.append(results._makeRefDict(ref)['nm2'])
        else:
            if nr_components[myCombo1.get()] == 1:
                lista.append(results._makeRefDict(ref)['nm1'])
            if nr_components[myCombo1.get()] == 3:
                lista.append(results._makeRefDict(ref)['nm1'])
                lista.append(results._makeRefDict(ref)['nm2'])
                lista.append(results._makeRefDict(ref)['nm3'])
            else:
                lista.append(results._makeRefDict(ref)['nm1'])
                if "nm2" in results._makeRefDict(ref):
                    lista.append(results._makeRefDict(ref)['nm2'])
                if "nm3" in results._makeRefDict(ref):
                    lista.append(results._makeRefDict(ref)['nm3'])
            
    a = list(set(lista))

    with open('list_of_unique_compounds.dat', 'w') as f:
        for item in a:
            f.write("%s\n" % item)
    
    subprocess.call(['java', '-jar', 'opsin-2.4.0-jar-with-dependencies.jar', '-osmi', 'list_of_unique_compounds.dat', 'comp_smiles.dat'])
    
    dataset = pythermo.report.getAllData(results, verbose = True)

    writeReport(dataset, resDOI = True, reportDir=str(var3), verbose = True)
    
    
label6 = Label(root, text="Execute the query")
label6.pack()
    
button9 = Button(text = "Query", command = pyilt2)
button9.pack()

def smiles():
    import csv
    import subprocess
    import os  
    import os, fnmatch
    
    def findReplace(directory, find, replace, filePattern):
        for path, dirs, files in os.walk(os.path.abspath(directory)):
            for filename in fnmatch.filter(files, filePattern):
                if filename == "report.txt":
                    continue
                else:
                    filepath = os.path.join(path, filename)
                    with open(filepath) as f:
                        s = f.read()
                    s = s.replace(find, replace)
                    with open(filepath, "w") as f:
                        f.write(s)

    path = newReportDir+'/'
    print('path: ', path)
    
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                if file=="report.txt":
                    continue
                else:
                    with open(path+file) as fin:
                        lines = fin.readlines()
                    lines[0] = lines[0].replace(' ', '_')
                    lines[0] = lines[0].replace(';', ',')
        
                    with open(path+file, 'w') as fout:
                        for line in lines:
                            fout.write(line)   

    findReplace(path, "__", " ", "*.txt")
    findReplace(path, "#_", "", "*.txt")
    
    path = '{}/'.format(newReportDir)
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                with open(path+file, 'r') as in_file:
                    stripped = (line.strip() for line in in_file)
                    lines = (line.split(" ") for line in stripped if line)
                    with open(path+os.path.splitext(file)[0].replace('"', "'")+'.csv', 'w') as out_file:
                        writer = csv.writer(out_file, delimiter=";")
                        writer.writerows(lines)

    import os
    import numpy as np
    import subprocess
    from numpy import genfromtxt
                        
    comps = []
    b=[]
    j=0


    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)


    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                with open(path+file, 'r') as in_file:
                    b.append(list(os.path.basename(path+file).split(".csv")))
                    dim = len(b[j][0].split("',"))
                    reader = csv.reader(in_file, delimiter=';')
                    headers = np.array(next(reader))
                    headers = headers.reshape(1,headers.shape[0])
                    data = np.array(list(reader)).astype(float)
                    mat = np.concatenate((headers, data), axis=0)
                    j = j + 1
                    if dim == 1:
                        rep = data.shape[0] - 1
                        comp1 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[0].replace("'","")).reshape(1,1)
                        if hasNumbers(str(comp1[-1])):
                            char = str(comp1).split("'")[1]
                            while char[-1].isdigit():
                                comp1 = np.array(char[:-1]).reshape(1,1)
                                char = char[:-1]
                        header1 = np.array('comp1').reshape(1,1)
                        comps.append(comp1[0][0])
                        if rep > 0:
                            compCol1 = np.repeat(comp1,rep+1).reshape(rep+1,1)
                            col1 = np.concatenate((header1, compCol1), axis=0)
                            matriz_final = np.concatenate((mat, col1), axis=1)
                        else: 
                            col1 = np.concatenate((header1, comp1), axis=0)
                            matriz_final = np.concatenate((mat, col1), axis=1)
                    if dim == 2:
                        rep = data.shape[0] - 1
                        comp1 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[0].replace("'","")).reshape(1,1)
                        comp2 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[1].replace("'","").replace(" ", "",1)).reshape(1,1)
                        if hasNumbers(str(comp2[-1])):
                            char = str(comp2).split("'")[1]
                            while char[-1].isdigit():
                                comp2 = np.array(char[:-1]).reshape(1,1)
                                char = char[:-1]
                        header1 = np.array('comp1').reshape(1,1)
                        header2 = np.array('comp2').reshape(1,1)
                        comps.append(comp1[0][0])
                        comps.append(comp2[0][0])
                        if rep > 0:
                            compCol1 = np.repeat(comp1,rep+1).reshape(rep+1,1)
                            compCol2 = np.repeat(comp2,rep+1).reshape(rep+1,1)
                            col1 = np.concatenate((header1, compCol1), axis=0)
                            col2 = np.concatenate((header2, compCol2), axis=0)
                            matriz = np.concatenate((mat, col1), axis=1)
                            matriz_final = np.concatenate((matriz, col2), axis=1)
                        else: 
                            col1 = np.concatenate((header1, comp1), axis=0)
                            col2 = np.concatenate((header2, comp2), axis=0)
                            matriz = np.concatenate((mat, col1), axis=1)
                            matriz_final = np.concatenate((matriz, col2), axis=1)
                    if dim == 3:
                        rep = data.shape[0] - 1
                        comp1 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[0].replace("'","")).reshape(1,1)
                        comp2 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[1].replace("'","").replace(" ", "",1)).reshape(1,1)
                        comp3 = np.array(file.split("'.*'")[0].split(".csv")[0].split("',")[2].replace("'","").replace(" ", "",1)).reshape(1,1)
                        if hasNumbers(str(comp3[-1])):
                            char = str(comp3).split("'")[1]
                            while char[-1].isdigit():
                                comp3 = np.array(char[:-1]).reshape(1,1)
                                char = char[:-1]
                        header1 = np.array('comp1').reshape(1,1)
                        header2 = np.array('comp2').reshape(1,1)
                        header3 = np.array('comp3').reshape(1,1)
                        comps.append(comp1[0][0])
                        comps.append(comp2[0][0])
                        comps.append(comp3[0][0])
                        if rep > 0:
                            compCol1 = np.repeat(comp1,rep+1).reshape(rep+1,1)
                            compCol2 = np.repeat(comp2,rep+1).reshape(rep+1,1)
                            compCol3 = np.repeat(comp3,rep+1).reshape(rep+1,1)
                            col1 = np.concatenate((header1, compCol1), axis=0)
                            col2 = np.concatenate((header2, compCol2), axis=0)
                            col3 = np.concatenate((header3, compCol3), axis=0)
                            matriz = np.concatenate((mat, col1), axis=1)
                            matriz2 = np.concatenate((matriz, col2), axis=1)
                            matriz_final = np.concatenate((matriz2, col3), axis=1)
                        else: 
                            col1 = np.concatenate((header1, comp1), axis=0)
                            col2 = np.concatenate((header2, comp2), axis=0)
                            col3 = np.concatenate((header3, comp3), axis=0)
                            matriz = np.concatenate((mat, col1), axis=1)
                            matriz2 = np.concatenate((matriz, col2), axis=1)
                            matriz_final = np.concatenate((matriz2, col3), axis=1)
                    np.savetxt(path+file.split(".csv")[0]+'.csv', matriz_final, delimiter=";", fmt='%s')
             
    with open(path+"comp_list.dat", "w") as output:
        for line in comps:
            output.write(str(line)+'\n')

    subprocess.call(['java', '-jar', 'opsin-2.4.0-jar-with-dependencies.jar', '-osmi', path+'comp_list.dat', path+'comp_smiles.dat'])             

    with open(path+'comp_list.dat') as f:
        cmpds = f.read().splitlines()
    with open(path+'comp_smiles.dat') as g:
        smiles = g.read().splitlines()

    dictionary = {}
    for i in range(len(cmpds)):
        dictionary[cmpds[i]] = smiles[i]
    
    
    j=0
    b=[]
    dim=0


    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:     
                b.append(list(os.path.basename(path+file).split(".csv")))
                dim = len(b[j][0].split("',"))
                f = open(path+file)
                reader = csv.reader(f, delimiter=";")
                headers = np.array(next(reader, None))
                headers = headers.reshape(1,headers.shape[0])
                lines = [line for line in reader]
                nr_lines = len(lines)
                data = np.array(lines).reshape(nr_lines, headers.shape[1])
                mat = np.concatenate((headers, data), axis=0)
                j = j + 1
                if dim == 1:
                    rep = nr_lines - 1
                    comp1 = np.array(file.split("'.*'")[0].split(".csv")[0].split("';")[0].replace("'","")).reshape(1,1)
                    if hasNumbers(str(comp1[-1])):
                        char = str(comp1).split("'")[1]
                        while char[-1].isdigit():
                            comp1 = np.array(char[:-1]).reshape(1,1)
                            char = char[:-1]
                    header1 = np.array('smiles1').reshape(1,1)
                    if rep > 0:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        compCol1 = np.repeat(smiles1,rep+1).reshape(rep+1,1)
                        matriz_final = np.concatenate((mat, compCol1), axis=1)
                    else:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        col1 = np.concatenate((header1, smiles1), axis=0)
                        matriz_final = np.concatenate((mat, col1), axis=1)
                if dim == 2:
                    rep = nr_lines - 1
                    comp1 = np.array(file.split(".csv")[0].split("',")[0].replace("'","")).reshape(1,1)
                    comp2 = np.array(file.split(".csv")[0].split("',")[1].replace("'","").strip()).reshape(1,1)
                    if hasNumbers(str(comp2[-1])):
                        char = str(comp2).split("'")[1]
                        while char[-1].isdigit():
                            comp2 = np.array(char[:-1]).reshape(1,1)
                            char = char[:-1]
                    header1 = np.array('smiles1').reshape(1,1)
                    header2 = np.array('smiles2').reshape(1,1)
                    if rep > 0:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        smiles2 = np.array(dictionary[str(comp2).split("'")[1]]).reshape(1,1)
                        compCol1 = np.repeat(smiles1,rep+1).reshape(rep+1,1)
                        compCol2 = np.repeat(smiles2,rep+1).reshape(rep+1,1)
                        col1 = np.concatenate((header1, compCol1), axis=0)
                        col2 = np.concatenate((header2, compCol2), axis=0)
                        matriz = np.concatenate((mat, col1), axis=1)
                        matriz_final = np.concatenate((matriz, col2), axis=1)
                    else:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        smiles2 = np.array(dictionary[str(comp2).split("'")[1]]).reshape(1,1)
                        col1 = np.concatenate((header1, smiles1), axis=0)
                        col2 = np.concatenate((header2, smiles2), axis=0)
                        matriz = np.concatenate((mat, col1), axis=1)
                        matriz_final = np.concatenate((matriz, col2), axis=1)
                if dim == 3:
                    rep = nr_lines - 1
                    comp1 = np.array(file.split(".csv")[0].split("',")[0].replace("'","")).reshape(1,1)
                    comp2 = np.array(file.split(".csv")[0].split("',")[1].replace("'","").strip()).reshape(1,1)
                    comp3 = np.array(file.split(".csv")[0].split("',")[2].replace("'","").strip()).reshape(1,1)
                    if hasNumbers(str(comp3[-1])):
                        char = str(comp3).split("'")[1]
                        while char[-1].isdigit():
                            comp3 = np.array(char[:-1]).reshape(1,1)
                            char = char[:-1]
                    header1 = np.array('smiles1').reshape(1,1)
                    header2 = np.array('smiles2').reshape(1,1)
                    header3 = np.array('smiles3').reshape(1,1)
                    if rep > 0:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        smiles3 = np.array(dictionary[str(comp2).split("'")[1]]).reshape(1,1)
                        smiles2 = np.array(dictionary[str(comp3).split("'")[1]]).reshape(1,1)
                        compCol1 = np.repeat(smiles1,rep+1).reshape(rep+1,1)
                        compCol2 = np.repeat(smiles2,rep+1).reshape(rep+1,1)
                        compCol3 = np.repeat(smiles3,rep+1).reshape(rep+1,1)
                        col1 = np.concatenate((header1, compCol1), axis=0)
                        col2 = np.concatenate((header2, compCol2), axis=0)
                        col3 = np.concatenate((header3, compCol3), axis=0)
                        matriz = np.concatenate((mat, col1), axis=1)
                        matriz2 = np.concatenate((matriz, col2), axis=1)
                        matriz_final = np.concatenate((matriz2, col3), axis=1)
                    else:
                        smiles1 = np.array(dictionary[str(comp1).split("'")[1]]).reshape(1,1)
                        smiles3 = np.array(dictionary[str(comp2).split("'")[1]]).reshape(1,1)
                        smiles2 = np.array(dictionary[str(comp3).split("'")[1]]).reshape(1,1)
                        col1 = np.concatenate((header1, smiles1), axis=0)
                        col2 = np.concatenate((header2, smiles2), axis=0)
                        col3 = np.concatenate((header3, smiles3), axis=0)
                        matriz = np.concatenate((mat, col1), axis=1)
                        matriz2 = np.concatenate((matriz, col2), axis=1)
                        matriz_final = np.concatenate((matriz2, col3), axis=1)
                np.savetxt(path+'/data/'+file, matriz_final, delimiter=";", fmt='%s')
    

label7 = Label(root, text="Encode chemical structure")
label7.pack()
    
button8 = Button(text = "SMILES", command = smiles)
button8.pack()

button = Button(text = "Quit", command = close_window)
button.pack()

root.mainloop()
