---
workflowType: 'prd'
workflow: 'edit'
classification:
  domain: 'healthcare'
  projectType: 'web_app'
  complexity: 'high'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-03-08.md
stepsCompleted:
  - 'step-01-init'
  - 'step-02-discovery'
  - 'step-02b-vision'
  - 'step-02c-executive-summary'
  - 'step-03-success'
  - 'step-04-journeys'
  - 'step-05-domain'
  - 'step-07-project-type'
  - 'step-08-scoping'
  - 'step-09-functional'
  - 'step-10-nonfunctional'
  - 'step-e-01-discovery'
  - 'step-e-02-review'
  - 'step-e-03-edit'
  - 'step-e-04-complete'
lastEdited: '2026-03-08'
editHistory:
  - date: '2026-03-08'
    changes: 'Added measurable accessibility target, clarified session tracking rules, aligned FR1-FR10 with epics, added minimal UX guardrails, and improved PRD to epics traceability.'
  - date: '2026-03-08'
    changes: 'Quantified key NFRs, added responsive behavior expectations, clarified non-clinical healthcare boundary, added explicit out-of-scope items, and replaced chatter with a platform-neutral activity history term.'
---
# Product Requirements Document - dev

**Author:** Martin
**Date:** 2026-03-07
**Last Edited:** 2026-03-08

## Executive Summary
Entre Vos Mains is a pragmatic digital platform built on Odoo Community to help a foundation support patients who need physiotherapy but struggle with the cost of care. The MVP focuses on a simple, controlled reimbursement support flow: physiotherapists submit funding requests for patients, the foundation reviews and approves cases, patients access their case securely, and the foundation validates supporting invoices before handling payment outside the platform.

The product is designed to reduce administrative friction for all parties while maintaining strong control over the use of foundation funds. It deliberately avoids complex medical, financial, and legal workflows in favor of a fast, operationally realistic first version. The MVP includes low-friction portal and back-office workflows, explicit session counters, and minimal asynchronous communication on key case and payment-request events.

Key differentiators:
- Simple tri-party workflow connecting physiotherapist, patient, and foundation
- Physiotherapists can submit funding requests quickly and easily, with minimal administrative burden
- Patients gain secure access to their case, can understand their remaining support, and can upload invoices and supporting documents without confusion
- Foundation members can review cases and payment requests, request complementary information, and track sessions and payments with clear traceability
- All parties experience reduced friction, explicit status feedback, and traceable operational follow-up throughout the process

### Business Success
- The foundation achieves operational rollout within a short timeframe (e.g., 3 months)
- Approved cases, supporting documents, sessions, and payments are tracked with high accuracy
- Administrative workload is reduced compared to previous manual or email-based processes
- No sensitive medical or financial data is mishandled; compliance and privacy are maintained

### Technical Success
- The platform is stable, secure, and easy to maintain
- No critical bugs or outages during the first 6 months
- All workflows are completed as designed, with no major user complaints
- MVP key journeys are accepted with no blocking accessibility defect against WCAG 2.2 AA on supported browsers

## User Journeys
### Physiotherapist
- Opening Scene: A physiotherapist, overwhelmed by paperwork and informal support requests, wishes to help patients access foundation funding without extra admin burden.
- Rising Action: They log into the platform, submit a funding request for a patient in minutes, and receive confirmation of submission.
- Climax: The foundation reviews and approves the case, and the physiotherapist is notified without extra manual follow-up.
- Resolution: The physiotherapist can focus on care, while still consulting the case status and the authorized support level.

### Patient
- Opening Scene: A patient, worried about the cost of physiotherapy, learns their therapist has submitted a support request.
- Rising Action: The patient receives secure access to their case, consults the case status and session balance, uploads invoices and supporting documents, and submits payment requests.
- Climax: The foundation validates the documents or asks for complementary information, and the patient receives clear feedback on the next action.
- Resolution: The patient receives timely reimbursement, enabling continued treatment.

### Foundation Member
- Opening Scene: Foundation staff struggle to track cases, documents, sessions, and payments across emails and spreadsheets.
- Rising Action: They review submitted cases and payment requests in the platform, validate supporting documents, request complementary information when needed, and manually track sessions and payments.
- Climax: The platform provides clear traceability, comments, notifications, and explicit session counters, reducing risk and administrative workload.
- Resolution: Foundation members can confidently manage support, ensuring funds are used appropriately.

