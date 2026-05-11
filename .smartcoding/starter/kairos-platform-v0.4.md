# Kairos Platform Specifications

**Version:** 0.4  
**Last Updated:** December 2025  
**Document Type:** Platform Constraints & Technical Reference

---

## Overview

The Kairos Platform provides a comprehensive framework for building and hosting Agentic AI solution.
It combines a robust backend infrastructure with flexible UI capabilities, enabling the development of sophisticated business applications with AI-powered decision-making and a user experience optimized for Human and AI collaboration.

---

## Platform Architecture
Platform exists out a Kairos core and one or more Kairos Apps.

### Kairos Core

The core framework provides:
- **Hosting environment** for LangGraph multi-agent AI solutions based on Aegra (similar to LangGraph Platform)
- **Authentication & Authorization** - Centralized security management
- **MCP-enabled DMN Engine** - Deterministic rules validation and calculations compliant to DMN 1.2
- **Admin UI** - to manage the deployment and basic configurations of the Karios Apps.
- **observability** - based on LangSmith for the LLM based observability and Azure Appinsight (openTelemetry) for the other core components.

 

### Kairos Flow
User interface and experience layer providing.
Kairos Flow offers userinterface and behaviors for the Kairos Apps.
It allows users to login and use Kairos Apps where they are authorized to use for this user.
It offers also standard components like notifications, HITL, action panels which can be used by the Kairos Apps.
The actual rendering of the UI is managed by Kairos Flow, where the 'description' what to show is defined in the Kairos App. 
- **UI capabilities** based on streaming agent-to-agent protocol
- **AGUI protocol** support for advanced interactions between the area AI backend and the various User facing component, not limited to UI but also voice or mobile. AGUI works real time and bi-directional
- **A2UI protocol rendered** support genUI capabilities. Flow has a library of UI controls with approriate style and behavior which are used during the render stage of a2ui events. This allows Kairos Apps using Kairos Flow to deliver custom build and dynanically generated UI based on latest standards. 
- **React-based UI component library** with Next.js and Tailwind CSS based on Figma Design

### Kairos Apps
- **Dynamic UI Description** - GenUI Json visualization for AI LLM outputs beyond plain text based on A2UI protocol
- **Multi Agent** - langgraph configurations are specific for the Kairos App, executed by the Aegra in Kairos Core.
- **Dependancies** - Other dependancies needed by the Kairos App, like integration interfaces, Databases, ... are managed through containerized apps which will be part of the deployment package of a Kairos App.
These all will be bundled togheter with the Customer-specific solutions containing:
- **Business logic components** specific to customer use cases
- **Data source integrations** 
- **MCP clients** to external services (SharePoint, MS Fabric, etc.)


## Technical Architecture

### Multi-Agent System
- **Framework:** LangGraph hosted in Aegra
- **Monitoring:** LangSmith for AI agent observability
- **Orchestration:** Agent-to-agent communication and coordination
- **Conversation memory:** supported by out of the box langgraph conversation memory


### Decision Logic
- **Deterministic Logic:** Kairos DMN modules (DMN 1.2 compliant)
- **Non-Deterministic Logic:** AI/LLM-powered decision-making
- **Process Management:** Kairos CMMN module for process flows

### Semantic Layer
- **Ontology Hub:** OWL and RDF-based industry models
- **Purpose:** Captures semantics of Kairos Apps
- **Benefit:** Ensures consistent understanding across agents and systems

### Human-in-the-Loop (HITL)
- **Core functionality** embedded in Kairos Platform
- **Purpose:** Enable human oversight and intervention in AI workflows
- **Integration:** Seamless handoff between automated and manual processes

---

## Infrastructure & Deployment

### Hosting
- **Cloud Platform:** Microsoft Azure
- **Deployment Model:** Customer-owned Azure Resource Group dedicated to Kairos
- **Architecture:** Modular and flexible, leveraging containerized services

### Container Strategy
- All Kairos components (Core, Flow, Apps) are containerized
- Enables scalability, portability, and consistent deployment
- Supports microservices architecture patterns

---

## Technical Constraints

When designing solutions on Kairos Platform, consider these constraints:

### Backend & AI
- ✅ Multi-agent assistants **must** be based on LangGraph hosted in Aegra
- ✅ AI agent monitoring **must** use LangSmith
- ✅ Deterministic business rules **should** use Kairos DMN modules (DMN 1.2)
- ✅ Semantic modeling **should** use Kairos Ontology Hub (OWL/RDF)

### Process & Workflow
- ✅ Process flows **must** be managed using Kairos CMMN module
- ✅ Human-in-the-Loop (HITL) **is available** as core platform functionality

### User Interface
- ✅ UI development **uses** Kairos Flow framework genUI following the A2UI guidance
- ✅ Frontend technology stack for Kairos FLow 'shell' and our A2UI component rendering 
  - React (UI library)
  - Next.js (framework)
  - Tailwind CSS (styling)
- ✅ Advanced UX **can leverage** AG UI for real-time cross-device interactions
-
### Integration
- ✅ External service integrations **should use** MCP clients where applicable
- ✅ Supported integrations: SharePoint, MS Fabric, and other MCP-compatible services

### Deployment
- ✅ Hosting **must be** on Microsoft Azure
- ✅ Infrastructure **must use** containerized services
- ✅ Deployment **requires** customer-owned Azure Resource Group

---

## Platform Capabilities Summary

| Capability | Technology/Approach |
|------------|---------------------|
| Multi-Agent AI | LangGraph on Aegra |
| Agent Monitoring | LangSmith |
| Deterministic Rules | DMN Engine (DMN 1.2) |
| Semantic Modeling | Ontology Hub (OWL/RDF) |
| Process Management | CMMN Module |
| GenUI Framework | A2UI with renderind based on React + Next.js + Tailwind CSS |
| Advanced UX | AG UI Protocol |
| Authentication/Authorization | Platform Core |
| Human-in-the-Loop | Platform Core |
| External Integrations | MCP Clients |
| Infrastructure | Azure + Containers |

---

## Design Guidelines

### When designing a Kairos App:

1. **Leverage platform capabilities** - Don't reinvent authentication, HITL, or UI frameworks
2. **Use DMN for rules** - Deterministic logic belongs in DMN modules, not code
3. **Model semantics** - Define your domain using Ontology Hub for consistency
4. **Configure, don't code UI** - Describe UI behavior using Kairos framework configuration
5. **Think multi-agent** - Design workflows as agent collaborations on LangGraph
6. **Plan for HITL** - Identify decision points requiring human oversight
7. **Container-ready** - Ensure your app can run in containerized environment
8. **Azure-native** - Design with Azure services and constraints in mind

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.4 | Dec 2025 | Current specification - formatted documentation |
| 0.3 | Dec 2025 | beta |
| 0.2 | - | Previous iteration |
| 0.1 | - | Initial platform specification |

---

**For Questions or Updates:** Contact the Kairos Platform team or refer to internal platform documentation.
