# Setting up and running Hendrix

## Dashboard
The Dashboard is your home page. It shows the state and license you are working in and one card per module, so you can see at a glance what needs attention. Inspectors care because it shows the company runs one controlled system per license.

**Where:** left menu → Dashboard (always shown). **Who:** everyone who is approved. Each person sees only the cards and menu items for the modules they have access to. Only a system admin sees **Team and Access** and **Roles** in the menu.
**CSQ:** 1.1 (one documented safety and quality system)

![The Dashboard for Black Fox (MAN000109), Missouri, signed in as a system admin](shots/found_dashboard.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You are new and need an account | Sign-in screen → **Create an account**, then wait for an admin to approve you |
| You created an account but cannot get in | The screen says **Waiting for approval**. Ask an admin, then click **Check again** |
| You start your shift | Sign in, check that the **State** and **License** at the top are correct, and read the cards |
| You work at a second license | Change the **License** at the top. Every page then shows that license's records |
| A card is red (for example "1 need attention") | Click the link on the card (for example **Open equipment**) |
| You finish for the day or leave a shared computer | Click **Sign out** (top right) |
| Hendrix is brand new and empty | The Dashboard says **Step 1: create your first state**. An admin clicks **Set up States and Licenses** |

### Create an account
1. Open Hendrix. On the sign-in screen, click **Create an account**.
2. Fill in the fields and click **Create account**.
3. Hendrix shows **Waiting for approval**. An admin must approve you on **Team and Access** before you can enter.
4. When the admin tells you that you are approved, click **Check again** (or sign in again).

![Creating an account](shots/found_signin_create.png)

| Field | What to enter | Required |
|---|---|---|
| Full name | Your first and last name, as it should appear on records and signatures | Yes |
| Email | Your work email. You sign in with it | Yes |
| Password | At least 8 characters | Yes |

> **Hendrix checks:** "Enter your name." if the name is blank. "Password must be at least 8 characters." if the password is too short. A new account cannot open any page until an admin approves it.

![A new account waits for approval](shots/found_signin_pending.png)

### Sign in
1. Enter your **Email** and **Password**.
2. Click **Sign in** (or press Enter).

![The sign-in screen](shots/found_signin_login.png)

| Field | What to enter | Required |
|---|---|---|
| Email | The email you signed up with | Yes |
| Password | Your password | Yes |

The small link **Change database connection** is only for the person who installs Hendrix. It asks for the database address and key. Do not use it unless your admin tells you to.

### Choose the State and License (top bar)
1. At the top of every page, pick the **State**. Hendrix then picks the first license in that state.
2. Pick the **License**. The list shows each license as "Name (license number)".
3. Hendrix remembers your choice on this computer.

Everything you record belongs to the license chosen at the top. Your name and the **Sign out** button are at the top right.

> **Hendrix checks:** The License list only shows active licenses in the chosen state that you are allowed to work in. If an admin limited you to some licenses, the others never appear. A record always carries both a state and a license, and the license must belong to that state. Hendrix will not let you save a record to a license in another state, or move a record to another state or license later.

### Read the Dashboard cards
The first row always shows:

| Card | What it tells you |
|---|---|
| Regulatory agency | The state's regulator and governing code, from States and Licenses |
| Active license | The license name, type and number, and how many licenses the state has |
| State rulebook | How many rules the state's Rulebook holds, with **Open rulebook** |

After that, a card appears for each module you can open, for example **Deviations & CAPA**, **Complaints**, **Internal audits**, **Training** (or **My training**), **SOPs**, **Suppliers**, **Receiving and holds**, **Equipment**, **Line clearance**, **Facility tests**, **Cultivation**, **HACCP**, **Risk and change**, **Quality objectives**, **Review and verification**, **Time clock**, **Production plans**, **Chemicals and SDS**, **Mock recall** and **Quality standard**. Each card shows a headline number, a short line of detail and a link to the module. Red text means something is overdue, missing or failed. Green means all clear.

The **Quality standard** card shows the CSQ standard the license follows, its target level, the adoption status, a progress bar and how many clauses are still open. It says **Not adopted** until someone adopts the standard on **Standards (CSQ)**.

![The Dashboard for a team member: fewer menu items and cards](shots/found_member_dashboard.png)

### Tips
- If a menu item you need is missing, you do not have access to it. Ask a system admin.
- Check the license at the top before you record anything. Records cannot be moved to another license later.

## States and Licenses
This is where the company's states and licenses are set up. Every record in Hendrix belongs to one license, and every license belongs to one state, so an inspector sees only the records of the license being inspected.

**Where:** left menu → States and Licenses. **Who:** everyone can view the page. Only a system admin can add, change, deactivate or delete states and licenses (other people see "View only. Only an admin can add or change states and licenses.").
**CSQ:** 1.3 (regulatory compliance), 3A.1.2 (cultivation sites)

![States and Licenses: Missouri with three licenses, Michigan with one](shots/found_locations_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Hendrix is new | **+ Add state**, then **+ Add license** under that state |
| The company gets a new license | Under the right state, **+ Add license** |
| The regulator or tracking system changes | **Edit** on the state |
| A license number or type changes | **Edit** on the license row |
| A license stops operating | **Deactivate** on the license row. It disappears from the License list at the top, but its records stay |
| A license starts operating again | **Activate** |
| A license was added by mistake | **Delete** on the license row (you confirm first) |
| You need a state's rules | **Open <state> rulebook** at the bottom of the state card |

### Add or edit a state
1. Click **+ Add state** (or **Edit** on a state card).
2. Fill in the form and click **Save**.

![The state form](shots/found_locations_state.png)

| Field | What to enter | Required |
|---|---|---|
| State name | For example Missouri | Yes (Save stays greyed out until it is filled) |
| Regulatory agency | For example Division of Cannabis Regulation (DCR) | No |
| Governing code / act | For example 19 CSR 100-1 | No |
| Track-and-trace system | Default METRC. Used in batch record labels, for example "Recorded on METRC?" | No (blank becomes METRC) |

> **Hendrix checks:** You cannot delete a state that still has licenses ("Delete or move this state's licenses first."). Deleting a state asks you to confirm, because its rulebook goes with it.

### Add or edit a license
1. Under the state, click **+ Add license** (or **Edit** on a license row).
2. Fill in the form and click **Save**.

![The license form, with the operation that decides which CSQ standards apply](shots/found_locations_license.png)

| Field | What to enter | Required |
|---|---|---|
| License / facility name | For example Black Fox | Yes |
| License number | For example MAN000109 or CUL000412 | No |
| License type | For example Manufacturer, Processor, Cultivation | No |
| Operation (decides which CSQ standards apply) | **Automatic** (Hendrix guesses from the number and type), **Manufacturing (processing, extraction, infusion)**, **Cultivation (CUL)** or **Other (dispensary, lab, transport...)** | No (Automatic by default) |

The line under **Operation** tells you what follows from your choice:
- Manufacturing → CSQ Standard for Manufacturing (3C) and CSQ Standard for Extraction (3B).
- Cultivation → CSQ Standard for Cultivation (Module 3A).
- Other → no CSQ standard.

The **CSQ** column in the licenses table shows the result for each license.

> **Hendrix checks:** When Operation is Automatic, a license number starting with CUL, or a type with "cultivation", "grow" or "nursery", makes it Cultivation. A number starting with MAN, or a type with "manufacturer", "processor", "extraction" or "infusion", makes it Manufacturing. Anything else is Other. If you change a license's operation later, the CSQ standards it follows change with it.

### Tips
- Set the operation correctly before you adopt the CSQ standard. A cultivation license can only follow the Cultivation standard, and a manufacturing license only Manufacturing and Extraction.
- Deactivate rather than delete a license that has records.

## Rulebook
The Rulebook holds one state's cannabis rules, for example Missouri 19 CSR 100. You can load the official rules PDF and Hendrix splits it into rules and sorts them by category. Inspectors care because it shows staff can find and follow the current state rules.

**Where:** left menu → <State> Rulebook (for example **Missouri Rulebook**). **Who:** View can read and search the rules. Edit can upload a rules PDF, add rules and edit them. Full can also delete rules and remove rules from an earlier PDF.
**CSQ:** 1.1 (local regulations kept in the system), 1.3 (regulatory compliance)

![The Missouri Rulebook after importing the official PDF](shots/found_rulebook_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You set up a new state | **Upload rules PDF** with the official rules PDF from the state website |
| The state publishes amended rules | **Upload rules PDF** with the new PDF. Hendrix shows what is new, changed and the same |
| A rule was repealed | Upload the new PDF and tick **Delete the N rules from an earlier PDF** (Full) |
| You need to add a company rule or a single rule | **+ Add rule** |
| A title or category is wrong | **Edit** on the rule |
| You need a rule during an inspection | Type in **Search <state> rules...** |
| You need the original PDF | **Open PDF** next to it under **Source PDFs** |

Each state has its own Rulebook. Switching the state at the top loads that state's rules. Rules can never be moved between states.

### Upload the official rules PDF
1. Click **Upload rules PDF** and choose the PDF.
2. Hendrix reads every page. A review window opens with the file name, the number of pages, the rule format it found (for example "Missouri Code of State Regulations (CSR)") and the number of rules found.
3. Check each row. Use the filter buttons **All**, **New**, **Changed**, **Same** and **To import**, or click a category badge to see one category.
4. Change a title or category if needed. Click **Text** to read the rule text as it came from the PDF.
5. If you want each numbered section (1), (2)... as its own rule, tick **Split each rule into its numbered sections (1), (2)...**.
6. If you want the AI to choose the categories, click **Sort categories with AI**.
7. Click **Import N rules**. Hendrix shows "Imported from <file>: N new, N updated." and lists the PDF under **Source PDFs**.

![Reviewing the rules found in the Missouri PDF before import](shots/found_rulebook_import.png)

| Field (per row) | What to enter | Required |
|---|---|---|
| Tick box | Ticked = import this row. New and changed rules are ticked for you; rules that are the same are not | — |
| Title | The rule title from the PDF. Change it if it was cut short | Yes |
| Category | General, Licensing, Labeling, Packaging, Testing, Facility, Security, Recordkeeping, Training, Inventory / Tracking, Advertising or Other | Yes |

> **Hendrix checks:**
> - Only PDF files are accepted ("Choose a PDF file.").
> - A scanned PDF with no text is refused: "This PDF has no readable text (it looks like a scan or a picture). Download the official text PDF from the state website and upload that one."
> - Hendrix recognizes Missouri CSR numbers, Michigan R numbers, numbered sections and numbered rules. Only when none of these are found does it ask the AI where each rule starts. The rule text itself is always kept word for word.
> - Page headers, footers and page numbers are removed. Two-column pages are read left column first.
> - Rows with very little text are probably table-of-contents lines. They are left unticked.
> - Nothing is saved until you click **Import**. Importing a changed rule replaces its title and text.
> - Rules from an earlier PDF that are not in the new one are kept unless someone with Full access ticks the delete box.
> - Imported rules keep the official order of the PDF. Rules typed by hand follow them.

### Add or edit a rule
1. Click **+ Add rule** (or **Edit** on a rule).
2. Fill in the form and click **Save**.

![Adding a company rule by hand](shots/found_rulebook_add.png)

| Field | What to enter | Required |
|---|---|---|
| Category | Pick from the list or type your own | No (blank becomes Other) |
| Citation (section / rule number) | For example 19 CSR 100-1.100 or Company policy QA-12 | No |
| Title | A short name for the rule | Yes |
| Rule text / what it requires | The rule text | No |

> **Hendrix checks:** Hendrix will not let you add or change rules without Edit access, or delete them without Full access. Every change to a rule is kept in the Audit Trail.

### Tips
- Long rules are shortened on the page. Click **Show all** to read the full text.
- Keep the newest official PDF loaded. The newest one is marked **latest** under Source PDFs.

## Standards (CSQ)
This page holds the CSQ (Cannabis Safety & Quality) standard clause by clause, and records how each license meets each clause. It is the conformance register an auditor works through, with the live Hendrix records behind each clause.

**Where:** left menu → Standards (CSQ). **Who:** View can read the standard and the conformance. Edit can also record and update conformance (status, owner, evidence, files). Full can also add or update the standard, adopt it for a license, set the target level and certification details, and upload the standard PDFs.
**CSQ:** all clauses in scope; in particular 1.1 (documented system covering the CSQ requirements) and 1.4 (documentation and records)

![The Standards page for Black Fox: alerts, adoption and progress](shots/found_standards_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Hendrix has no standard yet | Click **Add CSQ Standards (Manufacturing, Extraction, Cultivation) v2.0** (Full) |
| The license decides to follow CSQ | **Adopt for this license**, pick the standards and the target level (Full) |
| You book the certification audit | **Edit level and certification**, set Status **Audit scheduled** and the audit date |
| You check how you meet a clause | Open the clause → **Record conformance** |
| You fix a gap | Open the clause → **Update conformance** |
| A clause does not apply to you | **Update conformance**, Status **Not applicable**, and write why |
| Hendrix shows "N clauses are missing" | Click **Update the standard** (Full) |
| You have the licensed CSQ PDF | **Upload Manufacturing PDF** (or Extraction / Cultivation) |
| The auditor arrives | **Inspector view**, or **Print register** |

### Add or update the standard
1. When no standard is loaded, the page says **No standard added yet**. Click **Add CSQ Standards (Manufacturing, Extraction, Cultivation) v2.0**. Hendrix adds 130 clauses in its modules, each linked to the Hendrix records that prove it.
2. When Hendrix gets new clauses or new links to records, a message says, for example, "3 clauses are missing." or "Hendrix has new records for N clauses." Click **Update the standard**. Hendrix shows "Updated: N clauses added, N refreshed with the latest Hendrix links." Your statuses and evidence are never changed.

The three CSQ standards share Modules 1, 2A, 4A and 5. Only Module 3 differs: 3A Cultivation, 3B Extraction, 3C Manufacturing. Shared clauses are assessed once.

### Upload the CSQ standard PDFs
1. At the top, click **Upload Manufacturing PDF**, **Upload Extraction PDF** or **Upload Cultivation PDF**. You only see the ones that fit the license's operation.
2. Choose the licensed PDF. Hendrix says "Standard document saved."
3. Click **Manufacturing (PDF)** (and so on) to open it, or **Replace** to load a newer copy.

### Adopt the standard for a license
1. Pick the license at the top.
2. Click **Adopt for this license** (Full).
3. Fill in the form and click **Adopt standard**.

![Adopting CSQ at Level 2 for a manufacturing license](shots/found_standards_adopt.png)

| Field | What to enter | Required |
|---|---|---|
| Standards this license follows | Manufacturing licenses: **CSQ Standard for Extraction (Module 3B)** and/or **CSQ Standard for Manufacturing (Module 3C)**. Cultivation licenses: **CSQ Standard for Cultivation (Module 3A)** only (fixed) | Yes, at least one |
| Target level | **Level 1 - cGMP** (Modules 1, 2A, 3), **Level 2 - cGMP + HACCP** (adds 4A), **Level 3 - cGMP + HACCP + QMS** (adds 5). The audit length shows under the field | Yes (default Level 1) |
| Status | Following, Audit scheduled, Certified, Suspended, Withdrawn | Yes (default Following) |
| Certification body | For example Kiwa ASI | No |
| Audit date | Date of the certification audit | No |
| Certificate number | From the certificate | No |
| Certificate expiry | From the certificate | No |
| Notes | Anything else | No |

> **Hendrix checks:**
> - CSQ only applies to manufacturing and cultivation licenses: "CSQ applies to manufacturing and cultivation licenses. Set this license's operation (States and Licenses) first."
> - "Pick at least one CSQ standard for this license."
> - A cultivation license follows the Cultivation standard only, and the Cultivation standard is only for cultivation licenses.
> - An adoption is never deleted: "A standard cannot be removed from a license. Set its status to Withdrawn instead." A withdrawn adoption counts as not adopted.

### Read the page
- **Operational alerts** list what needs action: facility logs with no entries in the last 12 months, logs whose last entry is older than the limit set in **Settings → Facility logs**, clauses that are not conforming, clauses past their due date, and clauses not assessed yet. Click **Open** to go to the log, or **Show** to filter the clause list.
- The three cards show the standard, the license (operation, standards followed, target level, status, certification details) and **Conformance (Level N scope)**: the percent complete, a bar and the count per status.
- **Audit essentials** lists key audit facts (for example the yearly mock recall in under 2 hours).
- **By module** shows progress per module. Click a module to filter to it.
- Use the search box (**Search clauses, owners, evidence**), the module list, the status list (**Every status**, **Open (still to do)** or one status) and **My target level only** / **All levels** to narrow the list.

Percent complete = (Conforming + Not applicable) ÷ all clauses in the target-level scope.

### Record or update conformance on a clause
1. Click a clause to open it. You see the requirement, the **Live records in Hendrix (last 12 months)** with a green or red dot, the **Proof in Hendrix** buttons, and what Hendrix already holds for it.
2. Click **Record conformance** (or **Update conformance**).
3. Fill in the form and click **Save**.

![An open clause with its live records](shots/found_standards_clause.png)

![Recording conformance for clause 1.4](shots/found_standards_conformance.png)

| Field | What to enter | Required |
|---|---|---|
| Status | Not assessed, Conforming, Partial, Not conforming, Not applicable | Yes |
| Owner | Who is responsible, for example Compliance Officer | No |
| Due date | When the gap must be closed | No |
| SOP / document reference | For example SOP-QA-001 Document Control Rev 3 | No |
| Evidence - how we meet this clause | Where an auditor finds the proof: records, logs, SOPs, training, photos | No (required for Not applicable, then labelled **Justification (why it does not apply)**) |
| Evidence files | **+ Attach file** to add a file (stored privately) | No |

> **Hendrix checks:**
> - "Write why this clause does not apply before marking it Not applicable."
> - You can only record conformance after the license has adopted the standard ("This license has not adopted that standard yet.").
> - You can only record Module 3 clauses that are in the license's scope (for example no Cultivation clauses for a manufacturing license).
> - There is one conformance record per license and clause. It is never deleted. Files already saved on a clause stay attached. Every change goes to the Audit Trail.
> - A due date in the past shows a red **Overdue** badge until the clause is Conforming or Not applicable.

### Show the inspector
1. Click **Inspector view**. The page becomes read only.
2. Every clause opens and shows the requirement, how the facility meets it, the documents, files and live records. Clauses with no record show **Not assessed yet**. Internal alerts and edit buttons are hidden.
3. Click **Exit inspector view** when done. Click **Print register** for a printable conformance register of the target-level scope.

![Inspector view (read only)](shots/found_standards_inspector.png)

### Tips
- Use **Open (still to do)** in the status list as your work list before an audit.
- The green or red dot on a clause is live: it turns red when, for example, the Sanitation Log has not been filled in on time.

## Team and Access
This is where a system admin approves new people, gives them roles, chooses which licenses they work at and sets custom access. Inspectors care because it shows who can see and change which records.

**Where:** left menu → Team and Access. **Who:** system admins only. Other people do not see this page.
**CSQ:** 2A.13.1 (personnel roles and responsibilities), 4A.2 (HACCP team), 5.1.1 (quality system personnel)

![Team and Access with two people waiting for approval](shots/found_team_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new hire created an account | In **N waiting for approval**, click **Approve** |
| Someone changes job | **Manage** → change their roles |
| Someone should only work at one license | **Manage** → untick **All licenses, in every state** and tick their license |
| One person needs more or less access than their role gives | **Manage** → **Custom access** → pick a level for that module |
| Someone leaves the company | **Manage** → untick **Approved** → **Save** |
| Someone needs to run Hendrix | **Manage** → tick **System admin** |

The table shows each person's roles, licenses, access ("From roles", "Custom (N)" or "Full") and status (Approved or Waiting).

### Approve a person or change their access
1. Click **Approve** (new person) or **Manage** (approved person).
2. Fill in the form.
3. Click **Approve** (or **Save**).

![Approving a new team member: roles and licenses](shots/found_team_approve.png)

![Custom access for one person, next to what the roles give](shots/found_team_custom.png)

| Field | What to enter | Required |
|---|---|---|
| Approved | Ticked = can sign in to Hendrix | Ticked when you approve |
| System admin | Ticked = Full access to everything, plus States and Licenses, Team and Roles | No |
| Roles | Tick one or more roles (made on the Roles page). With several roles, the highest access wins | No |
| Licenses this person can work in | **All licenses, in every state**, or untick it and tick each license | Yes (at least one license) |
| Custom access | Per module: **Use role access (…)**, No access, View, Edit or Full. The **Roles:** column shows what the roles give. **Clear custom access** removes all overrides | No |

> **Hendrix checks:**
> - Only a system admin can change approval, roles, licenses or access: "Only a system admin can change roles and access."
> - "You cannot remove your own approval or admin rights." (the boxes are greyed out for yourself).
> - "Hendrix needs at least one system admin. Make someone else an admin first."
> - A person limited to some licenses only sees those licenses at the top, and Hendrix will not show or save their records anywhere else.
> - A person's level for a module is their custom setting if one is set, otherwise the highest level any of their roles gives. A single facility log with no setting of its own follows **Facility Logs (all)**.
> - These rules are enforced by the database, not only on screen.

### Tips
- Give access through roles. Use custom access only for exceptions.
- Unapproving someone does not delete anything they recorded. Their records and their Audit Trail history stay.

## Roles
Roles are access templates, for example Production Lead or Compliance Officer. Each role carries a View, Edit or Full level per module, plus the duties and requirements of the job. Inspectors care because CSQ asks for written roles, responsibilities and requirements.

**Where:** left menu → Roles. **Who:** system admins only.
**CSQ:** 2A.13.1 (personnel roles, duties and requirements), 2A.13.2 (training by role), 1.9 (product defense: controlled access), 5.1.1

![The Roles page with the Black Fox starter roles](shots/found_roles_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Hendrix is new | **Add Black Fox roles** to start from 12 job titles with suggested access |
| A new job title is created | **+ New role** |
| A role is similar to an existing one | **Duplicate** on that role, then change it |
| A role needs more or less access | **Edit** on the role |
| The auditor asks for job requirements | **Edit** → fill **Requirements (CSQ 2A.13.1)**. Cards without it show **Requirements not set** |
| A role is no longer used | **Delete** (Hendrix warns how many people lose the access it gives) |

The starter roles are: General Manager, Assistant of General Manager, Compliance Officer, Security Manager, Security Officer, Sanitation, Team Member, Inventory Manager, Extraction Manager, Production Manager, Sales Manager and Production Lead. Clicking **Add Black Fox roles** again only adds the ones that are missing.

Each card shows the number of people with the role, its duties, its requirements and its access per module.

### Create or edit a role
1. Click **+ New role** (or **Edit** / **Duplicate** on a card).
2. Fill in the form. For a whole group, use **All No access**, **All View**, **All Edit** or **All Full**.
3. Click **Save role**.

![Editing the Sanitation role](shots/found_roles_editor.png)

| Field | What to enter | Required |
|---|---|---|
| Role name | For example Production Lead | Yes |
| Duties and responsibilities | What this role does | No |
| Requirements (CSQ 2A.13.1) | Certifications, education, experience and training needed | No |
| Access per module (General, Production, Facility Logs) | No access, View, Edit or Full. Each module shows what each level allows. Audit Trail is View only. Single facility logs can follow **Same as Facility Logs (all)** | No |

What the levels mean: **View** = see records. **Edit** = create records, continue batches, add and edit. **Full** = change filled-in records with a reason, void, manage lists, delete.

> **Hendrix checks:** "Enter the role name." if it is blank. "A role with that name already exists." Only a system admin can create, change or delete roles. Every change is in the Audit Trail.

### Tips
- Fill in the requirements for every role. The Standards page flags roles that are missing them (clause 2A.13.1).

## Audit Trail
The Audit Trail is the permanent history of every change in Hendrix: who, when, the old value, the new value and the reason. Inspectors use it to check that records were not changed without a reason.

**Where:** left menu → Audit Trail. **Who:** anyone with View on Audit Trail (it has no Edit or Full level). Nobody, including admins, can change or delete it.
**CSQ:** 1.4 (documentation and records), 5.1.5 (change management)

![The Audit Trail for Missouri, last 30 days](shots/found_audit_page.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| An inspector asks who changed a batch record | Pick the area **Batch record**, or search the batch number |
| You need to know why an entry was voided | Look at the **Reason** column of the **Void** row |
| You need a change history for the auditor | Set the period and click **Export CSV** |
| You review changes for one person | Type their name in the search box |
| You need changes from all states | Untick **<State> only** |

### Find a change
1. Use the filters at the top:
   - **Search who, record, reason...**
   - the area list (for example Batch record, Facility log entry, Testing record, Standard conformance, Team and access)
   - the period: Last 24 hours, Last 7 days, Last 30 days (default), Last year, All time
   - **<State> only** (ticked by default; also shows changes that belong to no state, such as roles)
2. Read the table: **When**, **Who**, **Area**, **Record**, **Action** (Created, Changed, Void, Removed), **Changes** (field: old → new) and **Reason**.
3. Click **Export CSV** to download the list shown (with record IDs, state and license IDs).

![Filtered to batch records](shots/found_audit_filtered.png)

> **Hendrix checks:**
> - Every insert, change, void and removal is written by the database itself, with the user and time. It cannot be skipped.
> - "The audit trail cannot be changed or deleted."
> - Changes to log entries and batch records need a reason, and voids need a reason. The reason is stored here.
> - Entries made at a QR kiosk show "QR kiosk (name)" as the person.
> - The page loads the newest 1,000 changes for the filters you chose. Narrow the period to see older ones.

## Settings
Settings are kept per license: the business details and logo printed on records, the time clock break limits, how often each facility log must be filled in, and how often risks are reviewed. They make printouts and overdue flags match how the license really works.

**Where:** left menu → Settings. **Who:** View (and Edit) can see the settings ("View only: Full access on Settings is needed to change them."). Full can change and save them. System admins can always change them.
**CSQ:** supports 1.4 (controlled printouts); the log limits feed the live evidence for the facility log clauses on Standards (CSQ)

![Settings → General: business details, logo and printout header preview](shots/found_settings_general.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new license is set up | **General**: legal name, DBA, address, phone, email, footer, logo |
| The logo changes | **General** → **Replace logo** |
| Break rules change | **Time clock** → change the break minutes |
| Sanitation must be logged every day, not every 2 days | **Facility logs** → Sanitation Log → 1 |
| High risks must be reviewed more often | **Review cycles** → High (10-14) |
| You look for where something else is set | **Everything else** → **Open** on the right card |

The page always manages the license chosen at the top ("Managing Black Fox · MAN000109"). Switch the license at the top to manage another. After changes, click **Save settings** (top right). Hendrix says "Settings saved for <license>."

### General
The **License** card shows the name, number, type, operation and state (these are changed in States and Licenses).

| Field | What to enter | Required |
|---|---|---|
| Legal name | For example Black Fox Manufacturing LLC | No |
| Doing business as (shown first) | For example Black Fox | No |
| Address | Street, city, state, ZIP | No |
| Phone | Main phone | No |
| Email | Main email | No |
| Footer on printouts (optional) | For example Controlled copy - printed from Hendrix QMS | No |
| Logo (badges, kiosks, printouts) | **Upload logo** (PNG, JPG, WEBP or SVG). **Remove** takes it off | No |

The **Printout header preview** shows what will print at the top and bottom of every record. The logo also shows on badges and the time clock kiosk.

### Time clock
| Field | What to enter | Required |
|---|---|---|
| 1st break (min) | Default 15 | Yes |
| 2nd break (min) | Default 30 | Yes |
| 3rd break (min) | Default 15 | Yes |

A return later than the limit is flagged late, with the minutes over, on the kiosk and the sign-in sheet.

### Facility logs
![Settings → Facility logs: days without an entry before a log is flagged](shots/found_settings_logs.png)

One number per log: after how many days without an entry the log is flagged as not kept up (on the Dashboard and on Standards). Leave it blank to use the default.

| Log | Default (days) |
|---|---|
| Sanitation Log | 2 |
| Temp / Humidity Log | 2 |
| Waste Destruction Log | 31 |
| Scale Calibration Log | 35 |
| Security Equipment Inspection | 35 |
| Pest Control Log | 35 |
| Environmental Monitoring Log | 35 |
| Equipment Maintenance Log | 95 |
| Security Malfunction Log | 120 |

### Review cycles
The default review cycle for a new risk in the Risk Register, by its rating. Each risk can still be changed on its own.

| Rating | Default (days) |
|---|---|
| Critical (15-25) | 90 |
| High (10-14) | 180 |
| Medium (5-9) | 365 |
| Low (1-4) | 365 |

### Everything else
A list of cards with **Open** buttons for settings that live in other pages: States and Licenses, Team and Access, Roles (access templates), Products, Compliance Stickers, Facility Logs (pick lists and kiosk QR codes), Rulebook, Standards (CSQ), Org Chart, Quality Objectives and Time Clock and Badges. You only see the cards for pages you can open.

![Settings → Everything else](shots/found_settings_more.png)

> **Hendrix checks:**
> - "Only Full access on Settings can change the settings of this license."
> - "Break limits must be between 1 and 240 minutes."
> - "Log due days must be between 1 and 400." and "Review cycles must be between 7 and 1095 days."
> - The logo is resized to fit 400 × 200 pixels. If it is still too big: "That logo is too large even after resizing. Use a simpler PNG or JPG." Hendrix only accepts PNG, JPG, WEBP or SVG images under 200 KB.
> - "Check the email address." if the email is not valid.
> - Settings are never deleted and cannot move to another license. Every change is in the Audit Trail.

## Import (Excel / Sheets)
Import brings existing lists from Excel or Google Sheets into Hendrix: suppliers, equipment, chemicals, products, complaints, risks and the org chart. The AI can match the columns, you check a preview, and every row goes through the same checks as typing it in.

**Where:** left menu → Import (Excel / Sheets). **Who:** anyone with Edit on at least one of Suppliers, Equipment, Chemicals and SDS, Products, Complaints, Risk Register or Org Chart. You only see the kinds of list you have Edit access to.
**CSQ:** none directly (the imported records then serve as evidence in their own modules)

![Import: choose what you import, then the spreadsheet](shots/found_import_start.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You move the equipment list from Excel | **Equipment** → **Choose .xlsx / .csv file** |
| Your supplier list lives in Google Sheets | **Suppliers** → download as .xlsx or CSV, or copy the cells and **Use pasted cells** |
| You load all SKUs and flavors at once | **Products (SKUs and flavors)** |
| You bring in last year's complaint log | **Complaints** |
| You have a risk assessment in a spreadsheet | **Risk register** |
| You have an org chart with reporting lines | **Org chart** |

### Import a list
1. **1. What are you importing?** Click a card: Suppliers, Equipment, Chemicals and SDS, Products (SKUs and flavors), Complaints, Risk register or Org chart. Each card lists its required columns.
2. **2. The spreadsheet.** Click **Choose .xlsx / .csv file** (.xlsx, .xls, .csv, .tsv, .txt), or paste cells copied from Google Sheets or Excel (with the header row) and click **Use pasted cells**.
3. If the file has several sheets, pick the **Sheet**. Check the **Header row**. Hendrix skips title rows and finds the first row with at least two filled cells.
4. **3. Match the columns.** Hendrix matches the columns by their names. Click **Match with AI** to let the AI match them and translate values (for example "Mixer" → Production). Check every field. A required field that is not matched shows in red.
5. **4. Preview.** Read the badges (**N to import**, **N with problems**, **N already in Hendrix**) and the **Check** column. Untick any row you do not want.
6. Click **Import N rows**. Hendrix says "Imported N." and lists any row that failed with the reason.

![The preview: 2 rows to import, 1 already in Hendrix, 1 with a missing name](shots/found_import_preview.png)

| Kind | Required columns | What happens after import |
|---|---|---|
| Suppliers | Supplier name | Suppliers start as Pending. Approve each one in Suppliers |
| Equipment | Equipment name | Calibration and validation dates are recorded as events in Equipment |
| Chemicals and SDS | Chemical name | Chemicals start as Pending. Attach the SDS and approve each one |
| Products (SKUs and flavors) | Product type, SKU name | New SKUs are added switched off for every license in the state. Existing SKUs get only the new flavors |
| Complaints | Received on, Summary | Complaints come in Open |
| Risk register | Risk, Hazard, Root cause, Owner, Likelihood (1-5), Severity (1-5) | The review cycle comes from Settings → Review cycles |
| Org chart | Position | "Reports to" is matched to the position titles in the sheet or already on the chart |

> **Hendrix checks:**
> - A row with a required column empty is not imported ("Equipment name is missing").
> - Dates and numbers must be readable ("… is not a date", "… is not a number"). US dates like 03/10/2025 are read as March 10.
> - A choice value Hendrix cannot place stops the row if the field is required; otherwise the field is left blank with a warning.
> - Risks: likelihood and severity must be 1-5, and a risk scored 10 or more needs an immediate action and a target date.
> - Complaints: "Received on is in the future" is refused.
> - Rows whose name (or title) is already in Hendrix for this license are skipped ("Already in Hendrix - skipped"), so importing the same file twice adds nothing.
> - Org chart: a "Reports to" that matches no position is reported ("Reports to "Plant Manager" not found - set it on the Org Chart"), not guessed.
> - Every row is saved to the license chosen at the top and goes through the same database rules and Audit Trail as a record typed by hand.
> - If the AI is not set up, Hendrix says so and you match the columns by hand.

### Tips
- Check the license at the top before you import.
- The preview shows the first 500 rows; all ticked rows are imported.
