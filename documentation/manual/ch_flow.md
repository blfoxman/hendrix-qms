# How it all fits together

## The life of a batch
Every module in Hendrix is one part of a single chain: a material comes in from an approved supplier, is checked, turned into product under control, tested, labeled and shipped, and at every step it leaves a record. If you understand this chain, you understand why each page exists. Each step depends on the record of the step before it.

The table follows one batch of pre-rolls from start to finish. Other products follow the same path with different production steps.

| Step | What happens | Who | Where in Hendrix | The record it leaves | Why it matters |
|---|---|---|---|---|---|
| 1. Approve the supplier | QA checks a supplier's credentials and approves it for certain materials | QA | **Suppliers** | Approved supplier with its documents and review date | Only qualified suppliers can sell you materials. Unsafe materials are stopped before you even order. |
| 2. Receive the delivery | The delivery is counted, inspected and entered as a lot, in quarantine. Cannabis lots get their METRC package tag | Warehouse / inventory | **Receiving** | Lot number, quantity, METRC tag, inspection, COA | The lot number is the start of traceability. Quarantine means nobody can use it yet. |
| 3. Accept or reject | QA reviews the inspection and the COA, then accepts or rejects the lot | QA (Full access) | **Receiving** | Accepted or rejected, signed | Only accepted lots can go into product. A rejected lot can never be used. |
| 4. Store it | The lot goes to its room: vault, freezer, storage | Warehouse | **Rooms**, **Receiving** | Storage location on the lot; temperature log for the room | Materials must be kept at the right conditions and found again quickly. |
| 5. Plan the run | The planner works out each ingredient from the approved recipe and checks stock | Production manager | **Production Planner** | Numbered production plan and worksheets | The batch follows the approved formulation, and the run won't stop for lack of material. |
| 6. Clear the line | Before starting, the tech checks the line is empty of the last product, clean and ready, with calibrated equipment | Production tech | **Line Clearance and Rework** | Line clearance, passed, signed | Prevents mix-ups: wrong labels, leftover product, dirty equipment. |
| 7. Make the batch | The tech fills in the batch record as they work: each input by METRC tag (Hendrix deducts what was used from the lot), weights, counts, in-process checks, waste | Production tech | **Batch Tracker** | The batch record | Proves the batch was made the approved way. Links every package back to its inputs. Accounts for every gram for METRC. |
| 8. Check during the run | Critical steps are checked against their limits (for example oven time and temperature) | Production tech, then QA verifies | **HACCP**, **Batch Tracker** | CCP checks, verified | Hazards are controlled at the step where they happen. |
| 9. Test | A sample goes to the lab. The COA comes back and is read into Hendrix | QA / compliance | **Testing** | Test submission, result, COA | Product can't be sold until it passes. A failed test stops it. |
| 10. Decide | If it passes, the batch moves on. If it fails or anything is doubtful, it goes on hold until QA decides | QA (Full access) | **Hold and Release**, **QMS** | Hold and decision, deviation if needed | Nothing doubtful moves until a qualified person decides, with evidence. |
| 11. Label | Compliance stickers print with potency straight from the COA | Production / compliance | **Compliance Stickers** | Logged sticker print | Labels are legal statements and must match the lab result exactly. |
| 12. Ship | The order is loaded after a pre-load check, with its manifest and package tags | Shipping / inventory | **Shipping** | Shipment record | One step forward: you know which customer received each package. |
| 13. Follow up | Complaints and returns are linked back to the batch. Traces and mock recalls prove the chain works | QA | **Complaints**, **Traceability and Recall** | Complaint, trace, mock recall | If something is wrong, you can find and pull exactly the affected product, fast. |

Around this chain, the facility keeps itself under control every day: the building is cleaned, kept pest-free and at the right temperature (**Facility Logs**), equipment is maintained and calibrated (**Equipment**), chemicals are approved (**Chemicals and SDS**), visitors are signed in (**Visitor Log**), people are trained (**Training**) and work from approved instructions (**SOPs**).

The **Line Map** shows where every batch is in this chain right now, and turns it red when it's stopped, with the reason.

> **The key idea:** each record is the input to the next step. A lot that wasn't received can't be used in a batch. A batch that wasn't tested can't be released. A batch on hold can't be shipped. That's why records must be complete and made at the time: a missing record stops the chain, and a wrong record breaks the trace.

