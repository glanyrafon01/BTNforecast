from dataclasses import dataclass, replace
from typing import Any

import yaml


@dataclass
class ForecastConfig:
    lists: list[str]
    base_shares: list[float]
    seats: int
    sims: int
    concentration: float
    swing_sd: float
    swing_rho: float
    left_bloc: set[str]
    right_bloc: set[str]
    seed: int | None
    sensitivity_sims: int


def _normalize_shares(shares: list[float]) -> list[float]:
    total = sum(shares)
    if total <= 0:
        raise ValueError("base_shares must sum to a positive value")
    return [val / total for val in shares]


def _coerce_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    return [str(item) for item in value]


def _coerce_float_list(value: Any, field_name: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    try:
        return [float(item) for item in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must contain numeric values") from exc


def _coerce_int(value: Any, field_name: str, minimum: int = 1) -> int:
    try:
        int_value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc
    if int_value < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return int_value


def _coerce_float(value: Any, field_name: str, minimum: float | None = None) -> float:
    try:
        float_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number") from exc
    if minimum is not None and float_value < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return float_value


def _coerce_bloc(value: Any, field_name: str) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return {str(item) for item in value}


def _default_sensitivity_sims(sims: int) -> int:
    return min(2000, sims)


def _validate_blocs(lists: list[str], left_bloc: set[str], right_bloc: set[str]) -> None:
    unknown = (left_bloc | right_bloc) - set(lists)
    if unknown:
        raise ValueError(f"Bloc members not in lists: {sorted(unknown)}")
    overlap = left_bloc & right_bloc
    if overlap:
        raise ValueError(f"Bloc members appear in both blocs: {sorted(overlap)}")


def _resolve_blocs(
    lists: list[str],
    left_bloc: set[str],
    right_bloc: set[str],
) -> tuple[set[str], set[str]]:
    if not left_bloc and not right_bloc:
        return set(lists), set()
    if not right_bloc:
        return set(left_bloc), set(lists) - set(left_bloc)
    if not left_bloc:
        return set(lists) - set(right_bloc), set(right_bloc)
    return set(left_bloc), set(right_bloc)


def config_from_dict(raw: dict[str, Any]) -> ForecastConfig:
    lists = _coerce_list(raw.get("lists"), "lists")
    base_shares = _coerce_float_list(raw.get("base_shares"), "base_shares")
    if len(lists) != len(base_shares):
        raise ValueError("lists and base_shares must be the same length")

    base_shares = _normalize_shares(base_shares)

    seats = _coerce_int(raw.get("seats", 6), "seats")
    sims = _coerce_int(raw.get("sims", 10000), "sims")
    concentration = _coerce_float(raw.get("concentration", 50), "concentration", 0.0)
    swing_sd = _coerce_float(raw.get("swing_sd", 0.03), "swing_sd", 0.0)
    swing_rho = _coerce_float(raw.get("swing_rho", -0.5), "swing_rho")
    sensitivity_sims = _coerce_int(
        raw.get("sensitivity_sims", _default_sensitivity_sims(sims)),
        "sensitivity_sims",
    )

    left_bloc = _coerce_bloc(raw.get("left_bloc"), "left_bloc")
    right_bloc = _coerce_bloc(raw.get("right_bloc"), "right_bloc")
    left_bloc, right_bloc = _resolve_blocs(lists, left_bloc, right_bloc)
    _validate_blocs(lists, left_bloc, right_bloc)

    seed_value = raw.get("seed")
    seed = None if seed_value is None else _coerce_int(seed_value, "seed", 0)

    return ForecastConfig(
        lists=lists,
        base_shares=base_shares,
        seats=seats,
        sims=sims,
        concentration=concentration,
        swing_sd=swing_sd,
        swing_rho=swing_rho,
        left_bloc=left_bloc,
        right_bloc=right_bloc,
        seed=seed,
        sensitivity_sims=sensitivity_sims,
    )


def load_config(path: str) -> ForecastConfig:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Config file must contain a mapping")
    return config_from_dict(data)


def parse_config_yaml(text: str) -> ForecastConfig:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Config must contain a mapping")
    return config_from_dict(data)


def override_config(config: ForecastConfig, **overrides: Any) -> ForecastConfig:
    allowed = {
        "sims",
        "seed",
        "sensitivity_sims",
        "concentration",
        "swing_sd",
        "swing_rho",
    }
    filtered = {
        key: value
        for key, value in overrides.items()
        if key in allowed and value is not None
    }
    return replace(config, **filtered)
