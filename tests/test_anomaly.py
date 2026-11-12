from backend.app.anomaly import AnomalyDetector

LIMITS = {"temperature": (-20.0, 60.0)}


def make(**kw):
    return AnomalyDetector(LIMITS, window_size=30, min_samples=10, z_threshold=3.0, **kw)


def test_normal_values_not_flagged():
    d = make()
    for i in range(30):
        flagged, _ = d.check("temperature", 22.0 + (i % 3) * 0.1)
        assert not flagged


def test_hard_limit_flagged_immediately():
    d = make()
    flagged, reason = d.check("temperature", 99.0)
    assert flagged and "limits" in reason


def test_spike_flagged_after_warmup():
    d = make()
    for i in range(20):
        d.check("temperature", 22.0 + (i % 3) * 0.1)
    flagged, reason = d.check("temperature", 40.0)
    assert flagged and "z-score" in reason


def test_no_zscore_flag_during_cold_start():
    d = make()
    for _ in range(5):
        d.check("temperature", 22.0)
    flagged, _ = d.check("temperature", 40.0)
    assert not flagged


def test_outliers_do_not_pollute_baseline():
    d = make()
    for i in range(20):
        d.check("temperature", 22.0 + (i % 3) * 0.1)
    for _ in range(5):
        d.check("temperature", 40.0)
    flagged, _ = d.check("temperature", 40.0)
    assert flagged
