import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS

def graph_prices(prices_df: pd.DataFrame) -> None:
    """
    Generate graphs for price analysis, saves it in the graphs directory
    
    Args:
        df (pd.DataFrame): DataFrame with price data
    """
    # Calculate daily statistics
    daily_stats = prices_df.groupby('FECHA').agg({
        'PRECIO': ['mean', 'min', 'max']
    }).reset_index()
    daily_stats.columns = ['FECHA', 'PRECIO_MEDIO', 'PRECIO_MIN', 'PRECIO_MAX']

    # Create plt figure
    fig = plt.figure(figsize=(15, 15))

    # Set the style to ggplot
    plt.style.use('ggplot')

    # Create a gridspec with 3 rows, and 1 column for more control over subplot placement
    gs = fig.add_gridspec(3, 1, height_ratios=[0.01, 1, 1], hspace=0.4)

    # Add title in its own subplot
    title_ax = fig.add_subplot(gs[0])
    title_ax.set_title('Evolución del Precio Spot de la Electricidad en España (01/01/2020 - 04/02/2025)', 
                      fontsize=16, fontweight='bold')
    title_ax.axis('off')  # Hide the axis

    # Create the two main subplots
    ax1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])

    # Plot 1: Daily Price Range
    ax1.fill_between(daily_stats['FECHA'], 
                    daily_stats['PRECIO_MIN'], 
                    daily_stats['PRECIO_MAX'], 
                    alpha=0.7, 
                    color='skyblue', 
                    label='Rango de Precios')
    ax1.plot(daily_stats['FECHA'], 
            daily_stats['PRECIO_MEDIO'], 
            color='navy', 
            linewidth=1.5, 
            label='Precio Medio Diario')

    # Customize first plot
    ax1.set_title('Evolución del Precio Medio Diario', pad=20)
    ax1.set_ylabel('Precio (€/MWh)')
    ax1.set_ylim(-100, daily_stats['PRECIO_MAX'].max() * 1.1)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    # Format x-axis for better readability
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    for label in ax1.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    # Plot 2: Hourly Pattern
    hourly_avg = prices_df.groupby('HORA')['PRECIO'].mean()
    hours = range(24)

    ax2.bar(hours, hourly_avg, color='skyblue', alpha=0.7)
    ax2.plot(hours, hourly_avg, color='navy', linewidth=2, marker='o')

    # Customize second plot
    ax2.set_title('Precios Medios por Hora', pad=20)
    ax2.set_xlabel('Hora del Día')
    ax2.set_ylabel('Precio Medio (€/MWh)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(hours)
    ax2.set_xticklabels([f'{hour:02d}:00' for hour in hours], rotation=45)

    # Add price labels on the bars
    for i, price in enumerate(hourly_avg):
        ax2.text(i, price + 1, f'{price:.1f}€', ha='center', va='bottom', fontsize=8)

    # Add statistics text
    stats_text = (f'Precio Máximo: {prices_df["PRECIO"].max():.2f}€/MWh\n'
                f'Precio Mínimo: {prices_df["PRECIO"].min():.2f}€/MWh\n'
                f'Precio Medio: {prices_df["PRECIO"].mean():.2f}€/MWh')
    plt.figtext(0.5, 0.02, stats_text, fontsize=10, 
                bbox=dict(facecolor='white', 
                        alpha=0.8, 
                        edgecolor='lightgray',
                        boxstyle='round,pad=0.5'),
                horizontalalignment='center',
                verticalalignment='bottom')

    plt.savefig(PATHS['graphs']['price_graph'], 
                dpi=600,  # High resolution
                bbox_inches='tight', 
                pad_inches=0.5,
                format='png',  # Lossless format
                )
    plt.close()

    print("Price graph saved in ", PATHS['graphs']['price_graph'])

def graph_optimization_results(results_df: pd.DataFrame) -> None:
    """
    Generate graphs for optimization results. Saves them in the graphs directory.
    
    Args:
        results_df (pd.DataFrame): DataFrame with optimization results
    """
    plt.style.use('ggplot')
    
    # FIGURE 1: PROFIT OVER TIME
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Plot positive and negative values separately with different colors
    positive_mask = results_df['net_profit'] >= 0 #ganancia
    negative_mask = results_df['net_profit'] < 0 #perdida
    
    ax.plot(results_df[positive_mask].index, results_df[positive_mask]['net_profit'], 
            color='green', linewidth=2, label='Ganancias')
    ax.plot(results_df[negative_mask].index, results_df[negative_mask]['net_profit'], 
            color='red', linewidth=2, label='Pérdidas')
    
    ax.set_xlabel('Fecha', fontsize=10)
    ax.set_ylabel('Beneficio (€)', fontsize=10)
    ax.set_title('Beneficio Obtenido por la Batería (01/01/2020 - 04/02/2025)', 
                fontsize=12, pad=20, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PATHS['graphs']['beneficio'],
                dpi=600,  # High resolution
                bbox_inches='tight',
                pad_inches=0.5,
                format='png',  # Lossless format
                )
    plt.close()

    print("Benefit graph saved in ", PATHS['graphs']['beneficio'])

    # Calculate number of rows and columns needed for subplots
    years = results_df.index.year.unique()
    n_years = len(years)
    n_cols = 2
    n_rows = (n_years + n_cols - 1) // n_cols

    # FIGURE 2: PROFIT PER MWH Energy Capacity
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    fig.suptitle('Beneficio por MWh de Energía de la Batería por mes (2020 - 2025)', 
                y=1.02, fontsize=16, fontweight='bold')
    
    
    for idx, year in enumerate(years):
        row = idx // n_cols
        col = idx % n_cols
        
        year_data = results_df[results_df.index.year == year]
        monthly_data = year_data.groupby(year_data.index.month)['profit_per_mwh'].sum()
        
        axs[row, col].bar(monthly_data.index, monthly_data.values, color='skyblue')
        axs[row, col].set_title(f'Año {year}', fontsize=10, fontweight='bold')
        axs[row, col].set_xlabel('Mes', fontsize=9)
        axs[row, col].set_ylabel('Beneficio por MWh (€/MWh)', fontsize=9)
        axs[row, col].grid(True, alpha=0.3)
        axs[row, col].tick_params(axis='both', labelsize=8)
        axs[row, col].set_xticks(range(1, 13))
        axs[row, col].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    for idx in range(len(years), n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axs[row, col].set_visible(False)
    
    plt.tight_layout() 
    plt.savefig(PATHS['graphs']['profit_per_mwh'],
                dpi=600,  # High resolution
                bbox_inches='tight',
                pad_inches=0.5,
                format='png',  # Lossless format
                )
    plt.close()

    print("Profit per MWh graph saved in ", PATHS['graphs']['profit_per_mwh'])

    # FIGURE 3: PROFIT PER MW Power Capacity
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    fig.suptitle('Beneficio por MW de Potencia de la Batería por mes (2020 - 2025)', 
                y=1.02, fontsize=16, fontweight='bold')
    
    for idx, year in enumerate(years):
        row = idx // n_cols
        col = idx % n_cols
        
        year_data = results_df[results_df.index.year == year]
        monthly_data = year_data.groupby(year_data.index.month)['profit_per_mw'].sum()
        
        axs[row, col].bar(monthly_data.index, monthly_data.values, color='navy')
        axs[row, col].set_title(f'Año {year}', fontsize=10, fontweight='bold')
        axs[row, col].set_xlabel('Mes', fontsize=9)
        axs[row, col].set_ylabel('Beneficio por MW (€/MW)', fontsize=9)
        axs[row, col].grid(True, alpha=0.3)
        axs[row, col].tick_params(axis='both', labelsize=8)
        axs[row, col].set_xticks(range(1, 13))
        axs[row, col].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    for idx in range(len(years), n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axs[row, col].set_visible(False)
    
    plt.tight_layout() 
    plt.savefig(PATHS['graphs']['profit_per_mw'],
                dpi=600,  # High resolution
                bbox_inches='tight',
                pad_inches=0.5,
                format='png',  # Lossless format
                )
    plt.close()

    print("Profit per MW graph saved in ", PATHS['graphs']['profit_per_mw'])

if __name__ == "__main__":
    # Read the data for prices and optimization results
    prices_df = pd.read_csv(PATHS['downloads']['price_data'])
    results_df = pd.read_csv(PATHS['optimization']['results'])

    # Process prices datetime cols 
    prices_df['FECHA'] = pd.to_datetime(prices_df['FECHA'])
    prices_df['DATETIME'] = pd.to_datetime(prices_df['FECHA'].astype(str) + ' ' + prices_df['HORA'].astype(str) + ':00:00')
    prices_df = prices_df.sort_values('DATETIME')
    
    # Process results dataframe process datetime cols 
    results_df['datetime'] = pd.to_datetime(results_df['datetime'])
    results_df.set_index('datetime', inplace=True)
    
    # Generate price graphs
    graph_prices(prices_df)

    # Generate optimization results graphs
    graph_optimization_results(results_df)
