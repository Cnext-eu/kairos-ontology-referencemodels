Yes — logistics/freight forwarding has a **very comparable ecosystem** of “industry models”, but (like finance) it’s spread across **reference data models, message standards, legal instruments, and sector initiatives** rather than one single OWL ontology.

Here are the **best EU-relevant options**, and how they typically fit into an RDF “OntologyHub”.

---

## The closest thing to a “core logistics industry model”

### UN/CEFACT Multimodal Transport Reference Data Model (MMT RDM)

* **What it is:** a reference data model for transport & logistics concepts across modes (parties, consignment, transport movement, equipment, locations, etc.). ([UNECE][1])
* **Why it matters in EU:** it’s the semantic backbone that many digital transport document efforts align to (including eCMR-related work and FIATA mappings). ([unttc.org][2])
* **How to use it in an RDF hub:** treat as your “upper logistics” vocabulary (like FIBO Foundations in finance): stable terms for shipment/consignment/party/location/event/document.

### ISO “Buy-Ship-Pay” Reference Data Model (ISO 20197-1:2024)

* **What it is:** an ISO standard describing a generic RDM, generalizing concepts of the multimodal transport RDM. ([ISO][3])
* **Use:** if you want an ISO anchor for governance and cross-industry interoperability.

---

## EU regulatory anchor for freight data

### EU eFTI Regulation (Electronic Freight Transport Information)

* **What it is:** EU framework to replace paper with electronic freight information and define/commonize required data elements (“common dataset” + subsets). ([Mobility and Transport][4])
* **Very practical detail:** there are implementing acts/specifications (e.g., Commission Implementing Regulation (EU) 2025/2243) that emphasize re-use and standardized data elements. ([EUR-Lex][5])
* **How to use in RDF:** model eFTI as **compliance requirements and data-element obligations** (per mode/authority/process), not as your full business ontology. It becomes a “regulatory profile” layered on your canonical shipment model.

---

## Freight forwarder document standards (forwarder-centric)

### FIATA transport documents (esp. multimodal BL / eFBL)

* FIATA maintains standard forwarder documents and has a **secured digital FIATA Bill of Lading (FBL/eFBL)** initiative. ([FIATA][6])
* There’s also an **electronic FIATA Multimodal Bill of Lading data standard**, created by mapping FBL to UN/CEFACT MMT RDM and published open source. ([UNECE][7])
* **How to use in RDF:** treat FIATA as your “document vocabulary + workflow states” (issue/endorse/surrender etc.) and map document fields to your canonical shipment/consignment objects.

---

## Mode- and domain-specific standards you’ll hit in real EU forwarding

### Road: eCMR (electronic consignment note)

* **What it is:** an additional protocol enabling the electronic consignment note under the CMR convention. ([UNECE][8])
* **How to use in RDF:** as a document/profile for road consignments (again: a profile over your canonical shipment model).

### Ocean container shipping: DCSA standards (Track & Trace, Bill of Lading)

* **What they are:** open standards + APIs for container shipping events and bill of lading processes/data. ([DCSA][9])
* **How to use in RDF:** as an “ocean carrier interface vocabulary” — perfect for eventing and shipment visibility.

### Air cargo: IATA Cargo-XML

* **What it is:** IATA’s modern messaging standard for air cargo communication among airlines, forwarders, handlers, regulators. ([IATA][10])
* **How to use in RDF:** as a message/profile layer for air waybill / status updates etc.

### Customs (EU and global): EUCDM + WCO Data Model

* **EU Customs Data Model (EUCDM)** is designed using the WCO data mapping tool and is customizable by national customs while staying compliant with EU customs rules. ([Taxation and Customs Union][11])
* **WCO Data Model** provides a universal language for cross-border data exchange and single windows. ([World Customs Organization][12])
* **How to use in RDF:** model as “border compliance datasets” linked to shipments/consignments and declarations.

---

## Supply-chain visibility/event standards (very useful with agents + graph + vector)

### GS1 EPCIS + Core Business Vocabulary (CBV)

* **What it is:** a standard for sharing event data for traceability/visibility (“what happened, where, when, why”). ([GS1][13])
* **How to use in RDF:** as your “event ontology/profile” (ShipmentEvent, ObjectEvent, TransportEvent…) that can unify signals from carriers, warehouses, IoT, etc.

