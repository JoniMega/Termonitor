import itertools

import psutil
import shutil
import time
import os
import datetime
import csv
import sys
import plotext as plt
import pyamdgpuinfo
from prettytable import PrettyTable
from sympy.strategies.core import switch

from baseDades import guardar_temp_gpu, creacio_base_dades, lectura_base_dades
from configurador import create_config, read_config


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def taula(limit, dades, max_linies):

    aux = PrettyTable(field_names = ['PROGRAMA', 'CPU', 'RAM'], min_table_width=limit, max_table_width=limit)

    aux.align['PROGRAMA'] = 'l'
    aux.align['CPU'] = 'r'
    aux.align['RAM'] = 'r'
    for i in dades:
        aux.add_row(i)
        if max_linies-9 < len(aux.rows):
            break

    return aux.get_string()

def barra(limit, percentatge = 0, titol = '', titolmin = 0, sufix = '', sufixmin = 0):
    aux = ''    

    if len(titol) < titolmin:
        for i in range(0,titolmin-len(titol)):
            aux = aux + ' '
    aux = aux + '|'

    if len(sufix) < sufixmin:
        for i in range(0,sufixmin-len(sufix)):
            sufix = ' ' + sufix

    midaBarra = limit-2-max(len(titol),titolmin)-len(sufix)

    for lin in range(0,midaBarra):
        if lin/midaBarra < percentatge:
            aux = aux + '█'
        else:
            aux = aux + ' '
    
    return titol + aux + '|' + sufix

def barra_carrega(columnes, titol, titolmin = 0, carrega = 0, warning = 90, danger = 100, limit = 100, unitat = '', unitatmin = 0, truncatge = True):
    if truncatge:
        if carrega >= warning and carrega < danger:
            aux = bcolors.WARNING + barra(columnes, carrega/limit, titol, titolmin, (str(int(carrega)) + unitat), unitatmin) + bcolors.ENDC
        elif carrega >= danger:
            aux = bcolors.FAIL + barra(columnes, carrega/limit, titol, titolmin, (str(int(carrega)) + unitat), unitatmin) + bcolors.ENDC
        else:
            aux = barra(columnes, carrega/limit, titol, titolmin, (str(int(carrega)) + unitat), unitatmin)
    else:
        if carrega >= warning and carrega < danger:
            aux = bcolors.WARNING + barra(columnes, carrega/limit, titol, titolmin, (str(carrega) + unitat), unitatmin) + bcolors.ENDC
        elif carrega >= danger:
            aux = bcolors.FAIL + barra(columnes, carrega/limit, titol, titolmin, (str(carrega) + unitat), unitatmin) + bcolors.ENDC
        else:
            aux = barra(columnes, carrega/limit, titol, titolmin, (str(carrega) + unitat), unitatmin)
    return aux

def minim_byte(bytes):
    if int(bytes) < 0:
        return (bytes, 0)

    cont = 0
    while (int(bytes) > 0):
        bytes = bytes / 1024
        cont = +1
    return (bytes * 1024, cont)

def sort_CPU(e):
  return e[1]

def llistat_processos(process_iter):
    llistatprocessos = list()

    for process in process_iter:
        cpu =process.cpu_percent()
        memo = process.memory_percent()
        if cpu >= 1 or  memo >= 1:
            llistatprocessos.append([process.name(),cpu,int(memo)])

    llistatprocessos.sort(key=sort_CPU, reverse=True)
    return llistatprocessos

############################################################################################


buffer = []
os.system('cls' if os.name == 'nt' else 'clear')

_mode_ajuda = False
_mode_guardar = False
_mode_grafica = False
_mode_net = False
_mode_debug = False
_mode_config = False

n_arguments = len(sys.argv)

for argument in range(1, n_arguments):
    if sys.argv[argument] in ('-h','-help'):
        _mode_ajuda = True
    if sys.argv[argument] == '-s':
        _mode_guardar = True
    if sys.argv[argument] == '-g':
        _mode_grafica = True
    if sys.argv[argument] == '-n':
        _mode_net = True
    if sys.argv[argument] == '-d':
        _mode_debug = True
    if sys.argv[argument] == '-c':
        _mode_config = True

