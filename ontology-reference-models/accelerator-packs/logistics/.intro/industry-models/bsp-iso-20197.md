# BSP (ISO 20197-1) Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

| Item | Details |
|---|---|
| What is it? | The Buy-Ship-Pay reference data model (ISO 20197-1), represented as modular OWL domain ontologies. |
| Main focus | Party roles, commercial agreements, invoicing/charges, compliance, documents, and reference data. |
| Why selected in this blueprint | Supplies the commercial and financial backbone that complements operational transport standards. |
| Who is behind it | ISO standardization stream with UN/CEFACT-aligned concepts; implemented in Kairos domain modules. |
| Official site / references | https://www.iso.org |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/bsp#` |
| Adoption context | Strong fit for organizations that need standardized commercial and settlement semantics across transport chains. |
| Kairos modules used | `bsp/party`, `bsp/commercial`, `bsp/financial`, `bsp/documents`, `bsp/compliance`, `bsp/reference-data`, `bsp/cost-accounting`, `bsp/revenue-yield`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/BSP/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `TradeParty` | Generic business party participating in buy-ship-pay interactions. | `partyIdentifier`, `partyRole`, `hasAddress` |
| `SalesContract` | Commercial agreement defining terms, obligations, and conditions. | `contractNumber`, `validFrom`, `tradeTerm` |
| `Invoice` | Financial claim document for charges and settlement. | `invoiceNumber`, `invoiceDate`, `totalAmount` |
| `Charge` | Monetary component applied to transport/commercial transactions. | `chargeType`, `chargeAmount`, `currencyCode` |
| `TariffSchedule` | Structured pricing/rate framework used in contracting and billing. | `rateCode`, `effectiveDate`, `appliesToService` |
| `Payment` | Settlement action that clears invoices and outstanding balances. | `paymentReference`, `paymentDate`, `paidAmount` |
