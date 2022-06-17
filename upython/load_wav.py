#%%
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

#%%
file_path = r"D:\Downloads\sdrsharp-x86\SDRSharp_20211103_150104Z_434065000Hz_IQ.wav"
f_s, data = wavfile.read(file_path)
d_t = 1/f_s
data_n = len(data)
t_end = data_n / f_s
t = np.linspace(0, t_end, data_n)

iq = data[:, 0] + 1j * data[:, 1]
s = abs(iq)
# s /= max(s)
# s[s < .2] = 0
# s[s >= .2] = 1
plt.figure()
plt.plot(t, iq.real, t, iq.imag)
plt.figure()
plt.plot(t, s)

#%%
# t_start = 1.07
# t_stop = 1.11
t_start = 0
t_stop = max(t)
s_filt = s[(t > t_start) & (t < t_stop)]
t_filt = t[(t > t_start) & (t < t_stop)]

plt.figure()
plt.plot(t_filt, s_filt)
plt.show()