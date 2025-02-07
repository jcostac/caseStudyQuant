import os
from pathlib import Path

# API Settings
ESIOS_TOKEN = "df72d87995436ae960ef8e319af2da024aad7c81450d405752dc45199b020cf6"

# Base project directory (where config.py is located)
PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# File paths configuration
PATHS = {
    # precios diarios
    'downloads': {
        'dir': PROJECT_DIR / 'downloads',
        'price_data': PROJECT_DIR / 'downloads' / 'precios_diarios_2020-01-01_2025-02-04.csv'
    },
    
    # grafica precios diarios
    'graphs': {
        'dir': PROJECT_DIR / 'graficas',
        'price_graph': PROJECT_DIR / 'graficas' / 'grafica_precios.png',
        'profit_per_mwh': PROJECT_DIR / 'graficas' / 'profit_per_mwh.png',
        'profit_per_mw': PROJECT_DIR / 'graficas' / 'profit_per_mw.png',
        'beneficio': PROJECT_DIR / 'graficas' / 'beneficio.png'
    }, 

    # optimizacion
    'optimization': {
        'dir': PROJECT_DIR / 'optimizacion',
        'results': PROJECT_DIR / 'optimizacion' / 'results.csv'
    }
}

#Run once before running the program to create the directories
for directory in PATHS.values(): #for every key in the paths dictionary
    if 'dir' in directory: #check if the dirrecotry key exists
        directory['dir'].mkdir(parents=True, exist_ok=True) #create the parent directory if it doesn't exist
