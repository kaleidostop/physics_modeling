from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.linalg import eigh

app = Flask(__name__)

hbar = 1.054e-34
m = 9.11e-31
eV = 1.602e-19

def potential(x, kind, a, U0):
    if kind == "parabolic":
        return -U0 * (1 - (2*x/a)**2)
    if kind == "square":
        U = np.zeros_like(x)
        mask = np.abs(x) < a / 2
        U[mask] = -U0
        return U
    if kind == "double":
        return -U0 * (1 - (2*x / a)**2)**2
    if kind == "arbitrary":
        return -U0 * (x/a) * (10 - x/a)  # для произвольной формулы
    raise ValueError("Unknown potential")


def solve(a_nm, U0_ev, kind, kmax, N=200):
    a = a_nm * 1e-9
    U0 = U0_ev * eV

    L = 3 * a
    dx = L / (N + 1)
    x = np.linspace(-L / 2 + dx, L / 2 - dx, N)

    U = potential(x, kind, a, U0)

    main = (hbar**2 / (m*dx**2)) + U
    off = -hbar**2 / (2*m*dx**2)

    H = (
        np.diag(main)
        + np.diag(off*np.ones(N-1), 1)
        + np.diag(off*np.ones(N-1), -1)
    )

    E, psi = eigh(H)

    for n in range(psi.shape[1]):
        psi[:, n] /= np.sqrt(np.sum(psi[:, n]**2) * dx)

    energies_ev = E / eV
    U_ev = U / eV

    bound_idx = np.where(energies_ev < 0)[0]

    k = min(len(bound_idx), kmax)
    idx = bound_idx[:k]

    return {
        "x": (x*1e9).tolist(),
        "U": U_ev.tolist(),
        "energies": energies_ev[idx].tolist(),
        "psi": psi[:, idx].tolist(),
        "n_states": len(bound_idx),
        "k": k
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def api():
    data = request.json
    return jsonify(
        solve(
            data["a"],
            data["U0"],
            data["kind"],
            data["kmax"],
            data["N"]
        )
    )

if __name__ == "__main__":
    app.run(debug=True)
