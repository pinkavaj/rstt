#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import sys


class Src:
    def __init__(self, fname, block_size, navg = 1):
        self.offs = 0
        self.navg = navg
        self.block_size = block_size
        self.data = np.fromfile(fname, dtype=np.float32)
        l = divmod(len(self.data), block_size)[0]
        self.data = self.data[0:l*block_size]
        self.data = self.data.reshape(l, block_size)

    def read(self):
        navg = self.navg
        # do frame averaging"
        data = np.zeros(self.block_size)
        while navg > 0 and self.offs < len(self.data):
            data += self.data[self.offs]
            self.offs += 1
            navg -= 1
        if navg:
            return None
        return data / self.navg


class Extreme:
    def __init__(self, data, mean_rel):
        """Data should be integral of signal power value,
        mean_rel should be relative mean value, see Split.set_mean for details."""
        idx = self.idx = 0
        self.val = 0
        while idx < len(data):
            val = data[idx] - data[0] - mean_rel * idx
            if val > self.val:
                self.val = val
                self.idx = idx
            elif -val > self.val:
                self.val = -val
                self.idx = idx
            idx += 1


class Split:
    def __init__(self, start, _len):
        self.start = start
        self.len = _len

    def __str__(self):
        return "start = %f; len = %f; mean_rel = %f;" % (self.start, self.len, self.mean_rel, )

    def get_mean(self, data):
        return (self.mean_rel * (self.len - 1) + data[self.start]) / self.len

    def set_mean(self, data):
        """Set relative mean value for data in range defined by Split.
        Data should be integrated power value of signal."""
        if self.len > 1:
          l = self.len - 1
          self.mean_rel = (data[self.start + l] - data[self.start]) / l
        else:
          self.mean_rel = 0.

    def set_extreme(self, data):
        """Find new extreme."""
        self.extreme = Extreme(self.data(data), self.mean_rel)

    def data(self, data):
        return data[self.start:self.start+self.len]


class Show:
    """Noise level estimation. Input is vector of FFT(1024) series."""

    def __init__(self, src):
        self.src = src

    def run2(self, noise_pct = 0.33, noise_w = 0.05, threshold = 3):
        d = self.src.read()
        noise_pct = int(self.src.block_size * noise_pct)
        noise_w = int(self.src.block_size * noise_w)

        while len(d):
            # plot: original signal
            offs = int(len(d) / 2)
            x = range(0 - offs, len(d) - offs)
            plt.plot(x, d)

            # plot: ln(original signal)
            d_log = [np.log(p) for p in d]
            min_ = max(d_log)
            for p in d_log:
                if p < min_ and np.isfinite(p):
                    min_ = p
            d_log = [p if np.isfinite(p) else min_ for p in d_log ]
            #plt.plot(x, d_log)

            self.write_signal('out', d_log)

            # moving average and moving sigma
            mean = [sum(d_log[0:noise_w]), ]
            d_log2 = [x*x for x in d_log]
            mean2 = [sum(d_log2[0:noise_w]), ]
            for i in range(noise_w, len(d_log)):
              ii = i - noise_w
              mean.append(mean[ii] - d_log[ii] + d_log[i])
              mean2.append(mean2[ii] - d_log2[ii] + d_log2[i])
            mean = [i/noise_w for i in mean]
            mean2 = [i/noise_w for i in mean2]

            # signal dispersion around moving average
            s = []
            for i in range(0, len(mean)):
              s.append(np.sqrt(mean2[i] - mean[i]**2))

            #s_plt = [max(s),] * int(noise_w/2) + s
            #s_plt = s_plt + [max(s), ] * (len(x) - len(s))
            #plt.plot(x, s_plt)

            s.sort()
            s = s[:noise_pct]
            s = sum(s) / len(s) * threshold

            mean.sort()
            #plt.plot(range(0, len(mean)), mean)
            mean = mean[:noise_pct]
            mean = sum(mean) / len(mean)
            #plt.plot(x, [mean - s, ] * len(d_log))
            #plt.plot(x, [mean, ] * len(d_log))
            #plt.plot(x, [mean + s, ] * len(d_log))
            print(mean - s, mean, mean + s)

            s_lo = [np.exp(mean - s), ] * len(d_log)
            s_m = [np.exp(mean), ] * len(d_log)
            s_hi = [np.exp(mean + s), ] * len(d_log)
            plt.plot(x, s_lo)
            plt.plot(x, s_m)
            plt.plot(x, s_hi)
            plt.show()
            plt.close()


    def write_signal(self, fname, data):
       with open('out', 'w') as f:
           i = 0
           while i < len(data):
               f.write("%.4f, " % data[i])
               i += 1
               if i % 8 == 0 and i != 0:
                   f.write("\n")

if __name__ == '__main__':
    s = Show(Src(sys.argv[1], 1024, 2**11))
    s.run2()
