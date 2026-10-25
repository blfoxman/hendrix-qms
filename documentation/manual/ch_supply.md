# Suppliers, materials and traceability

This group follows a material from the supplier who makes it to the customer who buys the finished product. You approve the supplier first. Then you receive lots from that supplier into quarantine and accept them, and record which batch uses each lot. Anything suspect goes on hold. Finished batches ship to customers. Because every step is linked, Hendrix can trace any lot, batch or package tag one step back and one step forward in seconds, and you can prove it with a timed mock recall.

Every record in these modules belongs to the license picked at the top of the screen. You can't see, use or ship another license's lots, holds or shipments.

---

## Suppliers
The approved supplier list for the license. It records what each supplier must meet, its credentials, who approved it and on what basis, and its regular reviews. Inspectors use it to check that you buy only from suppliers you have qualified and that you keep watching them.

**Where:** left menu → Suppliers. **Who:** View can see the list, details and reviews, and print the approved supplier list. Edit can add suppliers and edit their details, credentials and files. Full can approve, record reviews, suspend, disqualify, and delete a supplier that was never approved.
**CSQ:** 2A.11, 2A.12.4, 2A.12.9 (testing labs), 2A.5.2 (pest control contractors), 5.1.7 (materials validated through supplier approval)

![Suppliers page: status totals at the top, then one card per supplier with its status, type, risk, credentials and next review date](shots/supply_suppliers_list.png)

The top of the page shows five totals:
- **Approved:** approved, plus approved with conditions.
- **Pending.**
- **Emergency.**
- **Reviews overdue:** the next review date has passed.
- **Credentials expiring:** a credential has expired or expires within 60 days.

Each card shows these badges:
- **High risk** for high-risk suppliers.
- The number of credentials on file.
- **N expiring** when a credential has expired or expires within 60 days.
- **Review overdue** when the next review date has passed.

The left edge of each card is green for approved suppliers, gold for pending or emergency suppliers, and red for suspended or disqualified suppliers.

Hendrix compares the lab names used on Testing records with this list. A red banner names any lab that is used in Testing but isn't approved here with a current ISO/IEC 17025 accreditation (CSQ 2A.12.9 g).

Use the search box and the **All types** / **Every status** filters to narrow the list. **Approved (all)** shows approved and approved-with-conditions suppliers together. **Approved supplier list** opens a printable list of every supplier except pending ones. Disqualified and suspended suppliers are included, with their reasons.

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You want to buy from a new vendor | Suppliers → **+ Add supplier** (it starts as Pending approval) |
| QA has reviewed the questionnaire, certificates and a trial lot | Open the supplier → **Approve** |
| You need material today from a vendor that isn't approved yet | **+ Add supplier** with Status **Emergency** and say how you will check every lot |
| A new testing lab will analyze your batches | Add it as **Testing Lab** with its ISO/IEC 17025 accreditation, then **Approve** |
| A supplier's certificate or accreditation is renewed | Open the supplier → **Edit** → update the credential number, expiry date and file |
| The yearly review is due (every 6 months for high risk) | Open the supplier → **Record review** |
| A supplier sends bad lots and you want to stop buying for now | Open the supplier → **Suspend** with the reason |
| A supplier fails badly and must never be used again | Open the supplier → **Disqualify** with the reason |
| A supplier was added by mistake and never approved | Open the supplier → **Delete** |
| An inspector asks for the approved supplier list | **Approved supplier list** (prints) |

### Add or edit a supplier
1. Click **+ Add supplier**. To change an existing supplier, open it and click **Edit**.
2. Fill in the form. Add each credential with **+ Add credential**. Then choose its type, enter its number and expiry date, and click **File** to attach the certificate.
3. Click **Add supplier** (or **Save changes**). A new supplier opens so you can check it.

![Add supplier form filled in for a packaging supplier with a food-grade certificate attached](shots/supply_suppliers_form.png)

| Field | What to enter | Required |
|---|---|---|
| Supplier name | Company name, e.g. "Futurola USA". Must be unique for this license. | Yes |
| Category / type | Cones/Pre-roll Supplies, Packaging, Distillate/Extract, Terpenes, Ingredients, Testing Lab, Equipment, Labels, Co-manufacturer, Pest Control, Waste Disposal, Chemicals / Sanitation, Gases / Solvents, Transport / Distribution, Service Provider, Biomass / Flower (cannabis), Nutrients / Fertilizers, Grow Media / Soil, Clones / Seeds, Crop Protection Products, Other | No (default Other) |
| Risk | Low, Medium or High. High-risk suppliers are reviewed every 6 months, the others every 12 months. | No (default Medium) |
| Status (new suppliers only) | **Pending approval**, or **Emergency (temporary, not yet approved)** | No (default Pending) |
| How materials are checked before use | Shown only for Emergency. For example: "COA reviewed and in-house test before release". | Yes, for Emergency |
| Products / services supplied | What you buy from them | No |
| Specifications the supplier must meet | For example: food-grade, COA with every lot, inhalation-grade terpenes. Receiving shows this text when a lot arrives. | No |
| Contact name, Contact email, Phone | Sales or quality contact. Traceability uses these during a recall. | No |
| Address | Supplier address | No |
| COA expiry date | Date the supplier's current COA or certificate expires | No |
| Last audit date | Date of your last second- or third-party audit of the supplier | No (needed to approve a Co-manufacturer) |
| Applies to license(s) | Tick the other licenses in the same state that also buy from this supplier. The current license is always ticked. | No |
| Credentials | One row per credential. Type: ISO/IEC 17025 accreditation, State license, Pest control applicator license, Food-grade / GMP certificate, Inhalation-grade statement, Organic / other certification, Insurance, Spec sheet / COA, Audit report, Other. Also number, expiry date and file. For a Testing Lab the first row defaults to ISO/IEC 17025, and for Pest Control to the applicator license. | Type is required for each row you add |
| Ethical sourcing confirmed (CSQ 2A.11 h) | Tick when confirmed | No |
| Notes / certifications | Anything else | No |

