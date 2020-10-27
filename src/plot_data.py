import altair as alt
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd


#-------------------------------------------------------------------------------
# Value of investment
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


#-------------------------------------------------------------------------------
# Pool rewards
#-------------------------------------------------------------------------------

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


def plot_pool_rewards_pyplot(user_data):
    '''Deprecated! Use altair instead.'''

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


def plot_gains_breakdown_altair(breakdown):
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


#-------------------------------------------------------------------------------
# Matplotlib bar graph helper functions
#-------------------------------------------------------------------------------

def _format_gains_breakdown_data(breakdown):
    types = [
        'rune_move',
        'asset_move',
        'fee_accrued',
        'imperm_loss',
        'net'  # update: call it "net gains" instead of "total gains"
    ]
    values = [
        breakdown['rune_movement']['value'],
        breakdown['asset_movement']['value'],
        breakdown['fees']['value'],
        breakdown['imp_loss']['value'],
        breakdown['total']['value']
    ]
    return types, values


def _set_bar_colors(barlist, values, alpha=1.):
    barlist[-1].set_color((1, 0, 1, alpha))  # magenta
    barlist[-1].set_color((1, 0.682, 0.259, alpha))  # orange

    for bar, val in zip(barlist[:-1], values[:-1]):
        bar.set_color((0, 0.8, 0, alpha) if val >=0 else (1, 0, 0, alpha))

    for bar in barlist:
        bar.set_edgecolor('black')


# https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
def _add_bar_labels(ax, rects, values):
    for rect, val in zip(rects, values):
        y = rect.get_y() + rect.get_height()
        x = rect.get_x() + rect.get_width() / 2

        spacing = 2.5 if val >= 0 else -2.5
        va = 'bottom' if val >=0 else 'top'
        label = '{}${:,.0f}'.format('+' if val >= 0 else '–', abs(val))  # minus sign here is en-dash

        ax.annotate(
            label,
            (x, y),
            xytext=(0, spacing),
            textcoords='offset points',
            ha='center',
            va=va
        )


def _set_ylims(ax):
    bottoms = [ rect.get_y() for rect in ax.patches ]
    tops = [ rect.get_y() + rect.get_height() for rect in ax.patches ]
    diff = max(tops) - min(bottoms)
    y_min = min(bottoms) - 0.1 * diff
    y_max = max(tops) + 0.1 * diff
    ax.set_ylim(y_min, y_max)


#-------------------------------------------------------------------------------
# Current G/L breakdown
#-------------------------------------------------------------------------------

# https://pbpython.com/waterfall-chart.html
def plot_gains_breakdown_waterfall(breakdown):
    types, values = _format_gains_breakdown_data(breakdown)

    trans = pd.DataFrame({'amount': values}, index=types)
    # Get the cumulative sum
    blank = trans.amount.cumsum()
    # Shift the data one place to bottom
    blank = blank.shift(1).fillna(0)

    # Steps to show changes
    step = blank.reset_index(drop=True).repeat(3).shift(-1)
    step[1::3] = np.nan
    blank.loc['net'] = 0

    fig, ax = plt.subplots(figsize=(8, 5))
    barlist = ax.bar(trans.index, trans.amount, bottom=blank)
    ax.plot(step.index, step.values, 'k', linewidth=1)

    _set_bar_colors(barlist, values)
    _set_ylims(ax)
    _add_bar_labels(ax, barlist, values)

    plt.ylabel('Value ($)')
    plt.axhline(0, color='black', linestyle='--', linewidth=1, zorder=0)  # Horizontal line at y = 0 **beneath the bars**
    return fig


def plot_gains_breakdown(breakdown):
    '''Deprecated! Use pyplot waterfall chart instead.'''

    types, values = _format_gains_breakdown_data(breakdown)

    fig, ax = plt.subplots(figsize=(8, 5))
    barlist = ax.bar(types, values)

    _set_bar_colors(barlist, values)
    # _set_ylims(ax)  # _set_ylims only works for waterfall charts
    _add_bar_labels(ax, barlist, values)

    plt.ylabel('Value ($)')
    plt.axhline(0, color='black', linestyle='--', linewidth=1, zorder=0)
    return fig


#-------------------------------------------------------------------------------
# Future G/L breakdown
#-------------------------------------------------------------------------------

def plot_gains_breakdown_compared_waterfall(current_breakdown, future_breakdown):
    types = [
        'rune_move',
        'asset_move',
        'fees',
        'IL',
        'current_net',
        'rune_move',
        'asset_move',
        'fees',
        'IL',
        'future_net'
    ]
    _, current_values = _format_gains_breakdown_data(current_breakdown)
    _, future_values = _format_gains_breakdown_data(future_breakdown)

    for i in range(4):
        future_values[i] -= current_values[i]
    values = current_values + future_values

    trans = pd.DataFrame({'amount': values})
    blank = trans.amount.cumsum().shift(1).fillna(0)

    step = blank.reset_index(drop=True).repeat(3).shift(-1)
    step[1::3] = np.nan
    step_x = step.index.tolist()
    step_y = step.tolist()

    # Adjust
    for idx in range(4, 10):
        blank.loc[idx] -= current_values[-1]
    blank.iloc[-1] -= future_values[-1]
    for idx in range(14, len(step_y)):
        step_y[idx] -= current_values[-1]

    fig, ax = plt.subplots(figsize=(8, 5))
    barlist = ax.bar(trans.index, trans.amount, bottom=blank)
    ax.plot(step_x, step_y, 'k', linewidth=1)

    _set_bar_colors(barlist[:5], values[:5], alpha=0.25)
    _set_bar_colors(barlist[5:], values[5:])
    _set_ylims(ax)
    _add_bar_labels(ax, barlist, values)

    plt.ylabel('Value ($)')
    plt.xticks(range(len(types)), types, rotation=45)
    plt.axhline(0, color='black', linestyle='--', linewidth=1, zorder=0)  # Horizontal line at y = 0 **beneath the bars**
    return fig


# https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/barchart.html
def plot_gains_breakdown_compared(current_breakdown, future_breakdown):
    '''Deprecated! Use pyplot waterfall chart instead.'''

    types, current_values = _format_gains_breakdown_data(current_breakdown)
    _, future_values = _format_gains_breakdown_data(future_breakdown)

    width = 0.45
    ind1 = [ ind - width / 2 for ind in range(len(types)) ]
    ind2 = [ ind + width / 2 for ind in range(len(types)) ]

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(
        ind1, current_values,
        width=width,
        label='Current'
    )
    rects2 = ax.bar(
        ind2, future_values,
        width=width,
        label='Predicted'
    )

    _set_bar_colors(rects1, current_values, alpha=.5)
    _set_bar_colors(rects2, future_values)

    _add_bar_labels(ax, rects1, current_values)
    _add_bar_labels(ax, rects2, future_values)

    plt.ylabel('Value ($)')
    plt.xticks(range(len(types)), types)
    plt.axhline(0, color='black', linestyle='--', linewidth=1, zorder=0)
    plt.legend()

    return fig
