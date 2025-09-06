import math

def k_for_linear_tolerance_general(p, delta, top=1, bottom=0, midpoint=0):
    """
    p       : percentile (0-100), e.g. 90 means enforce condition at x_p where identity = 90% of range
    delta   : max allowed deviation (same units as output, not normalized)
    top     : upper bound of sigmoid
    bottom  : lower bound
    midpoint: sigmoid midpoint in x-space

    Returns minimal k such that |sigmoid(x) - x| <= delta at x_p.
    """
    if not (0 < p < 100):
        raise ValueError("p must be in (0,100)")
    
    # expected x under identity at this percentile
    x_p = bottom + (p/100.0)*(top - bottom)
    
    # fraction of output range we must hit (normalized to [0,1])
    fraction = (x_p - delta - bottom) / (top - bottom)
    
    if fraction <= 0 or fraction >= 1:
        raise ValueError("delta too large for chosen p/top/bottom")
    
    k = (1.0 / (x_p - midpoint)) * math.log(fraction / (1 - fraction))
    return k


def sigmoid(x, top=1, bottom=0, midpoint=0.5, p=90, delta=0.1):
    # use the actual midpoint, not hard-coded 0
    k = k_for_linear_tolerance_general(p, delta=delta, top=top, bottom=bottom, midpoint=midpoint)
    return bottom + (top - bottom) / (1 + math.exp(-k * (x - midpoint)))

