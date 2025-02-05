import csv
import os
from datetime import datetime
import time


def creacio_base_dades():


    print('Inicialització Base de Dades')
    time.sleep(0.5)
    if not os.path.exists('gpu_temp.csv'):
        os.mknod('gpu_temp.csv')
        print('\t-Fitxer Base de dades Creat')
    else:
        print('\t-Fitxer Base de dades ja existent')
    time.sleep(0.5)

def lectura_base_dades():
    historial_temp_gpu = list()

    print('\t-Llegint Fitxer (gpu_temp.csv)')
    with open('gpu_temp.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        i = 0
        for row in csvreader:
            i = i + 1
            print('\t\t-Linies llegides: ' + str(i), end="\r")
            historial_temp_gpu.append(row)
            time.sleep(0.001)
        csvfile.close()
        print('\t\t-Linies llegides: ' + str(len(historial_temp_gpu)))

    return historial_temp_gpu



def guardar_temp_gpu(temp):
    with open('gpu_temp.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([str(datetime.datetime.now()), str(temp)])

    csvfile.close()