> **Hendrix checks:**
> - A name is required, and the same name can't be used twice for one license.
> - Every credential row needs a type.
> - An emergency supplier needs a note on how its materials are checked before use.
> - Only people with Full access can set a status other than Pending or Emergency. Approval always happens through **Approve**.
> - All licenses on a supplier must be in the supplier's state.
> - The license and the person who created the supplier can't be changed later.
> - A disqualified supplier can't be edited.

### Approve a supplier
**Approve** appears for suppliers that are Pending, Emergency or Suspended.
1. Open the supplier and click **Approve**.
2. Write what the approval is based on.
3. Tick **Approve with conditions** if the approval is conditional.
4. Check the **Next review** date and change it if needed.
5. Click **Approve supplier**.

![Approve supplier form with the approval basis filled in](shots/supply_suppliers_approve.png)

| Field | What to enter | Required |
|---|---|---|
| Approval based on | For example: supplier questionnaire, certificates and COA reviewed, trial lot passed incoming inspection | Yes |
| Approve with conditions | Tick to set the status to **Approved with conditions** instead of **Approved** | No |
| Next review | Pre-filled with today plus 6 months (high risk) or 12 months (others) | No |

> **Hendrix checks:**
> - **Only Full access can approve.** If the basis is blank, Hendrix will not approve and shows "Write what the approval is based on."
> - A **Testing Lab** can't be approved until its ISO/IEC 17025 accreditation is recorded as a credential. The form warns you first.
> - A **Co-manufacturer** can't be approved until the **Last audit date** is filled in.
> - Hendrix records your name and the time of approval, and marks the supplier as "ever approved". If the next review is left blank, Hendrix sets it 6 or 12 months ahead based on risk.

### Review a supplier
**Record review** appears for suppliers that are not Pending or Disqualified (Full access only). Review every approved supplier at least once a year. Look at quality, delivery, COAs, deviations and complaints since the last review.
1. Open the supplier → **Record review**.
2. Fill in the form and click **Save review**. The review appears under **Reviews** on the supplier.

![Supplier review form for a pest control contractor](shots/supply_suppliers_review.png)

| Field | What to enter | Required |
|---|---|---|
| Review date | Defaults to today. It can't be in the future. | Yes |
| Rating | Satisfactory, Needs improvement or Unsatisfactory | Yes (default Satisfactory) |
| Result | **Keep approved**, **Approve with conditions**, **Suspend** or **Disqualify** | Yes (default Keep approved) |
| Notes | What you reviewed and found | Yes, for Suspend or Disqualify |

> **Hendrix checks:**
> - Saving a review sets **Last review** to the review date and **Next review** to 6 months later (high risk) or 12 months later (others).
> - The result changes the supplier's status:
>   - **Approve with conditions** sets Approved with conditions.
>   - **Suspend** and **Disqualify** set those statuses and use your notes as the reason.
>   - **Keep approved** makes the supplier Approved. A supplier that is Emergency or Suspended keeps that status.
> - Reviews are permanent. They can't be changed or deleted.

### Suspend, disqualify or delete
- **Suspend:** shown for Approved, Approved with conditions and Emergency suppliers. Write the reason and click **Suspend**. You can approve the supplier again later.
- **Disqualify:** shown for any supplier that isn't already disqualified. Write the reason and click **Disqualify**. A disqualified supplier can no longer be edited, reviewed or used.
- **Delete:** shown only for a supplier that was **never** approved.

| Field | What to enter | Required |
|---|---|---|
| Reason | Why the supplier is suspended or disqualified. It appears on the supplier and on the printed list. | Yes (the button stays greyed out until you type) |

> **Hendrix checks:**
> - Suspend, Disqualify and Delete need Full access.
> - A supplier that was ever approved is never deleted. Hendrix shows "Disqualify it instead of deleting it."
> - Each status change and its reason are saved in the Audit Trail.

### Supplier details
Click any card to open the supplier.

![Supplier detail for an approved testing lab with an accreditation expiring soon](shots/supply_suppliers_detail.png)

