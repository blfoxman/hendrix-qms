@@SEC 1|About this pack@@

This pack is everything an auditor needs to accept Hendrix QMS as the electronic quality system of a licensed cannabis operation. It is written for three readers:

- **The CSQ certification body (ASI) auditor.** CSQ clause 1.1 asks for a documented safety and quality system, paper or electronic. Section 13 maps every CSQ clause to the Hendrix page that holds its evidence.
- **The state inspector (Missouri DCR, Michigan CRA).** They need to know the records are complete, attributable and cannot be changed without a trace.
- **Your own quality team.** They run and sign the validation protocols (IQ, OQ, PQ) and keep the system in a validated state.

> **What "certified" means here.** Neither CSQ nor the states certify software products. They certify or license the *operation*. An auditor accepts an electronic system when it can show three things: it is fit for its intended use (validation), its records are trustworthy (data integrity), and it is kept under control (change control, access, backups). This pack provides the evidence and the protocols. The certification decision belongs to the auditor, after the protocols in sections 9 to 11 are executed and signed on the live system.

### How to use this pack

| Step | What to do | Section | Status |
|---|---|---|---|
| 1 | Read the system description and intended use | 2, 3 | Prepared |
| 2 | Review the requirements, risk assessment and controls | 4, 5, 8 | Prepared, needs QA approval |
| 3 | Install Hendrix and run the Installation Qualification (IQ) | 9 | To execute |
| 4 | Run the Operational Qualification (OQ) on the live system | 10 | To execute |
| 5 | Run the Performance Qualification (PQ) in real use for 30 days | 11 | To execute |
| 6 | Sign the Validation Summary Report | 15 | To sign |
| 7 | Hand the auditor this pack, the signed report and inspector access | 13, 14 | At audit |

### Approach

Hendrix is validated with the risk-based approach of **ISPE GAMP® 5 (Second Edition)**, the method used across regulated food and pharma. Data integrity is judged against **ALCOA+**. The electronic records and signature controls are compared with **US FDA 21 CFR Part 11** as a benchmark. Part 11 is not a legal requirement for state-licensed cannabis, but it is the best-known yardstick for trustworthy electronic records, and auditors recognise it.

@@SEC 2|System description@@

| Item | Detail |
|---|---|
| System name | Hendrix QMS (Hendrix Quality Management) |
| Release covered | Release 41, October 2026 (source repository `blfoxman/hendrix-qms`, branch `main`, commit `9cdb4e9`) |
| System owner | Director of Production (Sam Salari) |
| Business process owner | Quality Assurance lead of each license |
| Operations covered | Licensed cannabis manufacturing, extraction and cultivation in Missouri and Michigan; each license kept separately |
| Users | Production technicians, QA, compliance, managers, owners; visitors and staff through kiosks (sign-in, logs, time clock) |
| Standards supported | CSQ Manufacturing, Extraction and Cultivation v2.0, Levels 1 to 3 (130 clauses) |

### Architecture

<div class="arch">
<div class="lane"><div class="box dark"><b>People</b><span>Browser on PC, tablet or phone; kiosk tablets at the door</span></div></div>
<div class="arrow">HTTPS (TLS)</div>
<div class="lane"><div class="box"><b>Hendrix app</b><span>One web page (index.html), served by GitHub Pages; no data stored on the device except the sign-in session and, on kiosks, entries waiting for the internet</span></div></div>
<div class="arrow">HTTPS + signed access token</div>
<div class="lane three"><div class="box"><b>Sign-in</b><span>Supabase Auth: email + password, optional authenticator code (TOTP), signed tokens</span></div><div class="box"><b>Database</b><span>Supabase PostgreSQL: every record, rule, signature and the audit trail</span></div><div class="box"><b>Files</b><span>Supabase Storage: COAs, SDS, certificates, photos</span></div></div>
<div class="arrow">server-side only</div>
<div class="lane three"><div class="box"><b>AI helper (hendrix-ai)</b><span>Supabase Edge Function; calls Anthropic Claude to read COAs, draft SOPs and courses, plan amounts and match import columns. The API key never reaches the browser.</span></div><div class="box"><b>Email (hendrix-notify)</b><span>Edge Function; daily task lists and urgent alerts through Resend; every email logged</span></div><div class="box"><b>METRC (hendrix-metrc)</b><span>Edge Function; reads the license's packages from METRC (read only) for METRC Check</span></div></div>
</div>

