#!/usr/bin/env python
"""
Rough cost estimator for the serverless GenAI showcase.

The calculation is intentionally simple and documented so FinOps teams can
replace it with something more precise (e.g., CUR queries or CloudWatch data).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class WorkloadProfile:
    monthly_invocations: int = 50000
    avg_duration_ms: int = 180
    avg_memory_mb: int = 256
    monthly_tokens: int = 2_000_000
    dynamodb_read_units: int = 5_000
    dynamodb_write_units: int = 3_000


LAMBDA_PRICE_PER_MS = 1e-6  # USD per ms at 256 MB (simplified)
TOKEN_COST_PER_1K = 0.002  # USD mock adapter placeholder
DDB_RCU_COST = 0.00013
DDB_WCU_COST = 0.00065


def estimate(profile: WorkloadProfile) -> dict:
    lambda_cost = profile.monthly_invocations * profile.avg_duration_ms * LAMBDA_PRICE_PER_MS
    token_cost = (profile.monthly_tokens / 1000) * TOKEN_COST_PER_1K
    ddb_cost = (
        profile.dynamodb_read_units * DDB_RCU_COST + profile.dynamodb_write_units * DDB_WCU_COST
    )
    total = lambda_cost + token_cost + ddb_cost
    return {
        "lambdaUsd": round(lambda_cost, 2),
        "tokensUsd": round(token_cost, 2),
        "dynamodbUsd": round(ddb_cost, 2),
        "estimatedMonthlyUsd": round(total, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Estimate showcase monthly spend.")
    parser.add_argument("--invocations", type=int, default=WorkloadProfile.monthly_invocations)
    parser.add_argument("--duration-ms", type=int, default=WorkloadProfile.avg_duration_ms)
    parser.add_argument("--tokens", type=int, default=WorkloadProfile.monthly_tokens)
    parser.add_argument("--rcu", type=int, default=WorkloadProfile.dynamodb_read_units)
    parser.add_argument("--wcu", type=int, default=WorkloadProfile.dynamodb_write_units)
    args = parser.parse_args()
    profile = WorkloadProfile(
        monthly_invocations=args.invocations,
        avg_duration_ms=args.duration_ms,
        monthly_tokens=args.tokens,
        dynamodb_read_units=args.rcu,
        dynamodb_write_units=args.wcu,
    )
    summary = estimate(profile)
    for key, value in summary.items():
        print(f"{key}: ${value}")


if __name__ == "__main__":
    main()
