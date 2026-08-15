# DCSA Domain v3.1.x fit-gap against Kairos DCSA ontology

**Baseline:** DCSA Domain v3.1.0, the released DCSA Components domain used for common simple types.

**Comparison context:** DCSA Domain v3.1.1 was also parsed. Upstream README marks v3.1.1 as not released and describes only minor latitude/longitude regex/example fixes.

**Local target:** `kairos_ontology_referencemodels/ontology-reference-models/derived-ontologies/DCSA/current/**/*.ttl`.

## Source provenance

| Source | Version | Path / URL | Notes |
|---|---:|---|---|
| DCSA OpenAPI | 3.1.0 | `dcsaorg/DCSA-OpenAPI/domain/dcsa/dcsa_domain_v3.1.0.yaml` | Released DCSA Domain v3.1.x baseline. |
| DCSA OpenAPI | 3.1.1 | `dcsaorg/DCSA-OpenAPI/domain/dcsa/dcsa_domain_v3.1.1.yaml` | Not released; parsed to check v3.1.x drift. |
| Kairos local DCSA ontology | 1.2.0 | `kairos_ontology_referencemodels/ontology-reference-models/derived-ontologies/DCSA/current/` | Modular OWL/Turtle reference ontology. |

## Executive summary

- Parsed DCSA Domain v3.1.0 schemas/simple types: **269**.
- Present in local DCSA ontology by exact/label-normalized match: **51**.
- Missing from local DCSA ontology by exact/label-normalized match: **218**.
- DCSA Domain v3.1.1 added **0** terms and removed **0** terms versus v3.1.0.

Important nuance: DCSA Domain is a shared component/simple-type catalog, not the same as the released Booking API payload. It can contain canonical DCSA data terms that are absent from specific API YAMLs.

## Fit-gap by area

| Area | Present | Missing |
|---|---:|---:|
| booking | 3 | 9 |
| common | 18 | 111 |
| dangerous_goods | 6 | 22 |
| document | 2 | 7 |
| equipment | 3 | 17 |
| location | 6 | 16 |
| party | 2 | 8 |
| transport | 11 | 28 |

## High-value terms

