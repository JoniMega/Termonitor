import configparser


def create_config(idioma = 'None', sensor_gpu = 'None', sensor_cpu = 'None', interficie_net = 'None'):
    config = configparser.ConfigParser()
    # Add sections and key-value pairs
    config['General'] = {'idioma': idioma}
    config['Preferencies'] = {'sensor_gpu': sensor_gpu, 'sensor_cpu': sensor_cpu, 'interficie_net': interficie_net}

    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()


def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    try:
        idioma = config.get('General', 'idioma')
        sensor_gpu = config.get('Preferencies', 'sensor_gpu')
        sensor_cpu = config.get('Preferencies', 'sensor_cpu')
        interficie_net = config.get('Preferencies', 'interficie_net')
    except:
        return {
            'idioma': 'None',
            'sensor_gpu': 'None',
            'sensor_cpu': 'None',
            'interficie_net': 'None'
        }
    # Return a dictionary with the retrieved values
    config_values = {
        'idioma': idioma,
        'sensor_gpu': sensor_gpu,
        'sensor_cpu': sensor_cpu,
        'interficie_net': interficie_net
    }

    return config_values