### Components

| Component | What it does | GAMP category | Supplier |
|---|---|---|---|
| Web browser | Runs the app | 1 (infrastructure) | Google, Apple, Microsoft |
| GitHub Pages | Hosts the app file | 1 (infrastructure) | GitHub |
| Supabase (PostgreSQL, Auth, Storage, Edge Functions) | Stores and protects the data; enforces the rules | 1 (infrastructure) | Supabase Inc. |
| Hendrix application and database rules | All screens, forms, calculations, approvals, locks and the audit trail | **5 (custom application)** | Built in-house |
| hendrix-ai function + Anthropic Claude | Suggestions that a person always reviews before saving | 5 (custom) on a 1 service | In-house / Anthropic |
| hendrix-notify function + Resend | Sends the daily task lists and urgent alerts | 5 (custom) on a 1 service | In-house / Resend |
| hendrix-metrc function + METRC API | Reads METRC packages for reconciliation (never writes) | 5 (custom) on a 1 service | In-house / Metrc LLC |
| Kiosk service worker (sw.js) | Keeps the kiosk page on the tablet so kiosks reopen without internet | 5 (custom) | Built in-house |

### Where the rules live

Hendrix enforces its rules **in the database**, not only on screen. The database accepts a record only when it passes these rules, whatever device or tool sends it:

- required fields;
- approvals and who may give them;
- reasons for change;
- locks after signing;
- numbering;
- "cannot be released or used" checks;
- license separation.

The rules are installed by numbered SQL step files (steps 4 to 41; step 35 needs none). Steps 13 to 41 are also in one file, `hendrix_install_13_to_41.sql`.

### Not in scope

- **Writing to METRC (state track and trace).** Hendrix stores METRC tags and compares its records with METRC (METRC Check, read only), but it never changes METRC. METRC stays the state's system of record for plant and package inventory.
- **Payroll.** The time clock records attendance only. It does not calculate pay.
- **Accounting.** Ingredient prices are used only for batch costing.

@@SEC 3|Intended use and GAMP classification@@

Hendrix is used to **create, approve, sign, keep and retrieve the quality records** that a licensed cannabis operation must keep under CSQ and state rules. Those records include SOPs, training, logs, batch records, testing, deviations and CAPA, complaints, audits, suppliers, receiving, holds, shipping, traceability and recalls, equipment, chemicals, facility tests, HACCP, risk, change control, objectives, management review and verification.

Records in Hendrix decide whether product is released and whether people are trained. That makes Hendrix a **GxP-relevant system with direct impact on product quality and consumer safety**. The application layer is **GAMP Category 5**, so it gets the full lifecycle:

| GAMP deliverable | Where it is in this pack |
|---|---|
| User requirements (URS) | Section 4 |
| Functional risk assessment | Section 5 |
| Functional and design description | Section 2 and the User Manual |
| Configuration and controls list | Section 8 |
| Supplier / developer testing | Section 7 (automated test suites) |
| Installation Qualification | Section 9 |
| Operational Qualification | Section 10 |
| Performance Qualification | Section 11 |
| Operating procedures | Section 12 |
| Validation summary report | Section 15 |

@@SEC 4|User requirements (URS)@@

Each requirement has an ID, a GxP impact rating and the place where it is verified. **High** means a failure could let unsafe product out or lose a required record. **Medium** means it could cause a compliance finding. **Low** means it is a convenience.

{{URS}}

@@SEC 5|Risk assessment@@

The risk assessment follows GAMP 5. Each function is rated for **severity** (harm to consumers or compliance), **probability** of failure and **detectability**. Controls and test depth follow the risk: high-risk functions are enforced in the database, automated tests cover them, and they are challenged again in the OQ.

