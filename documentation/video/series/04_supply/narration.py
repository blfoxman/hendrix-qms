# Video 04 - Suppliers, materials and traceability. (key, text): captions use the text, speech uses SAY.
NARR = [
    # ---- Introduction (title card)
    ('t1', "Hendrix QMS training, Video 04: Suppliers, materials and traceability."),
    ('t2', "This video follows a material from the supplier to the customer: Suppliers, Receiving and the Inventory tab, Hold and Release, Shipping, and Traceability and Recall."),

    # ---- Suppliers
    ('s1', "Suppliers is the approved supplier list for the license. The totals show approved and pending suppliers, overdue reviews and expiring credentials."),
    ('s1b', "Each card's left edge is green when the supplier is approved, gold when it's pending or emergency, and red when it's suspended or disqualified."),
    ('s2', "To add a vendor, click Add supplier. Enter the name, the category and the risk, and what you buy from them."),
    ('s3', "Fill in the specifications the supplier must meet, which Receiving shows to the person checking each delivery, and the contact. Then click Add credential, choose its type, and enter the number and the expiry date."),
    ('s4', "Click Add supplier. A new supplier starts as Pending approval, and no lots can be received from it yet."),
    ('s5', "When QA has reviewed the questionnaire, the certificates and a trial lot, click Approve. Hendrix checks: only Full access can approve, and the approval must say what it's based on. With the box empty, Hendrix won't approve."),
    ('s6', "Write the basis, check the next review date, and click Approve supplier. Hendrix records who approved it and when."),
    ('s7', "Review every approved supplier at least once a year, or every six months when it's high risk. Ozark Pest Solutions shows Review overdue. Open it, and click Record review."),
    ('s8', "Pick the rating and the result, write what you looked at, and click Save review. Hendrix moves the next review date forward, and the review can never be changed."),
    ('s9', "Tip: Approved supplier list prints the list for an inspector, including suspended and disqualified suppliers, with their reasons."),

    # ---- Receiving
    ('r1', "In Receiving, every delivery is recorded as a numbered lot. The totals show what's in quarantine and which lots are missing a COA. The list shows each lot's COA, inspection result and status."),
    ('r2', "When a delivery arrives, click Receive lot, and pick the supplier. Only approved, conditional and emergency suppliers are listed, and Hendrix shows the specs they must meet."),
    ('r3', "Enter the item, the category, the quantity and unit, the supplier's lot number, and where it's stored."),
    ('r4', "Tick each receiving check that passed, and leave a box empty if a check failed. Tick the COA box once you've checked the COA against the specs, and upload it."),
    ('r5', "Click Receive into quarantine. Hendrix numbers the lot, and it stays in quarantine until someone with Full access accepts it."),
    ('r6', "To accept it, open the lot and click Accept. Write a short note, and click Accept lot."),
    ('r7', "Hendrix checks: no COA, no acceptance. This label lot has no COA on file, so Accept lot stays greyed out. A failed check, or an emergency supplier, also needs a written reason. And a rejected lot goes on hold automatically."),
    ('r8', "The Inventory tab shows what's left in each lot. The oldest lot of each item that hasn't expired gets a Use first badge."),
    ('r9', "When production pulls material, click Record use, and pick the lot. If an older lot of the same item is still in stock, Hendrix names it, so you use that one first."),
    ('r10', "Pick the batch, enter the quantity, and click Record use. Always pick the batch: that link is what lets Traceability trace a batch back to its supplier lots."),

    # ---- Hold and Release
    ('h1', "Hold and Release is the quarantine register for rejected lots, suspect batches, single packages and customer returns. Open holds are red, and show how many days they've been open."),
    ('h2', "To hold something, click Put on hold, and choose what is held and the source. Here, it's a gummy batch after a customer complaint."),
    ('h3', "Enter the quantity and where it's kept, and write the reason. Tag the product HOLD, move it to quarantine, and click Put on hold."),
    ('h4', "Hendrix numbers the hold. While it's open, the batch can't be shipped. And a lot on hold can't be used."),
    ('h5', "Only someone with Full access decides a hold: open the hold, and click Decide. Hendrix checks: this cartridge batch failed its residual solvents test, with no passing retest, so Hendrix won't release it."),
    ('h6', "Back to the gummies. QA checked the retained samples and found no defects. Click Decide, choose Release, write the evidence, and click Save decision."),
    ('h7', "Hendrix records who decided and when, and a decided hold can't be changed. To scrap held product, choose Destroy, and record it in the Waste Destruction Log."),

    # ---- Shipping
    ('p1', "Shipping records every shipment: the customer, the state manifest, the transporter, and the batches and package tags loaded. A red Missing badge means the manifest number isn't recorded yet."),
    ('p2', "Click New shipment. Enter the customer and their license number, the destination, the manifest number, and the transporter, driver and vehicle."),
    ('p3', "Add a row for each batch and package tag. Under each row, Hendrix shows the batch status. Test passed is green."),
    ('p4', "Hendrix checks: a batch on hold, or with a failed test and no passing retest, can't be shipped. This cartridge batch is on hold, so remove its row."),
    ('p5', "Carry out the pre-load inspection, and tick each check. Record shipment stays greyed out until all eight pass. Then click Record shipment."),
    ('p6', "Open a shipment to see the full record. Add the manifest number here if it wasn't ready at loading. Mark delivered when the customer confirms. And Record return opens a hold for returned product."),

    # ---- Traceability and Recall
    ('c1', "Traceability and Recall traces any lot, batch or package tag one step back to its suppliers, and one step forward to its customers. On the Trace tab, type a lot number, a supplier lot, a batch or a package tag, and click the match."),
    ('c2', "One step back lists every supplier lot used in the batch, with its COA and the supplier's contact. The middle shows the batch and its tests. One step forward lists every customer, with quantities, manifests and package tags."),
    ('c3', "CSQ requires a mock recall every year, finished in under two hours. Click Start mock recall from this, give a reason, and click Start the clock. The clock runs on the server, so nobody can edit it."),
    ('c4', "Work through the steps, and tick each one as it's done. Click Save progress, and Hendrix stamps the time of each step. To carry on, open the exercise again from the Mock recalls and recalls tab."),
    ('c5', "Confirm the contacts, and fill in the quantity reconciliation. Hendrix shows how much of what was made is accounted for."),
    ('c6', "Hendrix checks: you can't close without findings. And a mock recall passes only when every step is ticked and it's closed within two hours. Otherwise it fails, and you can report a deviation."),
    ('c7', "The Recall team and contacts tab keeps the team, emergency services, regulators and customers, each with a verified date. A red badge means it wasn't verified in the last twelve months."),

    # ---- Wrap-up (end card)
    ('w1', "That's Video 04. Next: Video 05, Facility, equipment and people on site."),
    ('w2', "For every field and every check, see the Hendrix QMS User Manual, chapter five: Suppliers, materials and traceability. Thank you for watching."),
]

SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('SKU', 'S K U'), ('CSV', 'C S V'), ('HACCP', 'hassip'),
       ('read only', 'read-only'), ('Video 04', 'video four'), ('Video 05', 'video five'),
       ('Tag the product HOLD', 'Tag the product, hold')]