print('-----Inicialització-----')
if _mode_ajuda:
    print('usage: ' + sys.argv[0] + ' [option]')
    print('Options list:\n-h\t: print this help message and exit\n-s\t: Storing Mode enabled')
    sys.exit()
if _mode_guardar:
    print('Mode Guardar Dades: ' + bcolors.OKBLUE + 'Activat' + bcolors.ENDC)
else:
    print('Mode Guardar Dades: Desactivat')
time.sleep(0.5)
if _mode_grafica:
    print('Mode Gràfica: ' + bcolors.OKBLUE + 'Activat' + bcolors.ENDC)
else:
    print('Mode Gràfica: Desactivat')
time.sleep(0.5)
if _mode_net:
    print('Mode Internet: ' + bcolors.OKBLUE + 'Activat' + bcolors.ENDC)
else:
    print('Mode Internet: Desactivat')
time.sleep(0.5)
if _mode_debug:
    print('Mode Debug: ' + bcolors.OKBLUE + 'Activat' + bcolors.ENDC)
else:
    print('Mode Debug: Desactivat')
time.sleep(0.5)
if _mode_config:
    print('Mode Reconfiguració: ' + bcolors.OKBLUE + 'Activat' + bcolors.ENDC)
else:
    print('Mode Reconfiguració: Desactivat (es pot activar posant el parametre -c)')

time.sleep(2)
historial_temp_gpu = list()


def pregunta(llistat, preg = ''):
    for i in range(0,len(llistat)):
        print(str(i+1) + '. ' + str(llistat[i]))
    while True:
        resposta = input(preg)
        if resposta is not None and resposta != '' and resposta.isdigit():
            break
    return llistat[int(resposta)-1]


def ini_config():
    origen_temp = list(psutil.sensors_temperatures().keys())
    origen_net = list(psutil.net_if_stats().keys())
    idiomes = list(['cat', 'eng'])
    os.system('cls' if os.name == 'nt' else 'clear')
    idioma = pregunta(llistat=idiomes, preg='Escriu el num del sensor del idioma: ')
    os.system('cls' if os.name == 'nt' else 'clear')
    gpu = pregunta(llistat=origen_temp, preg='Escriu el num del sensor de la GPU: ')
    os.system('cls' if os.name == 'nt' else 'clear')
    cpu = pregunta(llistat=origen_temp, preg='Escriu el num del sensor de la CPU: ')
    os.system('cls' if os.name == 'nt' else 'clear')
    net = pregunta(llistat=origen_net, preg='Escriu el num de la interfície d\'internet: ')

    return {'idioma': idioma, 'sensor_gpu': gpu, 'sensor_cpu': cpu, 'interficie_net': net}


if _mode_debug:
    config = {'idioma': 'cat', 'sensor_gpu': 'amdgpu', 'sensor_cpu': 'k10temp', 'interficie_net': 'eno1'}
    #create_config(idioma='cat', sensor_gpu='amdgpu', sensor_cpu='k10temp')
else:
    config = read_config()
    if config.get('idioma') == 'None' or _mode_config:
        config = ini_config()
    create_config(idioma=config.get('idioma'), sensor_gpu=config.get('sensor_gpu'), sensor_cpu=config.get('sensor_cpu'))


if _mode_guardar or _mode_grafica:
    creacio_base_dades()
    if _mode_grafica:
        lectura_base_dades()

time.sleep(2)

max_net = psutil.net_if_stats().get('eno1').speed
in_net = psutil.net_io_counters(pernic=True, nowrap=True).get(config.get('interficie_net')).bytes_recv
out_net = psutil.net_io_counters(pernic=True, nowrap=True).get(config.get('interficie_net')).bytes_sent
time_net = datetime.datetime.now()
vel_in_net = 0
vel_out_net = 0

max_memo_cpu = psutil.virtual_memory().total / (1024 ** 3)

first_gpu = pyamdgpuinfo.get_gpu(0)
max_vram_gpu = round(first_gpu.memory_info.get('vram_size')/(1024**3))

