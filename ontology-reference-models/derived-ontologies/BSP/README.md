# BSP – Buy-Ship-Pay Domain Modules

Modular decomposition of the **ISO 20197-1:2024 Buy-Ship-Pay Reference Data Model** ontology into six domain-specific OWL modules.

## Structure

```
BSP/
├── bsp.ttl                            # Root ontology – imports all 6 domains
├── party/party.ttl                    # Trade party roles and contact information
├── commercial/commercial.ttl          # Commercial transactions, shipments, events
├── financial/financial.ttl            # Invoicing, payment, trade finance
├── documents/documents.ttl            # Trade, transport, and regulatory documents
├── compliance/compliance.ttl          # Regulatory requirements, tariffs, sanctions
└── reference-data/reference-data.ttl  # Locations, measurements, code lists
```

## Domain Modules

| Module | Namespace | Description |
|--------|-----------|-------------|
| **Party** | `https://www.kairosflow.ai/ont/bsp/party#` | TradeParty, Buyer, Seller, Carrier, Bank, and other party roles |
| **Commercial** | `https://www.kairosflow.ai/ont/bsp/commercial#` | PurchaseOrder, SalesOrder, Quotation, Shipment, TransportService, BusinessEvent |
| **Financial** | `https://www.kairosflow.ai/ont/bsp/financial#` | Invoice, Payment, PaymentTerms, LetterOfCredit, TradeFinanceInstrument |
| **Documents** | `https://www.kairosflow.ai/ont/bsp/documents#` | Document, BillOfLading, AirWaybill, Certificates, CustomsDeclaration |
| **Compliance** | `https://www.kairosflow.ai/ont/bsp/compliance#` | RegulatoryRequirement, TariffClassification, DutyTax, TradeSanction |
| **Reference Data** | `https://www.kairosflow.ai/ont/bsp/reference-data#` | Location, Address, Port, Airport, Country, Measurement, Weight, Volume |

## Design Principles

- **No cross-imports** between domain modules — each module is self-contained
- The **root `bsp.ttl`** imports all six domains via `owl:imports`
- Each module uses its own namespace: `https://www.kairosflow.ai/ont/bsp/<domain>#`
- All original comments and annotations from the monolithic source are preserved
- Properties are distributed to the domain of their primary class

## Source

Derived from the monolithic `buy-ship-pay.ttl` ontology based on:

- **ISO 20197-1:2024** Buy-Ship-Pay Reference Data Model
- **UN/CEFACT** Multi-Modal Transport Reference Data Model

## Versioning

- **Version:** 1.0.0
- **Created:** 2026-01-06
- **Last Modified:** 2026-05-16
- **Creator:** Kairos Ontology Team