| Function | What could go wrong | Severity / Probability / Detection → Risk | Controls in Hendrix | Verified by |
|---|---|---|---|---|
| Release of product (holds, testing) | Failed or untested product released | High / Low / High → **Medium** | Only Full access can decide a hold (release, destroy, return, rework) and must write why; held batches and batches with a failed test and no passing retest cannot be shipped; changing a final test result needs Full access and a reason (database rules) | OQ-05, OQ-06; suites t, mat |
| Use of raw materials | Quarantined or rejected lot used in a batch | High / Low / High → **Medium** | Lots come only from suppliers approved for the license and wait in quarantine until Full access accepts them; expired or held lots cannot be used (database rules) | OQ-05; suite mat |
| Batch records | Missing step, tag or sign-off | High / Medium / Medium → **High** | Batch number unique per license; only switched-on SKUs of the right type; a filled-in value can only be changed by an admin with a reason; voids need a reason; batches without a line clearance are flagged | OQ-07, OQ-08; suites b, lc |
| Deviations and CAPA | Deviation closed without root cause or effectiveness check | High / Low / High → **Medium** | Closing needs an immediate correction, and a root cause when Full access decides one is needed; a CAPA closes only when the fix is verified and rated Effective (database rules) | OQ-10; suite qms |
| Training | Untrained person does a task | Medium / Medium / High → **Medium** | Matrix shows gaps; online quizzes graded; records signed and dated | OQ-12; suites training, online |
| SOP control | Unapproved or old SOP in use | High / Low / High → **Medium** | Only Full access can publish; a revision needs a new version and a reason, keeps the old version unchanged and asks everyone to sign again (database rules) | OQ-11; suite sop |
| HACCP / CCP monitoring | CCP out of limit with no corrective action | High / Low / High → **Medium** | A reading outside the critical limits needs the corrective action and what happened to the product; records are reviewed by a second person; a plan is active only when complete and validated (database rules) | OQ-15; suite haccp |
| Recall and traceability | Cannot trace a lot in time | High / Low / High → **Medium** | One-step back and forward trace from records; mock recall timed against 2 hours | OQ-09; suite recall |
| Audit trail | Changes not recorded or altered | High / Very low / Medium → **Medium** | Every change written by the database with old and new values; the log cannot be edited or deleted | OQ-03, IQ-08; suite a |
| Access control | Wrong person approves or edits | High / Low / Medium → **Medium** | Approved accounts only; View / Edit / Full per module per person; checked by the database | OQ-02; suite acc |
| License separation | Records mixed between licenses or states | Medium / Low / High → **Low** | Every record carries state and license; the database rejects mismatches | OQ-04 |
| AI suggestions | Wrong value from AI saved as fact | Medium / Medium / High → **Medium** | AI only fills a draft; a person reviews and saves; COA values are shown for checking before saving | OQ-13; suites t, sop, pp, im |
| Calculations (planner, KPIs, costs) | Wrong amounts or wrong KPI | Medium / Low / High → **Low** | Exact formulas from saved formulations; results shown with source; tested | Suites pp, qs |
| Kiosks (visitors, logs, time clock) | Wrong person or fake entry | Medium / Low / Medium → **Low** | Kiosk works only for an active license; badge codes are random and can be reissued; double scans ignored | Suites ops, tc |
| Data loss | Database lost or corrupted | High / Very low / High → **Medium** | Hosted PostgreSQL with provider backups; restore test in the PQ | IQ-10, PQ-06 |

@@SEC 6|Data integrity and electronic records@@

### ALCOA+

| Principle | How Hendrix meets it |
|---|---|
| **Attributable** | Every user signs in with a personal account that an admin has approved. The database stamps every record, approval and change with the user's id and name from the session. Users cannot type them in. |
| **Legible** | Records are typed or picked from lists. Drawn signatures are stored as images. Every record can be printed with the license header. |
| **Contemporaneous** | Every save is stamped with the database server time, not the device time, next to the event date and time the person enters. A late entry is therefore always visible. Kiosks put the log form on the floor, so entries are made as the work happens. |
| **Original** | The first saved record is the original. Later changes keep the old values in the audit trail. Uploaded files (COAs, certificates) are kept as uploaded. |
| **Accurate** | Required fields, allowed values, ranges and cross-checks are enforced by the database. Examples: a CCP limit breach needs an action, and a lot can't be used beyond its quantity. |
| **Complete** | Records are never deleted. A wrong entry is **voided with a reason** and stays visible as void. The audit trail keeps every insert, change and void. |
| **Consistent** | One numbering scheme per record type (for example DEV-2026-001 and RK-001), set by the database. Dates are in ISO format, and times are in the server time zone. |
| **Enduring** | Data is stored in a managed PostgreSQL database with provider backups. Files are in managed storage. |
| **Available** | Records are found by search, filter, trace and print. The Standards page shows the evidence clause by clause, and inspectors can use a read-only view. |