while (True):
    temps = datetime.datetime.now()

    mida = shutil.get_terminal_size()
    altura_utilitzada = 0
    temp_gpu = psutil.sensors_temperatures().get(config.get('sensor_gpu'))[1][1]
    temp_cpu = psutil.sensors_temperatures().get(config.get('sensor_cpu'))[0][1]
    memo_cpu = psutil.virtual_memory().used/(1024**3)
    vram_gpu = first_gpu.query_vram_usage()/(1024**3)
    powr_gpu = first_gpu.query_power()


    if _mode_net:
        in_net = psutil.net_io_counters(pernic=True, nowrap=True).get('eno1').bytes_recv - in_net
        out_net = psutil.net_io_counters(pernic=True, nowrap=True).get('eno1').bytes_sent - out_net
        vel_in_net = in_net/(datetime.datetime.now()-time_net).total_seconds()
        vel_out_net = out_net / (datetime.datetime.now() - time_net).total_seconds()
        time_net = datetime.datetime.now()


    if _mode_guardar:
        guardar_temp_gpu(temp_gpu)

    buffer.append(barra_carrega(columnes=mida.columns, titol='TEMP GPU', carrega=temp_gpu, limit=110, warning=100, danger=110, unitat='º', unitatmin=4))
    buffer.append(barra_carrega(columnes=mida.columns, titol='VRAM GPU', carrega=vram_gpu, limit=max_vram_gpu, warning=max_vram_gpu*0.75, danger=max_vram_gpu*0.9, unitat='GB', unitatmin=4))
    buffer.append(barra_carrega(columnes=mida.columns, titol='TEMP CPU', carrega=temp_cpu, limit=100, warning=75, danger=90, unitat='º', unitatmin=4))
    buffer.append(barra_carrega(columnes=mida.columns, titol='MEMO CPU', carrega=memo_cpu, limit=max_memo_cpu, warning=max_memo_cpu*0.75, danger=max_memo_cpu*0.9, unitat='GB',unitatmin=4))
    altura_utilitzada += 4
    buffer.append('-----------------------')

    cont = 1
    cpu_percent = psutil.cpu_percent(percpu=True)
    max_titol = len('CPU ' + str(len(cpu_percent)))

    for cpu in cpu_percent:
        buffer.append(barra_carrega(columnes=mida.columns, titol='CPU ' + str(cont), titolmin=max_titol, carrega=cpu, limit=100, warning=95, danger=100, unitat='%', unitatmin=4))
        cont = cont + 1
        altura_utilitzada += 1

    process_iter = psutil.process_iter()
    buffer.append(taula(limit=mida.columns, dades=llistat_processos(process_iter), max_linies=mida.lines-altura_utilitzada))

    if _mode_net:
        buffer.append('-----------------------')
        buffer.append(barra_carrega(columnes=mida.columns, titol='NET IN', titolmin=7, carrega=(vel_in_net/(1024**2)), limit=max_net,
                                    warning=max_net * 0.8, danger=max_net * 0.9, unitat='MB/s', unitatmin=6))
        buffer.append(barra_carrega(columnes=mida.columns, titol='NET OUT', titolmin=7, carrega=(vel_out_net/(1024**2)), limit=max_net,
                                    warning=max_net * 0.8, danger=max_net * 0.9, unitat='MB/s', unitatmin=6))



    """
    plt.clear_data()
    plt.plot_size(height=30)
    temperaturesgpu = list()
    temps = list()
    for i in range(0,len(historial_temp_gpu)):
        temperaturesgpu.append(float((historial_temp_gpu[i][1])))
    plt.plot(temperaturesgpu)
    """


    temps_durat = (datetime.datetime.now()-temps).microseconds
    temps_durat_seg = (temps_durat/10**6)
    buffer.append(
        barra_carrega(columnes=mida.columns, titol='Temps', carrega=temps_durat_seg, limit=2,
                      warning=1, danger=2, unitat='s', unitatmin=9, truncatge = False))

    os.system('cls' if os.name == 'nt' else 'clear')
    print('\n'.join(buffer))
    #plt.show()
    buffer.clear()
    if(temps_durat_seg<2):
        time.sleep(2-temps_durat_seg)
    



        
