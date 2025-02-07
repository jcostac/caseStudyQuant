import requests
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
from typing import List
import pretty_errors
import time
import sys
from pathlib import Path
# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS, ESIOS_TOKEN

class ESIOS:
    """
    The ESIOS class interacts with the ESIOS API to fetch energy market data,
    processes it, and saves it to a CSV file.
    
    Attributes:
        token (str): API token for authenticating requests to the ESIOS API.
        ruta (str): Path to save files.
    """
    def __init__(self, token : str, ruta : str):
        self.token = token
        self.ruta = ruta
            
    def utc_to_local(self, utc_dt : datetime) -> datetime:
        """
        Converts a UTC datetime to local Madrid time.

        Args:
        utc_dt (datetime): The datetime in UTC to be converted.

        Returns:
        datetime: The datetime converted to local Madrid time.
        """
        local_tz = pytz.timezone('Europe/Madrid')
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)
    
    def download_precios(self, start_date : str, end_date : str, indicador : List[int]) -> pd.DataFrame:
        """
        Download daily energy prices from ESIOS API.

        Args:
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            indicador (List[int]): List of indicator IDs to download. In this case, we will use 600 which represents daily energy prices.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the daily energy prices.
        """
        # Initialize empty list to store price records
        registros = []
        
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Process data in 30-day chunks (was getting a 504 timeout error when trying to download all data 2020-2025 at once)
        while start_date <= end_date:

            # Calculate chunk end date (30 days or until end_date)  
            chunk_end = min(start_date + timedelta(days=30), end_date) #min() is used so that chunk size never exceeds end date 
            
            # Convert dates back to string format for API url
            chunk_start_str = start_date.strftime("%Y-%m-%d")
            chunk_end_str = chunk_end.strftime("%Y-%m-%d")
            
            print(f"\nFetching data from {chunk_start_str} to {chunk_end_str}")
            
            # Loop through indicator IDs
            for ind in indicador:
                # Construct API URL with indicator and chunk dates
                url = f'https://api.esios.ree.es/indicators/{ind}?start_date={chunk_start_str}&end_date={chunk_end_str}'
                
                # Prepare headers with API token
                headers = {'x-api-key': self.token}
                
                # Try the request up to 3 times
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Make GET request to ESIOS API
                        response = requests.get(url, headers=headers)
                        response.raise_for_status()  # Raise an error for bad status codes
                        
                        # Parse JSON response
                        datos = json.loads(response.text)
                        
                        # Process each data point in the response
                        for dato in datos['indicator']['values']:
                            # Only process data for Spain (geo_id is 3 for Spain)
                            if dato['geo_id'] == 3:
                                # Create a new record
                                rec = {}
                                
                                # Convert UTC timestamp to datetime object
                                fecha_utc = datetime.strptime(dato['datetime_utc'], "%Y-%m-%dT%H:%M:%SZ")
                                fecha_local = self.utc_to_local(fecha_utc)
                                
                                # Store date and price
                                rec['FECHA'] = fecha_local.strftime("%Y-%m-%d")
                                rec['HORA'] = fecha_local.strftime("%H")  # Add hour information
                                rec['PRECIO'] = dato['value']
                                
                                # Add record to list
                                registros.append(rec)
                        
                        # If successful, break the for loop and continue with the next chunk
                        break 
                        
                    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                        #if the request fails, print the error and wait for 2^attempt seconds before retrying
                        print(f"Attempt {attempt + 1} failed: {str(e)}") 
                        
                        if attempt < max_retries - 1: #-1 since python range is 0-indexed and we already tried once

                            wait_time = 2 ** attempt  # Exponential backoff  (longer wait time for each attempt)
                            print(f"Waiting {wait_time} seconds before retrying...")
                            time.sleep(wait_time)
                        else:
                            print(f"Failed to fetch data after {max_retries} attempts")
            
            # Move to next chunk (start date is 1 day after the end of the current chunk)
            start_date = chunk_end + timedelta(days=1)

        # Convert list of records to pandas DataFrame
        df = pd.DataFrame(registros)
        
        # Sort by date and hour
        if not df.empty:
            df = df.sort_values(['FECHA', 'HORA'])

        return df

    def save_precios(self, df : pd.DataFrame, file_name : str):
        """
        Save the prices to a CSV file.
        """
        file_path = self.ruta + "/" + file_name
        df.to_csv(file_path, index=False)
        print(f"Prices saved to {file_path}")
        return

if __name__ == '__main__':
    # Set the start and end dates for the price data
    start_date = "2020-01-01"  # Start with a more recent date for testing
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Set the indicator ID to download
    indicador = [600]

    # Set the API token and the path to save the files
    token = ESIOS_TOKEN
    ruta = PATHS['downloads']['dir']
    
    # Create an instance of the ESIOS class
    obj = ESIOS(token, ruta)
    
    # Download the daily energy prices
    df_precios_diarios = obj.download_precios(start_date, end_date, indicador)
    file_name = f"precios_diarios_{start_date}_{end_date}.csv"
    
    # Save the daily energy prices to a CSV file
    obj.save_precios(df_precios_diarios, file_name)