from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.linalg import eigh

app = Flask(__name__)

hbar = 1.054e-34
m = 9.11e-31
eV = 1.602e-19

def potential(x, kind, a, U0):
    if kind == "parabolic":
        return -U0 * (x/a) * (1 - x/a)
    if kind == "square":
        return -U0 * np.ones_like(x)
    if kind == "double":
        return -U0 * ((x - a/2)/(a/2))**4
    raise ValueError("Unknown potential")


def solve(a_nm, U0_ev, kind, kmax, N=200):
    a = a_nm * 1e-9
    U0 = U0_ev * eV

    dx = a / (N + 1)
    x = np.linspace(dx, a - dx, N)

    U = potential(x, kind, a, U0)

    main = (hbar**2 / (2*m*dx**2)) + U
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

    bound_idx = np.where(energies_ev < np.max(U_ev))[0]

    k = min(len(bound_idx), kmax)
    idx = bound_idx[:k]

    return {
        "x": (x*1e9).tolist(),
        "U": U_ev.tolist(),
        "energies": energies_ev[idx].tolist(),
        "psi": psi[:, idx].tolist(),
        "n_states": len(bound_idx)
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
            data["kmax"]
        )
    )

if __name__ == "__main__":
    app.run(debug=True)
