# HACCP and the management system

These seven modules hold your food safety plan and the top-level management system: the HACCP plans and their records, the risk register, change control, the org chart, the quality policy and objectives, the management review and the verification schedule. Together they are the evidence for CSQ Module 4A (Level 2) and Module 5 (Level 3).

Everything here belongs to the license picked at the top of the screen. Records are never deleted. Where something can be undone, Hendrix asks for a reason and keeps it in the Audit Trail.

## HACCP

HACCP holds your HACCP team, one plan per product or process (product description, process flow, hazard analysis, CCPs with critical limits), CCP monitoring records and HACCP verification. An inspector uses it to see that you follow the 12 Codex steps, that only complete and validated plans are in use, and that every CCP check is recorded and reviewed by a second person.

**Where:** left menu → HACCP. **Who:** View can see plans, records and the team and print plans. Edit can draft plans, record CCP checks, verify other people's checks and record verifications. Full can also validate, activate, revise and retire plans, manage the HACCP team and void records.
**CSQ:** 4A.1, 4A.2, 4A.3, 4A.4, 4A.5, 4A.6, 4A.7, 4A.8, 4A.9, 4A.10, 4A.11

![HACCP plans: two active plans and one draft, with the team, out-of-limit, verify and reanalysis counters](shots/mgmt_haccp_plans.png)

The counters at the top show: **Active plans** (and how many are in draft), **HACCP certified** (certified team members, out of the 2 needed), **Out of limits (30 days)**, **Records to verify** (CCP checks not yet reviewed by a second person) and **Reanalysis due** (active plans whose yearly reanalysis is late). The tabs are **Plans**, **CCP monitoring**, **Verification** and **HACCP team**.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You are setting up HACCP for the first time | **HACCP team** tab → **+ Member** for each member; make sure a leader and a backup are certified. Then **+ HACCP plan**. |
| You need a plan for gummies, cartridges, extraction or pre-rolls | **+ HACCP plan** → pick the batch type → **Start from a draft for this batch type**, then check every step against your process. |
| Distillate is weighed for a gummy batch (a CCP) | **+ CCP check** (or **CCP check** on the batch card in the Batch Tracker) → record the measured value. |
| A water activity reading is above the critical limit | **+ CCP check** → **Within the critical limit?** = No → record the corrective action and what happened to the product. Then **Deviation** on the record. |
| A supervisor reviews yesterday's CCP records | **CCP monitoring** tab → filter **Not verified yet** → **Verify** on each record. |
| The aw meter is checked against a standard | **Verification** tab → **+ Verification** → Kind: Monitoring equipment calibration check. |
| The yearly HACCP reanalysis is done | **Verification** tab → **+ Verification** → Kind: Yearly reanalysis of the whole plan, pick the plan. |
| A process change affects an active plan | **Plans** tab → **Revise**, update the plan, validate it again and **Activate plan**. |
| A product line is discontinued | **Plans** tab → **Retire** and give the reason. |
| A CCP record was entered against the wrong batch | **CCP monitoring** tab → **Void** with a reason, then record it again. |

### Build the HACCP team

1. Open the **HACCP team** tab and click **+ Member** (Full access).
2. Pick the person, or leave "(not a Hendrix user)" and type the name.
3. Set the role and department.
4. Tick **HACCP certified** for anyone who holds an International HACCP Alliance approved certificate, and enter the course, the date or a file.
5. Click **Save**.

| Field | What to enter | Required |
|---|---|---|
| Person | A Hendrix user with access to this license, or "(not a Hendrix user)" | No |
| Name | The person's name (filled in when you pick a user) | Yes |
| Role | Team leader, Backup or Member | Yes (default Member) |
| Department | e.g. Quality, sanitation, maintenance, management | No |
| HACCP certified (International HACCP Alliance approved course) | Tick if certified | No |
| Course / provider | The course and who ran it | One of course, date or file, if certified |
| Certified on | Certificate date | One of course, date or file, if certified |
| Certificate | Upload the certificate | One of course, date or file, if certified |
| On the team | Untick to take someone off the team (edit only) | No |

> **Hendrix checks:** Only Full access can add, change or remove team members. A certified member needs a course, a date or a file: "Enter the certificate (provider, date or file)." No plan can be validated or activated until at least **two active team members are certified** (one person and a backup, CSQ 4A.2).

### Create a HACCP plan

1. Click **+ HACCP plan**.
2. Enter the **Plan name** and pick the batch type the plan **Covers**.
3. For gummies, cartridges, ethanol or BHO extraction, and pre-rolls (also infused flower, moon rocks, snow caps), click **Start from a draft for this batch type**. Hendrix fills in a starting flow, hazards and CCPs. Treat it as a starting point: your team must check every step, limit and control against your own process and state rules.
4. Work through the five tabs below. The box **Still needed before validation** lists what is missing.
5. Click **Save draft** at any time. When the plan is complete, Full access clicks **Validate** or goes straight to **Activate plan**.

![Plan editor, tab 1: the product description](shots/mgmt_haccp_product.png)

**Tab 1. Product** (CSQ 4A.3)

| Field | What to enter | Required |
|---|---|---|
| Plan name | e.g. Gummies, Cartridges, BHO extraction | Yes |
| Covers batch type | The Batch Tracker batch type the plan covers, or "(no batch link)" | No |
| Product name(s) | The finished products | No |
| Important safety characteristics (aw, pH, cannabinoids...) | e.g. THC per piece, water activity, pH | No |
| Ingredients | Every ingredient | Yes, to validate |
| Allergens | Allergens present, or "None" | Yes, to validate |
| Packaging material | e.g. child-resistant opaque pouch | Yes, to validate |
| Intended use | e.g. adult use by consumers 21+ as labeled | Yes, to validate |
| Target market (consumers) | e.g. adults 21+ through licensed dispensaries | No |
| Shelf life / date | e.g. 12 months from the batch date | No |
| Labeling instructions | e.g. state warnings, THC per serving, batch number | No |
| Storage and distribution | e.g. cool, dry place | Yes, to validate |

