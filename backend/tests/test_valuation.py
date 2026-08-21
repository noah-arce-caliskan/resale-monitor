from resale_monitor.valuation import ComparableInput, ValuationInput, valuate


def test_active_asking_comps_produce_explainable_promising_result() -> None:
    result = valuate(
        ValuationInput(
            asking_price_minor=100_000,
            additional_cost_low_minor=20_000,
            additional_cost_high_minor=30_000,
            comparables=[
                ComparableInput(price_minor=price, weight_bp=4500)
                for price in [150_000, 180_000, 200_000, 220_000, 250_000]
            ],
        )
    )

    assert result.fair_value_low_minor == 180_000
    assert result.fair_value_midpoint_minor == 200_000
    assert result.fair_value_high_minor == 220_000
    assert result.total_cost_high_minor == 130_000
    assert result.conservative_advantage_minor == 50_000
    assert result.confidence_bp == 5500
    assert result.opportunity_label == "promising"
    assert result.effective_sample_size == 5


def test_sparse_comps_do_not_emit_false_precision() -> None:
    result = valuate(
        ValuationInput(
            asking_price_minor=100_000,
            additional_cost_low_minor=0,
            additional_cost_high_minor=10_000,
            comparables=[
                ComparableInput(price_minor=150_000, weight_bp=4500),
                ComparableInput(price_minor=175_000, weight_bp=4500),
            ],
        )
    )

    assert result.fair_value_low_minor is None
    assert result.conservative_advantage_minor is None
    assert result.confidence_bp == 0
    assert result.opportunity_label == "insufficient_evidence"


def test_blocking_risk_prevents_positive_opportunity_label() -> None:
    result = valuate(
        ValuationInput(
            asking_price_minor=50_000,
            additional_cost_low_minor=0,
            additional_cost_high_minor=0,
            comparables=[
                ComparableInput(price_minor=200_000, weight_bp=4500) for _ in range(8)
            ],
            has_blocking_risk=True,
        )
    )

    assert result.opportunity_label == "insufficient_evidence"