### System Administrator
- Opening Scene: An admin is tasked with maintaining the platform's security and stability.
- Rising Action: They monitor user access, update roles, and ensure compliance with privacy requirements.
- Climax: The platform operates smoothly, with no outages or security incidents.
- Resolution: The admin's workload is manageable, and the platform remains reliable for all users.

## Domain Requirements
### Compliance
- Medical standards and liability considerations are addressed
- Regulatory pathways for healthcare support are followed

### Compliance Boundary
- The product is a non-clinical administrative support platform and does not provide diagnosis, treatment recommendation, or clinical decision support
- No automated medical decision is produced by the platform; reimbursement and case decisions remain human-reviewed

### Technical
- Secure data handling and access control are mandatory
- Audit trails and integration with Odoo Community are required

### Patterns
- Simple case management and manual session tracking
- Invoice-based proof and avoidance of sensitive medical data
- Session tracking remains aggregate-based in V1; no session-by-session medical logging is required

### Risks
- Risks include data breaches, improper access, non-compliance, operational errors, and user confusion on document or payment-request status
- Mitigations: strong access controls, clear workflows, explicit feedback states, manual validation, and traceable comments and notifications
- Safety assumption: platform safety relies on sensitive-data minimization, strict access control, explicit workflow states, and human validation rather than automated clinical reasoning

## Project-Type Requirements
- Application type: Multi-Page Application (MPA)
- Browser support: Chrome, Firefox, Safari, and other major browsers
- SEO: Not required
- Real-time features: Not needed
- Accessibility target: MVP user-facing journeys must meet WCAG 2.2 AA on supported browsers for the following flows: physiotherapist case creation, patient case consultation and payment-request submission, foundation case review, and foundation payment-request review
- Responsive behavior: MVP journeys must remain usable on desktop and recent mobile browsers, with no horizontal scrolling required for core portal and back-office actions

### Minimal UX Guardrails For MVP
These guardrails are the minimum UX specification embedded directly in the PRD until a dedicated UX artifact becomes necessary.

- Simplicity of journeys: Each role must have one clear entry point to its relevant work. Core actions must be available directly from the case view or payment-request view without requiring navigation through unrelated menus.
- Feedback and errors: After each submit, validation, refusal, request-for-information, upload, or payment-confirmation action, the system must display immediate feedback in French. Blocking validation errors must be shown near the relevant field and as a page-level summary, while preserving already entered data.
- Navigation and readability: Status, next available action, and key counters must be visible in list and detail views. On case and payment-request screens, authorized, consumed, and remaining sessions must be readable without opening secondary screens.
- Accessibility constraints for design and QA: Primary actions must be keyboard-operable, focus must remain visible, status information must not rely on color alone, and essential content must remain usable at 200% zoom.

## Scoping
### MVP
- Physiotherapist submits funding requests for patients
- Foundation reviews and approves cases
- Patient accesses their case securely, consults session balance, uploads invoices or supporting documents, and submits payment requests
- Foundation validates documents, requests complementary information when needed, and tracks sessions and payments manually
- Minimal asynchronous communication is available through notes, comments, activity history, and notifications on key workflow events
- Platform is user-friendly, secure, accessible on major browsers, and user-facing content is in French
- Odoo accounting module integration supports payment management and history

### Nice-to-Have
- Automated session tracking
- Enhanced reporting and analytics
- Additional user roles (e.g., external auditors)
- Advanced notification rules, channels, or templates beyond the MVP event set

### Out of Scope
- Session-by-session entry or clinical treatment logging
- Online payments or banking automation
- Structured storage of clinical or diagnostic data
- OCR, automatic invoice analysis, or advanced reporting