The detail shows:
- the status and why;
- for an emergency supplier, how materials are checked;
- products, contact, COA expiry and last audit;
- who approved it and when;
- last and next review;
- the approval basis and specifications;
- every credential, with an expiry badge (green when OK, gold within 60 days, red when expired) and its file;
- every review.

### Tips
- Fill in **Specifications the supplier must meet**. Receiving shows this text to the person checking each delivery.
- Add your transporter as a **Transport / Distribution** supplier and approve it. Shipping then suggests it in the Transporter field.
- The dashboard card shows how many suppliers are approved, how many are pending, and how many have an overdue review or an expiring credential.

---

## Receiving
Every incoming delivery is recorded here as a numbered lot. It goes into quarantine, is inspected on arrival, and has its COA reviewed before anyone can use it. The **Inventory** tab tracks what is left in each lot and which batches used it. This is how you trace one step back to the supplier.

**Where:** left menu → Receiving (tabs **Receiving** and **Inventory**). **Who:** View can see lots, stock and use records, and print the receiving log. Edit can receive lots, edit a lot while it's in quarantine, update the location, files and notes later, and record use. People with Edit on Batch Tracker can also record use. Full can accept or reject lots and void use records.
**CSQ:** 2A.10.2, 2A.9.4, 2A.10.1, 2A.10.3, 2A.12.4; also 3A.1.5, 3B.1.4 and 3C.1.2 (inputs received from approved suppliers and recorded against batches)

![Receiving tab: quarantine totals, then the list of lots with COA, inspection result and status](shots/supply_receiving_list.png)

The Receiving tab shows these totals:
- In quarantine;
- Missing COA (lots in quarantine);
- Received in the last 30 days;
- Rejected in the last 12 months;
- Failed inspection in the last 12 months.

The list shows each lot's number, date, item, supplier, quantity, whether a COA is on file, the inspection result (Pass or Failed) and the status: Quarantine, Accepted, Rejected, On hold, Returned or Destroyed. Search by lot, item, supplier, supplier lot or tag, or filter by status. **Receiving log** prints every lot with its inspection result and decision.

When anything is on hold, a red banner at the top of these tabs lists the open holds.

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A delivery of distillate, cones, cartridges or labels arrives | Receiving → **+ Receive lot** |
| The COA arrives a day after the product | Open the lot (still in quarantine) → **Edit** → tick the COA box and upload the file |
| QA has checked the lot and its COA | Open the lot → **Accept** |
| Cartons are wet, seals are broken or the COA is wrong | Open the lot → **Reject** (the lot goes on hold automatically) |
| An accepted lot is moved to another shelf | Open the lot → **Location / files** |
| Production pulls material for a batch | Inventory → **+ Record use** (or open the lot → **Record use**) |
| A use was recorded against the wrong batch | Inventory → **Void** on the use record, then record it again |
| You suspect a problem with a lot after acceptance | Open the lot → **Put on hold** and/or **Deviation** |
| An inspector asks for receiving records | **Receiving log** (prints) |

### Receive a lot
1. Click **+ Receive lot**.
2. Pick the supplier. Only approved, conditionally approved and emergency suppliers are listed. Hendrix shows the specifications that supplier must meet. For an emergency supplier, it also shows how lots must be checked.
3. Fill in the item and quantity details.
4. Tick each receiving check that passed. Leave a box empty if the check failed.
5. Tick the COA box if the COA or certificate of conformance came with the lot and you checked it against the specs. Upload the COA, invoice, manifest or photos.
6. Click **Receive into quarantine**. Hendrix gives the lot its number, for example RCV-2026-018.

![Receive a lot form filled in for a distillate delivery, with every check ticked and the COA uploaded](shots/supply_receiving_form.png)

| Field | What to enter | Required |
|---|---|---|
| Supplier (approved only) | Pick from the approved list | Yes |
| Received on | Defaults to today. It can't be in the future. | Yes |
| Item received | For example: 98mm pre-roll cones | Yes |
| Category | Packaging, Labels, Hardware (cartridges, batteries), Cones / pre-roll supplies, Ingredients, Terpenes, Distillate / extract, Cannabis (flower, trim, biomass), Chemicals / sanitation, Gases, Solvents, Nutrients / fertilizers, Grow media / soil, Clones / seeds, Crop protection products, Other | No (default Packaging) |
| Quantity | Amount received. Must be more than 0. | Yes |
| Unit | each, g, kg, mL, L, lb, oz, case, roll, box | No (default each) |
| Supplier lot # | The supplier's own lot number | No |
| Expiry / best before | Expiry date | No |
| METRC tag (cannabis) | Package tag for cannabis inputs | No |
| PO / invoice # | Purchase order or invoice number | No |
| Storage location | For example: Quarantine shelf Q1 | No |
| Receiving inspection | Seven checks: Matches the order, invoice or manifest · Packaging intact: no damage, leaks or wet cartons · Clean: no pests, dirt, odors or foreign matter · Seals / tamper evidence intact · Labeled with item, lot and expiry · Temperature and condition OK on arrival · Delivery vehicle clean and secure | No (unticked checks are recorded as failed) |
| COA or certificate of conformance received and reviewed against the specs | Tick when the COA is in hand and checked | No (but needed to accept) |
| Documents | Upload the COA, invoice, manifest or photos | No |
| Inspection notes | What you saw | No |

