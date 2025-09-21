---
title: "Security, Privacy & Compliance Policies (Master Catalog)"
version: "v1.0"
owner: "CISO, CPO/Privacy, General Counsel"
approved_by: "CISO, GC, CTO"
effective_date: "2025-09-19"
review_cycle: "Annual"
applies_to: ["All workforce members", "Contractors", "Vendors with access"]
frameworks: ["ISO 27001/27701", "SOC 2", "NIST CSF/800-53 (select controls)", "GDPR/CCPA", "HIPAA if applicable"]
is_catalog: true
retrieval_weight: 0.6
---

# Security, Privacy & Compliance Policies (Master Catalog)

> Core **security, data, privacy, legal & risk** policies for a mid/large tech company. Each policy includes Purpose, Scope, Definitions, Policy, Standards, Procedures/Playbooks, Roles (RACI), Exceptions, Monitoring/Metrics, Enforcement, Records/Retention, Related Docs, Revision History.

---

## 1) Information Security Policy (Top-Level)
- **Key rules**
  - Risk-based ISMS; management commitment; security by design.
  - Control families: governance, asset mgmt, HR security, physical, ops, comms, access, dev, supplier, incident, BCM.
- **Metrics**: risk register coverage, treatment plan SLAs, audit findings.

## 2) Acceptable Use & Workforce Security
- **Key rules**
  - Authorized use only; no circumvention of controls; no illegal content.
  - Prohibits sharing credentials; MFA required.
  - Monitoring notice and privacy expectations on company systems.

## 3) Asset Management & Inventory
- **Key rules**
  - Hardware/software/cloud inventories; ownership and classification.
  - Joiners/Movers/Leavers asset changes synchronized with HRIS.

## 4) Data Classification & Handling
- **Classes**: Public, Internal, Confidential, Restricted (PII/PHI/PCI/Trade Secret).
- **Handling**: encryption requirements at rest/in transit; sharing/labeling; approved storage locations.

## 5) Access Control & Identity (IAM)
- **Key rules**
  - Least privilege; role-based access; SSO + MFA mandatory.
  - Joiner/Leaver automation; quarterly access reviews for high-risk systems.
  - Break-glass accounts with enhanced logging and approval.

## 6) Password & Authenticator Standards
- **Key rules**
  - Strong secrets or passkeys; rotation for shared secrets only; no hardcoding.
  - Hardware keys for admins; conditional access for high-risk sign-ins.

## 7) Endpoint Security (Devices)
- **Key rules**
  - Full-disk encryption, EDR, auto-patching; screen lock, USB controls as needed.
  - BYOD permitted only with MDM enrollment and containerization.

## 8) Network & Cloud Security
- **Key rules**
  - Zero-trust principles; segmentation; WAF, IDS/IPS where applicable.
  - Cloud baseline: CIS Benchmarks; customer data only in approved regions.
  - Secrets in managed vaults; no shared root accounts.

## 9) Vulnerability & Patch Management
- **Key rules**
  - Scanning cadence by asset class; critical vulns patched ≤ 7 days.
  - SBOM tracking; third-party libraries monitored for CVEs.

## 10) Secure SDLC & Change Management
- **Key rules**
  - Threat modeling, code review, SAST/DAST/IAST, dependency scanning.
  - Change approvals by risk; emergency changes post-review.
  - Infrastructure as Code with peer review and pipeline gating.

## 11) Cryptography & Key Management
- **Key rules**
  - Approved algorithms/strengths; KMS/HSM for key storage.
  - Key rotation, separation of duties, escrow and recovery.

## 12) Logging, Monitoring & Detection
- **Key rules**
  - Centralized logs, time sync, tamper protection.
  - Detections tuned to MITRE ATT&CK; alert SLAs; runbooks.

## 13) Incident Response (IR)
- **Key rules**
  - 24/7 on-call; severity levels; comms plan (internal/external).
  - Forensics and containment steps; post-incident reviews with action items.
  - Breach notifications per law/contract (see Privacy Incidents).

## 14) Business Continuity (BCP) & Disaster Recovery (DR)
- **Key rules**
  - RTO/RPO defined per system; annual tests; crisis management team (CMT).
  - Redundancy for critical services; vendor contingency plans.

## 15) Physical & Facilities Security
- **Key rules**
  - Badge access; visitor logs; CCTV where lawful; clean desk in shared offices.
  - Data center controls; media disposal standards.

