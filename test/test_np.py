import numpy as np
np.random.seed(5)
first_x_card = 5
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
first_portion = a[:first_x_card]
second_portion = a[first_x_card:]
np.random.shuffle(first_portion)
a = first_portion + second_portion
print(a)