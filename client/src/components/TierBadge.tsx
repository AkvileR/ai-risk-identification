import React from "react";
import { RiskTier } from "../types";
import { TIER_CLASSNAME } from "../constants";

interface Props {
  tier: RiskTier;
}

export function TierBadge({ tier }: Props) {
  return <span className={TIER_CLASSNAME[tier]}>{tier.toUpperCase()}</span>;
}