## When something goes wrong: the quality loop
Problems are found in many places: a log entry fails, a weight check fails, a lab test fails, a customer complains, an internal audit finds a gap. All of them lead into the same loop.

| Step | What it means | Where in Hendrix |
|---|---|---|
| 1. Contain it | Stop the problem from spreading right away: stop the line, move the product, pull the bad units. If product may be affected, put it **on hold**. | The page where you found it; **Hold and Release** |
| 2. Report a deviation | Write what happened and what you did. Every page that can find a problem has a **Deviation** button, which fills in the details and links back. | **QMS** |
| 3. Decide if the cause must be found | QA decides whether a root cause analysis is needed. A one-off slip may only need the correction. A problem that could come back needs its cause found. | **QMS** (Full access) |
| 4. Find the root cause | Ask "why?" until you reach the cause you can fix, not just the symptom. "The weight was low" is a symptom; "the filler auger is worn and was past its calibration" is a cause. | **QMS** |
| 5. Fix the cause (CAPA) | A **corrective action** removes the cause so it doesn't happen again here. A **preventive action** stops the same thing happening somewhere else. | **QMS** → CAPA |
| 6. Check it worked | After enough time, someone checks whether the problem came back. If it did, the CAPA wasn't effective and needs more work. | **QMS** → Verify effectiveness |
| 7. Learn from the trend | Deviations, complaints and CAPAs are reviewed by month, category and area, and by management at least once a year. | **QMS** → Trends; **Management Review** |

**Three words people mix up:**

| Word | Meaning | Example |
|---|---|---|
| Correction | What you do right away to fix this case | Re-weigh the 120 pre-rolls and refill the 14 that were light |
| Corrective action | What removes the cause, so this doesn't happen again | Replace the worn auger and add the filler to the calibration schedule |
| Preventive action | What stops the same cause somewhere else | Check the augers on the other two fillers and add them to the schedule too |

**Where problems come from, and the button to use:**

| You found it in… | Use |
|---|---|
| A facility log entry that failed (temperature, pest, sanitation) | Facility Logs → the entry → **Deviation** |
| A batch record weight or count check | Batch Tracker → **Deviation** |
| A failed lab test | Testing → **Deviation** (prefilled as Critical) |
| A delivery (damage, wrong COA, missing tag) | Receiving → **Deviation** |
| A customer complaint | Complaints → **Raise deviation** |
| An internal audit finding | Internal Audits → **Raise deviation (CAPA)** |
| A CCP reading outside its limit | HACCP → **Deviation** |
| Anything else | QMS → **+ Report deviation** |

> **Report it even when you fixed it.** A deviation isn't an accusation. It's how the facility learns. A problem that was fixed but not reported can't be trended, and an inspector who finds it in a log with no deviation behind it will ask why.

## Good records: the five rules behind every page
Inspectors and auditors judge records by five simple tests, often remembered as **ALCOA**. Hendrix is built around them, and they explain most of what Hendrix asks of you.

| Rule | In plain words | What it means for you | How Hendrix helps |
|---|---|---|---|
| **Attributable** | We know who did it | Sign in as yourself. Never use someone else's open screen. | Every save carries your name. Signatures ask for your password. |
| **Legible** | Anyone can read it | Write full sentences in notes. No private abbreviations. | Typed records; printouts and PDFs. |
| **Contemporaneous** | Recorded when it happened | Fill in the log or batch record as you work, not at the end of the shift or week. | Every save is stamped with the server time next to the time you enter. |
| **Original** | The first record is kept | Don't re-create a record "cleanly" afterward. Attach the scale printout or photo. | Nothing is deleted. Changes keep the old value. Files are attached to the record. |
| **Accurate** | It's true and complete | Enter the real number, even when it's out of range. Never copy yesterday's values. | Limits are checked as you type; a failed check starts a deviation instead of being hidden. |

**Do and don't:**

| Do | Don't |
|---|---|
| Enter readings when you take them | Fill in a week of logs on Friday |
| Write the real reading, even if it fails | Round a failing reading to a passing one |
| Use the reason for change to explain a correction | Void a record to hide a mistake |
| Write "not done" and why, when a step was missed | Leave it blank, or tick it anyway |
| Sign out of shared tablets | Let a coworker finish your entry under your name |
| Ask when a field isn't clear | Guess, or copy what someone else wrote |