> **Hendrix checks:**
> - Hendrix will not receive a lot from a supplier that isn't approved. It shows, for example, "Prairie Packaging Group is not approved yet - receive only from approved suppliers (CSQ 2A.11)." If the license has no approved suppliers, the form says so and the button is greyed out.
> - The supplier must be on file for this license.
> - Every new lot starts in **Quarantine**. It can't be used until someone with Full access accepts it.
> - Lots are numbered RCV-year-### per license, and the number can't be changed.
> - The number, supplier, the person who received it and the license can never be changed.

### Accept or reject a lot
**Accept** and **Reject** appear on a lot in quarantine for people with Full access.
1. Click the lot in the list. The detail shows every check (✓ or ✗), the documents and the batches that used it.
2. Click **Accept** or **Reject**.
3. Write your notes and click **Accept lot** or **Reject lot**.

![Lot detail for a lot in quarantine: no COA, one failed check and an emergency supplier](shots/supply_receiving_detail.png)

![Accept form: blocked because no COA is recorded, with the failed check listed](shots/supply_receiving_accept.png)

| Field | What to enter | Required |
|---|---|---|
| Decision notes (Accept) | Why the lot is accepted | Yes, if any receiving check failed or the supplier is an emergency supplier (say how the lot was verified) |
| Reason for rejection (Reject) | Why the lot is rejected | Yes |

> **Hendrix checks:**
> - Only Full access can accept or reject, and only while the lot is in quarantine.
> - **No COA, no acceptance.** **Accept lot** stays greyed out, and Hendrix shows "The lot needs its COA or certificate of conformance before it can be accepted." Edit the lot and add the COA first.
> - If any receiving check failed, you must write why the lot is still accepted, or reject it.
> - A lot from an emergency supplier needs a note on how it was verified.
> - A lot past its expiry date can't be accepted.
> - **A rejected lot is put on hold automatically** (source "Receiving inspection") and kept apart until it is returned to the supplier or destroyed. It can never be released.
> - Hendrix records who decided and when.
> - After the decision, only the storage location, files and inspection notes can change.
> - Lots are never deleted.

### Inventory and recording use
The **Inventory** tab lists every lot that still has quantity left and is Accepted, On hold or in Quarantine. Lots are sorted by item, oldest first.

The tab shows these totals:
- Lots in stock;
- Expired in stock;
- Expiring in 30 days;
- Uses recorded in the last 30 days.

For each item, the oldest accepted lot that hasn't expired gets a **Use first** badge. The expiry badge is gold when a lot expires within a month and red when it has expired. Below the stock list, **Use records** lists every use with its date, lot, batch, quantity and who recorded it.

![Inventory tab: stock by lot with Use first badges, expiry, quantity left and status](shots/supply_receiving_inventory.png)

To record use:
1. Click **+ Record use** on the Inventory tab, or open an accepted lot and click **Record use**.
2. Pick the lot. Only accepted lots that have quantity left and haven't expired are listed, oldest first. If an older lot of the same item exists, Hendrix shows a **FIFO** message naming the lot to use first.
3. Pick the batch and enter the quantity, then click **Record use**.

![Record use form with the FIFO reminder that an older lot should be used first](shots/supply_receiving_use.png)

| Field | What to enter | Required |
|---|---|---|
| Lot (oldest first) | Lot number, item, quantity left, date received, expiry | Yes |
| Used in batch | The batch from Batch Tracker, or "(not for a batch)" | No (pick a batch so the trace works) |
| Quantity | Amount used, in the lot's unit | Yes |
| Date | Defaults to today. It can't be in the future. | No |
| Notes | For example: line, shift | No |

> **Hendrix checks:**
> - You can only use from a lot that is **Accepted**. A lot in quarantine or on hold can't be used.
> - You can't use a lot after its expiry date.
> - You can't use more than is left. Hendrix shows, for example, "Only 3800 each left in lot RCV-2026-014."
> - The batch must belong to this license and must not be void.
> - Recording use lowers the quantity left on the lot. You can't change it by editing the lot.
> - A use record can't be changed. To fix one, someone with Full access to Receiving clicks **Void**, writes a reason, and the quantity goes back to the lot. Then record the use again.
> - Use records are never deleted.

### Tips
- Always pick the batch when recording use. That link is what lets Traceability and Recall trace a batch back to its supplier lots.
- Keep lots in quarantine on a marked shelf, and put that shelf in **Storage location**.

---

## Hold and Release
This is the quarantine register for anything that must not be used or shipped: rejected lots, suspect batches, single packages and customer returns. Each hold is numbered, says why it was placed, and stays open until someone with Full access decides it and writes the evidence.

**Where:** left menu → Hold and Release (also the **Hold and Release** tab next to Receiving). The tab shows the number of open holds. **Who:** View can see holds. Edit can put a lot, batch, package or return on hold. Full can decide a hold (release, destroy, return, rework).
**CSQ:** 2A.10.4, 2A.12.9, 1.8, 3B.2.2