---

# How to structure this in an RDF OntologyHub (recommended)

Think in **three layers**:

## 1) Canonical logistics core (your hub’s “truth”)

Use UN/CEFACT MMT RDM / ISO Buy-Ship-Pay concepts as guidance:

* `Shipment`, `Consignment`, `ConsignmentItem`
* `TransportMovement` (legs), `TransportEquipment` (container, trailer)
* `Party` roles: shipper/consignee/forwarder/carrier/notify party
* `Location` / `Facility`
* `Document` (abstract), `ReferenceNumber`/`Identifier`
  This is the semantic backbone you project into LPG, vectors, prompts.

## 2) Profiles / document schemas (don’t make them your core)

Model as RDF “profiles” (constraints + mappings):

* eCMR profile (road)
* FIATA FBL/eFBL profile (forwarder)
* DCSA B/L + Track&Trace profile (ocean)
* IATA Cargo-XML profile (air)
* EUCDM/WCO profile (customs)
* eFTI dataset profile (EU regulatory)

## 3) Event layer (visibility)

Use EPCIS/CBV-style events to unify tracking across parties and modes.

---

# What “similar to FIBO” means here

In finance, **FIBO Foundations** gives you reusable core semantics (party, contract, dates, legal context).
In logistics, the closest equivalents are:

* **UN/CEFACT MMT RDM / ISO Buy-Ship-Pay** for canonical shipment/consignment semantics ([UNECE][1])
* **EPCIS/CBV** for canonical event semantics ([GS1][13])
  …and then you layer the EU/regulatory/document profiles (eFTI, eCMR, FIATA, customs) on top. ([Mobility and Transport][4])

---

If you tell me which modes you support most (**road-only vs multimodal incl. ocean/air**) and whether you need **customs** in scope, I can propose a **minimal “logistics module import list”** (analogous to your minimal FIBO list) and a clean namespace layout for your OntologyHub.

[1]: https://unece.org/trade/uncefact/rdm?utm_source=chatgpt.com "Reference Data Models (RDM) - un/cefact"
[2]: https://unttc.org/documents/using-uncefact-multimodal-transport-reference-data-model-and-semantic-standards-roll-out?utm_source=chatgpt.com "Using the UN/CEFACT Multimodal Transport Reference Data ..."
[3]: https://www.iso.org/obp/ui/en/?utm_source=chatgpt.com "ISO 20197-1:2024(en), Buy-Ship-Pay reference data model"
[4]: https://transport.ec.europa.eu/transport-themes/logistics-and-multimodal-transport/efti-regulation_en?utm_source=chatgpt.com "The eFTI Regulation - Mobility and Transport - European Union"
[5]: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202502243&utm_source=chatgpt.com "Commission Implementing Regulation (EU) 2025/2243 of 6 ..."
[6]: https://fiata.org/digital-bill-of-lading/?utm_source=chatgpt.com "Secured digital FIATA Bill of Lading"
[7]: https://unece.org/digitalization/press/electronic-fiata-multimodal-bill-lading-data-standard-available-open-source?utm_source=chatgpt.com "Electronic FIATA Multimodal Bill of Lading data standard ..."
[8]: https://www.unece.org/fileadmin/DAM/trans/conventn/e-CMRe.pdf?utm_source=chatgpt.com "additional protocol to the convention on"
[9]: https://dcsa.org/standards/track-and-trace/standard-documentation-track-and-trace?utm_source=chatgpt.com "Track & Trace standards documentation for ..."
[10]: https://www.iata.org/en/programs/cargo/e/cargo-xml/?utm_source=chatgpt.com "Cargo-XML Standards"
[11]: https://taxation-customs.ec.europa.eu/online-services/online-services-and-databases-customs/eu-customs-data-model-eucdm_en?utm_source=chatgpt.com "EU Customs Data Model (EUCDM)"
[12]: https://www.wcoomd.org/DataModel?utm_source=chatgpt.com "WCO Data Model"
[13]: https://www.gs1.org/standards/epcis?utm_source=chatgpt.com "EPCIS & CBV"
 

 ---------------------

 https://unece.org/trade/uncefact/rdm


 
 “Widely adopted” depends on what you mean by *adopted*: **as a conceptual reference** vs **implemented as the primary production data model**.

### UN/CEFACT MMT RDM

**Adoption reality**

