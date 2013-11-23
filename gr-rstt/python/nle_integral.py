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
# why "+ 1", because this point is last one with value above mean_rel on the
# descenting side of peak, so we need firt point which does not belogn to peak
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

    def run(self, noise_pct = 0.2, nsplits = 60, threshold = 2):
        d = self.src.read()
        while len(d):
            # plot: original signal
            offs = int(len(d) / 2)
            x = range(0 - offs, len(d) - offs)
            plt.plot(x, d)

            # plot: log(original signal)
            d_log = [np.log(d_) for d_ in d]
            min_ = max(d_log)
            for d_ in d_log:
                if d_ < min_ and np.isfinite(d_):
                    min_ = d_
            d_log = [d_ if np.isfinite(d_) else min_ for d_ in d_log ]
            #plt.plot(x, d_log)

            self.write_signal('out', d_log)

            # get splits
            d_ilog = [d_log[0], ]
            for idx in range(1, len(d_log)):
                d_ilog.append(d_ilog[idx - 1] + d_log[idx])
            split = Split(0, len(d_log))
            splits = [split, ]
            split.set_mean(d_ilog)
            split.set_extreme(d_ilog)
            for sn in range(0, nsplits):
                smax = max(splits, key=lambda s: s.extreme.val)
                snew = Split(smax.start + smax.extreme.idx + 1, smax.len - smax.extreme.idx - 1)
                splits.append(snew)
                snew.set_mean(d_ilog)
                snew.set_extreme(d_ilog)
                smax.len = smax.extreme.idx + 1
                smax.set_mean(d_ilog)
                smax.set_extreme(d_ilog)

            # get mean and sigma for noise
            splits.sort(key=lambda v: v.get_mean(d_log))
            l = 0
            mean = 0
            sigma = 0
            for split in splits:
                #print(split)
                for v in split.data(d_log):
                    mean += v
                    sigma += v**2
                l += split.len
                if l > len(d) * noise_pct:
                    break
            mean /= l
            sigma = np.sqrt(sigma/l - mean**2) * threshold

            print("%.4f %.4f %.4f" % (mean - sigma, mean, mean + sigma, ))
            n_lo, mean, n_hi = np.exp(mean - sigma), np.exp(mean), np.exp(mean + sigma)
            plt.plot(x, [n_lo for a in x])
            plt.plot(x, [mean for a in x])
            plt.plot(x, [n_hi for a in x])

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
    s = Show(Src(sys.argv[1], 1024, 100))
    s.run()
