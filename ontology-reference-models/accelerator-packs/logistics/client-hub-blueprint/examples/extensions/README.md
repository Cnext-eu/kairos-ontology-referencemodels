# Silver Extension Examples

These files are **starter templates** for silver-layer projection annotations.
They show recommended SCD types, natural keys, FK declarations, and naming
conventions for each reference model domain.

## How to use

1. Copy the relevant `*-silver-ext.ttl` file into your client hub's
   `model/extensions/` folder.
2. Rename to match your domain (e.g., `party-silver-ext.ttl`).
3. Customize:
   - Adjust `kairos-ext:scdType` based on your history-tracking needs.
   - Update `kairos-ext:naturalKey` to match your source system identifiers.
   - Add/remove `kairos-ext:silverForeignKey` declarations for your join patterns.

## Important

These are **suggestions, not rules**. Silver extensions are implementation
decisions that depend on your data platform, source systems, and reporting
requirements. Treat them as a starting point, not a specification.

## Contents

| File | Domain | Classes |
|------|--------|---------|
| `party-silver-ext.ttl` | BSP Party | TradeParty + 11 subtypes |
| `commercial-silver-ext.ttl` | BSP Commercial | SalesContract, TradeTerms, etc. |
| `financial-silver-ext.ttl` | BSP Financial | Invoice, Charge, Payment, etc. |
| `documents-silver-ext.ttl` | BSP Documents | Document types and evidence |
| `compliance-silver-ext.ttl` | BSP Compliance | ComplianceObligation, Policy |
| `reference-data-silver-ext.ttl` | BSP Reference Data | Code lists, locations, UoM |
| `cost-accounting-silver-ext.ttl` | BSP Cost Accounting | CostAllocation, Budget, Variance |
| `revenue-yield-silver-ext.ttl` | BSP Revenue & Yield | RevenueItem, LoadFactor, RateCard |
| `demurrage-detention-silver-ext.ttl` | DCSA D&D | Demurrage/Detention charges, tariffs |

## See also

- [BLUEPRINT.md](../../BLUEPRINT.md) — full domain architecture and medallion layers
- [data-domains.yaml](../../data-domains.yaml) — domain import registry
- **kairos-design-silver** skill — interactive guide for creating silver extensions