## Who does what
Most people use a handful of pages every day. Find your job below to see which pages are yours and which chapters to read first. Your admin may have given you more or less access than shown here.

| Job | Every day | When it happens | Read first |
|---|---|---|---|
| **Production tech** | Line clearance before each batch; the batch record as you work; Facility Logs by QR (sanitation, temperature) | Report a deviation; sign new SOPs; take assigned training | Batch Tracker, Line Clearance and Rework, Facility Logs, QMS, SOPs |
| **Production lead / manager** | Dashboard and Line Map; plans; check batch records are complete | Check line clearances; approve rework; start plans; review deviations from the line | Line Map, Production Planner, Batch Tracker, Products, QMS |
| **Extraction tech** | Extraction batch records with yields; CCP checks | Report low yields and deviations | Batch Tracker, HACCP, Equipment |
| **QA / compliance** | Dashboard; holds; tests and COAs; deviation and CAPA follow-up | Accept or reject lots; release holds; run internal audits and mock recalls; approve SOPs | QMS, Hold and Release, Testing, Receiving, Internal Audits, SOPs, Traceability and Recall |
| **Inventory / warehouse** | Receiving deliveries into quarantine; storage; shipments with pre-load checks | Inventory counts; returns on hold | Receiving, Hold and Release, Shipping, Rooms |
| **Sanitation** | Sanitation log; chemicals as approved | Report pests, spills and failed cleans | Facility Logs, Chemicals and SDS |
| **Facility / maintenance** | Maintenance requests; equipment maintenance and calibration | Out of service, repairs, facility tests | Equipment, Facility Logs, Facility Tests |
| **Security** | Security inspection and malfunction logs; visitor log; badges | Lost badges; incidents | Time Clock and Badges, Visitor Log, Facility Logs |
| **Person in charge** | GMP hygiene walk every shift; employee illness and exclusion decisions | Exclude ill staff; report deviations | Facility Logs, Org Chart |
| **Cultivation** | Grow records; nutrient and pesticide applications; scouting | Harvest, drying, curing; temperature and humidity | Cultivation, Facility Map, Chemicals and SDS |
| **General manager / owner** | Dashboard and Line Map | Management review; risk register; objectives; approve changes | Line Map, Management Review, Risk Register, Quality Objectives, Change Control |
| **Admin** | Approve new people; set roles and access | Remove people who leave; settings; System Health | Team and Access, Roles, Settings, System Health |

## The rules and standards behind the records
Four sets of requirements explain almost everything Hendrix asks you to record. You don't have to know them by heart. It helps to know which one a record is for.

| Requirement | What it is | Who checks it | What it asks for (examples) | In Hendrix |
|---|---|---|---|---|
| **Your state's cannabis rules** | The law for licensed cannabis in your state, enforced by the state regulator | State inspectors | Security, visitor logs, inventory tracking in METRC, testing before sale, labels, waste destruction, training | Rulebook; every module that keeps a required record |
| **METRC** | The state's seed-to-sale tracking system. Every plant and package has a tag, and every gram must be accounted for | The state, through METRC and audits | Tags on every cannabis package, matching quantities, lab status, transfers on manifests | METRC tags on lots and batches, Batch Tracker, Shipping, METRC Check |
| **cGMP and food safety (21 CFR 117)** | Good manufacturing practice: the basic hygiene and control rules for making anything people consume | Food safety inspectors; CSQ auditors | Clean facility, pest control, employee hygiene and illness rules, approved chemicals, maintained equipment, records | Facility Logs, Chemicals and SDS, Equipment, Training, SOPs |
| **HACCP** | A method to find hazards and control them at the critical steps | Food safety inspectors; CSQ auditors | Hazard analysis, CCPs with critical limits, monitoring, corrective actions, verification | HACCP |
| **CSQ** | The Cannabis Safety & Quality certification standard, audited by an independent body | CSQ certification auditors | A full quality system: document control, training, suppliers, traceability, deviations and CAPA, audits, management review | Standards (CSQ) shows each clause and the records that meet it |

When you wonder "why do we have to fill this in?", the answer is almost always one of these. Each module's chapter names the CSQ clauses it supports, and the Rulebook holds your state's rules.
