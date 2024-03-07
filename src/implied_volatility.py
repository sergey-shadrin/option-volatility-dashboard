import math
import numpy as np
from scipy.stats import norm

OPTION_TYPE_CALL = 'C'
OPTION_TYPE_PUT = 'P'


def inflexion_point(S, K, T, r):
    m = S / (K * math.exp(-r * T))
    return math.sqrt(2 * np.abs(math.log(m)) / T)


def option_price(S, sigma, K, T, r, option_type=OPTION_TYPE_CALL):
    d1 = (math.log(S / K) + (r + .5 * sigma ** 2) * T) / (sigma * T ** .5)
    d2 = d1 - sigma * T ** 0.5
    price = 0
    if option_type == OPTION_TYPE_CALL:
        n1 = norm.cdf(d1)
        n2 = norm.cdf(d2)
        DF = math.exp(-r * T)
        price = S * n1 - K * DF * n2
    elif option_type == OPTION_TYPE_PUT:
        n1 = norm.cdf(-d1)
        n2 = norm.cdf(-d2)
        DF = math.exp(-r * T)
        price = K * DF * n2 - S * n1
    return price


def vega(S, sigma, K, T, r, option_type=OPTION_TYPE_CALL):
    d1 = (math.log(S / K) + (r + .5 * sigma ** 2) * T) / (sigma * T ** .5)
    v = 0
    if option_type == OPTION_TYPE_CALL:
        v = S * T ** 0.5 * norm.pdf(d1)
    elif option_type == OPTION_TYPE_PUT:
        v = S * T ** 0.5 * norm.pdf(-d1)
    return v


def implied_vol(C, S, K, r, T, tol, option_type=OPTION_TYPE_CALL):
    x0 = inflexion_point(S, K, T, r)
    p = option_price(S, x0, K, T, r, option_type)
    v = vega(S, x0, K, T, r, option_type)

    while abs((p - C) / v) > tol:
        x0 = x0 - (p - C) / v
        p = option_price(S, x0, K, T, r, option_type)
        v = vega(S, x0, K, T, r, option_type)
        if not v:
            return None
    return x0