### Electronic records and signatures (21 CFR Part 11 benchmark)

| Expectation | How Hendrix meets it | Gap or note |
|---|---|---|
| Validated system (11.10a) | This pack, plus 40 automated test suites, the database tests and the Edge Function tests, run on every change (GitHub Actions) | Execute IQ/OQ/PQ on the live system |
| Accurate, complete copies (11.10b) | Print or PDF of every record; inspector view; Audit Trail export to CSV for any period | None |
| Record protection and retention (11.10c) | No deletes; voids with a reason; managed database and backups | Confirm the backup retention of the hosting plan (IQ-10) |
| Limited access (11.10d) | Personal accounts, admin approval, View / Edit / Full per module; two-step sign-in can be required per person (enforced by the database); idle sessions signed out (default 30 min) | None |
| Secure, time-stamped audit trail (11.10e) | Written by the database for every insert, change and void, with old and new values, user, time and reason. The log cannot be changed or deleted, even by admins. | Read access is given per person (View on Audit Trail), e.g. QA or an inspector account |
| Operational checks (11.10f) | Status flows enforced in order, e.g. requested → approved → implemented → closed | None |
| Authority checks (11.10g) | Approvals need Full access; the database checks this on every write | None |
| Device checks (11.10h) | Kiosks work only for an active license and a valid badge | None |
| Trained users (11.10i) | Training module; system training recorded like any other training | Add "Hendrix user training" to the training matrix |
| Signature manifestation (11.50) | Signed records show the signer's name, the date and time, and the meaning; the signature box shows the meaning before signing, and every signature is kept in the signature log with the meaning ("Approved and published this SOP", "Decided this hold: released") | None |
| Signature linking (11.70) | Signatures are fields of the record itself, fixed by the database after signing; the signature log names the record table and id and cannot be changed or deleted | None |
| Unique signatures (11.100) | One account per person; shared accounts not allowed | Enforce through the access SOP (section 12) |
| Signature components (11.200) | Each signature needs the password again (and the authenticator code with two-step sign-in), checked by the sign-in service at the moment of signing; the signer is taken from that sign-in | None. The password step is on by default and System Health fails if a license switches it off |
| Password controls (11.300) | Passwords of at least 8 characters, hashed by the provider; accounts can be disabled by the admin; two-step sign-in with an authenticator app | Require two-step sign-in for admins and approvers (IQ-16) |

@@SEC 7|Developer testing@@

Every release of Hendrix is tested in three ways before it goes live:

1. **Automated browser test suites.** These are scripted runs of the real app in a headless Chrome browser against a test database. They fill in forms, click buttons and check the result. The full set runs after every change.
2. **Database tests.** Every SQL step is installed on a local PostgreSQL copy. Each rule is then challenged: the test tries to break it, for example by closing without a reason, using a held lot or editing a signed record, and confirms that the database refuses.
3. **Clean install test.** The one-file install (steps 13 to 41) is run on an empty database that has steps 1 to 12, and run a second time on a full database. Both runs finish with no errors.

{{TESTS}}

@@SEC 8|Controls and traceability matrix@@

The controls below are the specific guarantees the system makes. Each one is traced to how it is enforced and to the automated test that proves it. The URS IDs (section 4) map to the modules shown here.

{{TRACE}}

@@SEC 9|Installation Qualification (IQ)@@

**Purpose:** to show that Hendrix is installed and configured correctly in the production environment.

**Execute** each step, write the actual result, mark Pass or Fail, and initial and date it. A Fail is raised as a deviation in Hendrix (QMS → Report deviation, source "Validation") before you continue.

{{IQ}}

@@SEC 10|Operational Qualification (OQ)@@

**Purpose:** to show that the critical functions work as specified **on the live system**.

Use a test license (for example "VALIDATION – do not use") so that production records stay clean. When the OQ is complete, set that license to inactive. Its records stay in the audit trail as evidence.

Each test lists:
- the steps;
- the expected result;
- the automated test that already proves the same thing in development.

{{OQ}}

@@SEC 11|Performance Qualification (PQ)@@

**Purpose:** to show that Hendrix supports the real process, run by the real people, over a real period.

**Period:** 30 days of live use at each license. During this period, keep the paper records in parallel for batch records and logs.

{{PQ}}

@@SEC 12|Keeping Hendrix in a validated state@@

