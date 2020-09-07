import math

sym_tab = {}

#get the math functions for free
sym_tab.update(vars(math))

sym_tab.update({
'max': max,
'min': min
})
