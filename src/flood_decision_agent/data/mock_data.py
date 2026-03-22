from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DataConsistencyReport:
    ok: bool
    errors: tuple[str, ...] = ()


class MockDataGenerator:
    def __init__(self, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)

    def generate_all(self) -> dict[str, pd.DataFrame]:
        rainfall = self.generate_rainfall_forecast()
        inflow = self.generate_inflow_forecast(rainfall)
        return {"rainfall_forecast": rainfall, "inflow_forecast": inflow}

    def validate_all(self, datasets: dict[str, pd.DataFrame]) -> DataConsistencyReport:
        errors: list[str] = []

        rainfall = datasets.get("rainfall_forecast")
        inflow = datasets.get("inflow_forecast")
        if rainfall is None or inflow is None:
            missing = []
            if rainfall is None:
                missing.append("rainfall_forecast")
            if inflow is None:
                missing.append("inflow_forecast")
            return DataConsistencyReport(
                ok=False, errors=(f"缺少数据集：{', '.join(missing)}",)
            )

        errors.extend(self.validate_rainfall_forecast(rainfall).errors)
        errors.extend(self.validate_inflow_forecast(inflow).errors)
        errors.extend(self.validate_pair_alignment(rainfall, inflow).errors)
        return DataConsistencyReport(ok=(len(errors) == 0), errors=tuple(errors))

    def generate_rainfall_forecast(
        self,
        hours: int = 72,
        freq: str = "1h",
        start_time: datetime | None = None,
    ) -> pd.DataFrame:
        if start_time is None:
            start_time = datetime.now(tz=timezone.utc).replace(
                minute=0, second=0, microsecond=0
            )

        times = pd.date_range(start=start_time, periods=int(hours), freq=freq, tz="UTC")
        base = self._rng.gamma(shape=1.5, scale=2.0, size=len(times))
        spikes = self._rng.binomial(n=1, p=0.08, size=len(times)) * self._rng.uniform(
            10.0, 30.0, size=len(times)
        )
        rainfall = np.maximum(0.0, base + spikes)
        return pd.DataFrame({"timestamp": times, "rainfall_mm": rainfall})

    def generate_inflow_forecast(
        self,
        rainfall_forecast: pd.DataFrame,
        base_inflow_m3s: float = 2000.0,
    ) -> pd.DataFrame:
        if (
            "timestamp" not in rainfall_forecast.columns
            or "rainfall_mm" not in rainfall_forecast.columns
        ):
            raise ValueError("rainfall_forecast 缺少必要字段：timestamp, rainfall_mm")

        rainfall_mm = rainfall_forecast["rainfall_mm"].to_numpy(dtype=float)
        response = np.convolve(rainfall_mm, np.array([0.2, 0.5, 0.3]), mode="same")
        inflow = (
            base_inflow_m3s
            + response * 80.0
            + self._rng.normal(0.0, 30.0, size=len(rainfall_mm))
        )
        inflow = np.maximum(0.0, inflow)
        return pd.DataFrame(
            {
                "timestamp": rainfall_forecast["timestamp"],
                "inflow_m3s": inflow,
            }
        )

    def validate_rainfall_forecast(self, df: pd.DataFrame) -> DataConsistencyReport:
        errors: list[str] = []
        errors.extend(self._validate_time_index(df, "timestamp"))
        errors.extend(self._validate_non_negative(df, "rainfall_mm"))
        return DataConsistencyReport(ok=(len(errors) == 0), errors=tuple(errors))

    def validate_inflow_forecast(self, df: pd.DataFrame) -> DataConsistencyReport:
        errors: list[str] = []
        errors.extend(self._validate_time_index(df, "timestamp"))
        errors.extend(self._validate_non_negative(df, "inflow_m3s"))
        return DataConsistencyReport(ok=(len(errors) == 0), errors=tuple(errors))

    def validate_pair_alignment(
        self, rainfall_forecast: pd.DataFrame, inflow_forecast: pd.DataFrame
    ) -> DataConsistencyReport:
        errors: list[str] = []
        if len(rainfall_forecast) != len(inflow_forecast):
            errors.append("rainfall 与 inflow 记录数不一致")
        else:
            left = rainfall_forecast["timestamp"].reset_index(drop=True)
            right = inflow_forecast["timestamp"].reset_index(drop=True)
            if not left.equals(right):
                errors.append("rainfall 与 inflow 的 timestamp 不对齐")
        return DataConsistencyReport(ok=(len(errors) == 0), errors=tuple(errors))

    def _validate_time_index(self, df: pd.DataFrame, col: str) -> list[str]:
        errors: list[str] = []
        if col not in df.columns:
            return [f"缺少字段：{col}"]
        ts = pd.to_datetime(df[col], errors="coerce", utc=True)
        if ts.isna().any():
            errors.append(f"{col} 存在无法解析的时间")
            return errors
        if ts.is_monotonic_increasing is False:
            errors.append(f"{col} 不是单调递增")
        if ts.duplicated().any():
            errors.append(f"{col} 存在重复时间戳")
        return errors

    def _validate_non_negative(self, df: pd.DataFrame, col: str) -> list[str]:
        errors: list[str] = []
        if col not in df.columns:
            return [f"缺少字段：{col}"]
        values = pd.to_numeric(df[col], errors="coerce")
        if values.isna().any():
            errors.append(f"{col} 存在无法解析为数值的记录")
            return errors
        if (values < 0).any():
            errors.append(f"{col} 存在负值")
        return errors
