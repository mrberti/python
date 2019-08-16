import math
import matplotlib.pyplot as plt

u_vect = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
y_d = 0
u_d = 0
y_vect = []
Ts = 0.2
T = 3
a0 = math.e**(-Ts/T)
a1 = 1-a0

for u in u_vect:
    y = u_d * a1 + y_d * a0
    y_d = y
    u_d = u
    y_vect.append(y)

print(a0)
print(a1)
print(y_vect)

plot = plt.plot(y_vect)
plt.show()