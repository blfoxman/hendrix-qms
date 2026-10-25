# Quality system: deviations, complaints, audits, SOPs and training

## QMS
QMS is where you record every deviation (anything that did not go as written), fix it, decide whether it needs a root cause analysis, and run corrective and preventive actions (CAPAs) until they are verified effective. Inspectors and CSQ auditors use it to see that problems are corrected, investigated when needed, and not repeated.

**Where:** left menu → **QMS**. You can also raise a deviation from many other pages (see *Raise a deviation from another page*). **Who:** View can see deviations and CAPAs and report a deviation; Edit can also update deviations and create and work CAPAs; Full can also decide whether a root cause analysis is needed, close and cancel deviations, verify CAPA effectiveness, and reopen closed records.
**CSQ:** 1.6 (a–g), 4A.9; also evidence for 2A.2.2, 2A.5.1, 2A.9.3, 2A.10.4, 2A.12.6 and 5.1.6 when deviations are raised from those areas.

![QMS dashboard: open and overdue counts, items that need action, and the last 12 months](shots/qual_qms_dashboard.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A pre-roll weight check fails on the line | QMS → **+ Report deviation**, Department *Production*, Category *Product quality*, write the correction you took |
| A Temp / Humidity log entry fails | Facility Logs → the failed entry → **Deviation**. The form opens prefilled and linked to the log entry |
| A lab test comes back Failed | Testing → the test → **Deviation**. Priority is set to *Critical* and the lot is filled in |
| A customer complaint points to a production problem | Complaints → open the complaint → **Raise deviation**. The deviation is linked back to the complaint |
| An internal audit finds a nonconformity | Internal Audits → the finding → **Raise deviation (CAPA)** |
| QA decides the problem needs a root cause | Open the deviation → **Edit** → *Root cause analysis needed?* = *Yes* (Full access) |
| The problem needs a long-term fix | Open the deviation → **+ Create CAPA** |
| The CAPA has been running long enough to judge it | Open the CAPA → **Verify effectiveness** |
| Annual review of deviations and CAPAs | QMS → **Trends** → **Print annual trend review**, discuss it, sign it |
| A deviation was entered twice by mistake | Open it → **Cancel**, give the reason (Full access) |

### Read the QMS page
The page has four tabs:
- **Dashboard:** open deviations, open CAPAs, overdue items, deviations closed this year (with the average days to close) and the percentage of rated CAPAs that were *Effective*. **Needs action** lists overdue deviations and CAPAs, deviations waiting for a root cause decision (shown to Full access) and CAPAs rated *Partially effective* or *Ineffective*. Click **Open** to go straight to the record. Below are a 12-month chart and recent activity.
- **Deviations (n open)** and **CAPAs (n open)**: one card per record with number, status, priority, department and source. Search by number, title, lot, product or owner. The status filter offers *Open + in progress* (default), *Overdue*, *Everything*, *Open*, *In progress*, *Closed* and *Cancelled*.
- **Trends:** charts by month, category, source, department and priority for the current year.

A record is **Overdue** when it is open or in progress and its due date has passed.

### Report a deviation
1. Click **+ Report deviation** (top right of QMS).
2. Fill in the form. Write what happened and what you did right away.
3. Click **Submit deviation**. Hendrix gives it the next number, for example *DEV-2026-009*, and opens it.

![Report deviation form, filled in for a broken drum seal at receiving](shots/qual_qms_report_form.png)

| Field | What to enter | Required |
|---|---|---|
| Deviation title | Short name of the problem | Yes |
| Department | Facility, Production, Sanitation, Compliance, Security, Warehouse, Distribution or Sales | Yes (defaults to Production) |
| Category | Product quality, Process / procedure, Equipment, Environment / temperature, Sanitation, Pest, Security, Documentation, Labeling / packaging, Testing result, Supplier / material, Safety or Other | No |
| Priority | Critical, Major or Minor | Yes (defaults to Major) |
| Date it happened | The date of the event | No (defaults to today) |
| Product affected | Product or material name | No |
| Lot / batch number | The lot or batch involved | No |
| What happened? | Full description | Yes |
| Correction / immediate action taken | What you did right away to contain it | No, but needed before closing |
| Root cause analysis needed? | *Not decided yet*, *Yes - find the root cause* or *No - the correction is enough*. Shown only to Full access | No, but a decision is needed before closing |
| Root cause | Why it happened. Marked * when root cause analysis is *Yes* | Needed before closing when RCA is *Yes* |
| Owner (who resolves it) | Name of the person responsible | No |
| Due date | When it must be resolved | No |
| Status | *Open* or *In Progress*. Shown only when you edit | — |
| Photos / files | **+ Attach file** for photos or documents | No |

> **Hendrix checks:** Hendrix will not save a deviation without a title and a description. The number (DEV-year-###, counted per license), who reported it and when are set by Hendrix and can never be changed, and neither can the license. A new deviation always starts *Open*. If someone without Full access fills in the root cause decision, Hendrix ignores it.

### Raise a deviation from another page
Many pages have a **Deviation** button (or **Raise deviation**) next to a record. It opens the same form, already filled in, and keeps a link to the source. The source shows at the top of the deviation ("Source: …") with an **Open** button that takes you back to that page.

| Page | Record |
|---|---|
| Facility Logs | A log entry (for example a failed temperature reading) |
| Batch Tracker | A batch |
| Testing | A lab test (Failed tests are prefilled as *Critical*) |
| Receiving / Hold and Release | A received lot or a hold |
| Traceability and Recall | A failed mock recall |
| Line Clearance and Rework | A line that was not cleared |
| Facility Tests | A failed facility test |
| HACCP | A CCP reading out of limits |
| Verification Schedule | A verification with issues |
| Complaints | A complaint (the deviation is linked back to the complaint) |
| Internal Audits | An audit finding (the deviation is linked back to the finding) |

Anyone with View access to QMS can raise a deviation this way.

### Work and close a deviation
1. Click the deviation card to open it. You see the badges, who reported it, the source, product and lot, what happened, the correction, the root cause decision, files and linked CAPAs.

![Deviation detail with its source (a lab test), root cause decision and linked CAPA](shots/qual_qms_deviation_detail.png)

2. Click **Edit** (Edit access) to add the correction, root cause, owner, due date or files, or to set the status to *In Progress*. Click **Update**.
3. When the work is done, click **Close deviation** (Full access). The close window shows three checks with a ✓ or ✗: correction recorded, root cause decision made, root cause recorded (when needed). If a check is missing, the **Close deviation** button stays greyed out. If linked CAPAs are still open, Hendrix tells you; they stay open until they are verified.
4. Enter an optional **Closing note** and click **Close deviation**.

Other buttons: **Print / PDF** prints the full deviation record; **Cancel** (Full) cancels it with a reason; **Reopen** (Full) reopens a closed or cancelled deviation.

> **Hendrix checks:** Hendrix will not close a deviation until the correction is written ("Every deviation needs its correction (immediate action) recorded before it is closed."), the root cause decision is made ("Decide whether a root cause analysis is needed before closing.") and, when RCA was marked as needed, a root cause is written ("A root cause is required before closing (RCA was marked as needed)."). Only Full access can close, cancel, reopen or make the root cause decision; Hendrix records who decided. A closed or cancelled deviation cannot be changed until it is reopened. Deviations are never deleted.

### Create a CAPA
Use **+ Create CAPA** inside an open deviation (fields are copied from it), or **+ New CAPA** at the top of QMS (Edit access).

| Field | What to enter | Required |
|---|---|---|
| CAPA title | Prefilled as "CAPA for DEV-…: title" | Yes |
| Linked deviation | The deviation it addresses, or *(none)* | No |
| Department | Same list as deviations | Yes (default from the deviation) |
| Priority | Critical, Major or Minor | Yes |
| Issue description | The problem being fixed | Yes |
| Root cause | Why it happened | No |
| Correction (immediate fix) | What fixed the immediate problem. Needed before the CAPA can close | No |
| Preventive action (long-term fix) | Process changes that stop it happening again | No |
| Responsible person | Pick from people with QMS access on this license | No |
| Due date | The timescale for the action | Yes |
| Status | *Open* or *In Progress*. Shown only when you edit | — |
| Verification method | How you will prove the fix worked, for example "30 days of in-range temperature logs" | No |

Click **Create CAPA**. Hendrix numbers it (CAPA-year-###).

> **Hendrix checks:** Hendrix will not save a CAPA without a title, an issue description and a due date ("Set a due date (CSQ 1.6: a timescale for every action)."). The linked deviation must belong to the same license. The number, creator, date and license cannot be changed. CAPAs are never deleted; Full access can cancel one with a reason.

### Verify a CAPA and close it
1. Open the CAPA and click **Verify effectiveness** (Full access). The planned verification method is shown at the top.
2. Write the **Verification evidence**: what you checked and what you found.
3. Pick **Effectiveness**: *Effective*, *Partially effective* or *Ineffective*.
4. If it is *Effective*, click **Verify & close CAPA**. Otherwise click **Save rating**: the CAPA stays open, moves to *In Progress* and appears in **Needs action**. Update the preventive action and verify again later.

![Verify effectiveness window for a CAPA rated Effective](shots/qual_qms_capa_verify.png)

| Field | What to enter | Required |
|---|---|---|
| Verification evidence | What was checked and the result | Yes |
| Effectiveness | Effective, Partially effective or Ineffective | Yes |

> **Hendrix checks:** "A CAPA closes only when it is verified Effective." Hendrix also needs the correction and the verification evidence before closing; **Verify & close CAPA** is greyed out until the correction is recorded. Only Full access can rate effectiveness or close a CAPA, and Hendrix stamps who verified it and when.

### Review trends
Open the **Trends** tab. It shows deviations opened and CAPAs closed by month (last 12 months), and this year's deviations by category, source, department and priority. Click **Print annual trend review** to print a summary with all the counts, every deviation of the year and its root cause, and a "Reviewed by (name, signature, date)" box.

![QMS Trends tab](shots/qual_qms_trends.png)

### Tips
- Report first, investigate later. A deviation needs only a title and a description to be saved.
- Fill in the correction as soon as you take it. It is the first thing Hendrix checks at closing.
- The **Standards (CSQ)** page shows live QMS evidence on clause 1.6 (deviations in 12 months, CAPAs closed effective).
- The Dashboard card **Deviations & CAPA** shows open and overdue counts for the license.

## Complaints
Complaints holds every consumer and dispensary complaint, product return, adverse event and piece of customer feedback, with the investigation, the response to the complainant and the link to deviations, batches and holds. Inspectors use it to see that every complaint was investigated by a named person, answered, and trended.

**Where:** left menu → **Complaints**. **Who:** View can see complaints and log new complaints and feedback; Edit can also investigate, respond, edit details, raise deviations and close; Full can also reopen and cancel.
**CSQ:** 1.7, 5.3

![Complaints page: summary cards, repeat-lot warning and the complaint list](shots/qual_complaints_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A customer calls about a harsh-tasting cart | **+ Log complaint**, Type *Consumer complaint*, Category *Taste / smell*, pick the batch |
| A dispensary returns a case of leaking carts | **+ Log complaint**, Type *Product return* or *Dispensary complaint* |
| Someone reports feeling unwell after a gummy | **+ Log complaint**, Type *Adverse event*. Report it to the state regulator and record the date |
| A buyer says a new flavor sells well | **+ Feedback**, pick the satisfaction rating |
| A complaint suggests the whole lot may be bad | Open the complaint → **Put batch on hold** |
| A complaint needs corrective action | Open the complaint → **Raise deviation** |
| Two complaints arrive on the same lot | Hendrix shows a red "Repeat complaints on the same lot" warning at the top |
| Inspector asks for the complaint log | **Complaint log** prints every complaint |

### Read the Complaints page
Cards at the top show **Open** and **Overdue** complaints, **Complaints (12 months)** with the number of adverse events, **Average days to close**, and **Customer satisfaction** (average feedback rating over 12 months). Feedback does not count as a complaint in these numbers. A red banner lists any lot with more than one complaint in 12 months.

The **Complaints** tab lists records with search (number, product, lot, customer, complainant, tag), a status filter (*Open* by default, *Every status*, or one status) and a type filter. The **Trends** tab shows received and closed complaints by month and complaints by category, type, lot / batch and customer.

### Log a complaint or feedback
1. Click **+ Log complaint** (or **+ Feedback**, which opens the same form with Type set to *Customer feedback*).
2. Fill in the form. If you pick a **Batch**, Hendrix fills the product and lot from it when you leave them blank.
3. Click **Log complaint** (or **Log feedback**). Hendrix numbers it CMP-year-### (feedback: FBK-year-###) and opens it.

![Log complaint form for a dispensary complaint linked to a pre-roll batch](shots/qual_complaints_form.png)

| Field | What to enter | Required |
|---|---|---|
| Type | Consumer complaint, Dispensary complaint, Product return, Adverse event or Customer feedback | Yes (defaults to Consumer complaint) |
| Priority | Critical, Major or Minor (not shown for feedback) | Yes (defaults to Minor) |
| Satisfaction | Feedback only: 5 Very happy … 1 Very unhappy | Yes, for feedback |
| Received on | Date received, not in the future | Yes (defaults to today) |
| Title | Short summary | Yes |
| Received by | Phone, Email, In person, Dispensary, Website / social media, State regulator or Other | Yes (defaults to Phone) |
| Complainant | Name, or anonymous | No |
| Contact | Phone or email | No |
| Customer (dispensary) | The dispensary | No |
| Category | Taste / smell, Potency / effect, Foreign matter, Mold / contamination, Hardware / packaging failure, Labeling, Leaking / damage, Adverse health effect, Delivery / service or Other (not shown for feedback) | No |
| Batch | Pick from this license's batches, or *(unknown / not listed)* | No |
| Product | Product name / SKU | No |
| Lot number | Lot | No |
| Package tag | The state package tag (1A4…) | No |
| Description | What the customer said | No |
| Attachments | **+ Attach photo or file** | No |

When you pick *Adverse event*, Hendrix shows: "Adverse event: report it to the state regulator. It cannot be closed until the report date is recorded."

> **Hendrix checks:** Hendrix will not save without a title, or feedback without a rating. The received date cannot be in the future. The batch must belong to the same license. The number, date logged and license can never be changed.

### Investigate, respond and close
1. Click the complaint to open it. The top card shows the received date and channel, complainant, customer, product, lot, tag, who logged it and any linked deviation.
2. In **Investigation (CSQ 1.7)** fill in the fields below. The due date starts one month from today.
3. Click **Save and start investigating** (the status becomes *Investigating*). Later saves use **Save**.
4. If needed, click **Raise deviation** (opens a prefilled deviation and links it) or **Put batch on hold** (opens the hold form with the batch and source *Complaint*; needs Edit access to Hold and Release).
5. When it is resolved and the complainant is answered, click **Close**.

![Complaint detail with the investigation section and the linked deviation](shots/qual_complaints_detail.png)

| Field | What to enter | Required |
|---|---|---|
| Investigator (responsible) | Who investigated | Yes, to close |
| Due date | When the investigation must be done | No (defaults to one month) |
| Investigation | What was checked: retained sample, batch record, COA, other complaints on the batch | Yes, to close |
| Root cause | Why it happened | No |
| Resolution | What was done for the complainant | Yes, to close |
| Corrective action to stop it happening again | The fix | No |
| Response to the complainant | What you told them | No |
| Answered on | Date you answered, not in the future | Yes, to close, when a contact or customer is recorded |
| Reported to the state regulator on | Adverse events only | Yes, to close an adverse event |

Other buttons: **Edit details** reopens the logging form; **Print** prints the complaint record; **Cancel** (Full) cancels with a reason; **Reopen** (Full) reopens a closed or cancelled complaint. Feedback records have no investigation section and close without these checks.

> **Hendrix checks:** Hendrix will not close a complaint without an investigator ("Name who investigated the complaint (CSQ 1.7 a)."), the investigation, the resolution, and — when you have a contact or customer — the date the complainant was answered ("Record when the complainant was answered before closing (CSQ 1.7 a)."). "An adverse event must be reported to the state regulator before it is closed." A closed or cancelled complaint cannot be changed until someone with Full access reopens it. View users see the investigation fields greyed out. Complaints are never deleted.

### Review trends and print the log
Open the **Trends** tab for the charts, and click **Complaint log** to print every complaint with its investigator, resolution, corrective action, deviation and status.

![Complaints Trends tab](shots/qual_complaints_trends.png)

### Tips
- Always link the batch. It makes the repeat-lot warning and the "By lot / batch" chart work, and lets you put the batch on hold in one click.
- Log dispensary praise as **+ Feedback**: the satisfaction average is CSQ 5.3 evidence.
- Complaints can also be imported in bulk from **Import (Excel / Sheets)**.

## Internal Audits
Internal Audits holds your annual internal audit program: which CSQ clauses were audited in the last 12 months, each audit with its checklist and evidence, and every finding through to a verified correction. CSQ requires every applicable clause to be audited every year by someone who does not audit their own work.

**Where:** left menu → **Internal Audits**. **Who:** View can see audits; Edit can plan and run audits, fill in checklists, record findings, raise deviations and close findings; Full can also close audits, reopen audits and findings, and cancel audits.
**CSQ:** 1.5

![Internal Audits list with coverage and findings summary](shots/qual_intaudits_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Start of year: plan the CSQ audits | **Annual program (coverage)** → **Plan an audit of the N clauses not audited**, or **+ Plan audit** per module |
| Audit day | Open the audit → **Start audit**, then **Edit / checklist** to record results and evidence |
| A clause is nonconforming | Open the audit → **+ Finding** (Hendrix suggests the clause) |
| A finding needs corrective action | On the finding → **Raise deviation (CAPA)** |
| The correction is done and checked | On the finding → **Close finding**, write how it was verified |
| Results presented at the managers meeting | In the audit, fill **Share the results**, then **Close audit** |
| Inspector asks for the audit report | Open the audit → **Print report** |
| A department audit (METRC, packaging, sanitation…) | **+ Plan audit**, pick the audit type, write the scope |

### Read the Internal Audits page
Cards show **CSQ clauses audited** (percent and count in the last 12 months), **Audits done (12 months)**, **Open findings**, **Overdue findings** and **Next planned** audit. The **Audits** tab lists audits with status, type, number of clauses, nonconforming clauses and open findings.

The **Annual program (coverage)** tab lists every CSQ clause in scope for this license (the CSQ parts and level come from the license's standard on the Standards page; level 1 by default). It shows a progress bar per module and, per clause, the last audit date, result, audit number and auditor, or **Not audited**. Filter by *Every clause*, *Not audited in 12 months* or *Nonconforming*.

![Annual program: coverage per module and per clause](shots/qual_intaudits_program.png)

### Plan an audit
1. Click **+ Plan audit** (Edit access).
2. Fill in the details. Add clauses with the module buttons (for example **+ Module 2A · cGMP (34)**, which adds the clauses not yet on the list) or one at a time with **+ One clause...**. Remove a clause with **×**.
3. Click **Save audit**. Hendrix numbers it IA-year-### and opens it with status *Planned*.

![Plan an internal audit form with a six-clause checklist](shots/qual_intaudits_form.png)

| Field | What to enter | Required |
|---|---|---|
| Audit title | Name of the audit | Yes |
| Audit type | CSQ internal audit, METRC Audit, Packaging Audit, Security Audit, Training Audit, Testing Audit, SOP Compliance Audit, Equipment Calibration Audit, Sanitation Audit, Full Facility Audit or Custom | Yes (defaults to CSQ internal audit) |
| Department | Same list as QMS | Yes (defaults to Compliance) |
| Planned date | When it is planned | No (defaults to today) |
| Audit date (done) | When it was done, not in the future | Yes, to complete |
| Lead auditor | Auditor name | Yes, to complete |
| Auditor qualification | For example "CSQ internal auditor course 2026" | Yes, to complete |
| The auditor does not audit their own work (CSQ 1.5 c) | Tick to confirm independence | Yes, to complete |
| Audit scope | Areas and processes reviewed | Clauses or scope needed to complete |
| CSQ checklist | Per clause: result (*Conforming*, *Nonconforming*, *Observation*, *Not applicable*) and **Evidence seen** | A result for every clause, to complete |
| Recommendations | Auditor recommendations | No |
| Conclusion | Overall conclusion | No |
| Next audit date | When to audit again | No |
| Attachments | **+ Attach** | No |

### Run and complete an audit
1. Open the audit. Click **Start audit** (status *In progress*).
2. Click **Edit / checklist** to record results and evidence, then **Save**.
3. For each nonconforming clause click **+ Finding**. Hendrix shows a red list of "Nonconforming clauses without a finding".
4. Click **Complete audit**.

![Audit detail: checklist results, findings and the Share the results box](shots/qual_intaudits_detail.png)

> **Hendrix checks:** Hendrix will not complete an audit until it has the audit date (not in the future), the auditor and their qualification, the independence box ("Confirm the auditor does not audit their own work (CSQ 1.5 c)."), clauses or a scope, a result on every checklist clause, and "a finding for each nonconforming clause". The number and license cannot be changed.

### Record and close a finding
Click **+ Finding** in the audit (Edit access, while the audit is not closed or cancelled).

| Field | What to enter | Required |
|---|---|---|
| Clause | A clause from the checklist, or *(general)*. Prefilled with the first nonconforming clause without a finding | No |
| Severity | Critical, Major, Minor or Observation | Yes (defaults to Minor) |
| Finding | What was found | Yes |
| Corrective action required | What must be done | No, but needed to close unless a deviation is linked (not for observations) |
| Owner | Who fixes it | No |
| Due date | Defaults to one month from today | No |

Click **Save finding**. On an open finding you can **Edit**, **Raise deviation (CAPA)** (not for observations; the deviation is linked to the finding) and **Close finding**. Closing asks "How the correction was verified as effective". A finding past its due date shows **Overdue**. Full access can **Reopen** a closed finding.

> **Hendrix checks:** Hendrix will not close a finding without the verification text, without a corrective action or linked deviation (except observations), or while its linked deviation is still open ("Close deviation DEV-… first (corrective action process)."). Findings of a completed audit are never deleted.

### Close the audit
1. When the audit is *Completed*, the **Share the results (CSQ 1.5 e)** box appears (Full access). Enter **Shared with** (for example "Managers meeting") and **On** (date, not in the future).
2. Click **Close audit**.

| Field | What to enter | Required |
|---|---|---|
| Shared with | Who the results were presented to | Yes, to close |
| On | Date shared | Yes, to close (defaults to today) |

> **Hendrix checks:** "Only someone with Full access can close an audit." Every finding must be closed first ("Close every finding first (CSQ 1.5 f).") and the sharing must be recorded ("Record who the results were shared with and when (CSQ 1.5 e)."). A closed or cancelled audit cannot be changed until Full access reopens it. **Cancel** needs a reason.

**Print report** prints the audit with the checklist, every finding, its corrective action, deviation, owner, due date and verification.

### Tips
- The quickest annual plan is the **Plan an audit of the N clauses not audited** button: it opens a new audit already holding every clause not audited in the last 12 months.
- Only *Completed* and *Closed* audits with an audit date count toward coverage.
- The Standards (CSQ) page shows this coverage as live evidence on clause 1.5.

## SOPs
SOPs is your controlled document library: every Standard Operating Procedure is numbered, versioned, approved by someone with Full access, signed by the people who must follow it, and reviewed on schedule. Earlier versions are kept unchanged. This is the core of CSQ document control.

**Where:** left menu → **SOPs**. **Who:** View can read published SOPs, sign them and download the PDF; Edit can also write and edit drafts (manually or with AI) and sees the signature progress; Full can also approve and publish, revise published SOPs, change their settings, archive and restore, see archived SOPs and delete drafts.
**CSQ:** 1.1, 1.2, 1.4, 2A.12.1, 5.2; the procedures themselves are evidence for many process clauses (for example 1.9, 2A.4, 2A.13.3–2A.13.7).

![SOPs library with signature status and review dates](shots/qual_sops_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You need a new procedure and have the text | **+ Manual SOP**, save as *Draft* |
| You need a first draft fast | **🤖 AI Generate SOP**, review, **Save as draft** |
| A draft is ready to go live | Open it → **✓ Approve & publish** (Full access) |
| A process changed | Open the published SOP → **🔄 Revise SOP**, new version and reason |
| You are told to read a new SOP | Open it → **👍 I have read and understood this SOP**, draw your signature |
| An SOP should only be signed by production staff | **Settings** (or the draft form) → *Who must read and sign it?* → *By role* |
| An SOP is no longer used | Open it → **Archive** (Full access) |
| Inspector asks for the document list | **Master list** prints every SOP with number, revision, dates, approver and signatures |
| You need a printed copy for the floor | Open it → **📄 Download PDF** |

### Read the SOPs page
Cards show **Total SOPs**, **Published**, **Needs my signature**, **I've signed**, and for Edit access **Review overdue** and **Signatures complete** (percent of required signatures done). A red banner tells you how many SOPs are waiting for your signature. Folder tabs filter the list: *All*, *General*, *Production*, *HR*, *Compliance*, *Security*, *Distribution*, *Sales*, and *Archived* (Full access only). Each card shows status, folder, version, number, badges (*Needs my signature*, *✓ Signed*, *Review overdue*), number of steps and signatures.

### Write an SOP manually
1. Click **+ Manual SOP** (Edit access).
2. Fill in the form. Click **Suggest** to get the next free number for the folder (for example SOP-PRD-004).
3. Add steps with **+ Add step**; remove one with **×**. Attach flow charts or forms with **+ Attach file**.
4. Click **Create SOP**.

![New SOP form with a suggested number, signers by role and three steps](shots/qual_sops_form.png)

| Field | What to enter | Required |
|---|---|---|
| Title | SOP title | Yes |
| Document number | For example SOP-PRD-001. **Suggest** uses the folder code: GEN, PRD, HR, CMP, SEC, DST, SLS | No, but must be unique on the license |
| Folder | General, Production, HR, Compliance, Security, Distribution or Sales | Yes |
| Category | One of 20 categories (for example *Production — Cart Department*). Picking one moves a *General* SOP to the matching folder | No |
| Version | Defaults to 1.0 | Yes |
| Status | *Draft*, or *Published (I approve it)* (Full access only) | Yes |
| Effective date | Leave blank to use today when published | No |
| Next review | Leave blank to use one year after the effective date | No |
| Applies to license(s) | Tick the licenses in this state that use it; the current license is fixed | Yes |
| Who must read and sign it? | *Everyone on the license(s)*, *By role* (tick roles) or *Pick people* | Yes (at least one role or person when you choose those) |
| Description / purpose | What the SOP is for | No |
| Procedure steps | One box per step | No |
| Attachments | Files | No |

> **Hendrix checks:** Hendrix will not save without a title or at least one license, and will not accept *By role* or *Pick people* with nothing ticked. A number already used on the license is refused ("Document number … is already used under this license."). Only Full access can publish; Hendrix records you as the approver and fills the effective date and the next review (one year) when you leave them blank. Every license must be in the SOP's state.

### Generate an SOP with AI
1. Click **🤖 AI Generate SOP** (Edit access). The first step shows the license and state; the AI uses this state's Rulebook entries and writes to cGMP / CSQ.
2. Enter the **SOP title**, pick the **Category / department**, and optionally add a **Reference document** (.pdf, .txt or .md) and **Instructions for the AI**. You can instead load an SOP file exported from the generator; this jumps straight to review.
3. Click **Generate SOP with AI**. Hendrix writes the purpose, scope and responsibilities, then the steps.
4. Review everything on **Review & Save**: title, document number, purpose, scope and each step are editable. Critical steps carry a red **Critical** badge; regulatory notes show under the step.
5. Click **Save as draft**. Someone with Full access reviews and publishes it.

![AI SOP Generator, Review & Save step](shots/qual_sops_ai_review.png)

| Field | What to enter | Required |
|---|---|---|
| SOP title | Title | Yes |
| Category / department | One of the 20 categories; sets the folder | Yes |
| Reference document | Optional file the AI should use | No |
| Instructions for the AI | For example "include METRC steps; keep to 8 steps" | No |

> **Hendrix checks:** An AI SOP is always saved as a draft. A placeholder number from the AI (with brackets) is dropped. If the AI is not set up, Hendrix says so instead of saving.

### Approve and publish a draft
Open the draft. Edit access can click **Edit draft** to change anything. Full access clicks **✓ Approve & publish**. Full access can also **Delete draft** (drafts are the only SOPs that can be deleted).

### Read and sign an SOP
1. Open a published SOP. If you must sign it and have not, you see **👍 I have read and understood this SOP**.
2. Read the procedure, click the button, and draw your signature in the box.
3. Click **✓ Sign & acknowledge**. The SOP shows "✓ You signed this version".

The **Signatures · v…** box shows the progress bar, who signed (with date) and who is still pending (Edit access sees the full list).

![SOP detail with the signature box and the sign button](shots/qual_sops_detail.png)

> **Hendrix checks:** "Draw your signature first." Only a published SOP can be signed, only in your own name, once per version ("You already signed this version."). Signatures are permanent and cannot be changed or deleted. Hendrix records your name, roles and the time.

### Revise a published SOP
1. Open the SOP and click **🔄 Revise SOP** (Full access).
2. Choose **Edit it myself**, or **Revise with AI** and describe what needs to change, then click **Revise with AI** and review the result.
3. Check the **New version** (Hendrix suggests the next one, for example 1.1 → 1.2) and write the **Reason for revision**.
4. Edit the purpose and steps, then click **Approve and publish v…**.

| Field | What to enter | Required |
|---|---|---|
| New version | Must differ from the current version | Yes |
| Reason for revision | What changed and why | Yes |
| Purpose / description | Updated purpose | No |
| Procedure | Updated steps (**+ Add step**, **×** to remove) | No |
| What needs to change? | AI mode only | Yes, to run the AI |

> **Hendrix checks:** "Changing a published SOP is a revision: give it a new version number." A reason is required. Hendrix keeps the old version unchanged in **Version history**, publishes the new version with you as approver, resets the effective date to today and the next review to one year, and everyone must sign the new version. A published SOP can never go back to draft.

**Version history** lists every earlier version with who replaced it, when and why ("Replaced because: …"); click one to read its text.

### Other SOP actions
- **Settings** (Full, published SOPs): change folder, licenses, who must sign and the next review date without creating a new version.
- **Archive** (Full): moves the SOP to *Archived*, visible only to Full access. **Restore** puts it back in its folder.
- **📄 Download PDF**: a controlled-document PDF with number, revision, status, effective and review dates, approver, the procedure (critical steps marked "CRITICAL STEP — Verify and document before proceeding"), revision history, and the signatures for the current revision. Drafts print blank signature lines. The footer says printed copies are uncontrolled.
- **Master list**: prints the SOP master list with number, title, folder, revision, status, effective date, next review (overdue marked), approver and signatures.

![First page of an SOP PDF](shots/qual_sops_pdf.png)

### Tips
- *Review overdue* appears when a published SOP passes its next review date. Revise it (or update the review date in **Settings**) after the review.
- Use *By role* for department SOPs so the signature percentages are meaningful.
- An SOP can also count as training: see *Courses* in Training.

## Training
Training is your training program and matrix: which courses each role must take, who is current, due or expired, who trained them and how they were assessed, plus online courses with graded quizzes. Inspectors use it to see that every person is trained before working, by qualified trainers, with refreshers on time.

**Where:** left menu → **Training**. **Who:** View can see their own training (**My training**), the **Courses** list, and take online courses; Edit can also record training, and see the matrix, SOP signatures and records for the license; Full can also add and edit courses, write and publish online course content, and void records.
**CSQ:** 2A.13.2, 1.3, 2A.13.1, 2A.13.4–2A.13.7, 1.9, 4A.2, 3B.1.2, 5.1.4, 5.2

![Training matrix with status per person and course](shots/qual_training_matrix.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new license starts using Hendrix | Open **Training** with Full access once: Hendrix creates the CSQ courses and draft online courses |
| Classroom cGMP session for six people | **+ Record training**, tick the six people, attach the sign-in sheet |
| A new hire must learn hygiene rules | They open **My training** → **Take course** on *Personnel hygiene, handwashing and PPE* |
| A manager gets HACCP certified | **+ Record training** on *HACCP certification*, method *External certification*, attach the certificate |
| A gap shows red in the matrix | Click the red cell to record that training for that person |
| The Missouri rules change | Courses → *Missouri regulatory compliance* → **Online course** → **Draft from the Missouri Rulebook with AI**, review, publish |
| A job task is trained by reading an SOP | **+ Course**, *Met by signing an SOP* |
| A record was entered for the wrong person | Records → **Void**, give the reason, then record it again |
| An inspector asks for one employee's training | Matrix → **PDF** on that person's row |

### Starter courses and online content
The first time someone with Full access opens Training on a license with no courses, Hendrix creates the CSQ training courses:

| Course | Who must take it | Refresher | Notes |
|---|---|---|---|
| *State* regulatory compliance (state rules), for example "Missouri regulatory compliance" | Everyone | 12 months | Only for that state's licenses |
| Current Good Manufacturing Practices (cGMP) | Everyone | 12 months | Assessment required |
| Cannabis safety principles | Everyone | 12 months | Assessment required |
| Personnel hygiene, handwashing and PPE | Everyone | 12 months | |
| Product defense and security awareness | Everyone | 12 months | |
| Chemical safety and SDS | Manager roles and Sanitation roles (Optional when no such roles exist) | 12 months | |
| CSQ Certification Program Overview | Manager roles; at least 1 certified | One time | Outside certification |
| HACCP certification (International HACCP Alliance) | Manager roles; at least 2 certified | One time | Outside certification |
| Extraction safety and solvent controls (manufacturing licenses) or cGACP (cultivation licenses) | Extraction roles (Optional otherwise) / Everyone | 12 months | Assessment required |

Manager roles are any role whose name contains manager, compliance, director, supervisor or owner. Hendrix also loads Hendrix starter lessons and quizzes, written from the CSQ standard, as **drafts** for six courses. A banner **Online courses ready** lists them: review them (Courses → **Online course**) and click **Publish all** so people can take them. **Add missing CSQ starter courses** on the Courses tab adds any starter course you do not have.

### Read the Training page
Cards show **Training current** (percent of required courses current for everyone), **Fully trained** (people at 100%), **Expired or missing**, **Due in 30 days**, and one card per "at least N people" course (for example *HACCP certification 1 / 2 — needs 1 more*).

Tabs (Edit access): **Training matrix**, **SOP signatures**, **Records**, **My training**, **Courses**. View access sees **My training** and **Courses** only.

**Training matrix:** one row per person, one column per active course. Search people, filter by role, and filter *Everyone*, *Has gaps* or *Fully trained*.

| Cell | Meaning |
|---|---|
| ✓ green | Current |
| ! gold | Due: expires within 30 days |
| × red | Expired |
| + red | Missing (required, not done) |
| — | Not required for this person |

Edit users can click any cell that is not current to open **Record training** prefilled with that course and person. The % column is the share of that person's required courses that are current or due. **PDF** downloads the person's Employee Training Record (required courses with status and expiry, plus SOP signatures). **Print matrix** prints the matrix.

**SOP signatures:** one row per person, one column per published SOP; ✓ when they signed the current version, — when the SOP does not apply to them, and a signing rate per person.

**Records:** online quiz attempts (date, person, course, score, result, time, content version), training counted from your other licenses, and every training record with trainer, method, assessment, expiry, attachments and **Void** (Full).

**My training:** your required courses with status and **Take course** buttons, other online courses, your quiz attempts, SOPs waiting for your signature (with **Open SOPs**), and **Download my training record (PDF)**.

### Manage courses
The **Courses** tab lists each course with its topic, badges (*Online · v1 · pass 80%*, *Online draft*, *Outside certification*, *Shared · all licenses* or *Shared · all Missouri licenses*), who must take it, the refresher, and whether an assessment is required.

![Courses tab with online and shared badges](shots/qual_training_courses.png)

To add one, click **+ Course** (Full access); to change one, click **Edit**. Click **Save course**.

| Field | What to enter | Required |
|---|---|---|
| Course name | Name, unique on the license | Yes |
| Topic | Required by law, cGMP, cGACP, Extraction, Cannabis safety, Personnel hygiene & safety, Product defense, Job-specific, Safety, CSQ program, HACCP or Other | Yes (defaults to Job-specific) |
| What it covers | Description | No |
| Who must take it | Everyone on the license, Chosen roles, At least N people, or Optional | Yes |
| How many people (at least) / Certified people needed (at least) | Shown for *At least N people*, and for CSQ program / HACCP courses by role | Yes, when shown (minimum 1) |
| Refresher every (months, 0 = once) | Months until retraining | Yes (defaults to 12) |
| Roles that must take it | Tick roles; **+ All manager roles** ticks every manager role | Yes, for *Chosen roles* |
| Met by signing an SOP (read and sign training) | A published SOP, or *(no - record it as training)* | No |
| Assessment required | Tick when a pass/fail assessment is needed | No |
| Active | Untick to switch a course off (it leaves the matrix) | — |
| Same course at all my licenses | Share the course and its records across your licenses (not for SOP-linked courses) | No |

> **Hendrix checks:** "A course with that name already exists." A course for chosen roles needs at least one role. An SOP-linked course must use an SOP that applies to this license. A course with training records cannot be deleted: switch it off instead.

**Read-and-sign courses:** when a course is met by signing an SOP, a person's signature on the SOP's current version counts as completing the course on the date they signed (expiry = signature date + refresher). When the SOP is revised, they must sign again.

### Record training
1. Click **+ Record training** (Edit access), or click a gap in the matrix.
2. Pick the course; Hendrix shows its refresher and whether an assessment is required.
3. Tick everyone who was trained (**Select all** / **Clear**).
4. Fill in the trainer and assessment, attach the certificate or sign-in sheet, and click **Save record** (or **Save N records**). Hendrix saves one record per person.

![Record training form for a cGMP make-up session](shots/qual_training_record_form.png)

| Field | What to enter | Required |
|---|---|---|
| Course | Active course | Yes |
| Date completed | Not in the future | Yes (defaults to today) |
| Who was trained | One or more people on the license | Yes |
| Trainer | Name or provider | Yes |
| Trainer qualification | For example "QA Manager, 8 yrs; PCQI certified" | No |
| Method | Classroom, On the job, Online course, Read and sign, or External certification | Yes (defaults to Classroom) |
| Language | Language of the training | No (defaults to English) |
| Assessment | Passed or Failed; *Not required* when the course has no assessment | Yes, when the course requires an assessment |
| Score | For example 18/20 | No |
| Notes | Anything else | No |
| Attachments | **+ Attach certificate / sign-in sheet** | No |

> **Hendrix checks:** Hendrix will not save without the course, at least one person and a trainer ("Enter the trainer (CSQ: trainers must be qualified)."). "This course requires an assessment: choose Passed or Failed." The date cannot be in the future. Hendrix calculates the expiry date from the course refresher and records who entered it. A *Failed* record does not count as trained. A training record cannot be changed afterwards (only certificates and notes can be added): void it with a reason and record it again. Only Full access can void, and a voided record stays on file crossed out.

### Take an online course
1. Open **My training** (or **Courses**) and click **Take course**.
2. Read each lesson and click **Next lesson**; the bar shows your progress. On the last lesson click **Go to the quiz**.
3. Answer every question and click **Submit answers**.
4. Hendrix shows your score. At or above the pass mark: "Passed - your training is recorded". Below it: "Not passed (pass mark …%)" with **Read again and retake**. Wrong answers are listed with an explanation.

![A lesson in the cGMP online course](shots/qual_training_lesson.png)

![Quiz result: passed at 90% with the explanation for the one wrong answer](shots/qual_training_quiz_result.png)

> **Hendrix checks:** The quiz is graded by Hendrix on the server: the correct answers are never sent to your screen. You must answer every question. Every attempt is kept with the score, answers, time spent and content version. A pass records the training automatically: today's date, *Online course*, *Passed*, the score, and "Course content version N approved by …" as the trainer qualification. A failed attempt adds no training record. You can take a course only at a license you are assigned to.

### Write or publish an online course
1. Courses → **Online course** on the course (Full access; not offered for HACCP and CSQ Program Overview, which are outside certifications).
2. Use **Load Hendrix starter content** (starter topics), or for the state regulatory course **Draft from the *state* Rulebook with AI**. The AI writes the lessons and quiz only from that state's Rulebook entries; read and correct them, because you are approving the legal content.
3. Edit lessons (title and text: a blank line starts a paragraph, "- " makes a bullet, "## " makes a heading; **↑** moves a lesson up) and questions (2 to 6 options; tick the correct one; add the "Why" explanation shown after a wrong answer). **Preview** shows the course as a learner sees it.
4. Click **Save draft**, or **Publish online** (**Publish new version** if it is already published).

| Field | What to enter | Required |
|---|---|---|
| Pass mark % | 50 to 100 | Yes (defaults to 80) |
| Minutes (about) | Expected time | Yes (defaults to 15) |
| Source of the content | Where the content came from, for example "Written by QA from SOP-PRD-001" | No |
| Lessons | Title and text | At least one, to publish |
| Quiz | Question, options, correct answer, why | At least one, to publish |

> **Hendrix checks:** Hendrix will not publish without at least one lesson and one question, each question with text and at least two filled options, and a correct answer for every question. Publishing makes the assessment required. Every change to published content creates a new content version, stamped with who published it. Only Full access can change content or the answers. If the state Rulebook is empty, the AI draft is refused ("The … Rulebook is empty. Add the state rules first; the course is written from them.").

### Training shared across licenses
The CSQ starter courses are shared across all your licenses in both states; the state regulatory course is shared across all licenses of the same state; a custom course is shared when you tick *Same course at all my licenses*. For a shared course:
- A person's valid training at one license counts at the others. It appears in the matrix and on the Records tab under **Counted from your other licenses**, showing where it was done. The record itself stays at the license where it was done.
- Missouri law training does not count in Michigan, and the other way round.
- Publishing new online content at one license updates the course at every license that shares it where you have Full access. A new license's copy starts from the latest published version.

### Tips
- There is no separate training kiosk: people take online courses from **My training** under their own login.
- Check the **HACCP** and **CSQ Certification Program Overview** cards: red means you have fewer certified people than required.
- The Standards (CSQ) page shows live training evidence on clause 2A.13.2.