![Hold and Release tab: open holds in red with their age, and a released hold below](shots/supply_holds_list.png)

The page shows these totals:
- Open holds;
- Oldest open hold, in days (red when older than 30 days);
- Customer returns in the last 12 months;
- Holds decided in the last 12 months.

Each card shows the status (ON HOLD, released, destroyed, returned, reworked), what kind of item is held, the source, the hold number, the item, the reason, who placed it and when, how many days it has been open, and the location. Filter by **All holds**, **Open**, **Released**, **Destroyed**, **Returned** or **Reworked**, or search.

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A lot is rejected at receiving | Nothing: Hendrix opens the hold automatically |
| A batch fails its lab test | Hold and Release → **+ Put on hold** → What is held: Batch, Source: Failed test |
| A complaint makes you doubt a batch | **+ Put on hold** → Batch, Source: Complaint |
| A single package tag is damaged or mislabeled | **+ Put on hold** → Package tag |
| A dispensary returns product | Shipping → open the shipment → **Record return** (opens the hold form pre-filled) |
| An accepted lot looks contaminated | Receiving → open the lot → **Put on hold** |
| A recall is started | In the recall, **Put every affected batch and lot on hold** |
| QA has checked the retained sample and the product is fine | Open the hold → **Decide** → Release |
| Held product must be scrapped or sent back | Open the hold → **Decide** → Destroy / Return to supplier / Rework |

### Put something on hold
1. Click **+ Put on hold** (red button).
2. Choose what is held and the source, and fill in the rest of the form.
3. Mark the product with a HOLD tag, move it to the quarantine area, and click **Put on hold**. Hendrix gives the hold its number, for example HOLD-2026-007.

![Put on hold form for a gummy batch after a consumer complaint](shots/supply_holds_form.png)

| Field | What to enter | Required |
|---|---|---|
| What is held | Received lot, Batch, Package tag, Customer return, Other | Yes (default Received lot) |
| Source | Receiving inspection, Failed test, Deviation, Customer return, Complaint, Recall, Storage / expiry, Other | Yes (default Deviation; Customer return for returns) |
| Lot | Shown for Received lot. Only lots in quarantine or accepted are listed. | Yes, for Received lot |
| Batch | Shown for every kind except Received lot | Yes, for Batch |
| Package tag | Shown for Package tag, Customer return and Batch | Yes, for Package tag |
| Description | Shown for Package tag, Customer return and Other. For example: "12 cartridges returned by Dispensary A". | Yes for Other and Customer return, unless a batch is picked |
| Quantity held | For example: 40 units | No |
| Held at (location) | Defaults to "Quarantine area" | No |
| Reason | Why it is held | Yes |

> **Hendrix checks:**
> - You need Edit access to Hold and Release to place a hold.
> - A reason is always required.
> - A lot that is already on hold, returned or destroyed can't be held again.
> - **A lot on hold can't be used.** Its status changes to On hold.
> - **A batch on hold, or a package tag on hold, can't be shipped.**
> - Holds are numbered HOLD-year-### per license.
> - While a hold is open, only its location and linked deviation can change. What is held and why can't be changed.

### Decide a hold
**Decide** appears on open holds for people with Full access.
1. Click the hold card, then **Decide**.
2. Choose the decision, write the reason or evidence, and click **Save decision**.

![Decide form: destroying a customer return, with the reminder to record it in the Waste Destruction Log](shots/supply_holds_decide.png)

| Field | What to enter | Required |
|---|---|---|
| Decision | **Release (approved for use)**, **Destroy**, **Return to supplier** (only for received lots and customer returns), **Rework** | Yes |
| Reason / evidence for the decision | What you checked and found | Yes |

When you choose Destroy, Hendrix reminds you to record the destruction in the Waste Destruction Log and, for cannabis, in METRC.

> **Hendrix checks:**
> - Only Full access to Hold and Release can decide a hold (CSQ 2A.10.4), and a reason is required.
> - **A lot rejected at receiving can't be released.** Release isn't offered for it. Return it to the supplier or destroy it.
> - **A batch with a failed test and no passing retest after it can't be released.** Hendrix shows "This batch has a failed test and no passing retest after it. It cannot be released."
> - For a held lot, the decision sets the lot's status:
>   - **Release** puts the lot back to what it was before the hold (accepted or quarantine).
>   - **Destroy** marks the lot Destroyed. **Return to supplier** marks it Returned.
>   - **Rework** puts the lot back into quarantine.
> - Hendrix records who decided and when. A decided hold can't be changed.
> - Holds are never deleted.

### Tips
- The hold detail has a **Deviation** button for open holds. Use it to report a deviation that is already linked to the hold.
- A red banner on the Receiving, Inventory and Shipping tabs lists open holds so nobody misses them.
- Rework can be recorded from a hold in Line Clearance and Rework.

---

## Shipping
Each shipment is recorded with the customer, state manifest, transporter, the batches and package tags loaded, and a pre-load inspection that must pass. This is your one-step-forward record. It shows exactly which customer received each batch and tag.

