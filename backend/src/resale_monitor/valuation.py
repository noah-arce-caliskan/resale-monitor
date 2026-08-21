from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class ComparableInput:
    price_minor: int
    weight_bp: int


@dataclass(frozen=True)
class ValuationInput:
    asking_price_minor: int | None
    additional_cost_low_minor: int
    additional_cost_high_minor: int
    comparables: list[ComparableInput]
    has_blocking_risk: bool = False


@dataclass(frozen=True)
class ValuationResult:
    fair_value_low_minor: int | None
    fair_value_midpoint_minor: int | None
    fair_value_high_minor: int | None
    total_cost_low_minor: int | None
    total_cost_high_minor: int | None
    conservative_advantage_minor: int | None
    confidence_bp: int
    opportunity_label: str
    effective_sample_size: float


def _weighted_quantile(comparables: list[ComparableInput], quantile: float) -> int:
    ordered = sorted(comparables, key=lambda item: item.price_minor)
    total_weight = sum(item.weight_bp for item in ordered)
    threshold = ceil(total_weight * quantile)
    running_weight = 0
    for comparable in ordered:
        running_weight += comparable.weight_bp
        if running_weight >= threshold:
            return comparable.price_minor
    return ordered[-1].price_minor


def _effective_sample_size(comparables: list[ComparableInput]) -> float:
    weight_sum = sum(item.weight_bp for item in comparables)
    square_sum = sum(item.weight_bp**2 for item in comparables)
    return (weight_sum**2) / square_sum if square_sum else 0.0


def valuate(command: ValuationInput) -> ValuationResult:
    comparable_count = _effective_sample_size(command.comparables)
    if (
        command.asking_price_minor is None
        or comparable_count < 3
        or command.has_blocking_risk
    ):
        return ValuationResult(
            fair_value_low_minor=None,
            fair_value_midpoint_minor=None,
            fair_value_high_minor=None,
            total_cost_low_minor=None,
            total_cost_high_minor=None,
            conservative_advantage_minor=None,
            confidence_bp=0,
            opportunity_label="insufficient_evidence",
            effective_sample_size=comparable_count,
        )

    low = _weighted_quantile(command.comparables, 0.25)
    midpoint = _weighted_quantile(command.comparables, 0.5)
    high = _weighted_quantile(command.comparables, 0.75)
    total_low = command.asking_price_minor + command.additional_cost_low_minor
    total_high = command.asking_price_minor + command.additional_cost_high_minor
    advantage = low - total_high
    confidence = min(5500, 4000 + round(min(comparable_count, 8) / 8 * 2400))
    if comparable_count < 8:
        confidence = min(confidence, 6000)

    if advantage <= 0:
        label = "not_attractive"
    elif advantage >= max(round(low * 0.2), 30_000) and confidence >= 7000:
        label = "strong"
    elif advantage >= max(round(low * 0.1), 15_000) and confidence >= 5000:
        label = "promising"
    else:
        label = "watch"

    return ValuationResult(
        fair_value_low_minor=low,
        fair_value_midpoint_minor=midpoint,
        fair_value_high_minor=high,
        total_cost_low_minor=total_low,
        total_cost_high_minor=total_high,
        conservative_advantage_minor=advantage,
        confidence_bp=confidence,
        opportunity_label=label,
        effective_sample_size=comparable_count,
    )