* **Widely used as a reference / alignment target** in standards and public-sector harmonization efforts, especially in Europe.
* Concrete examples of “reference adoption”:

  * **EU eFTI** (Electronic Freight Transport Information) work explicitly defines the common dataset/subsets and is described as being **based on UN/CEFACT MMT RDM** in multiple eFTI-related materials. ([European Commission][1])
  * **FIATA eFBL** (electronic FIATA Bill of Lading) data standard was created by mapping FIATA’s paper FBL to **UN/CEFACT MMT RDM** and released as open source. ([UNECE][2])
  * UN/CEFACT itself positions MMT RDM as a framework for cross-border transport data harmonization. ([digitalizetrade.org][3])

**What’s *not* (yet) true**

* It’s **not as ubiquitous in day-to-day forwarder/carrier system integrations** as older, entrenched options (e.g., EDIFACT, proprietary carrier portals, mode-specific standards).
* In practice, many organizations *map to it* rather than *store their operational data in it*.

**Takeaway:** MMT RDM is “widely adopted” as a **semantic backbone for harmonization and mapping**, less so as a **native operational canonical model** inside TMS/WMS/forwarder platforms.

---

### ISO Buy–Ship–Pay (ISO 20197-1:2024)

**Adoption reality**

* **Too new to be “widely adopted” in implementations**. Part 1 is a business requirements specification published late 2024. ([ISO][4])
* It’s best understood today as an **ISO umbrella framing** for the UN/CEFACT family of reference data models, rather than the thing vendors have already implemented. ([UN Trade and Development (UNCTAD)][5])

**Takeaway:** ISO BSP is valuable for **governance and credibility** (especially with public sector / cross-border programs), but it’s **early** in terms of real-world software adoption.

---

## What this means for your OntologyHub decision

If you’re building an RDF “OntologyHub” for an EU freight forwarder ecosystem:

### Use MMT RDM / BSP as your **semantic spine** when:


* You need **interoperability across modes** (road/rail/sea/air).
* You expect to align with **EU eFTI** requirements now/soon. ([European Commission][1])
* You want a stable model to map **documents** like FIATA eFBL and (eventually) other e-docs. ([UNECE][2])

### But plan for “translation layers” because:

* Most partners will still talk in **their operational schemas** (carrier APIs, EDI, GS1 EPCIS events, DCSA, IATA Cargo-XML, etc.).
* Your hub should be the **mapping and governance layer**, not necessarily the schema everyone natively stores in.

---

## Practical recommendation (works well)

1. **Canonical RDF concepts**: base your core logistics ontology on MMT RDM concepts (Shipment/Consignment/Party/Location/Equipment/TransportMovement/Document). ([digitalizetrade.org][3])
2. Add **EU profile layers**: eFTI dataset/subsets as constraints/mappings on top. ([European Commission][1])
3. Add **document profiles**: FIATA eFBL mapping as a forwarder document profile. ([UNECE][2])
4. Keep a **partner interface layer**: “adapters” for the standards your partners actually use.

If you tell me your dominant modes (road-only vs multimodal) and whether you must support eFTI compliance in 2026–2027, I can propose a minimal “MMT-inspired module list” similar to the minimal FIBO list we did.

[1]: https://webgate.ec.europa.eu/regdel/web/delegatedActs/2565/documents/latest?lang=en&utm_source=chatgpt.com "EN EN | European Union"
[2]: https://unece.org/digitalization/press/electronic-fiata-multimodal-bill-lading-data-standard-available-open-source?utm_source=chatgpt.com "Electronic FIATA Multimodal Bill of Lading data standard ..."
[3]: https://www.digitalizetrade.org/implementation-instrument/business-requirement-specifications-brs-multi-modal-transport-reference?utm_source=chatgpt.com "Multi Modal Transport Reference Data Model"
[4]: https://www.iso.org/obp/ui/en/?utm_source=chatgpt.com "ISO 20197-1:2024(en), Buy-Ship-Pay reference data model"
[5]: https://unctad.org/news/digitalization-multimodal-data-and-document-exchange-using-un-standards-electronic-corridors?utm_source=chatgpt.com "Digitalization of multimodal data and document exchange ..."


--------------------

https://service.unece.org/trade/uncefact/publication/Transport-Logistics/MMT-RDM/HTML/0521.htm

