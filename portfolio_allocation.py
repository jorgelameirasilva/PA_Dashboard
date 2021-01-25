from db_consumer import find_in_db
import numpy as np
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.cla import CLA
from pypfopt import plotting as Plotting
from pypfopt import discrete_allocation


def get_allocations(etfs_name, portfolio_value):
    price_data = []
    df_stocks = pd.DataFrame(columns=["ctm", "close"])
    for ticker in range(len(etfs_name)):
        prices = find_in_db(etfs_name[ticker])
        prices["close"] = prices["open"] + prices["close"]
        prices = prices[["ctm", "close"]]
        prices = prices.rename(columns={"close":etfs_name[ticker]})
        if df_stocks.shape[0] == 0:
            df_stocks = prices
        else:
            df_stocks = df_stocks.merge(prices, on="ctm")
    df_stocks.drop("ctm", axis=1, inplace=True)

    mu = expected_returns.mean_historical_return(df_stocks)
    sigma = risk_models.sample_cov(df_stocks)
    ef = EfficientFrontier(mu, sigma, weight_bounds=(-1, 1))
    sharpe = ef.max_sharpe()
    minvol_pwt = ef.clean_weights()
    latest_prices = discrete_allocation.get_latest_prices(df_stocks)
    allocation_minv, rem_minv = discrete_allocation.DiscreteAllocation(minvol_pwt, latest_prices, total_portfolio_value=portfolio_value).lp_portfolio()
    performance = ef.portfolio_performance(verbose=True, risk_free_rate = 0.27)
    allocations_df = pd.DataFrame(allocation_minv, index=["Position(Shares)"])
    allocations_df = allocations_df.T
    allocations_df["Weight"] = allocations_df["Position(Shares)"].abs() / allocations_df["Position(Shares)"].abs().sum()
    allocations_df.reset_index(inplace=True)
    allocations_df.rename(columns={"index":"ETF"}, inplace=True)

    performance = {"return": performance[0], "vol": performance[1], "sharpe":performance[2]}
    performance_df = pd.DataFrame(performance, index=[1])
    return allocations_df, performance_df


if __name__ == "__main__":
    print(get_allocations(["SPY.US_5", "QQQ.US_5", "UUP.US_5", "XRT.US_5", "VNQ.US_5"], 100000))