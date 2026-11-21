## How to use this book
This book explains every page of Hendrix QMS: what each page is for, when to use it, and exactly what to fill in.

You don't need to read it front to back:
- **New to Hendrix?** Read this chapter first: how Hendrix is organized, your access, and the rules for good records. Then read **How it all fits together**: the life of a batch, what to do when something goes wrong, and which pages are yours.
- **Something just happened?** Look it up in **What do I fill in when…** at the end of this chapter, for example "a delivery arrived", "a customer complained" or "the temperature was out of range". It sends you to the right page and section.
- **Learning a module?** Go to its chapter. Each module starts with **Understand it first**: what it is in plain words, why we do it, and what goes wrong without it. Then *When to use it*, then each form field by field. **Hendrix checks** boxes show what Hendrix will not let you do and why.
- **Prefer to watch?** The Training Center at **hendrixqms.com/training** has short videos for each area, picked for your job.

Hendrix is used every day by production technicians, QA, compliance staff, managers and owners. Visitors and staff also use it at kiosk tablets and by scanning QR codes with a phone, to sign in, fill in logs and clock in.

The examples and screenshots in this book use a made-up company, **Northfield Labs** (license MFG-48213), with made-up people, so what you see on your own screen will have your company's names. Your admin may also have customized lists, roles and timings.

![The dashboard: everything that needs attention at the selected license](shots/found_dashboard.png)

## How Hendrix is organized
**Your company's address.** Each company has its own Hendrix at its own address, for example **hendrixqms.com/yourcompany**. Bookmark it, or add it to your phone's home screen. Kiosks and QR codes open the same address.

**States and licenses.** Everything in Hendrix belongs to one **state** and one **license**. Each state has its own rules, products and law training. Each license has its own logs, batches, people and records. Choose the state and license in the top bar. Every page then shows, and saves to, that license only. Records of different licenses never mix.

**The left menu** starts with **Dashboard** and **My Tasks**, then a **Find a module** box (type a few letters to jump to any page), then the modules in groups. Click a group name to open or close it; Hendrix remembers which groups you keep open on each device.

| Group | What is in it |
|---|---|
| **Production** | Production Planner, Batch Tracker (with the Manufacturing Process tab), Testing, Compliance Stickers, Products, METRC Check, Line Map, Line Clearance and Rework |
| **Inventory and shipping** | Receiving (with the Inventory tab), Hold and Release, Shipping, Traceability and Recall, Suppliers |
| **Facility** | Facility Map, Rooms, Facility Logs, Equipment, Chemicals and SDS, Facility Tests, Visitor Log, Time Clock and Badges, Cultivation |
| **Quality** | QMS (deviations and CAPA), Complaints, Internal Audits, HACCP, Risk Register, Change Control, Verification Schedule |
| **SOPs and training** | SOPs, Training, Org Chart, the state's Rulebook |
| **Management** | Quality Objectives, Management Review, Standards (CSQ) |
| **Admin** | States and Licenses, Team and Access, Roles, Audit Trail, Settings, System Health, Import |

You only see the modules you have access to. **Cultivation** and **Facility Map** appear only at cultivation licenses, and the manufacturing pages (Production Planner, Batch Tracker, Products, Compliance Stickers, Line Map, Line Clearance) only at manufacturing licenses.

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
Hendrix is built so that inspectors and auditors can trust every record. These rules are enforced by Hendrix itself, not only by habit. The chapter *How it all fits together* explains why they matter.

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
| **Every shift** | Check the Dashboard and the Line Map; the person in charge does the GMP hygiene walk; fill in the sanitation log and the temperature / humidity log | Dashboard; Facility Logs (sanitation overdue after 48 hours by default) |
| **Every batch** | Line clearance before the batch; the batch record as you go; rework, if any | Line Clearance and Rework; Batch Tracker |
| **Every delivery** | Receive the lot into quarantine with its METRC tag (cannabis), inspect it, then accept or reject it | Receiving |
| **Every shipment** | Pre-load inspection and shipment record | Shipping |
| **When it happens** | Deviations, complaints, holds, visitor sign-in, security malfunctions, maintenance and purchase requests, employee illness | QMS, Complaints, Hold and Release, Visitor Log, Facility Logs |
| **Weekly (suggested)** | METRC Check: compare Hendrix with METRC and fix differences | METRC Check |
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
