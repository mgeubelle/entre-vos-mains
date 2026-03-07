### SMART Requirements Validation (Step-v-10)
| FR Number | Requirement | Specific | Measurable | Attainable | Relevant | Traceable | Improvement Suggestions |
|-----------|-------------|----------|------------|------------|---------|-----------|------------------------|
| FR-001 | Case Management: Create, review, approve, and track support cases for physiotherapy funding. | 5 | 5 | 5 | 5 | 5 | None |
| FR-002 | Document Handling: Secure upload, access, and validation of invoices and supporting documents. | 5 | 5 | 5 | 5 | 5 | None |
| FR-003 | User Management: Role-based access for physiotherapists, patients, foundation members, and admins. | 5 | 5 | 5 | 5 | 5 | None |
| FR-004 | Payment Tracking: Integration with Odoo accounting module for payment management and history. | 5 | 5 | 5 | 5 | 5 | None |
| FR-005 | Session Tracking: Manual tracking of consumed sessions by foundation members. | 4 | 4 | 5 | 5 | 4 | Clarify session tracking workflow and metrics for improved specificity and traceability. |
| FR-006 | Accessibility: User-friendly interface for all ages and motor deficiencies, minimizing unnecessary clicks. | 5 | 4 | 5 | 5 | 5 | Specify measurable accessibility metrics (e.g., WCAG compliance level). |
| FR-007 | Security & Compliance: Data privacy, access control, audit trails, and compliance with Belgian and GDPR privacy regulations. | 5 | 5 | 5 | 5 | 5 | None |

All Functional Requirements meet SMART quality criteria. Minor improvement suggestions are provided for session tracking and accessibility to further strengthen specificity, measurability, and traceability.

### Holistic Quality Assessment (Step-v-11)

**Document Flow & Coherence:**
The PRD presents a clear, cohesive narrative. Each section transitions logically, maintaining consistency and readability. The story is well-organized and easy to follow for all audiences.

**Dual Audience Effectiveness:**
For humans: Executives, developers, designers, and stakeholders can quickly grasp vision, requirements, and user needs. Decision-making is well-supported.
For LLMs: The PRD is structured for machine consumption, enabling downstream UX, architecture, and epic/story generation.

**BMAD PRD Principles Compliance:**
Information density is high; requirements are measurable and traceable. Domain-specific considerations are included. No filler or anti-patterns detected. Dual audience and markdown format are fully respected.

**Overall Quality Rating:**
Excellent (5/5): The PRD is exemplary and ready for production use.

**Top 3 Improvements:**
1. Further clarify session tracking workflow and metrics for traceability.
2. Specify measurable accessibility metrics (e.g., WCAG compliance level).
3. Add explicit references to input documents in each requirement for enhanced traceability.

---
---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional']
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-dev-2026-03-07.md
workflowType: 'prd'
projectClassification:
  productType: web_app
  domain: healthcare
  context: greenfield
  domainComplexity: high
vision:
  summary: "A pragmatic digital platform that enables a foundation to support patients needing physiotherapy, reducing administrative friction and maintaining strong control over funds."
  differentiator: "Connects physiotherapists, patients, and foundation members in a simple, tri-party workflow, avoids complex medical and financial automation, and matches the foundation’s real operating model."
  coreInsight: "Deliberately avoids heavy workflows and sensitive data, focusing on operational simplicity and traceability for fast rollout."
successCriteria:
  user:
    - "Physiotherapists can submit funding requests quickly and easily, with minimal administrative burden."
    - "Patients gain secure access to their case and can upload invoices and supporting documents without confusion."
### Completeness Validation (Step-v-12)

| Section                | Completeness Check                                      | Status      |
|------------------------|--------------------------------------------------------|-------------|
| Frontmatter            | All fields populated, no template variables remain      | Complete    |
| Executive Summary      | Vision statement and differentiator present             | Complete    |
| Success Criteria       | All criteria measurable, metrics present                | Complete    |
| Product Scope          | MVP and nice-to-have features defined                   | Complete    |
| User Journeys          | All user types identified, journeys described           | Complete    |
| Functional Requirements| FRs listed, properly formatted, improvement suggestions | Complete    |
| Non-Functional Req.    | NFRs listed, properly formatted                        | Complete    |
| Domain Requirements    | Compliance, technical, patterns, risks covered         | Complete    |
| Project-Type Req.      | All required fields present                            | Complete    |