**Where:** left menu → Shipping (also the **Shipping** tab next to Receiving). **Who:** View can see shipments and print the shipping log. Edit can record shipments, mark them delivered and add a missing manifest number. Full can cancel a shipment. Recording a customer return needs Edit on Hold and Release.
**CSQ:** 2A.9.4, 2A.10.1, 1.8

![Shipping tab: shipments in the last 30 days, in transit, customers and missing manifest numbers](shots/supply_shipping_list.png)

The page shows these totals:
- Shipments in the last 30 days;
- In transit;
- Customers in the last 12 months;
- Missing manifest #.

The list shows the shipment number, date, customer, batches, manifest number (a red **Missing** badge when blank) and status: shipped, delivered or cancelled. Search by customer, batch, tag or manifest, or filter by status. **Shipping log** prints every shipment with its items and pre-load inspection.

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A van is loaded for a dispensary order | Shipping → **+ New shipment** |
| The dispensary confirms receipt | Open the shipment → **Mark delivered** |
| The METRC manifest number was not ready at loading | Open the shipment → **Add manifest #** |
| The dispensary returns product | Open the shipment → **Record return** |
| A shipment was entered by mistake or never left | Open the shipment → **Cancel** with the reason (Full) |
| The driver needs a printed copy | Open the shipment → **Print** |
| An inspector asks where a batch went | **Shipping log**, or Traceability and Recall → Trace |

### Record a shipment
1. Click **+ New shipment** and fill in the customer, manifest and transport details.
2. Add a row for each batch and package. Under each row Hendrix shows the batch status:
   - **Test passed** (green);
   - **Test not final yet** or **No lab test on file** (gold);
   - **On hold (HOLD-…): cannot ship** or **Failed test, no passing retest: cannot ship** (red).
3. Carry out the pre-load inspection and tick each check.
4. Upload the manifest or invoice if you have it, and click **Record shipment**. Hendrix gives the shipment its number, for example SHP-2026-033.

![New shipment form: the second batch is on hold, so Record shipment stays greyed out](shots/supply_shipping_form.png)

| Field | What to enter | Required |
|---|---|---|
| Ship date | Defaults to today. It can't be in the future. | Yes |
| Customer | Dispensary name | Yes |
| Customer license # | Customer's state license | No |
| Destination address | Delivery address | No |
| State manifest # | METRC manifest number | No (shows as Missing until added) |
| Transporter | Own vehicle or transporter. Approved Transport / Distribution suppliers are suggested. | No |
| Driver | Driver name | No |
| Vehicle | Plate or unit | No |
| Batches and packages | One row each: batch, package tag, quantity, unit (default "units"). Use **+ Add batch / package** for more rows and × to remove one. | At least one batch |
| Pre-load inspection | Eight checks: Vehicle clean, dry and free of pests · Vehicle secure and locked; product out of sight · Temperature suitable for the product · Packages sealed and tamper evident · Products and quantities match the manifest · Labels and package tags correct · Every batch is released: tests passed, nothing on hold · No damage while loading; kept apart from chemicals and non-cannabis goods | All eight must be ticked |
| Documents | Manifest, invoice | No |
| Notes | Anything else | No |

> **Hendrix checks:**
> - The customer and at least one batch are required. Every item must name its batch so it can be traced.
> - **Every pre-load check must pass.** Otherwise **Record shipment** stays greyed out, and Hendrix shows "Every pre-load inspection check must pass before loading (CSQ 2A.9.4)."
> - **A batch on hold can't be shipped,** and neither can a package tag on hold.
> - **A batch with a failed test and no passing retest can't be shipped.**
> - Batches must belong to this license and must not be void.
> - Shipments are numbered SHP-year-### per license.

### After shipping
Open a shipment to see the printed record: customer, manifest, transporter, items, and the pass/fail result of each pre-load check.

![Shipment detail with batches, package tags, the pre-load inspection and the action buttons](shots/supply_shipping_detail.png)

- **Mark delivered** (Edit, shipped shipments): sets the delivery date to today.
- **Add manifest #** (Edit, shown when the manifest number is blank): enter the state manifest number.
- **Record return** (Edit on Hold and Release): opens **Put on hold** pre-filled as a Customer return, with the first batch and tag, the description "Returned by <customer> (<shipment>)", and a link to the shipment. Add the quantity and reason.
- **Cancel** (Full): write the reason and click **Cancel shipment**.
- **Print:** prints this shipment.

> **Hendrix checks:**
> - What was shipped, to whom and when can't be changed. Cancel the shipment with a reason and record it again.
> - Only the status, delivery date, cancel reason, notes, files and manifest number can change later.
> - A delivered shipment can't go back to shipped. A cancelled shipment can't be changed.
> - Cancelling needs Full access and a reason.
> - Shipments are never deleted.

---

## Traceability and Recall
This module traces any lot, batch or package tag one step back (suppliers and input lots) and one step forward (customers). It also runs timed mock recalls and real recalls or withdrawals, and keeps the recall team and contact list. CSQ requires a mock recall at least once a year, with the trace completed in under 2 hours.

