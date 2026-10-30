"""Physical regression checks: python -m unittest discover -s code -v."""
import unittest

import numpy as np

from spin_wave_2d import Params, evolve, estimate_k, initial_sy, initial_sz, make_grid, make_rhs, wave_packet


def exact_evolution(p, sy, sz, t):
    k = 2 * np.pi * np.fft.fftfreq(p.N)
    kx, ky = np.meshgrid(k, k, indexing="xy")
    # Independent analytic result for one-counted ferromagnetic bonds.
    energy = p.h + 2 * p.S * (p.Jx * (1 - np.cos(kx)) + p.Jy * (1 - np.cos(ky)))
    return np.fft.ifft2(np.fft.fft2(sy + 1j * sz) * np.exp(-1j * energy * t))


class SpinWaveTests(unittest.TestCase):
    def test_uniform_rotation_has_only_zeeman_frequency(self):
        for h in (0.0, 0.7):
            p = Params(N=8, S=0.5, Jx=1.3, Jy=0.4, h=h)
            sy, sz = np.full((8, 8), 0.02), np.full((8, 8), -0.01)
            dy, dz = make_rhs(p)(sy, sz)
            np.testing.assert_allclose(dy, h * sz, atol=1e-15)
            np.testing.assert_allclose(dz, -h * sy, atol=1e-15)

    def test_plane_wave_frequency_and_velocity(self):
        p = Params(N=16, S=0.5, Jx=1.2, Jy=0.3, h=0.4)
        x, y = make_grid(p.N)
        kx, ky = 2 * np.pi * 3 / p.N, -2 * np.pi * 2 / p.N
        psi = 0.01 * np.exp(1j * (kx * x + ky * y))
        energy = p.h + 2 * p.S * (p.Jx * (1 - np.cos(kx)) + p.Jy * (1 - np.cos(ky)))
        dy, dz = make_rhs(p)(psi.real, psi.imag)
        np.testing.assert_allclose(dy + 1j * dz, -1j * energy * psi, atol=1e-15)
        np.testing.assert_allclose(p.dispersion(kx, ky), (energy, energy))
        np.testing.assert_allclose(p.group_velocity(kx, ky),
                                   2 * p.S * np.array([p.Jx * np.sin(kx), p.Jy * np.sin(ky)]))

    def test_exact_spin_half_one_magnon_hamiltonian(self):
        p = Params(N=4, S=0.5, Jx=1.1, Jy=0.3, h=0.6)
        # Exact matrix of H-E_F in the one-spin-flip basis: each affected
        # spin-1/2 bond adds J/2 on the diagonal and -J/2 for a hop.
        matrix = np.eye(p.N ** 2) * p.h
        for y in range(p.N):
            for x in range(p.N):
                i = y * p.N + x
                for dx, dy, jval in ((1, 0, p.Jx), (0, 1, p.Jy)):
                    j = ((y + dy) % p.N) * p.N + (x + dx) % p.N
                    matrix[i, i] += jval / 2
                    matrix[j, j] += jval / 2
                    matrix[i, j] -= jval / 2
                    matrix[j, i] -= jval / 2
        rng = np.random.default_rng(17)
        psi = rng.normal(size=(p.N, p.N)) + 1j * rng.normal(size=(p.N, p.N))
        dy, dz = make_rhs(p)(psi.real, psi.imag)
        np.testing.assert_allclose((dy + 1j * dz).ravel(), -1j * matrix @ psi.ravel(), atol=3e-15)

    def test_rk4_matches_exact_fft_and_converges(self):
        rng = np.random.default_rng(29)
        sy, sz = rng.normal(size=(8, 8)) * 0.002, rng.normal(size=(8, 8)) * 0.002
        errors = []
        for dt in (0.1, 0.05):
            p = Params(N=8, S=0.5, h=0.4, dt=dt, tmax=2, frames=3)
            result = evolve(p, sy, sz, verbose=False)
            reference = exact_evolution(p, sy, sz, p.tmax)
            actual = result["sy"][-1] + 1j * result["sz"][-1]
            errors.append(np.linalg.norm(actual - reference) / np.linalg.norm(reference))
        self.assertLess(errors[1], 2e-5)
        self.assertGreater(errors[0] / errors[1], 12)
        self.assertLess(errors[0] / errors[1], 20)

    def test_default_step_conserves_norm_and_matches_fft(self):
        p = Params(N=16, tmax=4, frames=4)
        x, y = make_grid(p.N)
        sy, sz = initial_sy(x, y), initial_sz(x, y)
        result = evolve(p, sy, sz, verbose=False)
        reference = exact_evolution(p, sy, sz, p.tmax)
        actual = result["sy"][-1] + 1j * result["sz"][-1]
        self.assertLess(np.linalg.norm(actual - reference) / np.linalg.norm(reference), 1e-6)
        self.assertLess(np.max(np.abs(result["norm"] / result["norm"][0] - 1)), 1e-6)

    def test_packet_handedness_sets_actual_momentum(self):
        x, y = make_grid(32)
        for sign in (-1, 1):
            sy, sz = wave_packet(x, y, kx=2*np.pi*4/32, ky=0, handedness=sign)
            iy, ix = np.unravel_index(np.abs(np.fft.fft2(sy + 1j*sz)).argmax(), sy.shape)
            self.assertEqual(iy, 0)
            self.assertEqual(ix, (sign * 4) % 32)

    def test_default_amplitude_is_small(self):
        p = Params()
        x, y = make_grid(p.N)
        ratio = np.max(np.hypot(initial_sy(x, y), initial_sz(x, y))) / p.S
        self.assertLessEqual(ratio, 0.05 + 1e-15)

    def test_zero_hamiltonian_is_stationary(self):
        p = Params(N=4, Jx=0, Jy=0, h=0, tmax=1, frames=2)
        sy, sz = np.full((4, 4), 0.01), np.zeros((4, 4))
        result = evolve(p, sy, sz, verbose=False)
        np.testing.assert_allclose(result["sy"][-1], sy)
        np.testing.assert_allclose(result["sz"][-1], sz)

    def test_uniform_mode_is_not_excluded_from_spectrum(self):
        self.assertEqual(estimate_k(np.ones((8, 8)), np.zeros((8, 8)), 8), (0, 0))

    def test_invalid_background_and_unstable_step_are_rejected(self):
        for kwargs in ({"Jx": -1}, {"S": 0}, {"h": -1}, {"dt": 0}, {"dt": 2}):
            with self.subTest(kwargs=kwargs):
                p = Params(N=4, tmax=4, **kwargs)
                with self.assertRaises(ValueError):
                    evolve(p, np.ones((4, 4))*0.01, np.zeros((4, 4)), verbose=False)


if __name__ == "__main__":
    unittest.main()