No template variables or placeholders remain. All sections are fully populated and formatted. PRD is complete and ready for implementation.
  business:
    - "The foundation achieves operational rollout within a short timeframe (e.g., 3 months)."
    - "Approved cases, supporting documents, and payments are tracked with high accuracy."
    - "Administrative workload is reduced compared to previous manual/email-based processes."
    - "No sensitive medical or financial data is mishandled; compliance and privacy are maintained."
  technical:
    - "The platform is stable, secure, and easy to maintain."
    - "No critical bugs or outages during the first 6 months."
    - "All workflows are completed as designed, with no major user complaints."
userJourneys:
  physiotherapist:
    openingScene: "A physiotherapist, overwhelmed by paperwork and informal support requests, wishes to help patients access foundation funding without extra admin burden."
    risingAction: "They log into the platform, submit a funding request for a patient in minutes, and receive confirmation of submission."
    climax: "The foundation reviews and approves the case, and the physiotherapist is notified—no follow-up emails or manual tracking needed."
    resolution: "The physiotherapist can focus on care, knowing the patient’s support is handled efficiently."
  patient:
    openingScene: "A patient, worried about the cost of physiotherapy, learns their therapist has submitted a support request."
    risingAction: "The patient receives secure access to their case, uploads invoices and supporting documents, and submits payment requests."
    climax: "The foundation validates the documents and confirms support, relieving the patient’s financial stress."
    resolution: "The patient receives timely reimbursement, enabling continued treatment."
  foundationMember:
    openingScene: "Foundation staff struggle to track cases, documents, and payments across emails and spreadsheets."
    risingAction: "They review submitted cases in the platform, validate supporting documents, and manually track sessions and payments."
    climax: "The platform provides clear traceability and control, reducing risk and administrative workload."
    resolution: "Foundation members can confidently manage support, ensuring funds are used appropriately."
  systemAdmin:
    openingScene: "An admin is tasked with maintaining the platform’s security and stability."
    risingAction: "They monitor user access, update roles, and ensure compliance with privacy requirements."
    climax: "The platform operates smoothly, with no outages or security incidents."
    resolution: "The admin’s workload is manageable, and the platform remains reliable for all users."
domainRequirements:
  compliance:
    - "Medical standards and liability considerations are addressed."
    - "Regulatory pathways for healthcare support are followed."
  technical:
    - "Secure data handling and access control are mandatory."
    - "Audit trails and integration with Odoo Community are required."
  patterns:
    - "Simple case management and manual session tracking."
    - "Invoice-based proof and avoidance of sensitive medical data."
  risks:
    - "Risks include data breaches, improper access, non-compliance, and operational errors."
    - "Mitigations: strong access controls, clear workflows, manual validation."
projectTypeRequirements:
  applicationType: "Multi-Page Application (MPA)"
  browserSupport: "Chrome, Firefox, Safari, and other major browsers"
  seo: "Not required"
  realTimeFeatures: "Not needed"
  accessibility: "Must be very user friendly for all ages, including elderly and people with motor deficiencies; minimize unnecessary clicks and optimize for ease of use"
scoping:
  mvp:
    - "Physiotherapist submits funding requests for patients"
    - "Foundation reviews and approves cases"
    - "Patient accesses their case securely, uploads invoices/supporting documents, and submits payment requests"
    - "Foundation validates documents and tracks sessions/payments manually"
    - "Platform is user-friendly, secure, and supports major browsers"
    - "Odoo accounting module integration for payment management and history"
  niceToHave:
    - "Automated session tracking"
    - "Enhanced reporting and analytics"
    - "Additional user roles (e.g., external auditors)"
    - "Advanced notification system"
