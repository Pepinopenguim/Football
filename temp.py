def f(value):
        from numpy import log as ln
        # log function where
        # if
        # value = 1k -> 30
        # value = 200m -> 100
        return int(5.734850351364555 * ln(value) + 30)

print(f(2e5))