![Plan editor, tab 2: the process flow list and the flow diagram Hendrix draws, with the CCPs marked](shots/mgmt_haccp_flow.png)

**Tab 2. Process flow** (CSQ 4A.4). Add every input, step, outsourced step, rework, end product and waste, in order. For each row enter the step name, pick its type (Input (material / packaging), Process step, Outsourced step, Rework, End product, Waste / by-product) and tick **CCP** where a hazard is controlled at that step. Use the arrows to reorder and **×** to remove (removing a step also removes its hazards and CCP). Click **+ Step** to add a row. Hendrix draws the flow diagram below the list: inputs on the left, waste and rework on the right, CCP steps highlighted.

**Tab 3. Hazard analysis** (CSQ 4A.5). For every step, click **+ Hazard** and enter the type (Biological, Chemical, Physical, Allergen), the hazard, its cause and the **Control measure** (required). Tick **Significant** for hazards that need a CCP. If a step has no hazards, tick **No hazards reasonably expected**.

![Plan editor, tab 4: each CCP with its critical limit, monitoring, corrective action and verification](shots/mgmt_haccp_ccps.png)

**Tab 4. CCPs** (CSQ 4A.6 to 4A.9). Ticking **CCP** on a flow step adds a CCP here.

| Field | What to enter | Required |
|---|---|---|
| CCP name | e.g. CCP 2 Water activity | Yes |
| At step | The flow step | Yes |
| Critical limit (measurable) | e.g. aw ≤ 0.85; residual butane < 5000 ppm | Yes, to validate |
| Monitoring: what and how | What is measured and how | Yes, to validate |
| Frequency | e.g. Every batch | Yes, to validate |
| Who | Who does the check | No |
| Corrective action (bring under control, handle product) | What to do when the limit is missed | Yes, to validate |
| Verification | How the CCP is verified | Yes, to validate |

**Tab 5. Validation** (CSQ 4A.10). Enter **How the plan was validated** (studies, test results, scientific references, equipment validation) and upload the evidence under **Validation evidence**.

> **Hendrix checks:** Only Full access can validate or activate a plan. Before it does, Hendrix checks the plan is complete and will not let you continue if:
> - the product description is missing ingredients, allergens, packaging, intended use or storage;
> - the flow has fewer than 2 rows ("Draw the process flow (at least the inputs and the steps).");
> - a step has no hazards and is not marked "no hazards reasonably expected";
> - a hazard has no control measure;
> - there are significant hazards but no CCP;
> - a CCP is missing its critical limit, monitoring, frequency, corrective action or verification;
> - fewer than two team members are certified;
> - the validation is blank ("Record how the control measures and critical limits were validated (studies, tests, references).").
>
> Activating gives the plan its next **version number** and records who approved it and when. An **active plan is frozen**: "An active plan cannot be edited. Click "Revise" to start a new version." Changing the flow, hazards, CCPs or description of a validated plan puts it back to draft. Plans are numbered **HP-001, HP-002…** per license by Hendrix.

### Revise or retire a plan

- **Revise** (Full, active plans): Hendrix asks you to confirm, then puts the plan back to **Draft** and clears the validation. Validate and activate it again; it becomes the next version.
- **Retire** (Full, validated or active plans): enter **Why is the plan retired?** and click **Retire**. The plan stays on file, crossed out.
- **Print** gives the full plan: team, product description, flow diagram, hazard analysis, CCP summary and validation.

> **Hendrix checks:** Only Full access can revise or retire, and retiring needs a reason. A plan only moves draft → validated → active (or retired).

### Record a CCP check

1. Click **+ CCP check** (shown when there is an active plan), or **CCP check** on a batch card in the Batch Tracker.
2. Pick the plan, the CCP and the batch. The critical limit and monitoring method are shown.
3. Enter the measured value and who checked it.
4. If the value is outside the limit, choose **No - deviation** and fill in the corrective action and what happened to the product.
5. Click **Record**.

![CCP check out of the critical limit, with the corrective action and the product held](shots/mgmt_haccp_ccpcheck.png)

