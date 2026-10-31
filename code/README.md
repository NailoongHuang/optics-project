# Spin-wave model and verification

The current solver implements the polarized nearest-neighbor Heisenberg
ferromagnet on an N by N periodic square lattice. Units are hbar = a = 1;
spin operators are dimensionless and every undirected bond is counted once:

```text
H = -sum_(i,mu=x,y) J_mu S_i . S_(i+e_mu) - h sum_i S_i^x
h = g mu_B B
```

The supported ground-state expansion has S > 0, Jx,Jy >= 0, and h >= 0.
Spatial anisotropy Jx != Jy does not break spin rotation symmetry by itself.
The default S=1/2 matches one spin-only electron per site; use `--S 1` for
an effective spin-1 moment. No material-specific microscopic derivation of
Jx, Jy, or their field dependence is implemented.

## Quantum interpretation and equations

Quantize along +x: S^x = S - a^dag a, S^y+i S^z ~= sqrt(2S) a.
Keeping the quadratic Holstein-Primakoff terms gives

```text
H2 = E_F + [h+2S(Jx+Jy)] sum_i a_i^dag a_i
          - S sum_(i,mu) J_mu (a_i^dag a_(i+e_mu) + h.c.)
epsilon(k) = h + 2S [Jx(1-cos kx) + Jy(1-cos ky)]
i dot(a_i) = [h+2S(Jx+Jy)] a_i
             - S sum_mu J_mu (a_(i+e_mu)+a_(i-e_mu))
```

The plotted real fields obey dot(sy)=A sz and dot(sz)=-A sy, where A is
the one-particle operator above. They represent coherent transverse means,
psi=sy+i sz=sqrt(2S)<a>, rather than a full quantum many-body state.
The solver does not calculate magnon interactions, quantum correlations,
thermal fluctuations, damping, or driving. The dilute-spin-wave approximation
requires <n_i> << 2S; for coherent amplitudes it requires |psi_i|/S << 1.
The default maximum |psi|/S is 0.05.

The same operator is exact in the one-magnon sector of this Heisenberg model.
One may evolve a normalized one-magnon wavefunction with it, but that
wavefunction is not a transverse spin expectation: <a>=0 in a state of
definite magnon number. The +/- frequencies of the real two-component EoM
are conjugate descriptions, not two independent positive-energy bands.

Reference: Franz Utermohlen, [Spin-Wave Theory Using the Holstein-Primakoff
Transformation](https://cpb-us-w2.wpmucdn.com/u.osu.edu/dist/3/67057/files/2020/02/spin-wave_theory_using_the_Holstein-Primakoff_transformation.pdf),
sections 1-2. The field and spatially anisotropic terms above use this
project's Hamiltonian and bond convention.

## Run and test

From the project root:

```powershell
python code/spin_wave_2d.py --npz
python -m unittest discover -s code -v
```

The solver uses RK4 with dt <= 0.1/max(epsilon) by default and rejects a
user step outside its imaginary-axis stability bound. Exact linear dynamics
conserves Q=sum |psi|^2; the reported drift measures numerical error only,
not the validity of the underlying physical approximation.

`test_spin_wave_2d.py` checks uniform Larmor precession, zero-field rotation,
plane-wave dispersion, the exact spin-1/2 one-magnon Hamiltonian, Fourier
time evolution, fourth-order convergence, norm conservation, packet momentum,
small amplitude, zero Hamiltonian, and parameter validation.

Verified run on 2026-10-19: all 10 tests passed. The default 64 by 64 run
to t=40 used 1,400 steps and saved 180 frames. Its final relative L2 error
against independent exact Fourier evolution was 5.96e-8, with maximum
relative Q drift 1.65e-9. The largest |psi|/S over the saved trajectory was
0.05. All three GIFs decoded through their last frame; the dispersion and
snapshot images were visually inspected. Outputs are in `spin_wave_out/`.

`toy_model.py` and `toy_model_Gauss.py` share Params and the same dispersion.
The latter plots the Gaussian curvature of the energy graph in the chosen
coordinate units; this is not Berry curvature.

## Correction record (2026-10-19)

Original scripts and original animations are preserved in
`backups/2026-10-19-before-spin-wave-fix/`. The original solver failed all
eight initial physical regression cases (seven assertion failures and one
zero-Hamiltonian division error). The corrected solver:

- Restores the onsite exchange term 2S(Jx+Jy), including it in the timestep
  bound. Uniform precession now has frequency h independent of exchange.
- Uses S=1/2 by default and a small transverse amplitude, rather than
  interpreting S=1 as a single electron or using |s_perp|=S.
- Defines positive packet handedness as psi centered at +k, and reports the
  actual signed group velocity. It retains k=0 in spectral diagnostics.
- Removes the spurious zero-frequency ring interpretation and distinguishes
  one magnon band from conjugate frequency branches.
- Uses float64 frame storage and supports the zero Hamiltonian and a single
  requested snapshot.

The current reviewed derivation is `../Note/single_magnon_derivation/main.tex`
and its matching `main.pdf`. The older notes in `../Note/toy_model/` and
`../Note/toy_model_EOM/` are preserved as historical sources.
The following correction notes refer to those older documents: the missing onsite term in `toy_model_EOM`,
`h=mu_B B` dropping g, calling a single electron S=1, and an energy formula
missing 2S unless S=1/2. The microscopic passage also conflates an antiparallel
product state with a singlet: energies U +/- K label spatial exchange
symmetry / singlet-triplet sectors, not simply parallel versus antiparallel
product states. Its Coulomb-exchange integral and conversion to the spin
Hamiltonian require a separate microscopic derivation. A field-induced
difference between Jx and Jy is not established by the phenomenological
Hamiltonian. These limitations do not prevent using specified positive Jx,Jy
as effective model parameters.


## Contributed classical precompensation example (2026-10-31)

[PR #1](https://github.com/NailoongHuang/optics-project/pull/1) by xianjun-jiang
adds [classical_simulation/main.py](classical_simulation/main.py), its packet
utilities and authored output images, and extends the historical
[toy-model EOM note](../Note/toy_model_EOM/toy_model_EOM.tex). The reviewed
elementary solver and its regression contract above remain the current model.

The contribution compares ordinary Gaussian propagation with cubic spectral
phase precompensation intended to refocus near a chosen time T. Its width
second moment alone does not establish continuous shape preservation. Static
integration review identified the older equation without the onsite exchange
term 2S(Jx+Jy), and defaults S=1 with peak transverse amplitude 0.5. These
model conventions still need reconciliation with the current solver. The
submitted simulations have not been independently rerun during integration.

Windows compatibility relocation: `classical_simulation/aux.py` ->
[classical_simulation/packet_utils.py](classical_simulation/packet_utils.py).
The helper bytes are unchanged; SHA-256: `2094c3328385ee7b14e3f44ed2a657488118511f42dafb2ddbdc61df87b86b89`.
Only its import in main.py was adjusted (`import packet_utils as aux`).
The original filename and all contributed files remain in the PR history.