## 16) Data Privacy & Protection
- **Key rules**
  - Lawful basis for processing; DPIAs/PIAs for high-risk processing.
  - Data subject rights (access, deletion, portability) with defined SLAs.
  - Records of processing activities (RoPA); privacy by design checklists.
- **Cross-links**: cookie policy, product telemetry governance.

## 17) Privacy Incident & Breach Response
- **Key rules**
  - Triage with IR; regulator and customer notification timelines (e.g., GDPR 72h).
  - Evidence handling; single source of truth; remediation tracking.

## 18) Data Lifecycle & Retention
- **Key rules**
  - Create → Store → Use → Share → Archive → Destroy with controls per class.
  - Legal hold process with Legal; defensible deletion.

## 19) Third-Party Risk & Vendor Management
- **Key rules**
  - Risk-tiering; security/privacy questionnaires; right-to-audit clauses.
  - DPA/SCCs for cross-border transfers; subcontractor flow-downs.
  - Continuous monitoring for critical vendors.

## 20) Open Source Software (OSS) Use & Contribution
- **Key rules**
  - License compliance checks; approved license list.
  - Contributions require legal review; outbound code scanning.

## 21) AI/ML & Model Governance
- **Key rules**
  - Approved models/providers; red-teaming and safety review for launches.
  - Data sourcing and labeling standards; PII handling; privacy by design.
  - Evaluation benchmarks; human-in-the-loop for sensitive use cases.
  - Model cards, risk assessments, drift monitoring, rollback procedures.

## 22) Data Governance & Analytics
- **Key rules**
  - Data owners/stewards; cataloging/lineage; quality SLAs.
  - Access via approved platforms; anonymization/pseudonymization where appropriate.

## 23) Records Management & eDiscovery
- **Key rules**
  - Record classes and retention schedules; legal holds; defensible deletion.
  - Preservation/litigation support workflows; secure export to counsel.

## 24) Export Controls & Sanctions
- **Key rules**
  - Restricted party screening; encryption export classifications; destination controls.
  - Engineering controls for geofencing prohibited regions.

## 25) Anti-Corruption / Anti-Bribery (ABC)
- **Key rules**
  - Gifts/hospitality thresholds; books and records accuracy.
  - Third-party intermediaries due diligence and contract clauses.

## 26) Contracts & Commercial Approval
- **Key rules**
  - Standard templates; non-standard terms require Legal approval.
  - Clause libraries; playbooks for negotiators; e-signature systems.

## 27) Procurement & Spend Controls
- **Key rules**
  - Competitive bidding thresholds; SoW/PO requirements.
  - Segregation of duties; accruals and invoice verification.

## 28) Financial Controls (SOX readiness if public/IPO-track)
- **Key rules**
  - Key controls over revenue recognition, change mgmt, access, backups, logs.
  - Quarterly testing and remediation; audit committee oversight.

## 29) Risk Management & Internal Audit
- **Key rules**
  - Enterprise risk register; KRIs; quarterly reporting to leadership/Board.
  - Independent audit plan; issue tracking and closure SLAs.

## 30) Communications, Brand & Disclosure
- **Key rules**
  - Disclosure committee (if public); Reg FD compliance.
  - Brand use guidelines; incident/crisis comms alignment with IR.

## 31) Research, Customer Data & Ethics
- **Key rules**
  - Informed consent for user studies; IRB-like review board where appropriate.
  - Customer data minimization; sandboxing; contract-compliant use.

## 32) Security Training & Awareness
- **Key rules**
  - New-hire and annual refreshers; phishing simulations; targeted training for high-risk roles.
  - Training records retained per retention schedule.

## 33) Exceptions & Risk Acceptance
- **Key rules**
  - Formal risk acceptance with compensating controls, expiry date, and owner.
  - Logged in GRC tool; reviewed at least annually.

---

## Cross-References
- People/HR policies (`mentorvista_people_policies.md` and existing files).
- Product policies (AI/ML, Data Governance) must align with Security & Privacy.

## Metrics & Reporting
- Control maturity, audit findings, incident MTTR, vuln SLAs, DSR SLAs, vendor risk scores.

## Related Documents
- Security Standards (Platform/Network/Endpoint)
- IR Playbooks, BCP/DR Plans, Privacy Notices, Data Maps, DPIA templates
- Contracts Playbooks, DPA/SCCs, Procurement SOPs