## Functional Requirements
| ID | Requirement | Traceability |
|----|-------------|--------------|
| FR1 | Case Management: Users can create, review, approve, consult according to role, track, and close physiotherapy support cases. | Journeys: Physiotherapist, Foundation Member. Epics: 1, 3, 4 |
| FR2 | Document Handling: Users can securely upload, access, and validate invoices and supporting documents linked to payment requests, with case-level visibility of the related document set. | Journeys: Patient, Foundation Member. Epics: 2 |
| FR3 | User Management: The platform provides role-based access for physiotherapists, patients, foundation members, and administrators. | Journeys: Physiotherapist, Patient, Foundation Member, System Administrator. Epics: 1 |
| FR4 | Payment Tracking: The platform records payment requests, links them to Odoo accounting payment records, and preserves payment history. | Journeys: Patient, Foundation Member. Epics: 3 |
| FR5 | Session Tracking: The platform tracks requested, authorized, consumed, and remaining sessions per case, plus the declared session count per payment request. The foundation sets the authorized count when accepting a case, can adjust the session count on a payment request before validation, and the platform updates consumed and remaining counts only from validated payment requests without allowing a negative remaining balance. | Journeys: Patient, Foundation Member, Physiotherapist. Epics: 3 |
| FR6 | Accessibility And Low-Friction Use: Core MVP journeys minimize unnecessary navigation, present one obvious next action per screen, provide French labels and messages, and meet the accessibility target defined in Project-Type Requirements. | Journeys: Physiotherapist, Patient, Foundation Member. Epics: 1, 2 |
| FR7 | Security And Compliance: The platform protects personal data with strict access control, audit trails, and compliance with Belgian privacy requirements and GDPR. | Journeys: All. Epics: 1, 4 |
| FR8 | Patient Portal: After case acceptance, patients can securely access their case, consult its status and session balance, upload documents, and create payment requests. | Journeys: Patient. Epics: 2 |
| FR9 | Foundation Processing: Foundation members can process cases and payment requests, validate or refuse them, request complementary information, add operational comments, and follow operational status. | Journeys: Foundation Member. Epics: 3 |
| FR10 | Asynchronous Communication: The platform supports notes, comments, activity history, and notifications for key events at minimum: case accepted, case refused, payment request submitted, request for information, payment request validated, and payment request paid. | Journeys: Physiotherapist, Patient, Foundation Member. Epics: 4 |

### PRD To Epics Traceability Matrix
| PRD FR | Covered In Epics | Primary Journeys |
|--------|------------------|------------------|
| FR1 | Epic 1, Epic 3, Epic 4 | Physiotherapist, Foundation Member |
| FR2 | Epic 2 | Patient, Foundation Member |
| FR3 | Epic 1 | Physiotherapist, Patient, Foundation Member, System Administrator |
| FR4 | Epic 3 | Patient, Foundation Member |
| FR5 | Epic 3 | Patient, Foundation Member, Physiotherapist |
| FR6 | Epic 1, Epic 2 | Physiotherapist, Patient, Foundation Member |
| FR7 | Epic 1, Epic 4 | All |
| FR8 | Epic 2 | Patient |
| FR9 | Epic 3 | Foundation Member |
| FR10 | Epic 4 | Physiotherapist, Patient, Foundation Member |

### SMART Requirements Validation
| FR Number | Requirement | Specific | Measurable | Attainable | Relevant | Traceable | Improvement Suggestions |
|-----------|-------------|----------|------------|------------|----------|-----------|-------------------------|
| FR-001 | Case Management | 5 | 4 | 5 | 5 | 5 | None |
| FR-002 | Document Handling | 5 | 4 | 5 | 5 | 5 | None |
| FR-003 | User Management | 5 | 4 | 5 | 5 | 5 | None |
| FR-004 | Payment Tracking | 5 | 4 | 5 | 5 | 5 | None |
| FR-005 | Session Tracking | 5 | 5 | 5 | 5 | 5 | None |
| FR-006 | Accessibility And Low-Friction Use | 5 | 5 | 5 | 5 | 5 | None |
| FR-007 | Security And Compliance | 5 | 4 | 5 | 5 | 5 | None |
| FR-008 | Patient Portal | 5 | 4 | 5 | 5 | 5 | None |
| FR-009 | Foundation Processing | 5 | 4 | 5 | 5 | 5 | None |
| FR-010 | Asynchronous Communication | 5 | 5 | 5 | 5 | 5 | None |

The functional requirements are explicit, measurable enough for implementation planning, and directly traceable to both user journeys and epic coverage.

## Non-Functional Requirements
- Performance: Common list, detail, and workflow action screens must load or confirm in under 2 seconds for 95% of actions under normal business-hour usage, excluding file upload transfer time.
- Security: All sensitive data and documents must be protected through strict access control, audit trails, and secure data exchanges in line with GDPR and Belgian privacy requirements.
- Reliability: The platform must target at least 99.5% availability during the foundation's business hours, excluding planned maintenance windows.
- Accessibility: MVP user-facing journeys must meet WCAG 2.2 AA on supported browsers, primary actions must be keyboard-operable, focus must remain visible, status must not rely on color alone, and essential content must remain usable at 200% zoom.
- Integration: For each validated payment request, the Odoo accounting integration must either create and link exactly one payment record or fail with an explicit error without creating duplicates.
- Scalability: The platform must support at least 50 concurrent users and 10,000 historical cases or payment requests without perceptible degradation on MVP workflows.
