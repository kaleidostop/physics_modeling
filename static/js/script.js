async function run() {
  let mode = document.querySelector('input[name="mode"]:checked').value;

  let res = await fetch("/solve", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      a: +a.value,
      U0: +U0.value,
      kind: kind.value,
      kmax: +kmax.value
    })
  });

  let d = await res.json();

  // 1. Потенциал
  Plotly.newPlot("Uplot", [{
    x: d.x,
    y: d.U,
    name: "U(x)"
  }], {
    title: "Потенциал",
    xaxis: {title: "x, нм"},
    yaxis: {title: "U(x), эВ"}
  });

  // 2. psi или |psi|^2
  let psi_traces = [];
  for (let n = 0; n < d.energies.length; n++) {
    let y = d.psi.map(row =>
      mode === "psi" ? row[n] : row[n]*row[n]
    );
    psi_traces.push({
      x: d.x,
      y: y,
      name: "n=" + (n+1)
    });
  }

  Plotly.newPlot("psiplot", psi_traces, {
    title: {
        text: mode === "psi" ? "ψ_n(x)" : "$$|ψ_n(x)|^2",
        font: {size: 20}
    },
    xaxis: {title: "x, нм"}
  });

  // 3. Энергетические уровни
  let Etraces = [{
    x: d.x,
    y: d.U,
    name: "U(x)",
    line: {color: "black"}
  }];

  for (let E of d.energies) {
    Etraces.push({
      x: [d.x[0], d.x[d.x.length-1]],
      y: [E, E],
      mode: "lines",
      line: {dash: "dash"},
      name: "E"
    });
  }

  Plotly.newPlot("Eplot", Etraces, {
    title: "Энергетические уровни",
    xaxis: {title: "x, нм"},
    yaxis: {title: "Энергия, эВ"}
  });
}