**Where:** left menu → Traceability and Recall (tabs **Trace**, **Mock recalls and recalls**, **Recall team and contacts**). **Who:** View can trace, see exercises and contacts, and print. People with View here see the full trace even without access to Receiving or Shipping. Edit can run mock recalls, save progress, and add, edit and verify contacts. Full can start and close real recalls and market withdrawals, and cancel any exercise.
**CSQ:** 1.8, 1.11, 2A.10.1

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A customer asks which supplier lot is in a cartridge | Trace → type the package tag |
| A supplier warns about a bad lot | Trace → type the supplier lot number → see every batch and customer |
| The yearly mock recall is due | **Start mock recall**, or trace a batch → **Start mock recall from this** |
| Product must be pulled from the market | **Start recall** (Full) → **Put every affected batch and lot on hold** |
| Product is pulled for a non-safety reason | **Start recall** → Type: Market withdrawal |
| The inspector asks for the recall team and contacts | Recall team and contacts → **Print contact list** |
| New customers have been shipped to | Recall team and contacts → **Add N customers from shipments** |
| Yearly check of the contact list | Call or confirm each contact → **Mark all verified today** |
| A mock recall failed | Open it → **Deviation** |

### Trace a lot, batch or package tag
1. On the **Trace** tab, type a received lot number (RCV-…), a supplier lot, a METRC tag, an item, a batch number or SKU, or part of a package tag (at least 3 characters).
2. Click the matching result.
3. Hendrix shows totals: input lots, suppliers, batches, shipments, customers, quantity shipped and open holds. It then shows three columns:
   - **One step back:** each supplier and lot, with the item, supplier lot, date received, quantity and quantity left on site, location, whether a COA is on file, and the supplier's contact details. The box is marked **ON HOLD** when the lot is held.
   - **Batches:** each batch made with those inputs, with its test results. The box is marked **ON HOLD** when the batch is held.
   - **One step forward:** each customer, with the quantity, shipments, dates, manifest numbers and package tags.
4. Click **Print trace** for a printed report, or **Start mock recall from this** (Edit).

![Trace of a cartridge batch: three supplier lots back, one batch, three customers forward](shots/supply_recall_trace.png)

How the trace works:
- Tracing a lot shows the batches that used it, and the customers who received those batches.
- Tracing a batch shows the lots used in it.
- Tracing a package tag that matches a lot's METRC tag traces that lot.
- Tracing a finished package tag shows only the customers who received that tag.
- The trace uses the use records from Inventory, so a batch with no recorded use shows "No received lots recorded against this batch. Record use under Inventory."

### Start a mock recall, recall or withdrawal
1. Click **Start mock recall** (Edit) or **Start recall** (Full). From a trace you can also click **Start mock recall from this**.
2. Fill in the form and pick what to trace.
3. Click **Start the clock** (mock), **Start recall** or **Start withdrawal**. The clock starts on the server at that moment. Mock recalls are numbered MOCK-year-###, and recalls and withdrawals RCL-year-###.

![Start recall form: Class II recall of a cartridge hardware lot](shots/supply_recall_start.png)

| Field | What to enter | Required |
|---|---|---|
| Type | **Mock recall (yearly test, timed)**. With Full access also **Recall (product leaves the market)** or **Market withdrawal**. | Yes (default Mock recall) |
| Class | Recalls and withdrawals only: Class I (serious health risk), Class II (temporary or reversible health risk), Class III (unlikely to cause harm) | No |
| Lot, batch or package tag | Search and click the item to trace. **Change** picks another. | Yes |
| Reason | Mock: for example "Yearly mock recall 2026". Recall: what is wrong with the product. | Yes, for a recall or withdrawal |

> **Hendrix checks:**
> - A mock recall needs Edit access. A recall or withdrawal needs Full access and a reason.
> - You must pick something to trace.
> - The number, type, start time and traced product can never be changed after the start.

### Run the exercise against the clock
Open the exercise from the **Mock recalls and recalls** tab, or from the red "running" banner at the top of the page.

![Mock recall in progress: elapsed time, live trace, steps with time stamps, contacts and quantity reconciliation](shots/supply_recall_run.png)

1. Watch the **Elapsed** clock (limit 2:00:00). It is green, then gold after 90 minutes, then red after 2 hours.
2. Work through the steps and tick each one. Hendrix stamps the time each step is first ticked (+mm:ss from the start).
   - **Mock recall (8 steps):**
     1. Recall team assembled and roles assigned.
     2. Affected product identified (lot, batch, package tags).
     3. Traced one step back: every input lot and its supplier.
     4. Traced one step forward: every customer that received it.
     5. Quantities reconciled: made, shipped, on hand.
     6. Product still on site located (could be put on hold).
     7. Customer, regulator and certification body contacts confirmed current.
     8. Results reviewed by the recall coordinator.
   - **Recall or withdrawal (12 steps):**
     1. Team assembled.
     2. Affected product identified.
     3. All affected product on site put on hold.
     4. Traced back.
     5. Traced forward.
     6. Regulator notified.
     7. Certification body notified.
     8. Every customer notified.
     9. Product recovered from customers.
     10. Quantities reconciled.
     11. Recovered product destroyed or reworked (Waste log / METRC).
     12. Recall report and root cause (deviation / CAPA).
