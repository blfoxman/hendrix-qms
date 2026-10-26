# Facility, equipment and people on site

## Facility Logs
The nine daily facility records in one place: sanitation, waste destruction, scale calibration, security malfunctions, weekly security inspections, pest control, equipment maintenance, temperature / humidity and environmental monitoring. Inspectors ask for these first, because they show the building is clean, secure, pest-free and under control every day.

**Where:** left menu → **Facility Logs**. **Who:** each log has its own access level (the "Facility Logs (all)" setting is the default for any log without its own; the two security logs share one setting). View can read the log, search it, export CSV and print. Edit can also add entries and sees the log's kiosk QR code. Full can also manage the log's pick lists, correct entries (with a reason) and void entries (with a reason).
**CSQ:** 1.1, 1.9, 2A.1.2, 2A.2.2, 2A.2.3, 2A.3, 2A.4, 2A.4.1, 2A.5.1, 2A.6, 2A.8, 2A.9.3, 3A.1.1, 3A.1.4, 3A.1.14, 3A.1.16, 3A.2.2, 3B.1.2, 3B.1.3, 3B.1.11, 3B.2.1, 3C.1.9

![Facility Logs, Sanitation tab: kiosk QR for this log, the state's facility rules, and the entry list with results](shots/facility_logs_overview.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| The end-of-shift clean is done | **Sanitation** → **+ New entry**, tick the areas and equipment cleaned. A supervisor fills **Cleaning Verification**. |
| Product or trim is destroyed | **Waste Destruction** → **+ New entry**: tags, quantity, method, the four camera angles, supervisor. |
| Weekly scale check, or a scale was moved | **Scale Calibration** → **+ New entry**, weigh the test weights on 5 points of the pan. |
| A camera, lock or alarm stops working | **Security Malfunction** → **+ New entry**. Fill **Repair Completed Date** later (Full access edit). |
| The weekly walk-round of cameras, doors and alarms | **Security Equipment Inspection** → **+ New entry**, mark every item OK / FAIL / N/A, sign. |
| The pest control vendor visits or someone sees a pest | **Pest Control** → **+ New entry**, tick the stations checked. |
| A machine is serviced or repaired | **Equipment Maintenance** → **+ New entry** (or **Record maintenance** from Equipment). |
| Start of every shift: room conditions | **Temp / Humidity** → **+ New entry**, or scan the room's QR sign with a phone. |
| A swab, air or water sample is taken in-house | **Environmental Monitoring** → **+ New entry**. |
| A result is Fail, Flag or Open | Click **Deviation** on that row to open a deviation linked to the entry. |

### Find and read entries
1. Pick the log tab at the top (Sanitation, Waste Destruction, Scale Calibration, Security Malfunction, Security Equipment Inspection, Pest Control, Equipment Maintenance, Temp / Humidity, Environmental Monitoring). Hendrix remembers the last tab you used.
2. Type in **Search entries...** or change the period (Last 24 hours, Last 7 days, Last 30 days, Last year, All time). The red badge counts entries in the period that are Fail, Flag or Open.
3. Each row shows the date / time, the item (shift, room, scale, equipment...), a short summary, the **Result**, who submitted it, and a **QR** tag when it came from the kiosk.
4. Click **View** for the full record: every field, the signature, and (if you can see the Audit Trail) the history of changes. **Print / PDF** prints it.
5. **CSV** exports every field of the entries shown. **Print / PDF** at the top prints up to 300 entries, one per page.
6. The card under the QR code shows how many rules of the matching category (Facility, or Security for the security logs) your state's Rulebook holds. Click **Show** to read them.

### Add an entry
1. Open the log tab and click **+ New entry**. Today's date, the time and your name are filled in.
2. Fill the fields. A required field has a `*`. Pick lists come from your license's lists (see **Manage the pick lists**); if a list is empty you get a type-in box instead.
3. Watch the **Result** badge: Hendrix works it out from what you enter (rules below).
4. Sign in the box if you want (the signature is required on the Security Equipment Inspection).
5. Click **Submit entry**.

> **Hendrix checks:** every field marked `*` must be filled ("Personnel Involved is required."); number fields must be numbers ("Temperature (°F) must be a number."). When the result is Fail on the Scale Calibration, Temp / Humidity or Environmental Monitoring log, you must fill the corrective action ("Result is Fail. Fill in "Corrective Action..." before saving."). A failed Security Equipment Inspection needs **Notes / Issues Found**. Every entry is saved to the license and state picked at the top; Hendrix will not save an entry for a license that is not in that state, and a pick-list item from another license or another log is refused.

How the result is set:

| Log | Result |
|---|---|
| Sanitation | **Verified** when **Verified By** is filled; **Flag** when the verification result is "Re-clean required"; otherwise **Logged** |
| Waste Destruction | **Open** when "Recorded in Track-and-Trace?" is Pending; otherwise **Logged** |
| Scale Calibration | **Pass** when all 5 points are within tolerance; **Fail** if any point is outside tolerance or the annual certification is overdue |
| Security Malfunction | **Resolved** when a repair date or resolution is entered; otherwise **Open** |
| Security Equipment Inspection | **Pass** when every item is checked and none failed; **Fail** if any item is FAIL; **Incomplete** otherwise |
| Pest Control | **OK** when Pests Found starts with "None"; any other choice is **Flag** |
| Equipment Maintenance | **OK** for "Pass — returned to service", **Fail** for "Fail — out of service", **Flag** for the other choices |
| Temp / Humidity | **Pass** / **Fail** from "Within Acceptable Range?" |
| Environmental Monitoring | **Pass**, **Fail**, or **Flag** for "Inconclusive — retest required" |

### The fields of each log
**Sanitation Log** (daily / weekly / monthly)

| Field | What to enter | Required |
|---|---|---|
| Date, Time Completed | When the cleaning was finished | Date yes |
| Shift | From the Shifts list (built-in: Day, Evening, Night) | No |
| Cleaned By | Who cleaned | Yes |
| Sanitizer / Chemical Used, Concentration / Dilution | e.g. Quat sanitizer, 1:256 | No |
| Daily: Areas Cleaned / Facility Equipment Sanitized / Equipment Cleaned, Weekly: Areas Cleaned, Monthly: Areas Cleaned | Tick each item done (**Check all** / **Clear**). Unticked items are saved as not done. | No |
| Additional Notes | Observations, issues | No |
| Verified By | Supervisor or QA, not the person who cleaned | No |
| Verification Method | Visual inspection, ATP swab, Checklist review | No |
| Verification Result | Acceptable, Re-clean required | No |

**Waste Destruction Log** (every destruction event)

| Field | What to enter | Required |
|---|---|---|
| Date / Time of Waste Generation | When the waste was generated | Date yes |
| Personnel Involved | Names of all staff involved | Yes |
| Agent / Badge ID(s) | State agent ID numbers | Yes |
| Category | From the Categories list (e.g. Concentrate) | Yes |
| Strain / Flavor | Name | No |
| Track-and-Trace Tag(s) | Package tags, comma separated | Yes |
| Unit of Measure | Grams or EA (Each) | Yes |
| Quantity of Waste / Expired Product | e.g. 14.2 | Yes |
| Rendering Camera Angle 1 and 2 | The two cameras covering the rendering (making the waste unusable) | No |
| Disposal Camera Angle 1 and 2 | The two cameras covering the disposal | No |
| Location of Rendering, Method Used | From the lists; write each full method as your state requires | Method yes |
| Quantity of Rendered Waste | Weight after rendering | No |
| Date / Time of Disposal, Waste Management Company, Waste Manifest Number, Disposal Receipt Number, Location of Disposal | Disposal details | No |
| Additional Notes / Comments | Free text | No |
| Recorded in Track-and-Trace? | Yes - recorded before destruction, Yes - recorded after destruction, Pending | No |
| Compliance Verification | Tick box | No |
| Supervisor Name | Verifying supervisor | Yes |

**Scale Calibration Log** (weekly, and each time the scale is moved)

| Field | What to enter | Required |
|---|---|---|
| Date, Time | When the check was done | Yes |
| Scale ID / Asset Tag | Pick the scale. Its location, make, model, serial, capacity, NTEP number, last certification, certifier and tolerance fill in | Yes |
| Location / Room, Scale Make / Model | Filled from the scale; change if needed | Yes |
| Model Number, Serial Number, Capacity / Readability, NTEP Certificate of Conformance # | Filled from the scale | No |
| Last Annual Certification Date | Date on the certification sticker | Yes |
| Certified By, Certification seal / sticker is present and current | Service company; tick | No |
| Pre-checks: clean, level, no draft / vibration, reads zero | Tick each | No |
| Scale moved since the last check? | No / Yes — full verification performed | Yes |
| Test Weight Calibration Due Date | Due date of your test weights | No |
| Point 1 to 5 (Front Left, Front Right, Back Left, Back Right, Middle): Test Weight and Scale Reading | Grams | Yes |
| Scale status after check | In service — passed, Tagged out of service, Adjusted / repaired and re-verified | No |
| Corrective Action | What was done | Yes, if the result is Fail |
| Performed By | Your name | Yes |
| Reviewed / Verified By, Notes | Supervisor or QA | No |

The **Calibration check** box on the form shows each point's difference, OK or FAIL against the scale's tolerance (±0.1 g unless the scale has its own), when the annual certification is due (one year after the last one; "due soon" within 30 days), and the next weekly check (7 days after this one).

![Scale Calibration entry: one point is 0.2 g off, so the result is Fail and a corrective action is required](shots/facility_logs_scale_form.png)

**Security Malfunction Log**

| Field | What to enter | Required |
|---|---|---|
| Date, Time Discovered | When it was found | Date yes |
| Reported By | Your name | Yes |
| System Type | CCTV Camera, DVR/NVR Recorder, Motion Sensor, Door Access Control, Alarm System, Perimeter Fence/Gate, Safe/Vault, Other (or your own list) | Yes |
| Location | e.g. Front entrance camera | Yes |
| Description of Malfunction | What failed and how it was found | Yes |
| Regulator Notified? | Yes — within 24 hours, Yes — within 48 hours, Not required — minor, Pending | No |
| Temporary Security Measure | What covers the gap meanwhile | No |
| Repair Completed Date, Resolution / Repair, Verified Operational By, Notes | Close-out details | No |

**Security Equipment Inspection** (weekly)

| Field | What to enter | Required |
|---|---|---|
| Date, Time | When you inspected | Date yes |
| Inspected By | Full name | Yes |
| Cameras / Door Locks / Alarm System tabs | For each item on your lists: the camera view (Clear, Partial, Obstructed, Offline) or battery level (Good, Low, Critical, N/A - Wired), and **OK**, **FAIL** or **N/A**. The progress line shows "x / y checked" and the number of FAILs. | No |
| Notes / Issues Found | Describe failures | Yes, if any item failed |
| Signature | Sign in the box | Yes |

**Pest Control Log**

| Field | What to enter | Required |
|---|---|---|
| Date | Visit date | Yes |
| Type | Routine inspection, Pest sighting report, Treatment / Extermination, Follow-up inspection, Bait station check, Glue trap check (or your own list) | Yes |
| Performed By | Name or licensed vendor | Yes |
| Vendor License # | PCO license number | No |
| Areas Inspected | All areas inspected | Yes |
| Pests Found | None observed, Rodent evidence, Insects, Birds, Other (or your own list) | No |
| Stations Checked | Tick each numbered trap / bait station checked | No |
| Stations With Activity, Pest Detail, Treatment / Chemical Applied (product and EPA reg #), Corrective Action, Next Scheduled Inspection, Notes | Details | No |

**Equipment Maintenance Log**

| Field | What to enter | Required |
|---|---|---|
| Date | Date of the work | Yes |
| Equipment Name | Pick from the list (fills the ID / serial) or type | Yes |
| Equipment ID / Serial # | Asset tag or serial | No |
| Maintenance Type | Routine/Preventive, Corrective/Repair, Calibration, Deep clean, Inspection, Part replacement (or your own list). A **Routine/Preventive** entry resets the equipment's maintenance schedule in **Equipment**. | Yes |
| Performed By | Technician | Yes |
| Work Performed | What was done | Yes |
| Parts Replaced, Downtime (hours) | Details | No |
| Equipment Status After | Pass — returned to service, Conditional — monitor closely, Fail — out of service, Pending parts / repair | No |
| Next Scheduled Maintenance, Notes | An earlier next date here also moves the schedule in Equipment | No |

**Temp / Humidity Log** (every shift)

| Field | What to enter | Required |
|---|---|---|
| Date, Time | When you read it | Yes |
| Shift | From the Shifts list | No |
| Recorded By | Your name | Yes |
| Location / Room | Pick the room (or type it) | Yes |
| Temperature (°F), Relative Humidity (%) | Numbers | Yes |
| Within Acceptable Range? | Yes — within range, No — out of range (action taken), No — equipment malfunction. Set automatically when the room has min / max limits. | No |
| Corrective Action (if out of range) | What you did | Yes, if out of range |
| Notes | Free text | No |

![Temp / Humidity entry: 66% RH is above the vault's 62% limit, so Hendrix sets "out of range" and asks for the corrective action](shots/facility_logs_temp_form.png)

**Environmental Monitoring Log** (monthly minimum)

| Field | What to enter | Required |
|---|---|---|
| Date | Sample date | Yes |
| Performed By | QC technician | Yes |
| Sampling Location | From the list or typed | Yes |
| Sample Type | ATP swab (surface), Air sample, Water sample, Drain swab, Equipment surface swab, Hand swab (or your own list) | Yes |
| Test Method / Equipment, Result Value | e.g. ATP luminometer, 245 RLU | No |
| Pass / Fail | Pass — within limit, Fail — exceeds limit, Inconclusive — retest required | Yes |
| Corrective Action (if fail) | Immediate action | Yes, if Fail |
| Retest Date, Notes | Details | No |

### Manage the pick lists (Full access)
1. Open the log tab and click **Manage lists**. The lists belong to this license only; other licenses keep their own.
2. Type an item and click **+ Add**. Some lists also take details: scales (location, make / model, model number, serial, capacity, NTEP number, last annual certification, certified by, tolerance), temp / humidity rooms (min / max °F, min / max RH %), pest stations (type, location), equipment (ID / serial).
3. **Edit** renames an item or changes its details, **Hide** takes it off the forms (and **Show** brings it back), **Delete** removes it after a confirm. Past entries keep the name they were saved with.
4. Lists with built-in choices (shifts, pest types, maintenance types, sample types, system types...) say "Using the built-in choices". Click **Copy them here to edit** to change them. **Shifts** is shared by every log of the license.
5. A list with no items shows as a type-in box on the form.

![Manage lists for the Temp / Humidity Log: each room's limits set the in-range answer automatically](shots/facility_logs_lists.png)

> **Hendrix checks:** only Full access on that log can add, change or delete list items, and only for its own license.

### Use the kiosk (QR) on a phone or tablet
1. On the log tab, the gold card shows the **Kiosk QR** for this log and this license. Click **Print QR sign** to print a letter-size sign, or **Copy link**.
2. Staff scan the code with a phone camera. No login is needed. The page shows the state, license and log name.
3. They fill the same form, sign with a finger and tap **Submit entry**. The screen confirms "Saved. Thank you, <name>." and warns them to tell a supervisor when the result is Fail, Flag or Open. **Fill another** starts a new entry.
4. Kiosk entries show a **QR** tag in the list.

![The Temp / Humidity kiosk on a phone: no login, signature required](shots/facility_logs_kiosk.png)

> **Hendrix checks:** a kiosk entry needs a name and a signature ("Please sign in the box."). The link carries the log, the state and the license; Hendrix refuses a link with a missing state or license, an unknown log, or a license that is not active in that state ("This QR code is not linked to an active license in this state. Please ask a manager for the current code.").

### Correct or void an entry (Full access)
1. **Edit** on a row opens the entry. Change what is wrong, write the **Reason for change** and click **Save changes**. The old values, who changed them and when go to the Audit Trail.
2. **Void** asks for the **Reason for voiding**. The entry stays in the list, marked **Void**, with your name, the time and the reason. A void cannot be undone.

> **Hendrix checks:** entries are never deleted. A change without a reason is refused ("A reason for the change is required."), a void without a reason is refused ("A reason is required to void an entry."), and a voided entry cannot be changed. The license, state, log type, signature and source of an entry can never be changed.

### Tips
- Put a printed QR sign next to every room thermometer and in the cleaning closet; most entries then come from the kiosk.
- Settings → **Facility logs** sets after how many days without an entry a log is flagged as not kept up on the dashboard and in Standards.
- Add every scale in **Manage lists** with its tolerance; a 30 kg floor scale should not use the 0.1 g default.

## Visitor Log
The sign-in record of every visitor and contractor, with their agreement to the facility's GMP rules and an illness check. It shows an inspector who was on site, when, and that ill visitors were kept out of production.

**Where:** left menu → **Visitor Log**. **Who:** View can see and search the log and export CSV. Edit can also add a manual entry, sign visitors out and see the kiosk QR code. Other changes to an entry need Full access.
**CSQ:** 2A.13.8, 1.9

![Visitor Log: kiosk QR for this license, and the visitors with their GMP / health status and time out](shots/facility_visitor_log_overview.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A visitor or contractor arrives | They scan the QR sign at the door and sign in on their phone (or a tablet). |
| The visitor has no phone | Click **+ Manual entry**, ask the illness question and have them read the GMP rules. |
| A visitor leaves | They scan again and use **Sign out**, or you click **Sign out** on their row. |
| A visitor says they are ill | They may sign in, but the entry is marked **Ill — no production**. Keep them out of production and processing areas. |
| The inspector asks for the visitor log | Set the period, click **Export CSV**. |

### Visitor sign-in on the kiosk
1. Print the sign with **Print QR sign** (or copy the link) and put it at the entrance. The code works for this license only.
2. The visitor scans the code and stays on the **Sign in** tab.
3. They fill the form, sign, answer the illness question, read the six GMP rules and tick the box, then tap **Sign in**.
4. The screen thanks them and reminds them to sign out. If they answered Yes to illness it tells them not to enter production or processing areas.
5. To leave, they open the **Sign out** tab, find their name in the list of people signed in and tap **Sign out**.

![Visitor sign-in on a phone: details, signature, illness question and GMP rules](shots/facility_visitor_kiosk_signin.png)

| Field | What to enter | Required |
|---|---|---|
| Full name | Visitor's name | Yes |
| Company | Company | No |
| Purpose of visit | Vendor / delivery, Contractor / maintenance, Inspector / regulator, Customer / buyer, Interview, Meeting, Tour, Other | Yes |
| Who are you visiting? | Host | No |
| Vehicle plate (optional) | Plate | No |
| Signature | Sign in the box | Yes |
| Illness question | No / Yes: "Do you have any symptoms of illness right now (fever, vomiting, diarrhea, jaundice, sore throat with fever) or an open cut or wound?" | Yes |
| I have read the GMP rules above and will follow them. | Tick | Yes |

> **Hendrix checks:** sign-in is refused without a name, a purpose, a signature, an answer to the illness question ("Please answer the illness question.") and the GMP agreement ("Please confirm you have read and will follow the GMP rules."). The visit is always saved to the license in the QR link; a link to an inactive license or a license in another state is refused.

![The kiosk Sign out tab lists everyone signed in](shots/facility_visitor_kiosk_signout.png)

### Add a manual entry (Edit)
1. Click **+ Manual entry**.
2. Fill the details, ask the illness question and click **No** or **Yes**, let the visitor read the GMP rules, tick "The visitor read the GMP rules and agreed to follow them."
3. Click **Save**.

![Manual visitor entry](shots/facility_visitor_log_manual.png)

| Field | What to enter | Required |
|---|---|---|
| Full name | Visitor's name | Yes (Save stays greyed out) |
| Company, Purpose, Visiting, Vehicle plate | As above | No |
| Illness question | No / Yes | Yes |
| The visitor read the GMP rules and agreed to follow them. | Tick | Yes |

> **Hendrix checks:** "Ask the visitor the illness question and record the answer." and "The visitor must read and accept the GMP rules." A manual entry has no signature.

### Read the log
- Search by name, company, purpose or host; pick the period (Last 24 hours to All time).
- **GMP / Health** shows **GMP accepted**, **Ill — no production** or **Not recorded** (old entries from before the GMP question). **Time out** shows **On site** until the visitor signs out.
- **Signature** shows the visitor's signature. **Export CSV** includes state, license, GMP acceptance and declared illness.

> **Hendrix checks:** signing a visitor out needs only Edit access and no reason. Any other change needs Full access and a reason ("You can sign visitors out. Other changes need Full access to the Visitor Log."). Visitor entries are never deleted.

## Equipment
The equipment register: every machine and instrument with its preventive maintenance schedule, calibrations and certificates, IQ / OQ / PQ validation, temporary repairs and out-of-service history. Inspectors use it to check that equipment is maintained, measuring devices are calibrated on time and nothing broken is in use.

**Where:** left menu → **Equipment**. **Who:** View can see the register, open equipment and print the register. Edit can add and edit equipment and record calibrations, validations, temporary repairs, out of service and back in service. Full can also retire equipment and void equipment records.
**CSQ:** 2A.2.1, 2A.2.2, 2A.2.3, 5.1.7, 2A.7, 3A.1.4, 3B.1.1, 3B.1.2

![Equipment register: status, preventive maintenance, calibration, validation and repairs for every item](shots/facility_equipment_register.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| New equipment is installed | **+ Equipment**, set the maintenance schedule and, if needed, calibration and validation. |
| Your Facility Log lists already hold scales and machines | Click **Add them to the register** in the banner at the top. |
| A machine gets its scheduled service | **Open** → **Record maintenance** (goes to the Equipment Maintenance Log). |
| The scale company calibrates a scale | **Open** → **Record calibration**, attach the certificate. |
| A new extraction system is commissioned | **Open** → **Validation (IQ / OQ / PQ)**, once per stage. |
| A quick fix is made until a part arrives | **Open** → **Temporary repair** with a fix-by date; **Made permanent** when fixed. |
| A machine breaks or fails a check | **Open** → **Out of service** with the reason. |
| It is fixed and ready | **Open** → **Back in service**, tick the three checks. |
| A machine is sold or scrapped | **Open** → **Retire** (Full access) with the reason. |
| An inspector asks for the equipment list | **Print register**. |

### Read the register
- The cards count equipment in service, out of service, maintenance overdue, calibration overdue (and due in 30 days), open temporary repairs and validation due.
- Filter with **Search equipment**, the category and **In the register** / **Needs attention** / **Including retired**.
- **Preventive maintenance**: next due date = the last **Routine/Preventive** entry in the Equipment Maintenance Log (or the install date) plus the interval; an earlier "Next Scheduled Maintenance" on that entry wins. **Due** within 14 days, **Overdue** after, **Never recorded** when there is no entry and no install date.
- **Calibration**: from the last passed calibration. **Due** within 30 days, **Overdue** after, **Never calibrated**.
- **Validation**: **Not validated** until a passed PQ; revalidation is due one year after the last passed PQ or revalidation (**Due** within 30 days).
- **Repairs**: open temporary repairs; red when past the fix-by date.

### Add equipment
1. Click **+ Equipment**.
2. Fill the form and click **Save**. Hendrix gives it the next number (EQ-001, EQ-002...) and adds it to the Equipment Maintenance Log list, so it can be picked on the log and the kiosk. A scale is also added to the Scale Calibration Log list.

![New equipment form](shots/facility_equipment_form.png)

| Field | What to enter | Required |
|---|---|---|
| Name | e.g. Filling machine #2 | Yes |
| Category | Production, Packaging, Extraction, Scale / balance, Measuring instrument, Facility (HVAC, water, air), Safety system (gas, fire), Cultivation, Vehicle, Lab, Other | No |
| Location / room, Make, Model, Serial number, Asset tag, Installed on | Identification | No |
| Touches product (food-contact surface), Critical to product safety or quality | Tick boxes | No |
| Controls | Automated / electronic settings and who approved them | No |
| Preventive maintenance: Every (days) | Interval | No |
| Tasks (manufacturer requirements) | What the service includes | No |
| Needs calibration | Ticked automatically for a new Scale / balance or Measuring instrument | No |
| Every (months) | Calibration interval (default 12) | Yes, if calibration is needed |
| Method, Reference standard, Protected from adjustment by | e.g. NIST HB 44, NIST-traceable class F weights, sealed | No |
| Needs validation (IQ / OQ / PQ, revalidated every year) | Ticked automatically for new Extraction equipment | No |
| Manuals, drawings, certificates | Files | No |
| Notes | Free text | No |

> **Hendrix checks:** "Enter how often it is calibrated (months)." when calibration is ticked. If you lack Full access on the Equipment Maintenance Log, the equipment is saved but Hendrix tells you it could not be added to that log's list.

### Equipment detail and records
Click **Open** on a row. The detail shows the equipment, its maintenance, calibration and validation status, and the full history: calibrations, validations, repairs, out-of-service records and the Equipment Maintenance Log entries for it.

![Equipment detail: overdue maintenance, an open temporary repair and the history from the maintenance log](shots/facility_equipment_detail.png)

**Record calibration** (only when it needs calibration)

| Field | What to enter | Required |
|---|---|---|
| Date | Not in the future | Yes |
| Calibrated by (person / company) | Who did it | No |
| Result | Pass, or Fail - take it out of service | Yes |
| Reference standard used (traceable to NIST / ASTM) | Filled from the equipment | Yes, unless a certificate is attached |
| Next calibration due | Blank = date + the interval | No (when Pass) |
| Details | As found / as left | No |
| Calibration certificate | **+ Certificate** | Yes, unless a standard is named |

![Recording a calibration with its certificate](shots/facility_equipment_calibration.png)

**Validation (IQ / OQ / PQ)**: Date, Done by, **Stage** (IQ - installation qualification, OQ - operational qualification, PQ - performance qualification, Yearly revalidation), **Result** (Pass / Fail), Details, Files.

**Temporary repair**: Date, Done by, **Permanent repair must be done by** (required), **Temporary repair (what was done)** (required), Files. When fixed, click **Made permanent** in the history and describe what was done.

**Out of service**: Date, Done by, **Reason** (required), Files.

**Back in service**: Date, Done by, tick all three: "Tools, parts, lubricants and debris removed from the equipment and area", "Cleaned and sanitized before use", "Checked working as intended (test run)"; Details, Files.

> **Hendrix checks:** a calibration needs a certificate or the reference standard ("Attach the calibration certificate or name the reference standard used (e.g. NIST-traceable weights)."). A failed calibration or validation takes the equipment out of service automatically. "Tick every check before putting it back in service." Equipment that needs calibration cannot go back in service while its calibration is out of date ("The calibration is out of date. Record a calibration first."). A temporary repair needs a fix-by date. Records cannot be dated in the future, cannot be changed (void and record again), and cannot be added to retired equipment. The status, calibration and validation dates come only from these records; you cannot type them. Only Full access voids a record (with a reason) or retires equipment ("Give a reason for retiring this equipment."). Equipment with records is never deleted; retire it.

### Tips
- Add the equipment first, then record its latest certificate, so the register starts with the right due date.
- Recording a passed scale calibration also updates the scale's certification date in the Scale Calibration Log list.
- Line clearance will not clear a line that uses equipment out of service or out of calibration.

## Chemicals and SDS
The approved chemical list for the license: every cleaner, sanitizer, lubricant, solvent and pesticide on site, with its Safety Data Sheet, storage area, PPE and first aid. Inspectors check that nothing unapproved is used, every chemical has an SDS, and food-grade products are kept apart.

**Where:** left menu → **Chemicals and SDS**. **Who:** View can see the list, open SDS files and print the lists. Edit can add chemicals (new ones wait for approval) and edit them. Full can also approve chemicals, remove them from use and delete chemicals that were never approved.
**CSQ:** 2A.9.2, 2A.5.1

![Chemicals and SDS: approved list with grade, storage area, SDS and status](shots/facility_chemicals_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new chemical is bought | **+ Chemical**, attach the SDS, **Save**. A Full-access person reviews and approves. |
| A pending chemical needs approval | **Review** on its row, check the SDS fields, **Save and approve**. |
| A pesticide is brought in | Choose **Pesticide / crop protection** and enter the **EPA registration #**. |
| A product is no longer used | **Remove** (Full access) with the reason. |
| A chemical was entered by mistake and never approved | **Delete** (Full access). |
| Each storage area needs its chemical list posted | **Print storage area lists**. |
| An inspector asks for the approved list | **Print approved list**. |

### Add, review and approve a chemical
1. Click **+ Chemical** (or **Review** / **Edit** on a row).
2. Fill the form and attach the SDS with **+ SDS**.
3. Click **Save** to keep it as **Waiting for approval**, or (Full access) **Save and approve**. Hendrix numbers it CHEM-001, CHEM-002...

![Reviewing a pesticide: the EPA registration number is required before approval](shots/facility_chemicals_form.png)

| Field | What to enter | Required |
|---|---|---|
| Product name | Name on the label | Yes |
| Manufacturer, Product code | From the label | No |
| Used for | Cleaner, Sanitizer, Food-contact sanitizer, Lubricant (food grade H1), Lubricant / maintenance (non-food), Pesticide / crop protection, Nutrient / fertilizer, Extraction solvent or gas, Lab reagent, Other | No |
| Grade | Food grade, Food-contact sanitizer, Not food grade (set automatically for food-contact sanitizers and H1 lubricants) | No |
| Supplier | From your approved suppliers | No |
| EPA registration # | Shown for Pesticide / crop protection | Yes, to approve a pesticide |
| SDS file | **+ SDS** | Yes, to approve |
| SDS revision date | Date on the SDS | No |
| Hazards (SDS section 2), First aid (section 4), Spill response (section 6), Disposal (section 13) | From the SDS | No |
| PPE (SDS section 8) | Gloves, goggles... | Yes, to approve |
| Storage area | e.g. Chemical cage (earlier areas are suggested) | Yes, to approve |
| Restricted - authorized people only | Tick | No |
| Notes (secondary container labels, dilution...) | Free text | No |

> **Hendrix checks:** only Full access can approve; a chemical saved by someone with Edit access always stays **Waiting for approval**. Approval is refused without the SDS ("Attach the Safety Data Sheet (SDS) before approving."), the storage area, the PPE, and for a pesticide the EPA number ("Enter the EPA registration number of the pesticide."). Hendrix records who approved and when.

### Remove from use or delete
- **Remove** (approved chemicals, Full access): write why it is no longer used and click **Remove from use**. It stays on file, crossed out, with the reason.
- **Delete** (pending chemicals, Full access): only a chemical that was never approved can be deleted.

> **Hendrix checks:** "Give a reason for removing this chemical." An approved chemical is never deleted.

### Print the lists
- **Print approved list**: every approved chemical with use, grade, storage, SDS status (MISSING if none) and who approved it.
- **Print storage area lists**: one page per storage area (or the area picked in the filter) with the approved chemicals kept there, their hazards, PPE, first aid, spill response and SDS date. Post it in the area with the SDS binder.

![Printed storage area list](shots/facility_chemicals_storage_sheet.png)

### Tips
- The cards show approved chemicals, chemicals waiting for approval, chemicals with the SDS missing, and approved pesticides.
- Use the same storage area name every time so the area lists group correctly.

## Facility Tests
The test program for the building's air, water, process gases, surfaces, backflow devices and (for cultivation) soil, irrigation water and wastewater: what is tested, how often, the lab, and every result. Inspectors check that air and water are tested at least yearly by an accredited lab and that failures were acted on.

**Where:** left menu → **Facility Tests**. **Who:** View can see the program and results and print the program. Edit can add and edit test points and record results. Full can also switch a test point off and void results.
**CSQ:** 2A.6, 2A.7, 2A.3, 3A.1.1, 3A.1.9, 3A.1.10, 3A.1.12, 3B.1.3, 3B.1.5, 3B.1.7, 3B.1.11, 3C.1.5

![Facility Tests: each test point with its last result and status](shots/facility_envtests_overview.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Setting up a new license | Click **Add the test plan** in the gold banner. |
| You need an extra point (ice machine, a second tap) | **+ Test point**. |
| The lab report arrives | **Record result** on the point, attach the report. |
| A swab or test fails | Record it as **Fail** with the corrective action, then **History** → **Deviation**. |
| A test point is no longer used | **Edit**, untick **Active** (Full access). |
| An inspector asks for the program | **Print program**. |

### Start from the test plan
The banner lists the CSQ test points for your license type that you do not have yet. Every license gets incoming water (yearly, accredited lab), production room air (yearly, accredited lab), backflow preventer (yearly) and food-contact surface swabs (every 30 days). A manufacturing license adds process gas and process water / ice; a cultivation license adds irrigation water, soil / grow media and wastewater. Click **Add the test plan** (or **Add the missing ones**), then edit each point's location.

### Add or edit a test point
| Field | What to enter | Required |
|---|---|---|
| Name | e.g. Hand sink water | Yes |
| What is tested | Air quality, Incoming water (potable), Process water / ice, Irrigation water, Wastewater / runoff, Soil / grow media, Process gas, Surface swabs, Backflow device | No |
| Where (room / tap / line), Source | Location; e.g. City water | No |
| Every (days) | How often | Yes |
| Tested for (analytes), Limits / specification | What the lab tests and the pass limits | No |
| Must be tested by an ISO/IEC 17025 accredited lab | Ticked by default except for backflow, surface swabs, process gas and wastewater | No |
| Active | Shown when editing; only Full access can switch a point off | No |
| Notes | Free text | No |

The form shows which CSQ clauses the point supports.

### Record a result
1. Click **Record result** on the point.
2. Fill the form, attach the lab report with **+ Report**, click **Record result**.

![Recording an air test result from an accredited lab](shots/facility_envtests_result_form.png)

| Field | What to enter | Required |
|---|---|---|
| Sampled on | Sample date, not in the future | Yes |
| Sampled by, Report # | Who sampled; lab report number | No |
| Lab | The lab or tester (filled from the last result) | Yes, when the point needs an accredited lab |
| Result | Pass - within limits, Fail - out of limits | Yes |
| The lab is ISO/IEC 17025 accredited for this test | Tick | Yes, when the point needs it |
| Results (values) | e.g. E. coli not detected | Yes, unless a report is attached |
| Corrective action | What was done | Yes, when Fail |
| Lab report | **+ Report** | Yes, unless values are entered |

> **Hendrix checks:** "This test must be done by an ISO/IEC 17025 accredited lab." and "Enter the lab that tested the sample." for points that need a lab; "Attach the report or enter the results."; "A failed result needs the corrective action." Results cannot be changed; only Full access can void one, with a reason. A test point with results cannot be deleted; switch it off.

### Status and history
- **Next** due = last sample date + the frequency. **Due** within 30 days, **Overdue** after, **Never tested**, **Failed** when the latest result is a fail, **Off** when switched off.
- **History** lists every result with the lab, accreditation, values, corrective action and report. A failed result has a **Deviation** button; Full access sees **Void**.

![History of the surface swabs: a failed ATP swab with its corrective action](shots/facility_envtests_history.png)

## Line Clearance and Rework
Two controls on the production floor: the pre-operational inspection (line clearance) before a batch starts, and rework, tracked from the batch or hold it came from to the batch it went into. Inspectors use them to check lines were clean and ready, and that rework was tested, approved and traceable.

**Where:** left menu → **Line Clearance and Rework** (tabs **Line clearances** and **Rework**). A line clearance can also be started from a batch card in the Batch Tracker. **Who:** Line clearance and rework have separate access. Line clearance: View can see and print; Edit can record line clearances; Full can void them. Rework: View can see; Edit can identify, inspect and record use; Full can approve for use and destroy.
**CSQ:** 2A.12.3, 2A.12.5, 3B.1.2, 3B.1.12

![Line clearances: batches cleared in the last 30 days and every inspection](shots/facility_lineclear_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A batch is about to start | **+ Line clearance** (or **Line clearance** on the batch card), go through the checklist. |
| Something failed and you fixed it on the spot | Mark the item **Fail**, tick **Corrected**, describe the problem and the correction. |
| The line cannot be made ready | **Record NOT cleared**, then **Deviation** on the row. |
| A room or line is checked without a batch | Leave the batch empty and enter the **Room / line**. |
| Product is set aside to be reworked | **Rework** tab → **+ Rework**. |
| The rework has been checked and tested | **Inspect**. |
| QA decides it can be used | **Approve** (Full access). |
| It went into a new batch | **Use in batch**. |
| It cannot be used | **Destroy** (Full access) with the reason. |

### Record a line clearance
1. Click **+ Line clearance**.
2. Pick the **Batch** (recent batches of this license) or leave "(no batch - a room or line)" and fill **Room / line**.
3. Tick the **Equipment used**. Equipment out of service, retired or past its calibration date is flagged in red.
4. Answer every checklist item **Pass**, **Fail** or **N/A**. For a failed item fixed on the spot, tick **Corrected**.
5. If anything failed, fill **Problems found** and **Corrections / corrective action**.
6. Check **Inspected by** (your name is filled in) and add **Verified by** if a supervisor checked.
7. Click **Line cleared**, or **Record NOT cleared** if the line cannot start. Hendrix numbers it LC-2026-001, LC-2026-002...

![Line clearance for a BHO batch: SCALE-02 is out of calibration, so "Line cleared" is greyed out](shots/facility_lineclear_form.png)

The checklist: previous product, labels, packaging and paperwork removed; area and equipment cleaned and sanitized; equipment in good repair and within maintenance and calibration dates; correct materials, labels and packaging staged and checked; staff dressed per cGMP and hands washed; no pests, foreign matter, broken glass or brittle plastic; tools and utensils counted. Extraction batches add: gas detection, fire and life safety systems working, ventilation on; correct solvent / gas staged, within spec, with its COA.

| Field | What to enter | Required |
|---|---|---|
| Batch | Batch of this license | Batch or Room / line |
| Room / line | e.g. Cartridge filling line 1 | Yes, without a batch |
| Equipment used | Tick from the register | No |
| Checklist | Pass / Fail / N/A for every item; Corrected on a failed item | Yes |
| Problems found, Corrections / corrective action | What failed and what was done | Yes, if anything failed |
| Inspected by | Who inspected | Yes |
| Verified by (supervisor, optional) | Supervisor | No |

> **Hendrix checks:** "Answer every item on the checklist." "Describe each problem found and the correction or corrective action." The line cannot be cleared while a failed item is not corrected or while any equipment used is out of service, retired or out of calibration ("The line cannot be cleared: ..."); the form says why. A line clearance cannot be changed; only Full access can void it, with a reason.

On the list: **Print** prints the record (checklist, equipment, problems and corrections). A NOT cleared line has a **Deviation** button. The **Batches cleared (30 days)** card shows how many batches of the last 30 days have a cleared line clearance; the batch card in the Batch Tracker shows the line clearance button until the batch is cleared.

### Identify rework
1. On the **Rework** tab click **+ Rework**.
2. Fill the form and click **Save**. Hendrix numbers it RW-2026-001...

| Field | What to enter | Required |
|---|---|---|
| Comes from | A batch, A hold, Other (cannot be changed later) | Yes |
| Batch / Hold / Source | The batch or hold it came from, or a description | Batch or hold yes; Source no |
| Rework material | e.g. Distillate recovered from overfilled carts | Yes |
| Original product | Filled from the batch | No |
| Unit, Quantity | g, kg, mL, L, units, lb | No |
| Why it is reworked | e.g. Overfill recovered | Yes |
| Identified on | Not in the future | Yes |
| Rework tag / METRC tag, Stored at, Rework expires on | Tracking details | No |
| Files (photos, COA), Notes | Supporting files | No |

Details can be edited (**Edit**) only while the rework is **Identified**.

![Rework from source to use: identified, inspected, approved, used, destroyed](shots/facility_rework_list.png)

### Inspect, approve, use or destroy
1. **Inspect** (Edit): **Inspection (what was checked)** and **Analysis (test results / COA)** are required; choose the **Result** (Pass - can be approved / Fail - destroy) and **Inspected by**. Click **Record inspection**.
2. **Approve** (Full, only after a passed inspection): tick **Like-to-like: it goes back into the same product and is safe to use**, add a **Note**, set **Rework expires on** (required). Click **Approve**.
3. **Use in batch** (Edit): choose the **Batch it went into** (required), enter the **Finished product expires on**, **Quantity used** and **Used on**. Click **Record use**.
4. **Destroy** (Full, any time before use): write why, and how it was destroyed (waste log / track-and-trace).

![Approving rework for use](shots/facility_rework_approve.png)

> **Hendrix checks:** rework goes identified → inspected → approved → used (or destroyed), in that order. "Record the inspection and the analysis (test results / COA)." Only Full access approves; failed rework cannot be approved ("Rework that failed inspection cannot be approved. Destroy it."). "Confirm the rework goes into the same product (like-to-like)." Rework cannot go into a batch whose product expires after the rework ("The rework expires before the finished product. It cannot be used in this batch."). After inspection the material, quantity, source and results cannot be changed; used or destroyed rework is closed. Rework is never deleted.

## Time Clock and Badges
Photo ID badges with a secret QR code and barcode, a badge time clock at the door, the daily sign-in sheet and a live list of who is on site. It controls who enters the facility, flags late returns from breaks and gives you an emergency roll call.

**Where:** left menu → **Time Clock and Badges** (tabs **Sign-in sheet**, **On site now**, **Badges**, **Kiosk**). **Who:** View can see the sign-in sheet, who is on site and the kiosk link (everyone can also see their own punches). Edit can also make and print badges. Full can also re-issue lost badges, void punches and add missed punches.
**CSQ:** 1.9

![Sign-in sheet: every punch of the day, a late return in red, a missed punch marked M, and voids listed below](shots/facility_timeclock_sheet.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new employee starts | **Badges** → pick the person → title and photo → **Issue badge** → **Print**. |
| A badge is lost or stolen | **Badges** → the person → **Re-issue (lost)** (Full access), then print the new card. |
| Setting up the door tablet | **Kiosk** tab → **Open kiosk** on the tablet; plug in a barcode / QR scanner or use the camera. |
| Someone forgot their badge | **Sign-in sheet** → **+ Missed punch** (Full access) with the reason. |
| A wrong punch was recorded | Click the time on the sign-in sheet → void with a reason (Full access). |
| Fire alarm or evacuation | **On site now** → **Print roll call**. |
| Someone shows you a badge | Scan its QR code with any phone to see whose it is and whether it is valid. |

### Make a badge (Edit)
1. Open **Badges**. The list shows everyone with access to this license, with their badge ID or **No badge**.
2. Click a person. Their title is suggested from the Org Chart.
3. Enter the **Title on the badge**, click **Upload photo**, use **Zoom** and drag the photo on the card to place it.
4. Click **Issue badge** (or **Save badge** for an existing one). Hendrix gives the badge an ID number and a secret code.
5. Click **Print**. The card prints at 2.125 × 3.375 in (CR80). **Print all badges** prints every issued badge.

![Badge editor with the card preview: photo, title, ID number, QR code and barcode](shots/facility_timeclock_badges.png)

| Field | What to enter | Required |
|---|---|---|
| Title on the badge | e.g. Extraction Technician | No |
| Photo | Image file; cropped square | No |
| Zoom, photo position | Slider; drag on the card | No |

> **Hendrix checks:** only Edit access makes badges, and only for people who work at this license. The badge code is never shown to other users. **Re-issue (lost)** needs Full access and a reason ("Why (the old badge will stop working)"); the old QR code and barcode stop working at once.

### The time clock kiosk
1. On the **Kiosk** tab, copy the link or click **Open kiosk** on the tablet at the entrance. The link is `?kiosk=clock&state=..&lic=..` and works for this license only; no login is needed.
2. With a USB or Bluetooth scanner: people hold the QR code or barcode on their badge to it. With **Use camera**: face in the oval first ("Step 1"), then hold the badge to the camera ("Step 2").
3. Each scan records the person's next punch of the day, in this order: Clock in, 1st break out, 1st break back, 2nd break out, 2nd break back, 3rd break out, 3rd break back, Clock out. The screen shows the photo, name, title, the punch and the time.

![The time clock kiosk waiting for a badge scan](shots/facility_timeclock_kiosk.png)

> **Hendrix checks:** a second scan within a minute is ignored ("Already recorded"). After Clock out the kiosk says "Already clocked out for today". A return from break later than the limit (default 15 / 30 / 15 minutes, set in Settings → Time clock) is flagged with the minutes over ("5 min over the break limit — flagged for review"). Unknown or re-issued badges get "Badge not recognized."; a person without access to this license gets "Not authorized at this license."; a link with a wrong state or license is refused. Punches can only be made by the kiosk or as a missed punch.

### The sign-in sheet
1. Pick the date (today or earlier).
2. Each person has one row: the eight punches and **Worked** (clock in to clock out, less the breaks). A late return shows in red with the minutes over; **M** marks a missed punch added by a manager.
3. Missed punches and voids are listed under the table with the reason and who did it.
4. **Print sheet** prints the day.

**Add a missed punch (Full access):** click **+ Missed punch**.

| Field | What to enter | Required |
|---|---|---|
| Person | Someone at this license | Yes |
| Punch | Clock in ... Clock out | Yes |
| Time | Date and time of the punch | Yes |
| Reason | e.g. Forgot badge, confirmed by supervisor | Yes |

**Void a punch (Full access):** click the time on the sheet, write the reason, confirm.

> **Hendrix checks:** "Choose the person and give the reason." A missed punch cannot be in the future, cannot repeat a punch already recorded that day ("That punch is already recorded for the day. Void it first to replace it."), and is checked against the break limit like a scan. Punches are never edited or deleted; a void needs Full access and a reason, and every missed punch and void goes to the Audit Trail.

### Who is on site now
**On site now** shows everyone whose last punch today is not Clock out: "In since ..." or "On break since ... (x min)", red when over the break limit. The list refreshes every minute. **Print roll call** prints the names with an "Accounted for" box to tick at the muster point.

![On site now: who is in the building and who is on break](shots/facility_timeclock_onsite.png)

### Badge check with a phone
Anyone can scan a badge's QR code with a phone camera. The page (`?badge=CODE`) shows only the person's photo, name, title and "Valid Hendrix badge · ID ...", or that the badge is not valid / not recognized.

![Badge check page on a phone](shots/facility_timeclock_badge_check.png)

### Tips
- The cards at the top show who is on site (and on break), late returns today and how many people at the license have a badge.
- Re-issue a badge as soon as it is reported lost; the printed card is the only key to the time clock.
