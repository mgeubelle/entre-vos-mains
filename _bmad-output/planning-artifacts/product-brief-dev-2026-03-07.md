---
stepsCompleted: [1]
inputDocuments:
  - analyse-projet.md
date: 2026-03-07
author: Martin
---

# Product Brief: dev

## Executive Summary

Entre Vos Mains is a pragmatic digital platform built on Odoo Community to help a foundation support patients who need physiotherapy but struggle with the cost of care. The MVP focuses on a simple, controlled reimbursement support flow: physiotherapists submit funding requests for patients, the foundation reviews and approves cases, patients access their case securely, and the foundation validates supporting invoices before handling payment outside the platform.

The product is designed to reduce administrative friction for all parties while maintaining strong control over the use of foundation funds. It deliberately avoids complex medical, financial, and legal workflows in favor of a fast, operationally realistic first version.

---

## Core Vision

### Problem Statement

Patients who need physiotherapy may face financial barriers that limit access to treatment, while foundations that want to help often lack a lightweight, structured way to review requests, collect proof, and track granted support. At the same time, physiotherapists already face significant workload constraints and need a simple way to introduce eligible patients without being drawn into a heavy administrative process.

### Problem Impact

Without a simple shared platform, financial support management becomes fragmented, manual, and harder to monitor. Patients may delay or forgo care, physiotherapists lose time coordinating support informally, and the foundation has less visibility into approved cases, supporting documents, consumed sessions, and money spent. This creates both operational inefficiency and risk in the management of limited subsidy budgets.

### Why Existing Solutions Fall Short

Generic tools do not match this workflow well. Email, shared files, and ad hoc follow-up create scattered information and weak traceability. Traditional healthcare or payment platforms are often too heavy, too medically detailed, or too focused on automated billing and payment flows. The foundation needs a solution that is simpler: limited sensitive data, no online payment, no complex approval chains, and clear case-by-case tracking.

### Proposed Solution

Entre Vos Mains provides a secure, role-based case management flow for three actors: physiotherapists, patients, and foundation members. A physiotherapist submits a support request for a patient. The foundation approves or rejects the case. Once approved, the patient gains access to a secure portal where they can consult the case, upload invoices and supporting documents, and submit payment requests. The foundation reviews documents, requests additional information when needed, manually tracks consumed sessions, and records payment follow-up performed outside the platform.

For V1, payment proof is invoice-based rather than session-line-based, and session decrement remains a manual foundation action. This keeps the MVP operationally simple and aligned with the project’s pragmatic scope.

### Key Differentiators

Entre Vos Mains is differentiated by its narrow and practical focus. It is not a full medical platform, not a reimbursement automation engine, and not a generic document portal. It is a foundation support workflow tailored to a specific real-world process.

Its main differentiators are:
- A simple tri-party workflow connecting physiotherapist, patient, and foundation in one shared case
- Strong administrative simplicity with limited sensitive data and no financial automation
- A pragmatic MVP scope designed for fast operational rollout on Odoo Community
- Clear traceability of approved support, submitted proof, manually tracked sessions, and payments made outside the platform
- A workflow that matches the foundation’s real operating model instead of forcing enterprise-grade process complexity
