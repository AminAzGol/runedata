from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


__all__ = [ 'plot_gains_breakdown' ]


def plot_gains_breakdown(user_data):
    # Timestamps to datetime object
    dates = [ datetime.fromtimestamp(ts) for ts in user_data.timestamp ]

    # Decimals to percentages
    fee_accrual = [ fee * 100 for fee in user_data.fee_accrual ]
    imperm_loss = [ il * 100 for il in user_data.imperm_loss ]
    total_gains = [ tot * 100 for tot in user_data.total_gains ]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(dates, fee_accrual, color='magenta', label='Fee accrual')
    ax.plot(dates, imperm_loss, color='blue', label='Impermanent loss')
    ax.plot(dates, total_gains, color='red', label='Total gains')

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())  # Y-axis: use percentage
    plt.axhline(0, color='black', linewidth=0.5)            # Horizontal line at y = 0
    plt.xticks(rotation=25)                                 # Tilt x-axis labels
    plt.subplots_adjust(bottom=0.2)
    ax.legend()
    plt.tight_layout()
    # plt.show()

    return fig