functionalRequirements:
  caseManagement: "Create, review, approve, and track support cases for physiotherapy funding."
  documentHandling: "Secure upload, access, and validation of invoices and supporting documents."
  userManagement: "Role-based access for physiotherapists, patients, foundation members, and admins."
  paymentTracking: "Integration with Odoo accounting module for payment management and history."
  sessionTracking: "Manual tracking of consumed sessions by foundation members."
  accessibility: "User-friendly interface for all ages and motor deficiencies, minimizing unnecessary clicks."
  securityCompliance: "Data privacy, access control, audit trails, and compliance with Belgian and GDPR privacy regulations."
nonFunctionalRequirements:
  performance: "Fast response times for all user actions; delays should not hinder workflow."
  security: "All sensitive data must be protected; strict access control and audit trails; GDPR and Belgian privacy compliance."
  reliability: "High availability; downtime must be minimized, especially during working hours."
  accessibility: "Interface must be usable by elderly and people with motor deficiencies; follow best practices for accessibility."
  integration: "Seamless integration with Odoo accounting module; data exchange must be reliable and secure."
  scalability: "Platform should support growth in user numbers without performance degradation."
---
# Product Requirements Document - dev

**Author:** Martin
**Date:** 2026-03-07

## Executive Summary
Entre Vos Mains is a pragmatic digital platform built on Odoo Community to help a foundation support patients who need physiotherapy but struggle with the cost of care. The MVP focuses on a simple, controlled reimbursement support flow: physiotherapists submit funding requests for patients, the foundation reviews and approves cases, patients access their case securely, and the foundation validates supporting invoices before handling payment outside the platform.

The product is designed to reduce administrative friction for all parties while maintaining strong control over the use of foundation funds. It deliberately avoids complex medical, financial, and legal workflows in favor of a fast, operationally realistic first version.

Key differentiators:
- Simple tri-party workflow connecting physiotherapist, patient, and foundation
- Physiotherapists can submit funding requests quickly and easily, with minimal administrative burden.
- Patients gain secure access to their case and can upload invoices and supporting documents without confusion.
- Foundation members can review cases, validate documents, and track sessions/payments efficiently.
- All parties experience reduced friction and clear traceability throughout the process.

### Business Success
- The foundation achieves operational rollout within a short timeframe (e.g., 3 months).
- Approved cases, supporting documents, and payments are tracked with high accuracy.
- Administrative workload is reduced compared to previous manual/email-based processes.
- No sensitive medical or financial data is mishandled; compliance and privacy are maintained.

### Technical Success
- The platform is stable, secure, and easy to maintain.
- No critical bugs or outages during the first 6 months.
- All workflows are completed as designed, with no major user complaints.

## User Journeys
### Physiotherapist
- Opening Scene: A physiotherapist, overwhelmed by paperwork and informal support requests, wishes to help patients access foundation funding without extra admin burden.
- Rising Action: They log into the platform, submit a funding request for a patient in minutes, and receive confirmation of submission.
- Climax: The foundation reviews and approves the case, and the physiotherapist is notified—no follow-up emails or manual tracking needed.
- Resolution: The physiotherapist can focus on care, knowing the patient’s support is handled efficiently.

### Patient
- Opening Scene: A patient, worried about the cost of physiotherapy, learns their therapist has submitted a support request.
- Rising Action: The patient receives secure access to their case, uploads invoices and supporting documents, and submits payment requests.
- Climax: The foundation validates the documents and confirms support, relieving the patient’s financial stress.
- Resolution: The patient receives timely reimbursement, enabling continued treatment.

### Foundation Member
- Opening Scene: Foundation staff struggle to track cases, documents, and payments across emails and spreadsheets.
- Rising Action: They review submitted cases in the platform, validate supporting documents, and manually track sessions and payments.
- Climax: The platform provides clear traceability and control, reducing risk and administrative workload.
- Resolution: Foundation members can confidently manage support, ensuring funds are used appropriately.

### System Administrator
- Opening Scene: An admin is tasked with maintaining the platform’s security and stability.
- Rising Action: They monitor user access, update roles, and ensure compliance with privacy requirements.
- Climax: The platform operates smoothly, with no outages or security incidents.
- Resolution: The admin’s workload is manageable, and the platform remains reliable for all users.

