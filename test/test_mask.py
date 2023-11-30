import numpy as np
import random

a = np.array(list(range(6)))
mask = np.array([0, 1, 1, 1, 0, 1])
boolean_mask = mask.astype(bool)
print(boolean_mask)
print(a)
print(a[mask])
print(a[boolean_mask])
user_action = np.random.choice(a[boolean_mask], size=1).item()
print(user_action)
print(type(user_action))