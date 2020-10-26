import altair as alt
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd


#-------------------------------------------------------------------------------
# Plot using Altair
#-------------------------------------------------------------------------------

def plot_value_of_investment(user_data, baselines):
    data = pd.DataFrame({
        'date': [ datetime.fromtimestamp(ts) for ts in user_data.timestamp ] * 3,
        'value': user_data['total_value'].tolist() + baselines['hold_rune'].tolist() + baselines['hold_asset'].tolist(),
        'type': ['LP'] * len(user_data) + ['hold_rune'] * len(user_data) + ['hold_asset'] * len(user_data)
    })

    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('date', axis=alt.Axis(format='%_m/%_d')),
        y=alt.Y('value', axis=alt.Axis(format='$d'), scale=alt.Scale(domain=[min(data.value), max(data.value)])),
        color='type'
    )
    chart.height = 500
    return chart


def plot_pool_rewards(user_data):
    data = pd.DataFrame({
        'date': [ datetime.fromtimestamp(ts) for ts in user_data.timestamp ] * 3,
        'gains/losses': user_data['fee_accrual'].tolist() + user_data['imperm_loss'].tolist() + user_data['total_gains'].tolist(),
        'type': ['fee_accrual'] * len(user_data) + ['imperm_loss'] * len(user_data) + ['total_gains'] * len(user_data)
    })

    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('date', axis=alt.Axis(format='%_m/%_d')),
        y=alt.Y('gains/losses', axis=alt.Axis(format='%')),
        color='type'
    )
    chart.height = 500
    return chart


def plot_gains_breakdown(breakdown):
    data = pd.DataFrame({
        'type': ['rune_movement', 'asset_movement', 'fee_accrued', 'imperm_loss', 'total_gains'],
        'value': [
            breakdown['rune_movement']['value'],
            breakdown['asset_movement']['value'],
            breakdown['fees']['value'],
            breakdown['imp_loss']['value'],
            sum([
                breakdown['rune_movement']['value'],
                breakdown['asset_movement']['value'],
                breakdown['fees']['value'],
                breakdown['imp_loss']['value']
            ])
        ]
    })
    print(data)

    bars = alt.Chart(data).mark_bar().encode(
        x='type',
        y='value'
    )
    text = bars.mark_text(
        align='center',
        baseline='top'
    ).encode(
        text='value'
    )
    bars.height = 500
    return bars + text


def plot_future_gains_breakdown(fee_accrual, imperm_loss, total_gains):
    return None


#-------------------------------------------------------------------------------
# Deprecated: plot using Matplotlib
#-------------------------------------------------------------------------------

def plot_gains_breakdown_pyplot(user_data):
    # Timestamps to datetime object
    dates = [ datetime.fromtimestamp(ts) for ts in user_data.timestamp ]

    # Decimals to percentages
    fee_accrual = [ fee * 100 for fee in user_data.fee_accrual ]
    imperm_loss = [ il * 100 for il in user_data.imperm_loss ]
    total_gains = [ tot * 100 for tot in user_data.total_gains ]

    data = pd.DataFrame({
        'dates': dates,
        'fee_accrual': fee_accrual,
        'imperm_loss': imperm_loss,
        'total_gains': total_gains
    })

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(data.dates, data.fee_accrual, color='magenta', label='Fee accrual')
    ax.plot(data.dates, data.imperm_loss, color='blue', label='Impermanent loss')
    ax.plot(data.dates, data.total_gains, color='red', label='Total gains')

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())  # Y-axis: use percentage
    plt.axhline(0, color='black', linewidth=0.5)            # Horizontal line at y = 0
    plt.xticks(rotation=25)                                 # Tilt x-axis labels
    plt.subplots_adjust(bottom=0.2)
    ax.legend()
    plt.tight_layout()
    # plt.show()

    return fig


def plot_gains_breakdown_pyplot(breakdown):
    types = [
        'rune_move',
        'asset_move',
        'fee_accrued',
        'imperm_loss',
        'total_gains'
    ]
    values = [
        breakdown['rune_movement']['value'],
        breakdown['asset_movement']['value'],
        breakdown['fees']['value'],
        breakdown['imp_loss']['value'],
        breakdown['total']['value']
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    barlist = plt.bar(range(len(types)), values)

    # Set bar colors - green if positive, red if negative, magenta for total
    for bar, val in zip(barlist[:-1], values[:-1]):
        bar.set_color('g' if val >=0 else 'r')
    barlist[-1].set_color('magenta')

    # https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
    for rect, val in zip(ax.patches, values):
        y = rect.get_height()
        x = rect.get_x() + rect.get_width() / 2

        spacing = 2.5 if val >= 0 else -2.5
        va = 'bottom' if val >=0 else 'top'
        label = '{}${:,.2f}'.format('+' if val >= 0 else '-', abs(val))

        ax.annotate(
            label,
            (x, y),
            xytext=(0, spacing),
            textcoords='offset points',
            ha='center',
            va=va
        )

    plt.ylabel('Value ($)')
    plt.xticks(range(len(types)), types)
    plt.axhline(0, color='black', linewidth=1)  # Horizontal line at y = 0
    return fig