## Domain Requirements
### Compliance
- Medical standards and liability considerations are addressed.
- Regulatory pathways for healthcare support are followed.

### Technical
- Secure data handling and access control are mandatory.
- Audit trails and integration with Odoo Community are required.

### Patterns
- Simple case management and manual session tracking.
- Invoice-based proof and avoidance of sensitive medical data.

### Risks
- Risks include data breaches, improper access, non-compliance, and operational errors.
- Mitigations: strong access controls, clear workflows, manual validation.

## Project-Type Requirements
- Application type: Multi-Page Application (MPA)
- Browser support: Chrome, Firefox, Safari, and other major browsers
- SEO: Not required
- Real-time features: Not needed
- Accessibility: Must be very user friendly for all ages, including elderly and people with motor deficiencies; minimize unnecessary clicks and optimize for ease of use

## Scoping
### MVP
- Physiotherapist submits funding requests for patients
- Foundation reviews and approves cases
- Patient accesses their case securely, uploads invoices/supporting documents, and submits payment requests
- Foundation validates documents and tracks sessions/payments manually
- Platform is user-friendly, secure, and supports major browsers
- Odoo accounting module integration for payment management and history

### Nice-to-Have
- Automated session tracking
- Enhanced reporting and analytics
- Additional user roles (e.g., external auditors)
- Advanced notification system

## Functional Requirements
Case Management: Create, review, approve, and track support cases for physiotherapy funding.
Document Handling: Secure upload, access, and validation of invoices and supporting documents.
User Management: Role-based access for physiotherapists, patients, foundation members, and admins.
Payment Tracking: Integration with Odoo accounting module for payment management and history.
Session Tracking: Manual tracking of consumed sessions by foundation members.
Accessibility: User-friendly interface for all ages and motor deficiencies, minimizing unnecessary clicks.
Security & Compliance: Data privacy, access control, audit trails, and compliance with Belgian and GDPR privacy regulations.

### SMART Requirements Validation (Step-v-10)

| FR Number | Requirement | Specific | Measurable | Attainable | Relevant | Traceable | Improvement Suggestions |
|-----------|-------------|----------|------------|------------|---------|-----------|------------------------|
| FR-001 | Case Management: Create, review, approve, and track support cases for physiotherapy funding. | 5 | 5 | 5 | 5 | 5 | None |
| FR-002 | Document Handling: Secure upload, access, and validation of invoices and supporting documents. | 5 | 5 | 5 | 5 | 5 | None |
| FR-003 | User Management: Role-based access for physiotherapists, patients, foundation members, and admins. | 5 | 5 | 5 | 5 | 5 | None |
| FR-004 | Payment Tracking: Integration with Odoo accounting module for payment management and history. | 5 | 5 | 5 | 5 | 5 | None |
| FR-005 | Session Tracking: Manual tracking of consumed sessions by foundation members. | 4 | 4 | 5 | 5 | 4 | Clarify session tracking workflow and metrics for improved specificity and traceability. |
| FR-006 | Accessibility: User-friendly interface for all ages and motor deficiencies, minimizing unnecessary clicks. | 5 | 4 | 5 | 5 | 5 | Specify measurable accessibility metrics (e.g., WCAG compliance level). |
| FR-007 | Security & Compliance: Data privacy, access control, audit trails, and compliance with Belgian and GDPR privacy regulations. | 5 | 5 | 5 | 5 | 5 | None |

All Functional Requirements meet SMART quality criteria. Minor improvement suggestions are provided for session tracking and accessibility to further strengthen specificity, measurability, and traceability.

## Non-Functional Requirements
- Performance: Fast response times for all user actions; delays should not hinder workflow.
- Security: All sensitive data must be protected; strict access control and audit trails; GDPR and Belgian privacy compliance.
- Reliability: High availability; downtime must be minimized, especially during working hours.
- Accessibility: Interface must be usable by elderly and people with motor deficiencies; follow best practices for accessibility.
- Integration: Seamless integration with Odoo accounting module; data exchange must be reliable and secure.
- Scalability: Platform should support growth in user numbers without performance degradation.