Write these as SOPs in Hendrix: SOPs → **+ New SOP**. You can use the AI draft and then edit it. Have them approved and signed, and train the users on them.

| Procedure | What it must say |
|---|---|
| **Software change control** | Raise every change to Hendrix as a Change Control record (CC-YYYY-###), with risk, testing and approval. The developer works on a separate branch. The automated suites must pass before merge, and the release notes list the SQL steps. After release: re-run the affected OQ tests, update this pack's release number, and keep the old version available to roll back. |
| **User access** | Each person gets their own account. An admin approves new accounts and gives roles with the least access needed. Do a quarterly access review: remove leavers the same day, and record the review as a verification record. Do not share accounts. Sign out of shared devices. |
| **Backup and restore** | Keep the hosting provider's daily backups (point-in-time recovery if the plan allows). Do a yearly restore test into a test project and record it in Verification Schedule. Export the audit trail and key tables quarterly to secure storage. |
| **Periodic review** | Once a year, as part of Management Review: list changes, deviations about the system, access review results, test results and open risks; then decide whether validation is still current. |
| **Incidents** | If the system is down or gives a wrong result, raise a deviation. When Hendrix is unavailable, use the paper backup forms and enter them in Hendrix later, marked with the original time and the reason for late entry. |
| **AI use** | AI output is a draft. A competent person checks every AI-read COA value against the original certificate, and every AI-drafted SOP or course, before approval. The AI cannot approve, sign or release anything. |
| **Training** | "Hendrix user training" goes on the training matrix for everyone, with module training per role, using the User Manual. |

@@SEC 13|CSQ clause map@@

This table lists every CSQ clause Hendrix tracks, the Hendrix pages that hold its evidence, and how that evidence is produced. On the live system, the Standards page shows the same map, with the actual records, last dates and warnings for each license.

The clause summaries here are Hendrix's own short wording. They are not the CSQ text. Always audit against the licensed CSQ documents.

{{CSQ}}

@@SEC 14|Known limitations and recommendations@@

| # | Limitation | Risk | Recommendation |
|---|---|---|---|
| 1 | Two-step sign-in is per person, not forced for everyone | Low | Require it for admins and approvers (IQ-16); System Health flags admins without it |
| 2 | Email depends on an outside service (Resend) | Low | Settings > Email and System Health show when email stops; My Tasks always shows the same list in the app |
| 3 | Kiosk entries waiting on a tablet are lost if the tablet's browser data is cleared before the internet returns | Low | Do not clear kiosk browser data; the kiosk shows how many entries are waiting; the paper backup form covers long outages |
| 4 | Backups depend on the hosting plan | Medium | Confirm backup frequency and retention (IQ-10); run the yearly restore test |
| 5 | METRC Check reads METRC but does not write to it | Low | Fix differences in METRC by hand; run METRC Check weekly and before inspections |
| 6 | AI suggestions can be wrong | Medium | Human review is required (section 12); AI never approves |
| 7 | CSQ clause 3C.2.7 (topical products) has no dedicated page | Low (only if you make topicals) | If topicals are added, cover them with an SOP and product records, or ask for a topicals page |

@@SEC 15|Validation summary report@@

Complete this after the IQ, OQ and PQ.

| Item | Result |
|---|---|
| Release validated | Release 41 (commit `9cdb4e9`) — or the release installed: ____________ |
| IQ result | ☐ Pass ☐ Pass with deviations ☐ Fail — deviations: ____________ |
| OQ result | ☐ Pass ☐ Pass with deviations ☐ Fail — deviations: ____________ |
| PQ result | ☐ Pass ☐ Pass with deviations ☐ Fail — deviations: ____________ |
| Open deviations and how they are handled | |
| Limitations accepted (section 14) | |
| **Conclusion** | ☐ Hendrix QMS is validated and released for GxP use at: ____________ ☐ Not released |

### Approvals

<table class="sign"><thead><tr><th style="width:24%">Role</th><th style="width:28%">Name</th><th style="width:28%">Signature</th><th>Date</th></tr></thead><tbody>
<tr><td>System owner</td><td></td><td></td><td></td></tr>
<tr><td>Quality Assurance</td><td></td><td></td><td></td></tr>
<tr><td>Compliance</td><td></td><td></td><td></td></tr>
<tr><td>General Manager</td><td></td><td></td><td></td></tr>
</tbody></table>
