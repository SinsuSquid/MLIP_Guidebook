import sys
import numpy as np
import matplotlib.pyplot as plt

if (len(sys.argv) != 4):
    print("USAGE : python parity.py test.cfg out.cfg figure.png")
    exit(1);

true = []
numConfig = 0
with open(sys.argv[1], 'r') as fp:
    while(True):
        line = fp.readline().strip()
        if (line == ''): break
        elif (line == 'Energy'):
            numConfig += 1
            e = float(fp.readline().strip())
            true.append(e)
true = np.array(true)

pred = []
counter = 0
with open(sys.argv[2], 'r') as fp:
    while(counter < numConfig):
        line = fp.readline().strip()
        # if (line == ''): break
        if (line == 'Energy'):
            counter += 1
            e = float(fp.readline().strip())
            pred.append(e)
pred = np.array(pred)

plt.plot(true, pred, marker = 'o', alpha = 0.7, linestyle = 'none')
plt.plot([min(true.min(), pred.min()), max(true.max(), pred.max())],
         [min(true.min(), pred.min()), max(true.max(), pred.max())], linestyle = '--', color = 'k')

plt.xlabel("DFT Energy (eV)")
plt.ylabel("MTP Energy (eV)")

mae = (pred-true).mean()
rmse = np.sqrt(np.power((pred-true),2).mean())

plt.annotate(f"MAE: {mae:.6f} eV\nRMSE: {rmse:.6f} eV",
             xy = (0.1, 0.8),
             xycoords = 'axes fraction')

plt.savefig(sys.argv[3], dpi = 200)
plt.show()

print("\t>:D Done !")