| DCSA term | Status | Local term | Type | Description |
|---|---|---|---|---|
| `bargeCallSignNumber` | present | `bargeCallSignNumber` | string | A unique alphanumeric identity that belongs to the barge and is assigned by the International Telecommunication Union (ITU). It consists of a threeletter alphanumeric prefix that i |
| `bargeFlag` | present | `bargeFlag` | string | The flag of the nation whose laws the barge is registered under. This is the [ISO 3166 two-letter country code](https://www.iso.org/obp/ui/#iso:pub:PUB500001:en) |
| `bargeName` | present | `bargeName` | string | The name of the Barge. If the name is not known `TBD` (To Be Decided) should be used |
| `bargeOperatorCarrierCode` | present | `bargeOperatorCarrierCode` | string | The carrier who is in charge of the Barge operation based on either the SMDG or SCAC code lists |
| `bargeOperatorCarrierCodeListProvider` | present | `bargeOperatorCarrierCodeListProvider` | string | Identifies the code list provider used for the barge operator carriercodes. Possible values are: - SMDG (Ship Message Design Group) - NMFTA (National Motor Freight Traffic Associat |
| `bookingRequestDateTime` | present | `bookingRequestDateTime` | string/date-time | The date and time when the booking was created |
| `bookingUpdatedDateTime` | present | `bookingUpdatedDateTime` | string/date-time | Last date and time when the booking was updated |
| `facilityTypeCode` | present | `facilityTypeCode` | string | The code to identify the specific type of facility. - BORD (Border) - CLOC (Customer location) - COFS (Container freight station) - OFFD (Off dock storage) - DEPO (Depot) - INTE (I |
| `facilityTypeCodeOPR` | present | `facilityTypeCodeOPR` | string | A specialized version of the facilityCode to be used in Operations events. The code to identify the specific type of facility. - PBPL (Pilot boarding place) - BRTH (Berth) - ANCH ( |
| `facilityTypeCodeTRN` | present | `facilityTypeCodeTRN` | string | The code to identify the specific type of facility. The code indicates which role the facility plays during the `transportCall` or during *stuffing*/*stipping*. - BORD (Border) - C |
| `flashPoint` | present | `flashPoint` | number/float | Lowest temperature at which a chemical can vaporize to form an ignitable mixture in air. Condition: only applicable to specific hazardous goods according to the IMO IMDG Code amend |
| `imoClass` | present | `imoClass` | string | The hazard class code of the referenced dangerous goods according to the specified regulation. Examples of possible values are: - `1.1A` (Substances and articles which have a mass  |
| `isLimitedQuantity` | present | `isLimitedQuantity` | boolean | Indicates if the dangerous goods can be transported as limited quantity in accordance with Chapter 3.4 of the IMO IMDG Code. |
| `isMarinePollutant` | present | `isMarinePollutant` | boolean | Indicates if the goods belong to the classification of Marine Pollutant. |
| `isReportableQuantity` | present | `isReportableQuantity` | boolean | Indicates if a container of hazardous material is at the reportable quantity level. If `TRUE`, a report to the relevant authority must be made in case of spill. |
| `modeOfTransport` | present | `modeOfTransport` | string | The mode of transport as defined by DCSA. The currently supported values include: - VESSEL - RAIL - TRUCK - BARGE |
| `packingGroup` | present | `packingGroup` | integer/int32 | The packing group according to the UN Recommendations on the Transport of Dangerous Goods and IMO IMDG Code. |
| `properShippingName` | present | `properShippingName` | string | The proper shipping name for goods under IMDG Code, or the product name for goods under IBC Code and IGC Code, or the bulk cargo shipping name for goods under IMSBC Code, or the na |
| `technicalName` | present | `technicalName` | string | The recognized chemical or biological name or other name currently used for the referenced dangerous goods as described in chapter 3.1.2.8 of the IMDG Code. |
| `transportPlanStage` | present | `transportPlanStage` | string | Code qualifying a specific stage of transport e.g. pre-carriage, main carriage transport or on-carriage transport - PRC (Pre-Carriage) - MNC (Main Carriage Transport) - ONC (On-Car |
| `transportPlanStageSequenceNumber` | present | `transportPlanStageSequenceNumber` | integer/int32 | Sequence number of the transport plan stage |
| `unNumber` | present | `unNumber` | string | United Nations Dangerous Goods Identifier (UNDG) assigned by the UN Sub-Committee of Experts on the Transport of Dangerous Goods and shown in the IMO IMDG. |

## Missing DCSA Domain v3.1.0 terms

| DCSA term | Area | Type | Description |
|---|---|---|---|
| `additionalContainerCargoHandling` | booking | string | Text field to provide cargo handling information already known at the booking stage. |
| `bookingChannelReference` | booking | string | Identification number provided by the platform/channel used for booking request/confirmation, ex: Inttra booking reference, or GTNexus, other. Conditional on booking channel being used |
| `carrierBookingRequestReference` | booking | string | A reference to the booking during the booking request phase |
| `communicationChannelCode` | booking | string | Specifying which communication channel is to be used for this booking e.g. Possible values are: - EI (EDI transmission) - EM (Email) - AO (API) |
| `exportLicenseExpiryDate` | booking | string/date | Expiry date of the export license applicable to the booking. Mandatory to provide in booking request for specific commodities. |
| `exportLicenseIssueDate` | booking | string/date | Issue date of the export license applicable to the booking. Mandatory to provide in booking request for specific commodities |
| `isContainerInspectionCertificateProvided` | booking | boolean | Indicates if the container was inspected and the ensuing inspection certificate has been enclosed to the booking request. |
| `partyFunction` | booking | string | Specifies the role of the party in a given context. Possible values are: - `OS` (Original shipper) - `CN` (Consignee) - `COW` (Invoice payer on behalf of the consignor (shipper)) - `COX` (Invoice payer on behalf of the c |
| `shipmentCreatedDateTime` | booking | string/date-time | The date and time when the shipment was created (equivalent to when the Booking was confirmed). |
| `EMSNumber` | common | string | The emergency schedule identified in the IMO EmS Guide – Emergency Response Procedures for Ships Carrying Dangerous Goods. Comprises 2 values; 1 for spillage and 1 for fire. Possible values spillage: S-A to S-Z. Possible |
| `airExchangeSetpoint` | common | number/float | Target value for the air exchange rate which is the rate at which outdoor air replaces indoor air within a Reefer container |
| `amsFilingDueDate` | common | string/date | Date when AMS filing should latest be done in the last port of call before visiting the first US port. |
| `arrivalNoticeReference` | common | string | A set of unique characters provided by carrier to identify an Arrival Notice |
| `calculationBasis` | common | string | The code specifying the measure unit used for the corresponding unit price for this cost, such as per day, per ton, per square metre. |
| `cargoGrossVolume` | common | number/float | The grand total volume of the commodity |
| `cargoMovementTypeAtDestination` | common | string | Refers to the shipment term at the unloading of the cargo out of the container. Options are defined in the Cargo Movement Type entity. Possible values are: - `FCL` (Full Container Load) - `LCL` (Less than Container Load) |
| `cargoMovementTypeAtOrigin` | common | string | Refers to the shipment term at the loading of the cargo into the container. Options are defined in the Cargo Movement Type entity. Possible values are: - `FCL` (Full Container Load) - `LCL` (Less than Container Load) |
| `chargeName` | common | string | Free text field describing the charge to apply |
| `chargeTypeCode` | common | string | Description of the charge type applied. |
| `clauseContent` | common | string | The content of the clause. |
| `co2Setpoint` | common | number/float | The percentage of the controlled atmosphere CO<sub>2</sub> target value |
| `codedVariantList` | common | string | Four-character code supplied by Exis Technologies that assists to remove ambiguities when identifying a variant within a single UN number or NA number that may occur when two companies exchange DG information. Character  |
| `commodityType` | common | string | High-level description of goods to be shipped which allow the carrier to confirm acceptance and commercial terms. To be replaced by "description of goods" upon submission of `Shipping Instructions` |
| `competentAuthorityApproval` | common | string | Name and reference number of the competent authority providing the approval. |
| `contractQuotationReference` | common | string | Information provided by the shipper to identify whether pricing for the shipment has been agreed via a contract or a quotation reference. Mandatory if service contract (owner) is not provided. |
| `currencyCode` | common | string | The currency for the charge, using a 3-character code ([ISO 4217](https://en.wikipedia.org/wiki/ISO_4217)). |
| `customsImportDeclarationProcedure` | common | string | Instruction on the administrative processes for submitting tax & duties declarations to the local customs agency |
| `cutOffDateTimeCode` | common | string | Code for the cut-off time. Possible values are: - `DCO` (Documentation cut-off) - `VCO` (VGM cut-off) - `FCO` (FCL delivery cut-off) - `LCO` (LCL delivery cut-off) - `ECP` (Empty container pick-up date and time) - `EFC`  |
| `dateRange` | common | string/iso8601 | The time period for which schedule information is sent. The duration is populated in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) Duration format. |
| `declaredValue` | common | number/float | The value of the cargo that the shipper declares to avoid the carrier's limitation of liability and "Ad Valorem" freight, i.e. freight which is calculated based on the value of the goods declared by the shipper. |
| `declaredValueCurrency` | common | string | The currency used for the declared value, using the 3-character code defined by [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217). |
| `delayReasonCode` | common | string | Reason code for the delay. See SMDG [Code list DELAY](https://smdg.org/documents/smdg-code-lists/delay-reason-and-port-call-activity/) for a list of valid codes to be used for this attribute. |
| `deliveryOrderReference` | common | string | A set of unique characters provided by carrier to identify a Delivery Order |
| `demurrageFreetime` | common | number | The number of days that the consignee has to pick up the full container before demurrage fees are charged. Reference to carrier website or individual charge as per service contract/agreement. |
| `descriptionOfGoods` | common | string | The cargo description are details which accurately and properly describe the cargo being shipped in the container(s) as provided by the shipper. |
| `destinationChargesPaymentTermCode` | common | string | An indicator of whether destination charges are prepaid (PRE) or collect (COL). When prepaid, the charges are the responsibility of the shipper or the Invoice payer on behalf of the shipper (if provided). When collect, t |
| `detentionFreetime` | common | number | The number of days that the consignee has to pick up or return the empty container before detention fees are charged. Reference to carrier website or individual charge as per service contract/agreement. |
| `displayedName` | common | string | A line of the address to be displayed on the transport document. |
| `emptyIndicatorCode` | common | string | Code to denote whether the equipment is empty or laden. |
| `endOfHoldingTime` | common | string/date | Date by when the refrigerated liquid needs to be delivered. |
| `etaAtPlaceOfDeliveryDateTime` | common | string/date-time | The date of expected time of arrival of the shipment at place of delivery. **Condition**: Only when onward transport is done by the carrier to either an inland point or Door address. |
| `etaAtPortOfDischargeDateTime` | common | string/date-time | The date of expected time of arrival of the vessel at the Port of Discharge. |
| `eventComment` | common | string | An additional Comment to a timestamp that can be shared with the receiver party. |
| `expectedArrivalAtPlaceOfDeliveryEndDate` | common | string/date | The end date (provided as a range together with `expectedArrivalAtPlaceOfDeliveryStartDate`) for when the shipment is expected to arrive at final destination. If vessel/voyage or `expectedDepartureDate` is not provided,  |
| `expectedArrivalAtPlaceOfDeliveryStartDate` | common | string/date | The start date (provided as a range together with `expectedArrivalAtPlaceOfDeliveryEndDate`) for when the shipment is expected to arrive at final destination. If vessel/voyage or `expectedDepartureDate` is not provided,  |
| `expectedDepartureDate` | common | string/date | The date when the shipment is expected to be loaded on board a vessel as provided by the shipper or its agent. If vessel/voyage or expected date of arrival is not provided, this is mandatory |
| `exportDeclarationReference` | common | string | A government document permitting designated goods to be shipped out of the country. Reference number assigned by an issuing authority to an Export License. The export license must be valid at time of departure. Required  |
| `finalDestinationExpectedArrivalDate` | common | string/date | The dates (provided as a range) for when the shipment is expected to arrive at final destination. If vessel/voyage or expected departure date or pick-up date at place of receipt is not provided, this field is mandatory |
| `firmsCode` | common | string | A four digit alpha-numeric identifier assigned by U.S. Customs and Border Protection and required to clear customs at the Port of Discharge. **Condition**: Only applicable to imports into USA. |
| `floor` | common | string | The floor of the party’s street number. |
| `freightPaymentTermCode` | common | string | An indicator of whether freight and ancillary fees for the main transport are prepaid (PRE) or collect (COL). When prepaid the charges are the responsibility of the shipper or the Invoice payer on behalf of the shipper ( |
| `fumigationDateTime` | common | string/date-time | Date & time when the container was fumigated |
| `humiditySetpoint` | common | number/float | The percentage of the controlled atmosphere humidity target value |
| `importLicenseReference` | common | string | A certificate, issued by countries exercising import controls, that permits importation of the articles stated in the license. Reference number assigned by an issuing authority to an Import License. The import license nu |
| `incoTerms` | common | string | Transport obligations, costs and risks as agreed between buyer and seller as defined by [ICC](https://iccwbo.org/business-solutions/incoterms-rules/). A list of possible values: - EXW (Ex-Works) - FCA (Free Carrier) - FA |
| `inhalationZone` | common | string | The zone classification of the toxicity of the inhalant. Possible values are: - `A` (Hazard Zone A) can be asigned to specific gases and liquids - `B` (Hazard Zone B) can be asigned to specific gases and liquids - `C` (H |
| `isAMSACIFilingRequired` | common | boolean | Customs filing for US (AMS) or Canadian (ACI) customs |
| `isBulbMode` | common | boolean | Is special container setting for handling flower bulbs active |
| `isCargoProbe1Required` | common | boolean | Is `Cargo Probe 1 Required` enabled allowing the container to emit temperatures. |
| `isCargoProbe2Required` | common | boolean | Is `Cargo Probe 2 Required` enabled allowing the container to emit temperatures. |
| `isCargoProbe3Required` | common | boolean | Is `Cargo Probe 3 Required` enabled allowing the container to emit temperatures. |
| `isCargoProbe4Required` | common | boolean | Is `Cargo Probe 4 Required` enabled allowing the container to emit temperatures. |
| `isColdTreatmentRequired` | common | boolean | Indicator whether cargo requires cold treatment prior to loading at origin or during transit, but prior arrival at POD |
| `isCompetentAuthorityApprovalProvided` | common | boolean | Indicates if the cargo require approval from authorities |
| `isControlledAtmosphereRequired` | common | boolean | Indicator of whether cargo requires Controlled Atmosphere. |
| `isDrainholesOpen` | common | boolean | Is drainholes open on the container |
| `isExceptedQuantity` | common | boolean | Indicates if the dangerous goods can be transported as excepted quantity in accordance with Chapter 3.5 of the IMO IMDG Code. |
| `isExportDeclarationRequired` | common | boolean | Information provided by the shipper whether an export declaration is required for this particular shipment/commodity/destination. |
| `isGeneratorSetRequired` | common | boolean | Indicator whether reefer container should have a generator set attached at time of release from depot |
| `isHighValueCargo` | common | boolean | Cargo value exceeds USD XXX K (carrier specific) |
| `isHot` | common | boolean | Indicates if high temperature cargo is shipped. |
| `isImportLicenseRequired` | common | boolean | Information provided by the shipper whether an import permit or license is required for this particular shipment/commodity/destination. |
| `isPartialLoadAllowed` | common | boolean | Indication whether the shipper agrees to load part of the shipment in case where not all of the cargo is delivered within cut-off. |
| `isPreCoolingRequired` | common | boolean | Indicator whether reefer container should be pre-cooled to the temperature setting required at time of release from depot |
| `isShippedOnBoardType` | common | boolean | Specifies whether the Transport document is a received for shipment, or shipped on board. |
| `isToBeNotified` | common | boolean | Used to decide whether the party will be notified of the arrival of the cargo. |
| `isToOrder` | common | boolean | Indicates whether the B/L is issued `to order` or not. If `true`, the B/L is considered negotiable and an Endorsee party can be defined in the Document parties. If no Endorsee is defined, the B/L is blank endorsed. If `f |
| `isVentilationOpen` | common | boolean | If `true` the ventilation orifice is `Open` - if `false` the ventilation orifice is `closed` |
| `isWaste` | common | boolean | Indicates if waste is being shipped |
| `issueDate` | common | string/date | Local date when the transport document has been issued. Can be omitted on draft transport documents, but must be provided when the document has been issued. |
| `itNumber` | common | string | A number issued by U.S. Customs to track any imported goods moving inland from a Port of Discharge. **Condition**: Only applicable to imports into USA that include a `Place of Delivery`. |
| `measuredAirExchange` | common | number/float | The measured value for the air exchange rate which is the rate at which outdoor air replaces indoor air within a Reefer container |
| `measuredCo2` | common | number/float | The measured value of the controlled atmosphere `CO<sub>2</sub>` value in percent |
| `measuredHumidity` | common | number/float | The measured value of the controlled atmosphere humidity value in percent |
| `measuredO2` | common | number/float | The measured value of the controlled atmosphere `O<sub>2</sub>` value in percent |
| `naNumber` | common | string | Four-digit number that is assigned to dangerous, hazardous, and harmful substances by the United States Department of Transportation. |
| `netWeight` | common | number/float | Total weight of the goods carried, excluding packaging. |
| `nmftaCode` | common | string | The Standard Carrier Alpha Code (SCAC) provided by NMFTA. |
| `numberOfCopies` | common | integer/int32 | The requested number of copies of the Transport document to be issued by the carrier. Only applicable for physical documents |
| `numberOfCopiesWithCharges` | common | integer/int32 | The requested number of copies of the Transport document to be issued by the carrier including charges. Only applicable for physical (paper) documents |
| `numberOfCopiesWithoutCharges` | common | integer/int32 | The requested number of copies of the Transport document to be issued by the carrier **NOT** including charges. Only applicable for physical (paper) documents |
| `numberOfOriginalsWithCharges` | common | integer/int32 | Number of originals of the bill of lading that has been requested by the customer with charges. Only applicable for physical documents. |
| `numberOfOriginalsWithoutCharges` | common | integer/int32 | Number of originals of the bill of lading that has been requested by the customer without charges. Only applicable for physical documents. |
| `numberOfRiderPages` | common | integer/int32 | The number of additional pages required to contain the goods description on a transport document. Only applicable for physical transport documents. |
| `o2Setpoint` | common | number/float | The percentage of the controlled atmosphere O<sub>2</sub> target value |
| `originChargesPaymentTermCode` | common | string | An indicator of whether origin charges are prepaid (PRE) or collect (COL). When prepaid, the charges are the responsibility of the shipper or the Invoice payer on behalf of the shipper (if provided). When collect, the ch |
| `partialLoadAllowed` | common | boolean | Indication whether the shipper agrees to load part of the shipment in case where not all of the cargo is delivered within cut-off. |
| `paymentTermCode` | common | string | An indicator of whether a charge is prepaid (PRE) or collect (COL). When prepaid, the charge is the responsibility of the shipper or the Invoice payer on behalf of the shipper (if provided). When collect, the charge is t |
| `placeOfReceiptPickupDate` | common | string/date | The date when the shipment must be picked up by the carrier at place of receipt. Only applicable when carrier haulage is requested. |
| `portVisitReference` | common | string | The unique reference that can be used to link different `transportCallReferences` to the same port visit. The reference is provided by the port to uniquely identify a port call |
| `quantity` | common | number/float | The amount of unit for this charge item. |
| `receivedForShipmentDate` | common | string/date | Date when the last container linked to the transport document is physically in the terminal (customers cleared against the intended vessel). When provided on a transport document, the transportDocument is a `Received For |
| `referenceValue` | common | string | The actual value of the reference. |
| `requestedNumberOfOriginals` | common | integer/int32 | Number of original copies of the negotiable bill of lading that has been requested by the customer. |
| `returnDescription` | common | string | Additional instruction on the return process of the container |
| `sadt` | common | number/float | Lowest temperature in which self-accelerating decomposition may occur in a substance |
| `sapt` | common | number/float | Lowest temperature in which self-accelerating polymerization may occur in a substance |
| `sendToPlatform` | common | string | Indicates the shipper’s platform on which the eBL should be issued. The value **MUST** be one of: - `WAVE` (Wave) - `CARX` (CargoX) - `ESSD` (EssDocs) - `BOLE` (Bolero) - `EDOX` (EdoxOnline) - `IQAX` (IQAX) - `SECR` (Sec |
| `shipmentUpdatedDateTime` | common | string/date-time | Last date and time when the Shipment was updated. |
| `shippingMark` | common | string | The identifying details of a package or the actual markings that appear on the package(s). This information is provided by the shipper. |
| `shippingMarks` | common | string | The identifying details of a package or the actual markings that appear on the package(s). This information is provided by the shipper. |
| `specialCertificateNumber` | common | string | Text field to indicate certificate number & segment for specific stowage requirements overulling IMDG code |
| `startDate` | common | string/date | The start date of the period for which schedule information is sent. The value is populated in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) Date format. |
| `stateRegion` | common | string | The state/region of the party’s address. |
| `submissionDateTime` | common | string/date-time | Date and time of submitting the relevant document and attributes |
| `subsidiaryRisk` | common | string | Any risk in addition to the class of the referenced dangerous goods according to the IMO IMDG Code. |
| `taxReference1` | common | string | The identifying number of the consignee or shipper (Individual or entity) used for tax purposes. |
| `taxReference2` | common | string | Optional second identifying number of the consignee or shipper (Individual or entity) used for tax purposes. |
| `termsAndConditions` | common | string | Carrier terms and conditions of transport. |
| `url` | common | string | URL for the contact |
| `airExchangeUnit` | dangerous_goods | string | The unit for `airExchange` in metrics- or imperial- units per hour - MQH (Cubic metre per hour) - FQH (Cubic foot per hour) **NB:** This is a conditional field. If `airExchange` is specified then this field is required |
| `currencyAmount` | dangerous_goods | number/float | The monetary value of all freight and other service charges for a transport document, with a maximum of 2-digit decimals. |
| `demurrageAmount` | dangerous_goods | number/float | A per-day fee paid by consignee to carrier after expiry of freetime for storing a full container at the equipment handling facility (i.e., terminal or railhead). Fee relates to the cargo, inside the container. Reference  |
| `detentionAmount` | dangerous_goods | number/float | A per-day fee paid by consignee to carrier for holding ('detaining') a container upon release from the carrier facility. Fee relates to the use of equipment whether full or empty. Reference to carrier website or individu |
| `dgGrossWeight` | dangerous_goods | number/float | The grand total weight of the DG cargo and weight per UNNumber/NANumber including packaging items being carried, which can be expressed in imperial or metric terms, as provided by the shipper. |
| `dgRemarks` | dangerous_goods | string | To provide additional information |
| `dgVolume` | dangerous_goods | number/float | The volume of the referenced dangerous goods. |
| `dimensionUnit` | dangerous_goods | string | The unit of measure which can be expressed in - MTR (Meter) - FOT (Foot) |
| `isEmptyUncleanedResidue` | dangerous_goods | boolean | Indicates if the cargo is residue. |
| `isSalvagePackings` | dangerous_goods | boolean | Indicates if the cargo has special packaging for the transport, recovery or disposal of damaged, defective, leaking or nonconforming hazardous materials packages, or hazardous materials that have spilled or leaked. |
| `measuredAmbientTemperature` | dangerous_goods | number/float | The measured value of the ambient temperature of the Reefer. |
| `measuredTemperature` | dangerous_goods | number/float | The measured value of the temperature of the Reefer |
| `netExplosiveContent` | dangerous_goods | number/float | The total weight of the explosive substances, without the packaging’s, casings, etc. |
| `netExplosiveContentUnit` | dangerous_goods | string | Unit of measure used to describe the `netExplosiveWeight`. Possible values are - KGM (Kilograms) - GRM (Grams) |
| `netWeightUnit` | dangerous_goods | string | Unit of measure used to describe the `netWeight`. Possible values are - KGM (Kilograms) - LBR (Pounds) |
| `storageAmount` | dangerous_goods | number/float | A per-day fee paid for the occupancy of space in, or near, the port (e.g., container yard, terminal), and thus covers the cost incurred by the owner of the space. Reference to facility (or carrier) website. |
| `temperatureSetpoint` | dangerous_goods | number/float | Target value of the temperature for the Reefer based on the cargo requirement. |
| `unitPrice` | dangerous_goods | number/float | The unit price of this charge item in the currency of the charge. |
| `universalServiceReference` | dangerous_goods | string | A global unique service reference, as per DCSA standard, agreed by VSA partners for the service. The service reference must match the regular expression pattern: `SR\d{5}[A-Z]`. The letters `SR` followed by `5 digits`, f |
| `volumeUnit` | dangerous_goods | string | The unit of measure which can be expressed in either imperial or metric terms - FTQ (Cubic foot) - MTQ (Cubic meter) |
| `volumeUnitDG` | dangerous_goods | string | The unit of measure which can be expressed in either imperial or metric terms - FTQ (Cubic foot) - MTQ (Cubic meter) - LTR (Litre) |
| `weightUnit` | dangerous_goods | string | The unit of measure which can be expressed in imperial or metric terms - KGM (Kilograms) - LBR (Pounds) |
| `deliveryInstructionReference` | document | string | A set of unique characters provided by carrier to identify a Delivery Instruction |
| `documentReferenceNumber` | document | string | A unique number allocated by the shipping line to the transport document and the main number used for the tracking of the status of the shipment. |
| `packageNameOnBL` | document | string | To provide package description displayed on the BL |
| `publicKey` | document | string | The public key used for a digital signature. |
| `shippingInstructionsCreatedDateTime` | document | string/date-time | Date and time when the `Shipping Instructions` was created |
| `shippingInstructionsReference` | document | string | The identifier for a `Shipping Istructions` provided by the carrier for system purposes. |
| `shippingInstructionsUpdatedDateTime` | document | string/date-time | Date and time when the `Shipping Instructions` was updated |
| `confirmedEquipmentUnits` | equipment | integer/int32 | Number of confirmed equipment units |
| `containerDepositAmount` | equipment | number/float | A specified amount that the importer is made to pay as a guarantee for the return of the container after the goods in it have been stripped. A maximum of 2 digits should be provided |
| `containerInspectionBodyIdentifier` | equipment | string | Name of the person/company that performed the container inspection |
| `containerInspectionCertificateNumber` | equipment | string | Number of the container inspection certificate. |
| `equipmentSetpointAirExchange` | equipment | number/float | The value set on the container for the air exchange rate at which outdoor air replaces indoor air within a Reefer |
| `equipmentSetpointAmbientTemperature` | equipment | number/float | The value of the ambient temperature set for the Reefer. |
| `equipmentSetpointCo2` | equipment | number/float | The percentage value of the controlled atmosphere `CO<sub>2</sub>` set for the Reefer |
| `equipmentSetpointHumidity` | equipment | number/float | The percentage value of the controlled atmosphere humidity set for the Reefer |
| `equipmentSetpointO2` | equipment | number/float | The percentage value of the controlled atmosphere `O<sub>2</sub>` set for the Reefer |
| `equipmentSetpointTemperature` | equipment | number/float | The value of the temperature set for the Reefer |
| `isEquipmentSubstitutionAllowed` | equipment | boolean | Indicates if an alternate equipment type can be provided by the carrier. |
| `isNonOperatingReefer` | equipment | boolean | If the equipment is a Reefer Container then setting this attribute will indicate that the container should be treated as a `DRY` container. **Condition:** Only applicable if `ISOEquipmentCode` shows a Reefer type. |
| `reeferExtraMaterial` | equipment | string | spacers, filler, board or dunnage material used to stabilize cargo and ensure optimal airflow inside the Reefer container. |
| `reeferProductName` | equipment | string | Carrier specific commercial name indicating the technology service offered. |
| `requestedEquipmentUnits` | equipment | integer/int32 | Number of requested equipment units. |
| `sealSource` | equipment | string | The source of the seal, namely who has affixed the seal. This attribute links to the Seal Source ID defined in the Seal Source reference data entity. Possible values are: - CAR (Carrier) - SHI (Shipper) - PHY (Phytosanit |
| `sealType` | equipment | string | The type of seal. This attribute links to the Seal Type ID defined in the Seal Type reference data entity. Possible values are: - KLP (Keyless padlock) - BLT (Bolt) - WIR (Wire) |
| `UNLocationName` | location | string | The name of the UN Location identified by the UN location code above. |
| `addressLine` | location | string | A single address line to be used when a B/L needs to be printed. |
| `addressLineNumber` | location | integer/int32 | The order of items |
| `addressName` | location | string | Name of the address |
| `carrierLocationReference` | location | string | A carrier specific reference to location. |
| `cityName` | location | string | The city name of the party’s address. |
| `country` | location | string | The country of the party’s address. |
| `countryCode` | location | string | The 2 characters for the country code using [ISO 3166-1 alpha-2](https://www.iso.org/obp/ui/#iso:pub:PUB500001:en) |
| `eventLocationDateTime` | location | string/date-time | A date when the event is taking place at the location |
| `facilityCodeListProvider` | location | string | The provider used for identifying the facility Code. Some facility codes are only defined in combination with an `UN Location Code` - BIC (Requires a UN Location Code) - SMDG (Requires a UN Location Code) |
| `latitude` | location | string | Geographic coordinate that specifies the north–south position of a point on the Earth&apos;s surface. |
| `locationName` | location | string | The name of the location. |
| `longitude` | location | string | Geographic coordinate that specifies the east–west position of a point on the Earth&apos;s surface. |
| `postCode` | location | string | The post code of the party’s address. |
| `streetName` | location | string | The name of the street of the party’s address. |
| `streetNumber` | location | string | The number of the street of the party’s address. |
| `carrierCodeListProvider` | party | string | The provider used for identifying the issuer Code. Possible values are: - SMDG (Ship Message Design Group) - NMFTA (National Motor Freight Traffic Association) _includes SPLC (Standard Point Location Code)_ |
| `carrierServiceCode` | party | string | The carrier-specific code of the service for which the schedule details are published. |
| `carrierServiceName` | party | string | The name of a service as specified by the carrier |
| `contactName` | party | string | Name of the contact |
| `contactPhone` | party | string | Phone number for the contact |
| `email` | party | string | `E-mail` address to be used |
| `isCustomsFilingSubmissionByShipper` | party | boolean | Indicates whether the shipper will submit the destination customs filing directly. If `false` the shipper requests the carrier to submit the customs filing on their behalf. Mandatory if AMS/ACI filing is required |
| `partyName` | party | string | Name of the party. |
| `amendToTransportDocument` | transport | string | This field can be used to reference a Transport Document that is issued (documentStatus = `ISSU`) in order to amend or request changes. `AmendToTransportDocument` is used in Electronic Bill of Lading IFS "UseCase 10 - Re |
| `carrierExportVoyageNumber` | transport | string | The identifier of an export voyage. The carrier-specific identifier of the export Voyage. |
| `carrierImportVoyageNumber` | transport | string | The identifier of an import voyage. The carrier-specific identifier of the import Voyage. |
| `carrierVoyageNumber` | transport | string | The carrier-specific identifier of the Voyage. |
| `exportVoyageNumber` | transport | string | The identifier of an export voyage. The vessel operator-specific identifier of the export Voyage. |
| `importVoyageNumber` | transport | string | The identifier of an import voyage. The vessel operator-specific identifier of the import Voyage. |
| `transportCallReference` | transport | string | A carrier definied reference to a `TransportCall`. In the case the Means of Transport is a `Vessel` and the facility is a `Port`/`Terminal` - this reference should be considered a **Terminal Call Reference** |
| `transportCallSequenceNumber` | transport | integer/int32 | Transport operator&apos;s key that uniquely identifies each individual call. This key is essential to distinguish between two separate calls at the same location within one voyage. |
| `transportControlTemperature` | transport | number/float | Maximum temperature at which certain substance (such as organic peroxides and self-reactive and related substances) can be safely transported for a prolonged period. |
| `transportDocumentCreatedDateTime` | transport | string/date-time | Date and time when the TransportDocument was created |
| `transportDocumentTypeCode` | transport | string | Specifies the type of the transport document - BOL (Bill of Lading) - SWB (Sea Waybill) |
| `transportDocumentUpdatedDateTime` | transport | string/date-time | Date and time when the TransportDocument was updated |
| `transportEmergencyTemperature` | transport | number/float | Temperature at which emergency procedures shall be implemented |
| `universalExportVoyageReference` | transport | string | A global unique voyage reference for the export Voyage, as per DCSA standard, agreed by VSA partners for the voyage. The voyage reference must match the regular expression pattern: `\d{2}[0-9A-Z]{2}[NEWSR]` - `2 digits`  |
| `universalImportVoyageReference` | transport | string | A global unique voyage reference for the import Voyage, as per DCSA standard, agreed by VSA partners for the voyage. The voyage reference must match the regular expression pattern: `\d{2}[0-9A-Z]{2}[NEWSR]` - `2 digits`  |
| `universalVoyageReference` | transport | string | A global unique voyage reference, as per DCSA standard, agreed by VSA partners for the voyage. The voyage reference must match the regular expression pattern: `\d{2}[0-9A-Z]{2}[NEWSR]` - `2 digits` for the year - `2 alph |
| `vesselCallSign` | transport | string | A unique alphanumeric identity that belongs to the vessel and is assigned by the International Telecommunication Union (ITU). It consists of a threeletter alphanumeric prefix that indicates nationality, followed by one t |
| `vesselCallSignNumber` | transport | string | A unique alphanumeric identity that belongs to the vessel and is assigned by the International Telecommunication Union (ITU). It consists of a threeletter alphanumeric prefix that indicates nationality, followed by one t |
| `vesselDraft` | transport | number/float | The actual draft of the vessel. If the draft is specified in feet (`FOT`) then the decimal part should be concidered as a fraction of a foot and **not** as a number of inches. E.g. 120.5 feet means 120 and a half foot (w |
| `vesselFlag` | transport | string | The flag of the nation whose laws the vessel is registered under. This is the [ISO 3166](https://www.iso.org/obp/ui/#iso:pub:PUB500001:en) two-letter country code |
| `vesselLOA` | transport | number/float | The maximum length of a ship's hull measured parallel to the waterline (Length OverAll). If the length is specified in feet (`FOT`) then the decimal part should be concidered as a fraction of a foot and **not** as a numb |
| `vesselOperatorCarrierCode` | transport | string | The carrier who is in charge of the vessel operation based on either the SMDG or SCAC code lists |
| `vesselOperatorCarrierCodeListProvider` | transport | string | Identifies the code list provider used for the operator and partner carriercodes. |
| `vesselOperatorSMDGLinerCode` | transport | string | The carrier who is in charge of the vessel operation based on the SMDG code |
| `vesselPartnerCarrierCode` | transport | string | The identifier of the vessel partner for which the current message is intended. This field allows specifying multiple, `,` (comma) separated values if there is more than one vessel partner involved. |
| `vesselPartnerCarrierCodeListProvider` | transport | string | Identifies the code list provider used for the vessel operator and partner carrier codes. If `vesselPartnerCarrierCode` is populated, the code list provider field is to be populated as well. |
| `vesselType` | transport | string | Categorization of ocean-going vessels distinguished by the main cargo the vessel carries. Possible values: - GCGO (General cargo) - CONT (Container) - RORO (RoRo) - CARC (Car carrier) - PASS (Passenger) - FERY (Ferry) -  |
| `vesselWidth` | transport | number/float | Overall width of the ship measured at the widest point of the nominal waterline. If the width is specified in feet (`FOT`) then the decimal part should be concidered as a fraction of a foot and **not** as a number of inc |

## Present DCSA Domain v3.1.0 terms

| DCSA term | Local term | Local kind | Local domain | Local range |
|---|---|---|---|---|
| `HSCode` | `hsCode` | datatype_property | Commodity | string |
| `ISOEquipmentCode` | `isoEquipmentCode` | datatype_property | Container | string |
| `UNLocationCode` | `unLocationCode` | datatype_property | Location | string |
| `bargeCallSignNumber` | `bargeCallSignNumber` | datatype_property | BargeTransportCall | string |
| `bargeFlag` | `bargeFlag` | datatype_property | BargeTransportCall | string |
| `bargeName` | `bargeName` | datatype_property | BargeTransportCall | string |
| `bargeOperatorCarrierCode` | `bargeOperatorCarrierCode` | datatype_property | BargeTransportCall | string |
| `bargeOperatorCarrierCodeListProvider` | `bargeOperatorCarrierCodeListProvider` | datatype_property | BargeTransportCall | string |
| `bookingRequestDateTime` | `bookingRequestDateTime` | datatype_property | Booking | dateTime |
| `bookingUpdatedDateTime` | `bookingUpdatedDateTime` | datatype_property | Booking | dateTime |
| `cargoGrossWeight` | `cargoGrossWeight` | datatype_property | Shipment | decimal |
| `carrierBookingReference` | `carrierBookingReference` | datatype_property | Booking | string |
| `carrierCode` | `carrierCode` | datatype_property | Booking | string |
| `cutOffDateTime` | `cutOffDateTime` | datatype_property | CutOffTime | dateTime |
| `deliveryTypeAtDestination` | `deliveryTypeAtDestination` | datatype_property | Booking | string |
| `documentStatus` | `documentStatus` | datatype_property | TransportDocument | string |
| `equipmentReference` | `equipmentReference` | datatype_property | UtilizedTransportEquipment | string |
| `facilityCode` | `facilityCode` | datatype_property | Terminal | string |
| `facilityTypeCode` | `facilityTypeCode` | datatype_property | TransportCall | string |
| `facilityTypeCodeOPR` | `facilityTypeCodeOPR` | datatype_property | Event | string |
| `facilityTypeCodeTRN` | `facilityTypeCodeTRN` | datatype_property | TransportCall | string |
| `flashPoint` | `flashPoint` | datatype_property | Commodity | decimal |
| `imoClass` | `imoClass` | datatype_property | Commodity | string |
| `isElectronic` | `isElectronic` | datatype_property | TransportDocument | boolean |
| `isLimitedQuantity` | `isLimitedQuantity` | datatype_property | Commodity | boolean |
| `isMarinePollutant` | `isMarinePollutant` | datatype_property | Commodity | boolean |
| `isReportableQuantity` | `isReportableQuantity` | datatype_property | Commodity | boolean |
| `isShipperOwned` | `isShipperOwned` | datatype_property | Container | boolean |
| `modeOfTransport` | `modeOfTransport` | datatype_property | TransportCall | string |
| `numberOfPackages` | `numberOfPackages` | datatype_property | CargoItem | integer |
| `packageCode` | `packageCode` | datatype_property | CargoItem | string |
| `packingGroup` | `packingGroup` | datatype_property | Commodity | integer |
| `plannedArrivalDate` | `plannedArrivalDate` | datatype_property | TransportPlanLeg | dateTime |
| `plannedDepartureDate` | `plannedDepartureDate` | datatype_property | TransportPlanLeg | dateTime |
| `properShippingName` | `properShippingName` | datatype_property | Commodity | string |
| `receiptTypeAtOrigin` | `receiptTypeAtOrigin` | datatype_property | Booking | string |
| `sealNumber` | `sealNumber` | datatype_property | Container | string |
| `serviceContractReference` | `serviceContractReference` | datatype_property | Booking | string |
| `shipmentLocationTypeCode` | `shipmentLocationTypeCode` | datatype_property | Location | string |
| `shippedOnBoardDate` | `shippedOnBoardDate` | datatype_property | BillOfLading | date |
| `tareWeight` | `tareWeight` | datatype_property | Container | decimal |
| `technicalName` | `technicalName` | datatype_property | Commodity | string |
| `temperatureUnit` | `temperatureUnit` | datatype_property | ReeferContainer | string |
| `transportDocumentReference` | `transportDocumentReference` | datatype_property | TransportDocument | string |
| `transportPlanStage` | `transportPlanStage` | datatype_property | TransportCall | string |
| `transportPlanStageSequenceNumber` | `transportPlanStageSequenceNumber` | datatype_property | TransportCall | integer |
| `unNumber` | `unNumber` | datatype_property | Commodity | string |
| `vesselIMONumber` | `vesselIMONumber` | datatype_property | VesselTransportCall | string |
| `vesselName` | `vesselName` | datatype_property | VesselTransportCall | string |
| `volume` | `volume` | datatype_property | CargoItem | decimal |
| `weight` | `weight` | datatype_property | CargoItem | decimal |

## DCSA Domain v3.1.1 drift check

- Added in v3.1.1 vs v3.1.0: None.
- Removed in v3.1.1 vs v3.1.0: None.
- Changed definitions: **2**.

## Recommendation

Use DCSA Domain v3.1.0 as the reference-model enrichment baseline because it is the released v3.1.x domain. Treat v3.1.1 only as a non-released drift check until DCSA publishes it.

For ontology changes, add only terms that are useful as durable domain semantics. Do not attempt to mirror every simple type mechanically; classify low-level API validation details separately from business-relevant ontology properties.

Generated companion artifacts:

- `dcsa_domain_v3_1_0.parsed.json`
- `dcsa_domain_v3_1_0.parsed.csv`
- `dcsa_domain_v3_1_0.fit_gap.csv`
- `dcsa_domain_v3_1_x.diff.json`
