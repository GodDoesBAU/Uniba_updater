#!/usr/bin/env python3


import os
import re
import subprocess
import sys
import time
# import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#per scopi futuri
#Questa funzione controlla una lista di elementi e se è stata dichiarata una regola di filtraggio
#restituisce solo gli elementi che la rispettano
def formatta_output(output, regex=None):
    assert type(output)==list, 'the output parameter need to be a list'

    #se l'output non è filtrato elimino l'ultimo elemento(sempre vuoto) e lo restituisco
    if not regex:
        output.pop()
        return output

    #altrimenti creo una lista in cui inserire i dati filtrati e restituisco quella
    data = list()
    pattern = re.compile(regex)
    for line in output:
        match = pattern.search(line)
        if match:
            if pattern.groups > 0:
                set = list()
                for i in range(0, pattern.groups):
                    if match.group(i + 1) is not None:
                        set.append(match.group(i + 1))
                data.append(set)
            else:
                data.append(line)

    return data
#per scopi futuri
#Questa funzione esegue un comando sulla shell restituendone il risultato, filtrato con una regola dove necessario
def shell_output(command, regex=None):
    output = subprocess.check_output(command)
    lines = output.decode().split('\n')
    return formatta_output(lines, regex)

def download_wait(path_to_downloads,timeout):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds

def scarica_appunti(username,materia,link,Xpath_elemento,timeout):
    # creo webdriver object
    download_path="/home/"+username+"/Documents/"+materia
    prefs = {"download.default_directory" : download_path}
    options = webdriver.ChromeOptions()

    options.add_argument("user-data-dir=/home/"+username+"/Documents/BrowserSession")
    options.add_experimental_option("prefs",prefs)

    driver = webdriver.Chrome(options=options)

    driver.get(link)
    delay = 3

    try:
        appunti=WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, Xpath_elemento)))
        appunti.click()
        if(download_wait(download_path,timeout)>=timeout):
            raise TimeoutException
    except TimeoutException:
        print("Qualquadra non cosa")

def rimuovo_appunti_vecchi(username,materia,regex=None):
    if(os.path.exists(materia)):
        oldfiles=shell_output(['ls', materia],regex)
        if(len(oldfiles)>0):
            for file in oldfiles:
                subprocess.run(['rm', materia+'/'+file])
            print("Gli appunti vecchi sono stati rimossi")

user=os.environ.copy()['USER']
risorse=open('dati.txt')
dati=eval(risorse.readline())
rimuovo_appunti_vecchi(user,dati['materia'])
scarica_appunti(user,dati['materia'],dati['link'],dati['Xpath_elemento'],20)
