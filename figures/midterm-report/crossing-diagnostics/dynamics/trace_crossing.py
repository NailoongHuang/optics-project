"""Trace the crossing packet without changing any source animation.

The 1D product calculation is checked against the saved 2D state and the
project's full-band 2D propagator. Times below use Jx*t/hbar, with Jy=Jx.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT))
import common


def main():
    archive = np.load(ROOT / "curvature-design" / "design_data.npz")
    saved = archive["C_eta1_psi_t0"]
    chart = json.loads((ROOT / "curvature-design" / "chart_data.json").read_text())
    case = chart["cases"]["C_eta1"]
    N = case["N"]
    sigma = case["sigma_a"]
    x = np.arange(N) - N // 2
    q = 2 * np.pi * np.fft.fftfreq(N)
    psi1_initial = np.exp(-x*x/(4*sigma*sigma) + 1j*np.pi*x/2)
    psi1_initial /= np.linalg.norm(psi1_initial)
    coefficient = np.fft.fft(psi1_initial)
    e1 = 1 - np.cos(q)
    a0 = np.max(np.abs(saved))
    p0 = a0*a0
    even = x % 2 == 0
    saved_product_error = np.max(np.abs(
        np.outer(psi1_initial, psi1_initial) - saved))

    def trace(t):
        psi1 = np.fft.ifft(coefficient * np.exp(-1j*e1*t))
        u1 = psi1 * np.exp(-1j*np.pi*x/2 + 1j*t)
        rho = np.abs(psi1)**2
        cx = np.sum(x*rho)
        width = np.sqrt(np.sum((x-cx)**2*rho))
        pe = np.sum(rho[even])
        po = np.sum(rho[~even])
        ae = np.max(np.abs(u1[even]))
        ao = np.max(np.abs(u1[~even]))
        max_abs = max(ae, ao)**2
        even_peak = max(ae*ae, ao*ao) * abs(np.cos(2*t))
        odd_peak = ae*ao * abs(np.sin(2*t))
        real_norm = ((pe*pe + po*po)*np.cos(2*t)**2
                     + 2*pe*po*np.sin(2*t)**2)
        absnorm = np.sum(np.abs(psi1))
        even_l1 = np.sum(np.abs(u1[even]))
        odd_l1 = np.sum(np.abs(u1[~even]))
        real_l1 = ((even_l1**2 + odd_l1**2)*abs(np.cos(2*t))
                   + 2*even_l1*odd_l1*abs(np.sin(2*t)))
        row = dict(t=float(t), norm=float(np.sum(rho)**2),
                   probability_peak_over_initial=float(max_abs**2/p0),
                   absolute_amplitude_peak_over_initial=float(max_abs/a0),
                   real_absolute_peak_over_initial=float(max(even_peak, odd_peak)/a0),
                   rephased_real_absolute_peak_over_initial=float(max_abs/a0),
                   real_L2_squared=float(real_norm),
                   real_L1_over_abs_L1=float(real_l1/absnorm**2),
                   cx=float(cx), cy=float(cx), wx=float(width), wy=float(width),
                   cos2t=float(np.cos(2*t)), sin2t=float(np.sin(2*t)),
                   real_carrier_peak_factor=float(max(abs(np.cos(2*t)),
                                                      abs(np.sin(2*t)))),
                   max_imaginary_demodulated_envelope=float(np.max(abs(u1.imag))),
                   even_parity_probability=float(pe*pe+po*po))
        return row, psi1

    dense_times = np.linspace(0, 180, 3601)
    rows = [trace(t)[0] for t in dense_times]
    movie_rows = [trace(t)[0] for t in np.arange(0, 181, 3)]
    controls = [0, np.pi/8, np.pi/4, 3, 6, 9, 12, 15, 30, 60, 90, 120, 150, 180]
    representative = [trace(t)[0] for t in controls]
    exact_checks = []
    xx, yy = np.meshgrid(x, x, indexing="xy")
    for t in [0, np.pi/8, np.pi/4, 3, 9, 60, 90, 180]:
        row, one = trace(t)
        actual = common.propagate(saved, t, 1.)
        product = np.outer(one, one)
        envelope = actual * np.exp(-1j*np.pi*(xx+yy)/2 + 2j*t)
        rephased = actual * np.exp(2j*t)
        reconstructed_real = envelope.real * np.cos(np.pi*(xx+yy)/2-2*t)
        exact_checks.append(dict(
            t=float(t),
            product_max_error=float(np.max(abs(actual-product))),
            demodulated_envelope_imaginary_max=float(np.max(abs(envelope.imag))),
            real_factorization_max_error=float(np.max(
                abs(actual.real-reconstructed_real))),
            real_peak_formula_error=float(abs(
                np.max(abs(actual.real))/a0 - row["real_absolute_peak_over_initial"])),
            real_L2_formula_error=float(abs(
                np.sum(actual.real**2)-row["real_L2_squared"])),
            rephasing_probability_max_error=float(np.max(
                abs(abs(rephased)**2-abs(actual)**2))),
            rephased_real_peak_formula_error=float(abs(
                np.max(abs(rephased.real))/a0
                - row["rephased_real_absolute_peak_over_initial"]))))

    for name, data in [("dense_trace.csv", rows), ("movie_trace.csv", movie_rows)]:
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=data[0])
            writer.writeheader()
            writer.writerows(data)
    ranges = {key: [min(r[key] for r in rows), max(r[key] for r in rows)]
              for key in rows[0] if key != "t"}
    sampled_color = np.array([r["real_absolute_peak_over_initial"] /
                              r["absolute_amplitude_peak_over_initial"]
                              for r in movie_rows])
    maxima = np.flatnonzero((sampled_color[1:-1] > sampled_color[:-2]) &
                           (sampled_color[1:-1] > sampled_color[2:])) + 1
    results = dict(
        parameters=dict(N=N, sigma_a=sigma, q0=case["q0"], eta=1,
                        time_units="hbar/Jx", dense_dt=.05, movie_dt=3,
                        time_range=[0, 180]),
        saved_initial_product_max_error=float(saved_product_error),
        exact_factorization="psi_mn=exp(i*pi*(m+n)/2-2*i*t)*u_mn(t), with u real",
        conditions="N divisible by 4, periodic boundary, real initial demodulated envelope, q0=(pi/2,pi/2), eta=1",
        real_envelope_equation="du_mn/dt=-0.5*(u_(m+1,n)-u_(m-1,n)+u_(m,n+1)-u_(m,n-1))",
        sampled_phase_increment=6.,
        sampled_phase_increment_mod_2pi=float(6-2*np.pi),
        apparent_phase_period_frames=float(2*np.pi/(2*np.pi-6)),
        apparent_peak_color_modulation_period_frames=float((np.pi/2)/(2*np.pi-6)),
        measured_movie_peak_contrast_maxima_frames=maxima.tolist(),
        measured_movie_peak_contrast_maxima_gaps=np.diff(maxima).tolist(),
        ranges=ranges, representative=representative,
        original_movie_samples=movie_rows, checks=exact_checks,
        comparison_widths={name: {"initial_wx":r["track"]["wx"][0],
                                 "final_wx":r["track"]["wx"][-1],
                                 "final_wy":r["track"]["wy"][-1],
                                 "vvar":r["velocity_variance"]}
                           for name,r in chart["cases"].items()
                           if name in ("A_eta1","B_eta1","C_eta1")})
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({key: results[key] for key in
                     ["saved_initial_product_max_error","ranges",
                      "representative","checks","comparison_widths"]}, indent=2))


if __name__ == "__main__":
    main()
