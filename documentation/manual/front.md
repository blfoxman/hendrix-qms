## How to use this book
This book explains every page of Hendrix QMS: what each page is for, when to use it, and exactly what to fill in.

You don't need to read it front to back:
- **New to Hendrix?** Read this chapter first: how Hendrix is organized, your access, and the rules for good records.
- **Something just happened?** Look it up in **What do I fill in when…** at the end of this chapter, for example "a delivery arrived", "a customer complained" or "the temperature was out of range". It sends you to the right page and section.
- **Learning a module?** Go to its chapter. Each module starts with *When to use it*, then explains each form field by field. **Hendrix checks** boxes show what Hendrix will not let you do and why.

Hendrix is used every day by production technicians, QA, compliance staff, managers and owners. Visitors and staff also use it at kiosk tablets, to sign in, fill in logs and clock in.

![The dashboard: everything that needs attention at the selected license](shots/found_dashboard.png)

## How Hendrix is organized
**States and licenses.** Everything in Hendrix belongs to one **state** and one **license**. Each state has its own rules, products and law training. Each license has its own logs, batches, people and records. Choose the state and license in the top bar. Every page then shows, and saves to, that license only. Records of different licenses never mix.

**The left menu** has two parts:

| Part | What is in it |
|---|---|
| **Hendrix** (top) | Dashboard, States and Licenses, the state's Rulebook, Standards (CSQ), Team and Access, Roles, Audit Trail, Settings and Import. Mostly used by admins and QA. |
| **Modules** | The daily work. Overview: Line Map. Quality system: QMS, Complaints, Internal Audits, HACCP, Risk Register, Change Control, Org Chart, Quality Objectives, Management Review, Verification Schedule. People: Time Clock and Badges, Training, SOPs. Materials: Suppliers, Receiving, Hold and Release, Shipping, Traceability and Recall. Facility: Equipment, Chemicals and SDS, Line Clearance and Rework, Facility Tests, Cultivation, Visitor Log, Facility Logs. Production: Products, Production Planner, Batch Tracker, Testing, Compliance Stickers. |

You only see the modules you have access to. **Cultivation** appears only at cultivation licenses.

**The Dashboard** shows what needs attention at the selected license: overdue logs, open deviations, holds, due reviews, training gaps, expiring documents and more. Each card opens its page. **Start every shift here.**

## Your access: View, Edit and Full
An admin gives each person a level for each module, either through a role (for example "QA Manager" or "Production Tech") or one by one.

| Level | What you can do |
|---|---|
| **None** | You don't see the module. |
| **View** | See records, print them and sign what is yours to sign (for example read-and-sign an SOP). In QMS, anyone with View can report a deviation. |
| **Edit** | Create and fill in records, work on them and send them for approval. |
| **Full** | Approve, release, close, void and decide. Every approval in Hendrix needs Full access on that module. |
| **Admin** | Full on everything, plus Team and Access, Roles, Settings and the Audit Trail. |

If a button you expect is missing, you probably don't have the level for it. Ask your admin.

## The rules for good records
Hendrix is built so that inspectors and auditors can trust every record. These rules are enforced by Hendrix itself, not only by habit:

1. **Sign in as yourself.** Never share an account or use someone else's session. Everything you save is stamped with your name and the time. On a shared tablet, sign out when you're done.
2. **Enter it when it happens.** Hendrix stamps every save with the server time, next to the date and time you enter for the event. If you enter something late, the two will differ, so say why in the notes.
3. **Nothing is ever deleted.** A wrong record is **voided** with a reason. It stays visible, marked VOID, so the history is complete.
4. **Changes need a reason.** When you change a saved record, Hendrix asks for a **reason for change**. The old value, the new value, your name, the time and the reason all go into the **Audit Trail**.
5. **Signatures are final.** After a record is signed, approved or released, the signed parts are locked. To change something, raise a new version, a correction or a deviation.
6. **Approvals need the right person.** Releasing, closing and approving all need Full access. Hendrix checks this on every save.
7. **AI is a helper, not a signer.** AI can read a COA, draft an SOP or suggest amounts. Always check its work against the original before you save. The AI never approves anything.

> **Hendrix checks:** if you try to break one of these rules, Hendrix stops the save and tells you why, for example "A reason for change is required". Fix the problem and save again. Nothing is half-saved.

## Routines: what to do and how often
The defaults below are Hendrix's built-in timings. An admin can change them per license in **Settings**. **Verification Schedule** keeps all of these on one calendar.

| How often | What | Where in Hendrix |
|---|---|---|
| **Every shift** | Check the Dashboard and the Line Map; fill in the sanitation log and the temperature / humidity log | Dashboard; Facility Logs (overdue after 2 days) |
| **Every batch** | Line clearance before the batch; the batch record as you go; rework, if any | Line Clearance and Rework; Batch Tracker |
| **Every delivery** | Receive the lot into quarantine, inspect it, then accept or reject it | Receiving |
| **Every shipment** | Pre-load inspection and shipment record | Shipping |
| **When it happens** | Deviations, complaints, holds, visitor sign-in, security malfunctions | QMS, Complaints, Hold and Release, Visitor Log, Facility Logs |
| **Monthly** | Waste, pest control, environmental monitoring, scale calibration and security equipment inspection logs; objective results | Facility Logs (overdue after 31–35 days); Quality Objectives |
| **Quarterly** | Equipment maintenance log; access review of who can do what | Facility Logs (overdue after 95 days); Team and Access |
| **As planned** | Calibration and maintenance, facility tests, supplier reviews, HACCP verification | Equipment, Facility Tests, Suppliers, HACCP |
| **By risk** | Risk reviews: critical every 90 days, high every 180, medium and low every 365 | Risk Register |
| **Yearly** | SOP review, internal audit program, mock recall, management review, HACCP reanalysis, training refreshers | SOPs, Internal Audits, Traceability and Recall, Management Review, HACCP, Training |

## If Hendrix is not available
If you can't reach Hendrix because of the internet, a power cut or a device problem:
1. Write the record on the paper backup form, with the real date and time and your signature.
2. When Hendrix is back, enter it. In the notes, write "Entered late from paper form, original time …".
3. Keep the paper form with the batch or log records.
4. If the outage affected product, for example you couldn't check a hold, report a deviation.