3. In a real recall or withdrawal, click **Put every affected batch and lot on hold**. You need Edit on Hold and Release. Hendrix opens a hold (source Recall) for each traced batch and each traced lot that is accepted or in quarantine, then ticks the hold step.
4. Tick each contact as you confirm it (mock) or notify it (recall). Hendrix records the time. Only the customers in this trace are listed. A message names any traced customer with no contact on file.
5. Fill in the quantity reconciliation. Hendrix shows **Accounted for: N% of what was made** (shipped plus on hand, compared with made or received). The line is red when the gap is more than 1%.
6. Write the findings and any corrective actions, and attach call logs or notices.
7. Click **Save progress** at any time. When you're done, click **Stop the clock and close**.

| Field | What to enter | Required |
|---|---|---|
| Steps | Tick each step as it's done | All, to close a real recall. All within 2 hours, for a mock to pass. |
| Contacts confirmed / Notified | Tick each contact | No |
| Made / received | Quantity made or received | No |
| Shipped | Pre-filled from the trace | No |
| On hand | Quantity still on site | No |
| Could be recovered (mock) / Recovered (recall) | Quantity | No |
| Findings | What worked, what was slow or missing | Yes, to close |
| Corrective actions | What you'll change | No |
| Attachments | Call log, notices | No |

> **Hendrix checks:**
> - **The clock runs on the server.** The start and end times and the duration can't be edited.
> - A **mock recall passes** only when every step is ticked and it is closed within 120 minutes. Otherwise the result is **Fail**, and a **Deviation** button appears so you can report it.
> - A **real recall or withdrawal** can't be closed until every step is done ("Complete every recall step before closing."). Its result is **Completed**.
> - You can't close without findings ("Write the findings before closing.").
> - Closing a mock needs Edit. Closing a recall or withdrawal needs Full.
> - **Cancel** needs Full access and a reason.
> - A closed or cancelled exercise can't be changed.
> - Recall records are never deleted.
> - When the exercise is saved, Hendrix keeps a copy of the trace (lots, batches, customers, shipments).
> - **Print report** prints the steps with their times, the contacts, the quantities, the findings and the full trace.

### Mock recalls and recalls tab
![Exercises tab: last mock recall, next due date, open exercises and the list of past exercises](shots/supply_recall_exercises.png)

The totals show:
- **Last mock recall:** date, duration and result.
- **Next due:** 12 months after the last closed mock. It shows "Now" in red if no mock has ever been closed, and is red when overdue.
- **Open:** exercises in progress.
- **Real recalls / withdrawals.**

The table lists every exercise with its number, type, what was traced, start time, duration (or **Running**), result and who started it. Click a row to open it.

### Recall team and contacts
![Recall team and contacts tab: team, emergency services, regulators and certification body, each with a verified date](shots/supply_recall_contacts.png)

Contacts are grouped by type: Recall team, Emergency services, Regulators, Certification body, Customers, Suppliers, Testing lab, Other. Each contact shows a **Verified** badge. It is red when the contact has never been verified or was last verified more than 12 months ago.

- A red banner lists any required group with no active contact: **Recall team, Emergency services, Regulators, Certification body** (CSQ 1.8).
- A second banner counts the contacts not verified in the last 12 months.
- **+ Add contact** and **Edit** open the contact form.
- **Add N customers from shipments** adds every customer you have shipped to who isn't on the list yet. Their license number and destination are filled in, and they are marked "not verified".
- **Mark all verified today** sets today's date on every active contact.
- **Print contact list** prints every active contact.

| Field | What to enter | Required |
|---|---|---|
| Type | Recall team, Emergency services, Regulators, Certification body, Customers, Suppliers, Testing lab, Other | Yes (default Recall team) |
| Name | Person or office | Yes |
| Recall role (team) / Role / title (others) | For the team, suggestions are: Recall coordinator, Quality / compliance, Production, Inventory and distribution, Communications, Management, Legal | No |
| Organization | For example: DCR, CSQ certification body, Dispensary A | No |
| Phone, After-hours phone, Email | Contact details | No |
| Verified on | Defaults to today. It can't be in the future. | No |
| Backup / alternate | Tick for a backup person | No |
| Active | Edit only. Untick to switch off a contact you no longer use. | No |
| Notes | Anything else | No |

> **Hendrix checks:**
> - A name is required, and the verified date can't be in the future.
> - Adding and editing contacts needs Edit access.
> - Contacts aren't deleted from this screen. Switch them off (untick **Active**) instead. Only Full access can delete a contact.
> - Every change is saved in the Audit Trail.

### Tips
- Run the mock recall on a real batch that went to several customers. The trace then exercises both directions.
- Record use from Inventory against every batch. A batch with no input lots can't be traced back, and the Standards page shows how many shipped batches can be traced back.
- The dashboard card shows the last mock recall (duration and result), the next due date, and any exercise that is running.
