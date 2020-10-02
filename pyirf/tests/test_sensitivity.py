from astropy.table import QTable
import numpy as np
import astropy.units as u


def test_relative_sensitivity():
    from pyirf.sensitivity import relative_sensitivity

    # some general case
    n_on = 100
    n_off = 200
    alpha = 0.2
    assert 0.1 < relative_sensitivity(n_on, n_off, alpha) < 1.0

    # numbers yield lima = 5 relatively precisely, so sensitivity should be 1
    assert np.isclose(relative_sensitivity(81, 202, 0.2), 1, rtol=0.01)

    # test different target significance
    # numbers yield lima = 8 relatively precisely, so sensitivity should be 1
    result = relative_sensitivity(93, 151, 0.2, target_significance=8)
    assert np.isclose(result, 1, rtol=0.01)

    # no signal => inf
    assert np.isinf(relative_sensitivity(10, 100, 0.2))

    # no background, should work
    assert relative_sensitivity(10, 0, 0.2) > 0


def test_estimate_background():
    from pyirf.sensitivity import estimate_background
    N = 1000
    events = QTable({
        'source_fov_offset': np.append(np.full(N, 0.5), np.full(N, 1.5)) * u.deg,
        'reco_energy': np.tile([5, 50], N) * u.TeV,
        'weight': np.tile([1, 2], N),
    })
    reco_energy_bins = [1, 10, 100] * u.TeV
    theta_cuts = QTable({
        'low': [1, 10] * u.TeV,
        'high': [10, 100] * u.TeV,
        'center': [5.5, 55] * u.TeV,
        'cut': (np.arccos([0.9998, 0.9999]) * u.rad).to(u.deg),
    })
    background_radius = np.arccos(0.999) * u.rad

    bg = estimate_background(
        events,
        reco_energy_bins,
        theta_cuts,
        alpha=0.2,
        background_radius=background_radius
    )

    assert np.allclose(bg['n'], [1000, 500])
    assert np.allclose(bg['n_weighted'], [1000, 1000])
