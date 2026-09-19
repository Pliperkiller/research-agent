"""Known-bad fixture: every checkable rule is violated on purpose."""
import numpy as np
import matplotlib.pyplot as plt

Z = np.random.rand(100, 100) - 0.5
fig, ax = plt.subplots()
ax.imshow(Z, cmap="jet")
ax.set_title("field", fontsize=14)
ax.grid(True)
ax.set_facecolor("lightblue")
values = [3.1, 3.2, 3.15]
ax.bar(["a", "b", "c"], values)
ax.set_ylim(3.0, 3.3)
plt.savefig("fig.jpg", fontsize=10)
