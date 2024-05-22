# import modules
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import base64
import io

matplotlib.use("agg")


def get_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data


def get_current_risk_free_rate():
    # Define the ticker symbol for the 10-year U.S. Treasury bond
    ticker = "^TNX"

    # Get today and yesterdays date
    today = datetime.today()
    yesterday = today - timedelta(days=5)

    # Convert dates to strings
    today = today.strftime("%Y-%m-%d")
    yesterday = yesterday.strftime("%Y-%m-%d")

    # Attempt to fetch today's data
    data = yf.download(ticker, start=yesterday, end=today)

    # If data is still empty, raise an error
    if data.empty:
        raise ValueError("Failed to retrieve the 10-year Treasury yield data.")

    # Get the latest closing price, which represents the yield
    current_yield = data["Close"].iloc[-1]

    # Convert the yield to a decimal (from percentage)
    risk_free_rate = current_yield / 100

    return risk_free_rate


def get_adj_close_plot(ticker, start_date, end_date):
    # initialize parameters
    # TODO Add Check for inputs
    # start_date = datetime.strptime(start_date)
    # end_date = datetime.strptime(end_date)

    # get the data
    data = get_data(ticker, start_date, end_date)["Adj Close"]

    # display
    plt.figure(figsize=(20, 10))
    plt.plot(data)
    plt.title(
        "{} Adjusted Closing Prices from {} to {}".format(ticker, start_date, end_date)
    )

    # Save as png img
    img = io.BytesIO()
    plt.savefig(img, format="png")

    return img


def get_monte_carlo_plot(ticker, start_date, end_date, trading_days=5, iterations=100):
    # initialize parameters
    # TODO Add Check for inputs
    trading_days = int(trading_days)
    iterations = int(iterations)

    # get the data
    data = get_data(ticker, start_date, end_date)["Adj Close"]

    # Compute the logarithmic returns
    log_returns = np.log(1 + data.pct_change())
    std_dev = log_returns.std() * 250**0.5  # There are 250 trading days in a year

    #
    r = get_current_risk_free_rate()  # annual risk-free interest rate
    T = 1.0  # time horizon (1 year) - i.e. how long you are holding the stock
    t_intervals = trading_days  # The number of trading days you want to simulate
    delta_t = T / t_intervals
    iterations = iterations

    # Set up
    Z = np.random.standard_normal(
        (t_intervals + 1, iterations)
    )  # generate random normal variables to introduce randomness to simulation
    S = np.zeros_like(Z)  # Array of simulated stock prices
    S0 = data.iloc[-1]  # Last observed price of data
    S[0] = S0  # Set the first row as the initial stock price

    # Run simulation of Brownian motion model
    for t in range(1, t_intervals + 1):
        S[t] = S[t - 1] * np.exp(
            (r - 0.5 * std_dev**2) * delta_t + std_dev * delta_t**0.5 * Z[t]
        )

    # display
    plt.figure(figsize=(20, 10))
    plt.plot(S[:, :iterations])
    plt.title(
        "{} Monte Carlo Simulation {} simulations from {} to {}".format(
            ticker, iterations, start_date, end_date
        )
    )

    # Save as png img
    img = io.BytesIO()
    plt.savefig(img, format="png")

    return img
