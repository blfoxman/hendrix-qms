# Video 06 · Products, production and cultivation. Captions use the text as written; speech uses SAY.
NARR = [
    ('i1', "Hendrix QMS training, video six: Products, production and cultivation."),
    ('i2', "In this video: the Line Map, Products, the Production Planner, the Batch Tracker, Testing, Compliance Stickers and Cultivation. Together, they take a product from its recipe, through the batch record and the lab, to the printed label."),

    # Line Map
    ('l1', "The Line Map is a live subway map of production, for general managers and executives. Open it from the top of the Modules menu. The cards count the batches in production, moving, stopped and at the lab, what shipped, and who's on the floor."),
    ('l2', "Each line is a product type. Its stations are Planned, Line clearance, and then the sections of that product's batch record. Every line joins the shared trunk: Lab testing, QC release, Labels and Shipped."),
    ('l3', "Each batch sits at the station its records show. Gold, or the line color, means moving. Red means stopped. Dashed is waiting at the lab, outlined is a plan that hasn't started, and grey is shipped."),
    ('l4', "Click a stopped batch. Nobody marks a stop by hand: Hendrix finds it in the records. This cartridge batch has an open deviation. The box names the source record, who owns it, how long it's been stopped, and what clears it: closing the deviation."),
    ('l5', "Below that is the batch's journey, station by station. The Open buttons take you straight to the module behind it, if you have access to that module."),
    ('l6', "Stops right now lists every stop, longest first, and names the record behind each one. Click a stop to open it. This gummy batch has a cooking temperature out of limits, and a second person must verify the CCP record."),
    ('l7', "Click Stops only to dim every batch that's moving. Only stops, and batches waiting at the lab, stay bright."),
    ('l8', "When several batches share a station, the map shows one marker, like 2 batches at Lab testing. Click it, and pick a batch from the list. A batch whose test is still pending or submitted is waiting, not stopped."),
    ('l9', "Hendrix checks: the map reads everything through one protected database function. It only shows the license picked at the top, and it never shows costs or files."),
    ('l10', "Click Wall display to put the map full screen on an office or floor TV. It refreshes every minute."),
    ('l11', "A batch also stops when it goes too long without an update. Admins set those hours in Settings, under Line Map: from 1 to 72, and 4 by default. Then click Save settings."),

    # Products
    ('p1', "Products is the one catalog of SKUs, flavors, recipes and ingredient prices for a state. Every other module reads it. Open Products from the left menu."),
    ('p2', "Below the main tabs, there's one tab per product type. Each SKU card shows its status, the licenses that make it, its settings, its flavors and its recipes. This pod has no recipe yet, so it's off, and marked Needs formulation."),
    ('p3', "To launch a new product, open its type, here Gummies, and click New SKU. Enter the SKU name and the production settings. The Batch Tracker checks use them. Then type the flavors, one per line."),
    ('p4', "Click Next: formulation. Enter the standard batch size: the Planner scales from it. Add the raw materials from the price library, and enter the amounts. Hendrix shows the batch total and the cost per unit as you type."),
    ('p5', "Hendrix checks: a SKU can't be switched on until it has a formulation, and the database enforces it. Click Save SKU and formulation. The SKU, its flavors and its base recipe are saved, and the SKU is switched on."),
    ('p6', "The Formulation Bank lists every recipe in the state, grouped by product type, with its batch size and cost. Edit changes a recipe, and Duplicate copies it as the starting point for a flavor's own recipe."),
    ('p7', "Tip: once batches have used a SKU, switch it off instead of deleting it. Batch records point to it."),

    # Production Planner
    ('n1', "The Production Planner works out how much of each ingredient a run needs, from your saved formulations. Open it from the left menu. On New plan, pick the product type and the SKU."),
    ('n2', "Click Select all, or pick the flavors. Enter the units per flavor and the date. A buffer like 5% waste is applied exactly to every amount."),
    ('n3', "Click Calculate ingredients. The grand total adds up each ingredient across the flavors, and checks it against accepted lots in Receiving: on hand, short, or not in inventory."),
    ('n4', "Each flavor card shows where its amounts came from, its own recipe or the base recipe, and the tracking blanks for the worksheet."),
    ('n5', "Click Save plan. Hendrix numbers it, and opens it. Worksheets PDF prints one page per flavor for the floor."),
    ('n6', "When the run starts, click Start batch on a flavor card. The Batch Tracker opens with the SKU and flavor filled in, and the plan moves to In production."),
    ('n7', "Hendrix checks: plans are never deleted, only cancelled with a reason, by Full access. And once production has started, the amounts can't change."),

    # Batch Tracker
    ('b1', "The Batch Tracker is the batch production record: every input and output with its METRC tag, built-in weight checks, the testing status and a signature. Open it from the left menu. The tabs across the top are the eight batch types."),
    ('b2', "Each card shows the status, how many steps are recorded on METRC, the system checks, the test status and the line clearance. This one is on QC hold: its joint count is under weight."),
    ('b3', "To start a batch, click New Batch. Enter the batch number, then pick the SKU and the flavor. Only switched-on SKUs made under this license are offered."),
    ('b4', "Hendrix shows the formulation for that flavor. Work down the sections, and tick Recorded on METRC after each step is entered in the state system."),
    ('b5', "The System Check panels recalculate as you type. Eleven hundred eighty joints from 550 grams is more than the SKU's settings predict, so it shows UNDER WEIGHT. Corrected to 998, it passes."),
    ('b6', "Sign in the box, and click Submit and Sign. Hendrix checks: the batch number must be unique under this license, and the SKU must be switched on, and made under this license."),
    ('b7', "To correct a filled-in value, someone with Full access clicks Edit, changes it, and enters the reason for the change. People with Edit access use Continue instead: they can only fill in blank fields."),
    ('b7b', "Click Save changes. View shows the whole record, with the change history: the old value, the new one, who changed it and why. Batches are never deleted, only voided with a reason."),
    ('b8', "When the final package tag is filled in, click Submit for testing. Hendrix creates the Testing record for that tag, and the batch shows Test: Submitted."),

    # Testing
    ('t1', "Testing tracks every mandatory lab test per final package tag: the lab, the result, and the stored COA, read by Hendrix AI. Open Testing from the left menu. The tabs count the records by status."),
    ('t2', "When the lab emails the COA, click Upload COA on the record, and choose the file. Hendrix stores it privately, and reads it."),
    ('t3', "Hendrix fills in the potency and the lab license. The COA says Pass, and its tag matches the sample tag, so the record is marked Passed. If the tag didn't match, Hendrix would flag a tag mismatch, and leave the status unchanged."),
    ('t4', "The analysis opens below the record: the overall result, the potency, and every test category with its analytes. Show analysis and Hide analysis toggle it."),
    ('t5', "To change a record, click Update. Hendrix checks: changing a final result, Passed or Failed, needs Full access and a reason. The database enforces both."),
    ('t6', "A failed test offers Deviation, so the cause is investigated. Elsewhere in Hendrix, a batch with a failed test can't be released or shipped."),

    # Compliance Stickers
    ('s1', "Compliance Stickers holds the label template for each SKU and flavor, and prints the stickers for a tested batch. Open it from the left menu."),
    ('s2', "Click Edit on a template. It holds the product approval number, the servings and weight, the ingredients, the allergen declaration and the warning."),
    ('s3', "The preview shows the label with sample results, and warns you if the text is too long for a one-inch label."),
    ('s4', "Hendrix checks: a license can have only one template per SKU and flavor. A template without ingredients shows No ingredients, and Hendrix flags it again when you print."),
    ('s5', "To print, open Testing, and click Compliance Sticker on a record with a COA analysis. Hendrix picks the template for that SKU and flavor."),
    ('s6', "Set the number of labels, and the first free position on the sheet. On a new printer, print the alignment test sheet, and shift right or down until the boxes sit inside the labels."),
    ('s7', "Potency comes straight from the COA. Click Download PDF, and print it at actual size. Every print is logged, and the print log can never be changed or deleted."),

    # Cultivation
    ('c1', "Cultivation keeps the grow records for cultivation licenses, from propagation to cure. It only appears when the license at the top is a cultivation license. Pick it, and open Cultivation."),
    ('c2', "The cards count active plant batches, harvests on hold, harvests and applications. Each batch shows its cultivar and source, its stage and area, and when it can be harvested."),
    ('c3', "To start a plant batch, click Plant batch. Enter the cultivar and the number of plants, and pick the clone lot from Receiving, and the area."),
    ('c4', "Click Save. Hendrix numbers the batch, and starts it in Propagation. Hendrix checks: propagation material must come from an accepted lot of this license."),
    ('c5', "Open a batch to record its grow work. The buttons depend on the stage: nutrients, crop protection, scouting, stage moves, and harvest."),
    ('c6', "For a spray, click Crop protection. Only pesticides approved in Chemicals and SDS are offered. Enter the label rate, and the re-entry and pre-harvest intervals from the label."),
    ('c7', "Click Record. The earliest harvest moves to fourteen days from today, and the batch shows the pre-harvest warning."),
    ('c7b', "Hendrix checks: a harvest inside the pre-harvest interval is refused. Try to record it now, and Hendrix names the date the interval ends."),
    ('c8', "Tip: the Applications tab lists every feed and spray, and prints them for the inspector."),

    ('z1', "That's products, production and cultivation, and the full Hendrix QMS training series. For every field and every check, see Chapter 7 of the Hendrix QMS User Manual."),
    ('z2', "Thank you for watching."),
]
SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('SKUs', "S K U's"), ('SKU', 'S K U'), ('CSV', 'C S V'), ('HACCP', 'hassip'),
       ('METRC', 'metric'), ('PP-2026-017', 'P P twenty twenty-six oh seventeen'), ('5% waste', 'five percent waste'),
       ('read only', 'read-only'), ('1 to 72', 'one to seventy-two'), ('2 batches', 'two batches'), ('998', 'nine hundred ninety-eight'),
       ('550 grams', 'five hundred fifty grams'), ('UNDER WEIGHT', 'under weight'), ('Test: Submitted', 'Test Submitted'), ('EPA', 'E P A')]