| Field | What to enter | Required |
|---|---|---|
| HACCP plan | An active plan (shown with its version) | Yes |
| CCP | A CCP in that plan | Yes |
| Batch | A batch of the batch type the plan covers, or "(no batch)" | No |
| Measured value | e.g. aw 0.78; 12.1 g; 6 h at 110 °F, -29 inHg | Yes |
| Within the critical limit? | Yes, or No - deviation | Yes |
| Checked by | Who did the check (your name by default) | Yes |
| Corrective action taken | What was done (the plan's corrective action is shown as a hint) | Yes, if out of limits |
| Product | Held, Reworked, Destroyed, Released after evaluation | Yes, if out of limits |

> **Hendrix checks:** Checks are recorded only against an **active** plan and a CCP in it. An out-of-limit check needs both the corrective action and the product decision: "Out of the critical limit: record the corrective action." Each record keeps the plan version it was checked against. A record cannot be changed afterwards: "A monitoring record cannot be changed. Void it and record it again." Only Full access can void, with a reason.

### Review (verify) CCP records

![CCP monitoring: an out-of-limit check with its corrective action, Verify and Deviation buttons](shots/mgmt_haccp_monitoring.png)

On the **CCP monitoring** tab, filter by **All checks**, **Out of limits** or **Not verified yet**. Click **Verify** on a record to sign it as reviewed. On an out-of-limit record, click **Deviation** to raise a deviation that is linked to the check.

> **Hendrix checks:** "Records are verified by someone other than the person who did the check." The person who checked or recorded it cannot verify it. A verified record cannot be verified again. The Batch Tracker card shows **CCP x/y** (CCPs passed for that batch) and "· deviation" when a check failed.

### Record HACCP verification

1. Open the **Verification** tab and click **+ Verification**.
2. Fill in the form and click **Record**.

![HACCP verification: a yearly reanalysis of the gummy plan](shots/mgmt_haccp_verification.png)

| Field | What to enter | Required |
|---|---|---|
| Kind | Monitoring records review, Yearly reanalysis of the whole plan, Re-validation after a change, Monitoring equipment calibration check, Other verification | Yes |
| Plan | A plan, or "(whole HACCP system)" | No |
| Date | The date it was done (not in the future) | Yes |
| Done by | Who did it | Yes |
| What was checked and found | Findings | Yes |
| Result | The HACCP system is followed and controls the hazards, or Changes needed (revise the plan / raise a deviation) | Yes |
| Files | Reports, photos | No |

> **Hendrix checks:** A yearly reanalysis recorded against a plan resets the plan's **Reanalysis due** date to one year later (CSQ 4A.11). The due date is one year after the latest of plan activation and reanalysis. Verification records cannot be changed; only Full access can void them, with a reason.

### Tips
- The Dashboard **HACCP** card shows active plans and, for the last 30 days, CCP checks, out-of-limit checks and records waiting for review.
- A change in Change Control that ticks "HACCP plan / flow diagram" cannot be implemented until the plan has been reviewed (see Change Control).
- Raise a deviation from every out-of-limit check so the root cause goes through CAPA.

## Risk Register

The risk register lists every risk to product safety, quality and the business: the hazard, its root cause, the owner, the rating, the actions and a routine review. Inspectors use it as your risk management procedure (CSQ 5.1.6) and as your threat, fraud, allergen, supplier and site assessments.

**Where:** left menu → Risk Register. **Who:** View can see and print the register. Edit can add, edit, review and mark risks controlled, re-open them and add the suggested risks. Full can also close risks.
**CSQ:** 5.1.6, 1.9, 1.10, 2A.12.4, 2A.12.7, 3A.1.2

![Risk register: counters, heat map, risks by category with CSQ links, and the register](shots/mgmt_risk_register.png)

The page shows **Risks on the register**, **High or critical** (current rating 10 or more), **Reviews overdue** and **Fixes past target**. The **heat map** counts risks by their current rating (severity up, likelihood across). Click a cell to show only those risks; click **Clear heat map filter** to go back. **By category** lists the count per category and flags categories that CSQ asks for when none is assessed (Allergens 2A.12.7, Product defense 1.9, Fraud 1.10, Materials and suppliers 2A.12.4, and Site 3A.1.2 for cultivation). Filter the list by status (Open and controlled, Open, Controlled, Closed, All) and category. Click a risk's name to see its details and review history.

**How ratings work:** score = likelihood × severity (1 to 5 each). 1–4 Low, 5–9 Medium, 10–14 High, 15–25 Critical. Once a risk is controlled, its current rating is the residual rating (the table shows "was" with the old score).

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You are starting the register | **Suggested risks** → untick any that do not apply → enter the owner → **Add selected**. Then check each rating against your facility. |
| A deviation shows glass near the filling line | **+ Risk** → Found through: Deviation, enter the deviation number. |
| You do the yearly product defense (threat) assessment | **+ Risk** → Category: Product defense (threats). |
| The permanent fix is in place and shown to work | **Controlled** on the risk row → record the action, the verification and the residual rating. |
| A risk is due for its scheduled review | **Review** on the row → rate it today, say whether the controls work. |
| A controlled risk's controls fail | **Review** → untick **Controls are in place and working** and describe what will be done. The risk re-opens. |
| The process behind a risk no longer exists | **Close** (Full) → give the reason. |
| An inspector asks for the register | **Print register**. |

### Add the suggested risks

Click **Suggested risks**. Hendrix offers 12 manufacturing risks (or 10 cultivation risks on a cultivation license). Risks already on the register by the same title are greyed out. Enter **Owner for these risks** and click **Add selected**. High and critical suggestions get an immediate action ("Review the controls with the team" unless one is suggested) and a target date 90 days out.

### Add or edit a risk

1. Click **+ Risk** (or **Edit** on a row).
2. Fill in the form. The rating badge updates as you pick likelihood and severity.
3. Click **Save**.

![New risk form: a critical risk with its immediate action and target date](shots/mgmt_risk_form.png)

| Field | What to enter | Required |
|---|---|---|
| Risk | Short title, e.g. Residual solvent above the limit | Yes |
| Category | Product safety, Quality, Allergens, Product defense (threats), Fraud vulnerability, Materials and suppliers, Site and neighboring land, Facility and equipment, People and training, Regulatory and compliance, Business continuity, Other | Yes (default Product safety) |
| Hazard - what could go wrong | The hazard | Yes |
| Root cause - why it could happen | The cause | Yes |
| Owner | Who owns the risk (you, by default) | Yes |
| Area / process / product | Where it applies | No |
| Found through | Risk assessment, Deviation, Complaint, Audit / inspection, HACCP, Facility test, Supplier, Change, Other, plus a reference such as DEV-2026-004 | No |
| Likelihood | 1 Rare to 5 Almost certain | Yes (default 3) |
| Severity | 1 Negligible to 5 Severe (serious harm, license at risk) | Yes (default 3) |
| Existing controls | Controls in place today | No |
| Immediate action | What is done now | Yes, if the score is 10 or more |
| Permanent action (planned) | The permanent fix | No |
| Permanent fix by | Target date | Yes, if the score is 10 or more |
| Review every | Month, 3 months, 6 months, Year, 2 years. Set for you from the rating (critical 3 months, high 6 months, others a year) until you change it | Yes |
| CAPA | Link an open CAPA | No |
| Files (assessment, photos, test results) | Upload | No |
| Notes | Anything else | No |

> **Hendrix checks:** "Enter the risk, the hazard, its root cause and the owner." An open risk scoring 10 or more is blocked without both: "A high or critical risk (score 16) needs an immediate action and a target date for the permanent fix." Risks are numbered **RK-001, RK-002…** per license. The **next review** date is always the last review date plus "Review every"; editing a risk does not move the last review date. Risks are never deleted.

### Mark a risk controlled

Click **Controlled** on an open risk.

![Controlled and verified: the permanent action, its verification and the residual rating](shots/mgmt_risk_controlled.png)

| Field | What to enter | Required |
|---|---|---|
| Permanent action taken | What was done | Yes |
| Verification - how you know it works | e.g. 3 batches tested ND after the new purge | Yes |
| Verified by | Who verified it | Yes |
| Verified on | Date (not in the future) | Yes |
| Likelihood / Severity (residual rating) | The rating with the permanent controls in place | Yes |

> **Hendrix checks:** "Record how the permanent action was verified, by whom and when." A residual rating is required. Once controlled, the verification cannot be changed: "The verification is recorded. Re-open the risk to change it." **Re-open** (Edit) puts a controlled risk back to Open.

### Review a risk

Click **Review** on any risk that is not closed.

![Risk review: rating today, controls working, notes](shots/mgmt_risk_review.png)

| Field | What to enter | Required |
|---|---|---|
| Reviewed on | Date (not in the future) | Yes |
| Reviewed by | Who reviewed it | Yes |
| Likelihood / Severity | The rating today | Yes |
| Controls are in place and working | Tick if they work | — |
| Notes | What was looked at; if the controls do not work, what will be done | Yes, if the controls do not work |

> **Hendrix checks:** "The controls are not effective: describe what will be done." Each review is kept and cannot be changed or deleted. A review moves the next review date. On an open risk it updates the rating; on a controlled risk it updates the residual rating, and if the controls are not working the risk **goes back to Open**.

### Close a risk

Click **Close** (Full), enter **Why the risk no longer applies** and click **Close risk**. The risk leaves the live list (choose the "Closed" filter to see it).

> **Hendrix checks:** "Only Full access can close a risk." A reason is required. A closed risk cannot be changed (except its files and notes), and cannot be reviewed.

### Tips
- The Dashboard **Risk and change** card shows high or critical risks and overdue reviews first.
- Start from the suggested risks, but change every rating and control to fit your facility before an inspector sees it.
- The Verification Schedule picks up the date of your latest risk review automatically.

## Change Control

Change control makes sure every change to a product, process, piece of equipment, material, supplier, SOP or the team is assessed, approved, prepared for (training, trial run, HACCP review, notifications) and checked afterwards. Inspectors look for it under CSQ 5.1.5 and 5.4.1, and for HACCP revalidation after significant changes.

**Where:** left menu → Change Control. **Who:** View can see and print changes. Edit can request changes, edit them while requested, and record the work. Full can also approve, reject, cancel and close changes.
**CSQ:** 5.1.5, 5.4.1, 4A.10, 4A.11

![Change control: changes in every status, with the next step for each](shots/mgmt_change_list.png)

A change moves **Requested → Approved → Implemented → Closed**. It can also be **Rejected** (while requested) or **Cancelled** (once approved). The counters show changes **Waiting for approval**, **In progress**, **Effectiveness check due** (implemented, not closed; red after 60 days) and **Changes (12 months)**. The **Next step** column tells you what is needed; for an approved change it lists exactly what still blocks it.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You want to add a new gummy flavor | **+ Change** → Type: New or changed product / formulation. A trial run is ticked for you. |
| New silicone molds will replace the starch trays | **+ Change** → Type: Equipment; tick the impacts (HACCP, training, equipment). |
| An SOP needs a new step | **+ Change** → Type: Document / SOP; tick SOPs and records and pick the SOP. |
| A requested change is ready for sign-off | **Approve** (Full) → review the summary → add a note → **Approve**. |
| A change is not acceptable | **Reject** (Full) with a reason. |
| The team is putting an approved change in place | **Work** → tick actions done, training, trial result, HACCP review, notification date → **Save progress**. |
| Everything is done | **Work** → **Mark implemented**. |
| A month after the change, you check it worked | **Close** (Full) → describe the effectiveness check. |

### Request a change

1. Click **+ Change**.
2. Fill in the change, the impact assessment and the plan.
3. Click **Request change**.

![Request a change: impact assessment, trial run, who must be told and the action plan](shots/mgmt_change_form.png)

| Field | What to enter | Required |
|---|---|---|
| Change | Short title | Yes |
| Type | New or changed product / formulation, Process, Equipment, Facility / layout, Material, ingredient or supplier, People / organization, Document / SOP, Regulatory / license, IT / system, Other | Yes (default Process) |
| What changes | Description | Yes |
| Why | The reason | Yes |
| Product(s) | Products affected | No |
| Requested by | You, by default | No |
| Requested on | Date (not in the future) | Yes (default today) |
| Wanted by | Target date | No |
| Impact assessment | Tick everything affected: HACCP plan / flow diagram, Allergens, Labels and packaging, Product specs / formulation, SOPs and records, Training, Equipment (validation / calibration), Suppliers and materials, Testing, Facility, sanitation, pest control, License / regulator, Customers, METRC / track and trace, or "Nothing else is affected" | Yes, at least one tick |
| How it affects them | Notes | No |
| Risk of the change | Low, Medium, High | Yes (default Medium) |
| Risk register | Link a risk that is not closed | No |
| SOPs to update / HACCP plans affected / Training courses | Shown when SOPs, HACCP or Training is ticked; pick the records | No |
| Training needed before the change is used | Tick, and say who is trained on what | No |
| Trial run needed to prove it (CSQ 5.4.1) | Tick, and say what the trial must show | No |
| Who must be told | State regulator, CSQ certification body, Customers / dispensaries, Staff affected | No |
| Plan - actions to put the change in place | Each action with who and a due date (**+ Action**) | Needed before it can be implemented |
| Files | Upload | No |

Some boxes tick themselves: ticking the **Training** impact ticks "Training needed"; **License / regulator** ticks "State regulator"; **Customers** ticks "Customers / dispensaries"; choosing the type **New or changed product / formulation** ticks the trial run. Ticking "Nothing else is affected" clears the other impacts.

> **Hendrix checks:** "Enter the change, what changes and why." "Complete the impact assessment (tick what the change affects, or "Nothing else is affected")." Changes are numbered **CC-2026-001, CC-2026-002…** per license and year. **Edit** is only offered while the change is requested.

### Approve, reject or cancel

Click **Approve** (Full) on a requested change. The approval screen summarizes the change, what it affects, what must happen **Before use** and the plan. Add an **Approval note** (optional) and click **Approve**.

![Approve a change: the summary and the approval note](shots/mgmt_change_approve.png)

**Reject** (requested) and **Cancel** (approved) ask for a reason.

> **Hendrix checks:** "Only Full access (a qualified person) can approve a change." Hendrix records who approved it and when. After approval, what the change is cannot be rewritten: "The change was approved as written. Cancel it and request a new change to change what it is." The training and trial requirements are also fixed at approval. Only a requested change can be rejected, an implemented change cannot be cancelled, and both need a reason.

### Put the change in place

Click **Work** on an approved change.

![Work on an approved change: actions, training, HACCP review, notification, and what still blocks it](shots/mgmt_change_work.png)

| Field | What to enter | Required |
|---|---|---|
| Actions | Tick each action as done (Hendrix records the date); add or edit actions | All done, to implement |
| Training given before use | Tick when done (only if training is needed) | Yes, to implement, if needed |
| Trial run | Not run yet, Passed, Failed (only if a trial is needed) | Passed, to implement, if needed |
| Trial result / batch | Reference | No |
| HACCP plan reviewed and revalidated for this change | Tick (only if HACCP is affected) | Yes, to implement, if HACCP is affected |
| Told on | Date the regulator, certification body or customers were told (only if they must be told) | Yes, to implement, if needed |
| Who was told / reference | Name or reference | No |
| Files (evidence) | Upload | No |
| Implemented on | Date (not in the future; default today) | Yes |

Click **Save progress** to keep your work, or **Mark implemented** when the list under "Before it can be implemented" is empty.

> **Hendrix checks:** **Mark implemented** stays greyed out while anything blocks it, and even if you try another way Hendrix will not let you implement it: "List the actions that put the change in place." "2 action(s) are not done yet." "Training must be given before the change is used." "A trial run must pass before the change is implemented." "HACCP is affected: review (and revalidate) the HACCP plan before the change is implemented." "Record when the regulator / certification body / customers were told." After implementation the actions are on record and cannot be changed.

### Close a change

Click **Close** (Full) on an implemented change, answer **Did the change work as planned? What was checked**, and click **Close change**.

> **Hendrix checks:** "Record the effectiveness check (did the change work as planned?)." Closed, rejected and cancelled changes cannot be changed (except files and notes). Change records are never deleted. **Print** on any row gives the full change record.

### Tips
- Request the change before you change anything on the floor; the approval date is your evidence the change was reviewed first.
- If a change affects HACCP, revise the plan in HACCP, then tick the HACCP review here.

## Org Chart

The org chart shows every position, who holds it, who it reports to, their responsibilities, their backup and the safety, quality and CSQ roles they hold. Inspectors use it for CSQ 5.1.1 and to check that senior management, a quality lead and a quality backup are named.

**Where:** left menu → Org Chart. **Who:** View can see and print the chart. Edit can add and edit positions. Full can also remove positions.
**CSQ:** 5.1.1

![Org chart: counters, the drawn chart and the safety, quality and CSQ roles](shots/mgmt_org_chart.png)

The counters show **Positions** (and how many are vacant), **With responsibilities** and **Key CSQ roles** (Senior management, Quality / CSQ lead and Quality backup, each held by a named person). Hendrix draws the chart; boxes with a gold border hold a safety or quality role, and vacant positions show "Vacant" in red. Below the chart, **Safety, quality and CSQ roles** lists who holds each role and flags a missing key role as **Not assigned**. The table lists every position under its manager.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You are drawing the chart for the first time | **+ Position** for the owner or general manager, then **+ Under** on each row to add who reports to them. |
| A new QA technician is hired | **Edit** on the QA Technician position → enter the person. |
| A position is open | Leave **Person** blank; it shows as Vacant. |
| The quality backup is not named | **Edit** the right position → tick **Quality backup**. |
| A manager now reports to someone else | **Edit** → change **Reports to**. |
| A position is no longer needed | Move anyone who reports to it first, then **Remove** (Full). |
| An inspector asks for the org chart | **Print org chart**. |

### Add or edit a position

1. Click **+ Position**, **+ Under** on a row (pre-selects the manager), or **Edit**.
2. Fill in the form and click **Save**.

![Position form: reports to, backup, responsibilities and the safety, quality and CSQ roles](shots/mgmt_org_position.png)

| Field | What to enter | Required |
|---|---|---|
| Position | e.g. Quality Manager | Yes |
| Person | Who holds it (suggests Hendrix users); leave blank if vacant | No |
| Department | e.g. Quality | No |
| Reports to | Another position, or "(top of the chart)" | No |
| Backup | Who covers the position | No |
| Order | Sort order among positions with the same manager | No |
| Functions and responsibilities | What the position is responsible for, including safety, quality and CSQ duties | No (counted on the page) |
| Safety, quality and CSQ roles | Tick any of: Senior management, Quality / CSQ lead, Quality backup, HACCP team leader, Food safety / product defense, Recall coordinator, Regulatory contact (state / METRC), Training coordinator, Internal auditor, Sanitation lead, Maintenance / calibration | No |

> **Hendrix checks:** "Reports to" never offers the position itself or anyone below it, and Hendrix will not let you create a loop: "That reporting line would loop back to this position." **Remove** (Full, after a confirmation) is blocked while people report to the position: "People report to this position. Move them to another position first." Every add, change of person, change of reporting line and removal is in the Audit Trail.

### Tips
- **Print org chart** prints the drawing and a table of every position with its responsibilities, roles and backup.

## Quality Objectives

This page links your quality policy and tracks measurable quality objectives (KPIs) with targets, owners and a result for every month or quarter. Most KPIs are counted straight from Hendrix records. Inspectors use it for CSQ 1.2, 5.1.2 and 5.1.4.

**Where:** left menu → Quality Objectives. **Who:** View can see the board and print it. Edit can add and edit objectives and record results. Full can also link the quality policy and mark objectives achieved or dropped.
**CSQ:** 1.2, 5.1.2, 5.1.4

![Quality objectives: the linked policy SOP, counters and a card per objective with a 6-period chart](shots/mgmt_objectives_board.png)

At the top is the **Quality policy** (a linked SOP, with its status). The counters show **Active objectives**, **On target** and **Off target** (by the latest result) and **Results due** (objectives with no result for last month or last quarter). Each card shows the latest value, the target, a bar chart of the last 6 periods (green met, red missed, dashed line at the target), the owner, and the action recorded for a missed target.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You are setting objectives for the first time | **Suggested objectives** → set targets → enter the owner → **Add selected**. |
| The quality policy SOP is published | **Link the policy SOP** (Full) → pick the SOP → say how it is shared. |
| A new month starts | Click **Record <last month>** on each card that is due. Hendrix counts the value for you. |
| A KPI missed its target | Record the result and fill in **Action to get back on target**. |
| You track something Hendrix cannot count (e.g. on-time delivery) | **+ Objective** → Measured by: Entered by hand. |
| A result was entered wrong | **Record result** → pick the period → change the value → **Correct result**. |
| An objective was reached | **Achieved** (Full) → say what was achieved. |
| An objective no longer makes sense | **Drop** (Full) → say why. |
| You share the KPIs with staff | **Print KPI board**. |

### Link the quality policy

Write the safety, quality and compliance policy as an SOP (signed by senior management and everyone it applies to), then click **Link the policy SOP** (or **Change**).

| Field | What to enter | Required |
|---|---|---|
| Policy SOP | An SOP used at this license | No |
| How it is shared with staff | e.g. posted in the break room, signed by all staff, reviewed every year | No |

> **Hendrix checks:** "Only Full access can set the quality policy." "That SOP is not used at this license." Signatures for each version of the policy come from the SOP records.

### Add an objective

Click **+ Objective** (or **Suggested objectives** when you have none yet). The suggested set has 8 objectives, each counted from Hendrix: CAPAs closed on time, Deviations per month, Complaints per quarter, Batches line cleared before production, CCP checks within critical limits, Batch tests passed first time, Facility tests passed, Risk reviews on time. You only see suggestions for modules you can view.

![New quality objective counted from Hendrix line clearance records](shots/mgmt_objectives_form.png)

| Field | What to enter | Required |
|---|---|---|
| Objective | e.g. CAPAs closed on time | Yes |
| Category | Food safety, Quality, Compliance, Customers, People and training, Efficiency | Yes (default Quality) |
| Measured by | Entered by hand, or counted from Hendrix: CAPAs closed on time, Deviations recorded, Complaints received, Batches with a line clearance, CCP checks within limits, Batch tests passed, Facility tests passed, Risk reviews on time (today). Picking a counted measure sets the unit and direction | Yes |
| Target | A number | Yes |
| Unit | %, count, days… | No |
| Good is | At or above target, or At or below target | Yes |
| How often | Monthly or Quarterly | Yes |
| Owner | Who owns it (you, by default) | Yes |
| From | Start date | Yes (default today) |
| Reach by | Due date (not before the start) | No |
| Why it matters (link to the quality policy) | Link to the policy | No |
| Plan to reach it | The plan | No |

> **Hendrix checks:** "Enter the objective, a number for the target and the owner." "Every objective needs an owner." "The due date is before the start." Objectives are numbered **OBJ-001…** per license. A change of target, direction or measure is recorded in the Audit Trail as "Objective target changed". Objectives are never deleted.

### Record a result

Click **Record <period>** (when due) or **Record result** on a card.

![Recording September's result: counted from the CAPA records, target missed, action required](shots/mgmt_objectives_result.png)

| Field | What to enter | Required |
|---|---|---|
| Period | One of the last 12 months or 6 quarters (default: last month or last quarter); "(recorded)" marks periods that already have a result | Yes |
| Value | The value. For counted measures Hendrix fills it in; **Get from Hendrix** counts it again and shows how (e.g. "3 of 4 CAPAs closed on time") | Yes |
| Comment | Filled with the count detail for counted measures | No |
| Action to get back on target | What will be done | Yes, if the target was missed |

> **Hendrix checks:** Hendrix decides whether the target was met, from the value, the target and "Good is". "The target was missed: record the action that will be taken." There is one result per objective per period; recording again for the same period corrects it (the button reads **Correct result**). A monthly objective only takes monthly periods and a quarterly one only quarters. Results are marked as counted by Hendrix when you keep the counted value. Results are never deleted.

### Mark achieved or drop

Click **Achieved** or **Drop** (Full), enter what was achieved or why it is dropped, and confirm. The objective leaves the board; click **Show achieved and dropped** to see it again.

> **Hendrix checks:** "Only Full access can mark an objective achieved or dropped." A note is required. Once achieved or dropped, the objective cannot be changed or given new results.

### Tips
- The Dashboard **Quality objectives** card shows how many objectives are on target and how many results are due.
- The management review fills its KPI input from this page.

## Management Review

Senior management reviews the whole quality system at least once a year. Hendrix fills in the facts for each input from your records, you record the discussion, decisions and actions, Full access signs it as held, and you track the actions and who the minutes were shared with. This is the evidence for CSQ 5.1.3.

**Where:** left menu → Management Review. **Who:** View can see and print reviews. Edit can prepare reviews, save drafts and update actions and sharing after signing. Full can also sign a review as held and cancel drafts.
**CSQ:** 5.1.3, 1.2

![Management review list: last review, next review due, open actions and minutes shared](shots/mgmt_review_list.png)

The counters show the **Last review** (red if more than a year ago or never), **Next review due** (red when overdue), **Open actions** from signed reviews and whether the last review's **Minutes shared**. Each row shows the period, chair, status (Draft, Held · signed, Cancelled), actions done out of total, and when the minutes were shared.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| The yearly management review meeting is coming up | **+ Management review** → check the period → Hendrix fills the facts → **Save draft** to prepare. |
| You are in the meeting | **Continue** on the draft → type the discussion for each input, the decisions and the actions. |
| The meeting is over | **Sign as held** (Full). |
| An action from the review is done | **Follow-up** → tick it. |
| The minutes are sent to the managers | **Follow-up** → enter who and when. |
| A draft review will not take place | **Cancel** (Full) with a reason. |
| An inspector asks for the minutes | **Print**. |

### Prepare and sign a management review

1. Click **+ Management review**. Hendrix fills in the facts for the period at once.
2. Check **Period from** and **Period to** (by default from the day after the last review's period to today) and click **Fill from Hendrix** again if you change them.
3. Enter the chair and attendees.
4. For each input, check the facts (left box) and type the discussion and conclusions (right box). Inputs marked * are required.
5. Enter the decisions, resource needs and actions, and set the next review date.
6. Click **Save draft**, or (Full) **Sign as held**.

![New management review: facts filled from Hendrix records, discussion for each input, decisions and actions](shots/mgmt_review_form.png)

| Field | What to enter | Required |
|---|---|---|
| Meeting date | Date of the meeting (not in the future) | Yes |
| Period from / Period to | The period reviewed | No |
| Chair (senior management) | You, by default | Yes, to sign |
| Attendees | Names and roles | Yes, to sign |
| Actions from the last review * | Facts: open and done actions from the last signed review. Discussion | Discussion required to sign |
| Complaints and customer feedback * | Facts: complaints by category, closed, open today | Discussion required to sign |
| Internal, external and regulatory audits * | Facts: audits in the period, open findings and overdue ones | Discussion required to sign |
| Deviations and corrective actions (CAPA) * | Facts: deviations by category, critical ones, CAPAs closed, verified effective, open, overdue | Discussion required to sign |
| Risks and opportunities * | Facts: risks on the register, high / critical, controlled, reviews overdue, new | Discussion required to sign |
| HACCP and food safety performance | Facts: active plans, CCP checks, out of limits, verified | No |
| Quality objectives and KPIs | Facts: on target, off target, not measured | No |
| CSQ conformance * | Facts: the CSQ self-assessment counts | Discussion required to sign |
| Changes that could affect the system * | Facts: changes requested, implemented, open, stopped | Discussion required to sign |
| Supplier performance | Facts: suppliers by status, reviews overdue | No |
| Verification results | Facts: scheduled verifications, overdue, recorded, with issues | No |
| Training and competence | Type the facts and discussion | No |
| Resources (people, equipment, facility, budget) * | Type the facts and discussion | Discussion required to sign |
| Decisions and conclusions (is the system suitable, adequate and effective?) | The conclusions | Yes, to sign |
| Resource needs | Resources decided | No |
| Actions | Each action with who and due date (**+ Action**) | No |
| Next review (within 12 months) | Default one year from today | Yes, to sign |
| Files (agenda, sign-in sheet, slides) | Upload | No |

The facts are only counted for modules you can view. You can edit or add to any fact before signing.

> **Hendrix checks:** "Only Full access (senior management) can sign the management review." Hendrix will not sign until: the chair and attendees are entered ("Enter the chair and who attended."); every required input has a discussion ("Discuss every required input before signing: …"); the decisions are recorded ("Record the decisions and conclusions."); the meeting date is not in the future; and the next review is after the meeting and within 12 months ("Set the next review within 12 months of this one."). Hendrix records who signed and when. Reviews are numbered **MR-2026-001…** per license and year.

### Follow up after the review

Click **Follow-up** on a signed review. Tick actions as they are done (Hendrix records the date), and enter **Minutes shared with** and **Shared on** (not in the future). Click **Save**.

![Follow-up: tick actions done and record who the minutes were shared with](shots/mgmt_review_followup.png)

> **Hendrix checks:** "The minutes are signed. Only actions, sharing and files can be updated." "Actions decided in the review cannot be added or removed after it is signed." A held review cannot be cancelled or re-opened. Only a draft can be cancelled, by Full access with a reason. Reviews are never deleted.

### Tips
- The Dashboard **Review and verification** card turns red when there is no management review, when the next review is overdue, or when verifications are overdue.
- The next review's "Actions from the last review" is filled from this review's actions, so keep the follow-up current.

## Verification Schedule

The verification schedule lists every verification activity: what is verified, how, by whom, how often and where it is recorded. For most activities Hendrix takes the last date straight from the linked records, so overdue verifications show up on their own. This is the evidence for CSQ 5.1.8.

**Where:** left menu → Verification Schedule. **Who:** View can see the schedule, the history and print it. Edit can add and edit activities, add the suggested schedule and record verifications. Full can also turn activities off and on and void records.
**CSQ:** 5.1.8, 4A.11

![Verification schedule: last done from linked records, next due, overdue flags](shots/mgmt_verification_schedule.png)

The counters show **Scheduled activities** (and how many are linked to Hendrix records), **Overdue or never done**, **Due in 7 days** and **Recorded here (12 months)** (and how many had issues). For each activity, **Last done** is the latest of the linked records and the verifications recorded here; "from …" shows it came from a linked record. **Next due** is the last date plus the frequency: green, amber within 7 days, red "Overdue <date>", or "Due now" if it was never done.

### When to use it

| Situation | What you do in Hendrix |
|---|---|
| You are setting up the schedule | **Suggested schedule** → untick what does not apply → enter who does them → **Add selected**. |
| The supervisor signs the sanitation log | Nothing here: the date comes from the Sanitation log. |
| QA checks labels against the batch COA | **Record** on "Labels checked against the batch". |
| The check finds a problem | **Record** → Result: Issues found → findings and action taken. Then **History** → **Deviation**. |
| You add your own verification (e.g. scale daily check review) | **+ Activity**. |
| An activity no longer applies | **Turn off** (Full). |
| An inspector asks for the verification procedure | **Print schedule**. |

### Add the suggested schedule

Click **Suggested schedule** (shown while the schedule is empty). It offers 13 activities: sanitation records reviewed (7 days), CCP monitoring records reviewed (7 days), HACCP plan verification (90 days), scale and equipment calibration (30 days), line clearance verified (30 days), facility air and water tests reviewed (365 days), risk register review (90 days), KPI review (90 days), internal audit (365 days), management review (365 days), supplier performance review (365 days), labels checked against the batch (30 days, recorded here) and pest control service reports reviewed (30 days, recorded here). Activities linked to modules you cannot view are left out. Enter **Who does them** and click **Add selected**; change the person on each activity later.

### Add or edit an activity

Click **+ Activity** or **Edit**.

| Field | What to enter | Required |
|---|---|---|
| What is verified | e.g. CCP monitoring records reviewed | Yes |
| How | The method | No |
| Who | Who does it (you, by default) | Yes |
| Every (days) | Frequency in days (1 to 1095) | Yes (default 30) |
| Last date comes from | Recorded here, or a linked record: Sanitation log signed by a verifier, CCP records verified (HACCP), HACCP verification / reanalysis, Calibrations (Equipment), Internal audits, Facility tests, Line clearances verified by a supervisor, Risk reviews, KPI results, Management review, Supplier reviews | Yes (default Recorded here) |
| Recorded where | Where the record is kept | No |
| CSQ clause | e.g. 4A.8 | No |

> **Hendrix checks:** "Enter the activity and who does it." Activities are numbered **VS-001…** per license. They are never deleted: "Turn the activity off instead." Only Full access can turn an activity off.

### Record a verification

Click **Record** on the activity (it is highlighted when overdue).

![Recording a label check with issues found and the action taken](shots/mgmt_verification_record.png)

| Field | What to enter | Required |
|---|---|---|
| Date | The date it was done (not in the future) | Yes (default today) |
| By | Who did it | Yes |
| Result | No issues, or Issues found | Yes |
| Findings | What was found | Yes, if issues were found |
| Action taken | What was done | Yes, if issues were found |
| Files | Upload | No |

> **Hendrix checks:** "Describe the issues found and the action taken." "The date cannot be in the future." A record cannot be changed afterwards: void it and record it again. Only Full access can void, with a reason. Recording moves the activity's next due date.

### See the history

Click **History** on an activity to see every verification recorded here (and the latest date from the linked records). On a record with issues, click **Deviation** to raise a linked deviation. **Void** (Full) crosses a record out with a reason.

![History of an activity, with Deviation on the records that found issues](shots/mgmt_verification_history.png)

### Tips
- Most activities need no typing here at all: keep the linked logs and records current and the schedule keeps itself.
- The management review fills its "Verification results" input from this schedule.
