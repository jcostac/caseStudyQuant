import pandas as pd
import numpy as np

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    
    Parameters:
    data (pd.Series): Price data
    window (int): Window size for calculation
    
    Returns:
    pd.Series: Simple Moving Average
    """
    return data.rolling(window=window).mean()

def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    
    Parameters:
    data (pd.Series): Price data
    window (int): Window size for calculation
    
    Returns:
    pd.Series: Exponential Moving Average
    """
    return data.ewm(span=window, adjust=False).mean()

def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: int = 2) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands
    
    Parameters:
    data (pd.Series): Price data
    window (int): Window size for calculation (default: 20)
    num_std (int): Number of standard deviations (default: 2)
    
    Returns:
    tuple: (upper_band, middle_band, lower_band)
    """
    sma = calculate_sma(data, window) #calculate the simple moving average (20 days)
    std = data.rolling(window=window).std() #calculate the rolling standard deviation (20 days)
    upper_band = sma + (std * num_std) #calculate the upper band
    lower_band = sma - (std * num_std) #calculate the lower band
    return upper_band, sma, lower_band

def calculate_peak_offpeak_spread(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the spread between peak and off-peak hours.
    Peak hours are defined as 6:00-9:59 and 19:00-22:59 for all days.
    
    Parameters:
    df (pd.DataFrame): DataFrame with datetime index and 'PRECIO' column
    
    Returns:
    pd.Series: Spread between peak and off-peak prices
    """

    # Define morning and evening peak masks
    morning_peak = (df['DATETIME'].dt.hour >= 6) & (df['DATETIME'].dt.hour < 10)
    evening_peak = (df['DATETIME'].dt.hour >= 19) & (df['DATETIME'].dt.hour < 23)
    peak_mask = morning_peak | evening_peak #combine the masks
    offpeak_mask = ~peak_mask #opposite of peak_mask
    
    # Calculate average prices for each period
    peak_prices = df.loc[peak_mask, 'PRECIO'] #mask rows where HORA is in peak_hours
    offpeak_prices = df.loc[offpeak_mask, 'PRECIO'] #mask rows where HORA is not in peak_hours
    
    # Calculate the spread (peaks - offpeak)
    spread = pd.Series(index=df.index, dtype='float64')
    spread[peak_mask] = peak_prices - offpeak_prices.mean() #calculate the spread for the peak hours
    spread[offpeak_mask] = peak_prices.mean() - offpeak_prices #calculate the spread for the offpeak hours
    
    return spread