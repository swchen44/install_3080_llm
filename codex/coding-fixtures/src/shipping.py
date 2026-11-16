def shipping_price(weight_kg):
    """Return the shipping price in dollars; weights must be nonnegative."""
    if weight_kg < 0:
        raise ValueError("weight must be nonnegative")
    if weight_kg < 5:
        return 8
    if weight_kg < 10:
        return 12
    return 20
