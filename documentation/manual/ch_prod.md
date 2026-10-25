# Products, production and cultivation

This chapter covers the production side of Hendrix: the product catalog and recipes, planning a run, the batch record, lab testing, compliance stickers, and (for cultivation licenses) the grow records. These modules feed each other in this order:

**Products** (SKU + formulation) → **Production Planner** (how much of each ingredient) → **Batch Tracker** (the batch record) → **Testing** (lab result and COA) → **Compliance Stickers** (the printed label).

## Line Map
A live "subway map" of production for general managers and executives. Every batch of the license sits at its real station, from plan to shipment. A batch that is stopped turns red, and Hendrix tells you why, which record stopped it, who owns it and what clears it. Inspectors and owners see at a glance what is moving, what is stuck and for how long.

**Where:** left menu → Line Map (top of Modules), and the **Line map** card on the Dashboard. **Who:** View is all it needs. People with View on Line Map see the whole map even without access to the modules behind it. The **Open …** buttons only appear for modules they can open. Admins change the idle time in Settings → Line Map.
**CSQ:** no clause of its own; it shows, in one place, the evidence kept in the modules behind it.

![The Line Map: one line per product type, stations from the batch record, and the shared trunk to lab, release, labels and shipping](shots/prod_linemap_overview.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You start the day and want to know what is in production | Line Map: read the KPI cards and the map |
| A batch is red on the map | Click it: **Why it is stopped** shows the reason, source record, owner and what clears it |
| You want only the problems | Click **Stops only**, or read **Stops right now** (longest first) |
| Several batches sit at one station (for example Lab testing) | Click the "N batches" marker, then pick a batch from the list |
| You want to fix what stopped a batch | Click **Open …** in the reason box (for example **Open Hold and Release**) |
| You want the map on a TV in the office or on the floor | Click **Wall display** (full screen); it refreshes every minute |
| Batches show "No update" too soon or too late | Settings → **Line Map** → change the hours (default 4) |

### Read the map
- **Lines** are product types (Cartridges, Gummies, Pre-Rolls, extraction and so on). Only product types with a batch or a plan in the last 45 days are drawn.
- **Stations** on each line are **Planned**, **Line clearance** and then the sections of that product's batch record (for cartridges: Source Oil / Distillate, Primed Oil, Packaged). All lines then join the shared trunk: **Lab testing → QC release → Labels → Shipped**.
- **Where a batch sits** comes from its records: the last batch-record section with something filled in; Lab testing once a test is submitted; QC release once it passed; Labels once compliance stickers were printed; Shipped once it is on a shipment. A plan from the Production Planner sits on **Planned** until it is started.
- **Colors:** gold or the line color = moving · pulsing dot = worked on in the last 30 minutes · red = stopped · dashed = waiting at the lab · outlined = planned · grey = shipped (shown for 3 days).
- **KPI cards:** in production, moving, stopped (with the longest stop), at the lab, shipped in the last 3 days (and plans waiting) and people on the floor from the Time Clock.

![Click a batch: why it is stopped, the source record, who owns it, what clears it and its journey](shots/prod_linemap_detail.png)

### Why a batch stops
Nobody marks a stop by hand. Hendrix stops a batch by itself when it finds one of these, and the reason box names the record:

| Reason on the map | Comes from | What clears it |
|---|---|---|
| On hold | An open hold on the batch (Hold and Release) | Someone with Full access decides the hold |
| Failed test | A failed test with no passing retest (Testing) | A passing retest |
| QC hold / marked Failed | The batch record status (Batch Tracker) | Change the status, or decide the batch |
| Line clearance | No line clearance, or the last one not cleared (Line Clearance and Rework) | A line clearance that passes |
| Equipment | Equipment on the batch's line clearance is out of service or past calibration (Equipment) | Return to service, or a passing calibration |
| Deviation | An open deviation raised from the batch (QMS) | Close the deviation |
| CCP | A CCP reading out of limits not yet verified by a second person (HACCP) | Verification of the CCP record |
| No update | No change to the batch, its line clearance, tests or CCP records for the idle time (Settings) | Continue the batch record |

A batch at the lab whose test is still Pending or Submitted is **waiting**, not stopped.

> **Hendrix checks:** the map reads everything through one protected database function. It only shows the license picked at the top, only to people with Line Map access for that license, and never shows costs or files. Changing the idle time needs Full access on Settings and must be 1 to 72 hours.

### Change the idle time
1. Go to **Settings** → **Line Map**.
2. Enter the hours a batch in production can go without an update before it shows as stopped.
3. Click **Save settings**.

![Settings → Line Map](shots/prod_linemap_settings.png)

| Field | What to enter | Required |
|---|---|---|
| Hours without an update | 1 to 72 hours (default 4) | Yes |


## Products
Products is the one catalog of SKUs, flavors, formulations (recipes) and ingredient prices for a state. Every other module reads it. An inspector sees that every product has a defined specification and recipe before it can be made.

**Where:** left menu → Products. The page belongs to the **state** you picked at the top. All licenses in that state share it, and other states keep their own catalog. **Who:** Products has three access lines on Team and Access:
- **Products (SKUs and flavors):** View can see SKUs and flavors. Edit can add and edit SKUs and flavors and switch SKUs on or off. Full can delete SKUs and flavors.
- **Formulation Bank (recipes):** View can see the Formulation Bank tab and which recipe each flavor uses. Edit can add, edit and duplicate formulations. Full can delete formulations. Without View you never see a recipe anywhere in Hendrix.
- **Ingredient Prices:** View can see the price list. Edit can add and edit prices. Full can delete prices.

The left-menu item appears if you have View on any of the three. To create a new SKU you need Edit on both Products and Formulation Bank.

**CSQ:** 2A.12.4, 2A.12.7, 3B.1.10, 3B.1.12, 3B.2.3, 3C.1.2, 3C.1.8, 3C.1.10, 3C.2.4, 4A.3, 5.4.1, 5.4.2

![SKUs and Flavors tab: Cartridges SKUs, one switched off because it has no formulation](shots/prod_products_skus.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You launch a new product (for example a 20-pack gummy) | Products → **+ New SKU**. Enter the details and flavors, then the base formulation. |
| A SKU gets a new flavor | On the SKU card → **Flavors** → type the names under **Add flavors** → **+ Add flavors**. |
| One flavor needs a different recipe from the rest (for example its own terpene) | **Flavors** → **Own recipe** on that flavor row. |
| A recipe changes (new ratio, new hardware) | **Formulation Bank** tab → **Edit** on the formulation. To keep the old one as a starting point, use **Duplicate**. |
| You stop making a SKU for now | SKU card → **Switch off**. It disappears from the Batch Tracker and Planner but stays on old records. |
| A flavor is discontinued | **Flavors** → **Hide**. It stops showing in new batches. |
| Supplier prices change | **Ingredient Prices** tab → **Edit** on the item. |
| A SKU is made at only one of your licenses | SKU card → **Edit** → untick **Every license in …** and tick the licenses. |

### Read the SKUs and Flavors tab
The tab row under the page title holds **SKUs and Flavors**, **Formulation Bank (n)** and **Ingredient Prices (n)**. Below it, a second row has one tab per product type: Ethanol Extraction, BHO Extraction, Pre-Rolls, Cartridges, Gummies, Infused Flower, Moon Rocks and Snow Caps. The number in brackets is how many SKUs that type has.

Each SKU card shows:
- a status badge: **Active** (switched on), **Needs formulation** (off, with no recipe yet) or **Off**;
- the licenses it is made under;
- its production settings and its flavors;
- whether it has a base recipe and how many flavor recipes;
- the buttons **Flavors**, **Base recipe** (or **Add recipe**), **Edit**, **Switch on / Switch off** and **Delete**, depending on your access.

A red banner at the top counts the SKUs that still need a formulation. Use the search box to find a SKU or flavor by name.

### Create a new SKU
1. Open the product type tab, then click **+ New SKU**. The wizard opens on that type.
2. Fill in step 1 (details and flavors), then click **Next: formulation**.
3. Fill in step 2 (the base recipe). Hendrix shows the batch total and the cost per unit as you type.
4. Click **Save SKU and formulation**. The SKU, its flavors and its base recipe are saved, and the SKU is switched on.

![New SKU, step 1: details, production settings and flavors](shots/prod_products_wizard1.png)

**Step 1: details**

| Field | What to enter | Required |
|---|---|---|
| Product type | One of the 8 product types. You cannot change it after saving. | Yes |
| SKU name | The product name, for example "Muha Meds 2G AIO". It must be unique for that product type in the state. | Yes |
| Made under | Leave **Every license in [state]** ticked, or untick it and tick the licenses that make it. | Yes (default: every license) |
| Production settings | These depend on the type (see the table below). They drive the Batch Tracker checks and the Planner. Number fields must be numbers. | No |
| This SKU has flavors | Untick it for a plain SKU with no flavors. | - |
| Flavors - one per line | One flavor per line. Blank lines and repeated names are dropped, and the count under the box shows how many will be saved. | No |

Production settings by product type:

| Product type | Settings |
|---|---|
| Pre-Rolls | Grams per joint, filled / infused; Grams per joint after coating (blank = no coating step); Coating step (Kief or Diamond); Flower used (Infused or Ground); Package name (for example Jar or Mylar); Joints per package (blank = no packaging check); Infusion ingredients used (THCA, Terpene, Live Resin, HTE, Decarbed Cured Resin, Distillate, Trim, THCA (internal)) |
| BHO Extraction | Makes two products (THCA + HTE): No or Yes |
| Cartridges | Oil per cartridge (g) |
| Gummies | Grams per gummy; Gummies per package |
| Infused Flower, Moon Rocks, Snow Caps | Unit size (g) |
| Ethanol Extraction | None |

![New SKU, step 2: the base formulation with batch total and cost per unit](shots/prod_products_wizard2.png)

**Step 2: formulation** (the same fields appear in **New formulation** and **Edit formulation**)

| Field | What to enter | Required |
|---|---|---|
| Standard batch size (units) | The number of units this recipe makes, for example 1000. The Planner scales from this number. | No, but the Planner can only use a recipe that has it |
| Recipe name (optional) | Leave blank to name it "[SKU] — base recipe" (or "[SKU] — [flavor]"). | No |
| Raw Materials | One line per material: Material, Qty, Unit, Cost / Unit. Use **+ Add Material**, or pick from **+ Add from price library...** to fill the name, unit and price. | At least one line |
| Hardware & Packaging | Item, Qty, Unit, Cost / Unit. Use **+ Add Item**. | No |
| Labor | Role / Task, Hours, Unit, Rate / Hour. Use **+ Add Role / Task**. | No |
| Notes | Any recipe instructions. | No |

> **Hendrix checks:**
> - A SKU name that already exists for that product type in the state is refused: "A SKU with that name already exists for this product type in [state]."
> - The formulation needs at least one raw material ("Add at least one raw material."). Every named line needs a quantity, and a cost, if you enter one, must be a number.
> - A SKU cannot be switched on until it has at least one formulation: "Enter a formulation for this SKU before it can be switched on." The database enforces this, not only the screen.
> - If the SKU saves but its formulation does not, Hendrix tells you that the SKU is saved but not switched on, and you can fix it and press Save again.
> - The price library only offers items tagged for this product type (or for all types).

### Manage flavors and flavor recipes
1. On the SKU card, click **Flavors**.
2. The table lists each flavor with its recipe status: **Own recipe**, **Uses base recipe** or **No recipe**.
3. To add flavors, type them one per line in **Add flavors - one per line** and click **+ Add flavors**. Names already on the SKU are skipped.
4. Per flavor you can use **Rename**, **Own recipe** / **Edit recipe**, **Hide** / **Show** and **Delete** (Full access).

Clicking **Own recipe** opens the formulation editor locked to that SKU and flavor. Fill it in as in step 2 above and click **Save formulation**.

> **Hendrix checks:** a flavor name can only be on a SKU once ("That flavor is already on this SKU."). A flavor recipe must use a flavor of the same SKU. Deleting a flavor also deletes its own recipe.

### Work in the Formulation Bank
The **Formulation Bank** tab lists every formulation in the state, grouped by product type. Each card shows the recipe name, SKU, flavor (or "All flavors (base)"), the number of lines, the batch size, the batch cost and the first raw materials.

![Formulation Bank: recipes grouped by product type with batch size and cost](shots/prod_products_bank.png)

- **+ New formulation:** pick the Product type, SKU and Flavor ("All flavors (base recipe)" or one flavor), then fill in the recipe.
- **Edit:** change the recipe. The product type, SKU and flavor are fixed once saved.
- **Duplicate:** opens a copy as a new formulation for the same SKU, so you can save it for another flavor.
- **✕** (Full access): deletes the formulation. If it is the SKU's only formulation, Hendrix warns you, and the SKU is switched off automatically.

> **Hendrix checks:** each SKU has one base recipe, and each flavor at most one own recipe ("That SKU / flavor already has a formulation. Edit that one instead."). Deleting the last formulation of a SKU switches the SKU off.

### Keep the ingredient price list
The **Ingredient Prices** tab holds the prices for the state. Recipes pick from this list, and recipe costs use them.

![Ingredient Prices: adding Kief for pre-rolls](shots/prod_products_prices.png)

1. Fill in the form at the top and click **+ Add price**.
2. To change a price, click **Edit** on its row, change it and click **Save changes**. To delete a price, click **Delete** (Full access).

| Field | What to enter | Required |
|---|---|---|
| Category | Raw Materials, Hardware & Packaging or Labor | Yes (default Raw Materials) |
| Name | For example "Distillate" | Yes |
| Unit | For example g, each, hour | No |
| Cost / unit ($) (Rate / hour for Labor) | A number | No, but it must be a number |
| Used for | Tick the product types it applies to. Leave all unticked for every type. | No |

### Edit, switch off or delete a SKU
- **Edit** opens **Edit SKU**: SKU name, Made under, the production settings and **This SKU has flavors**. The product type cannot change.
- **Switch off / Switch on** removes the SKU from (or returns it to) the Batch Tracker, Planner and label lists. Old records keep the SKU name.
- **Delete** (Full access) deletes the SKU with its flavors and formulations, after a confirmation.

> **Hendrix checks:** a SKU cannot be moved to another state, and its product type cannot change ("The product type of a SKU cannot be changed. Create a new SKU instead."). A SKU can only be limited to licenses in its own state. Every change to SKUs, flavors, formulations and prices is written to the Audit Trail.

### Tips
- Enter the base recipe first. One base recipe covers every flavor, and the Planner names the terpene per flavor for you.
- Switch a SKU off instead of deleting it once batches have used it. Batch records point to it.
- Recipes are company know-how. Give Formulation Bank access only to the people who need it. Production techs still see the SKU and flavor lists.

## Production Planner
The Production Planner works out how much of each ingredient a run needs per flavor from your saved formulations. It checks the total against accepted inventory, prints production worksheets and keeps a numbered plan that batches are started from. It shows an inspector that production follows the approved formulation.

**Where:** left menu → Production Planner. Plans belong to the license picked at the top. **Who:** View can see plans, calculate ingredients and download worksheets. Edit can save plans, start batches from a plan (this also needs Edit on the Batch Tracker) and mark plans completed. Full can cancel plans.
**CSQ:** Hendrix lists no clause for the Planner on its own. It supports 3B.1.12 and 3C.1.10 (formulations followed batch by batch) together with Products and the Batch Tracker.

![New plan: three flavors of a pre-roll SKU, 1000 units each, with a 5% waste buffer](shots/prod_planner_calc.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| The production manager schedules next week's pre-roll run | **New plan** → pick the SKU and flavors → enter units → **Calculate ingredients** → **Save plan**. |
| You need to know whether there is enough flower and THCA | Read the **Grand total**. Each ingredient shows "on hand", "short" or "not in inventory". |
| The floor needs printed worksheets | **Worksheets PDF (n)** for all flavors, or **PDF** on one flavor card. |
| The run starts on the floor | Open the plan → **Start batch** on the flavor card. |
| Everything in the plan has been made | Open the plan → **Mark completed**. |
| The order is cancelled | Open the plan → **Cancel plan** → enter the reason (Full access). |

### Calculate and save a plan
1. On the **New plan** tab, fill in the form (see the table below).
2. Under **Flavors**, click each flavor to include, or click **Select all**. A plain SKU (no flavors) is calculated as one "Standard" line.
3. Read the note next to the button. It tells you whether the amounts come from saved formulations ("Exact amounts from saved formulations") or whether some flavors will be estimated by the AI.
4. Click **Calculate ingredients**.
5. Check the results (see below), then click **Save plan**. Hendrix gives the plan a number, PP-YYYY-### (for example PP-2026-017), and opens it.

| Field | What to enter | Required |
|---|---|---|
| Product type | One of the 8 product types | Yes |
| SKU | A switched-on SKU made under this license | Yes |
| Units per flavor | Whole number of units for each flavor, for example 1000 | Yes, 1 or more |
| Planned for | The production date (defaults to today) | Yes |
| Flavors | One or more flavors of the SKU | Yes, if the SKU has flavors |
| Additional instructions (optional) | For example "5% waste buffer". Any other wording, for example "use 1.5 g flower per joint", is sent to the AI. | No |

**How the amounts are worked out**
- A flavor with its own formulation is calculated from that recipe: (units ÷ the recipe's standard batch size) × each raw-material quantity.
- A flavor without its own recipe uses the SKU's base recipe. Any terpene line is renamed for the flavor, for example "Terpene - Mango Haze".
- A buffer written as "N% waste" (or buffer, extra, overage, overrun, allowance) is applied exactly to every amount.
- Only flavors with no usable recipe at all go to the AI. Those cards carry an **AI estimate** badge, and the worksheet says "AI estimate - check before use". If you write other instructions besides a buffer, every flavor is sent to the AI.
- Only ingredient names and amounts are read from the recipes. Costs, packaging and labor never reach the Planner.

![Results: grand total checked against inventory, and one card per flavor with its tracking blanks](shots/prod_planner_results.png)

**The results**
- **Grand total — all flavors** adds up each ingredient across flavors. If you have View on Receiving, each total is checked against accepted lots at this license with stock left. kg, mg, lb, oz and L are converted, and lots are matched by item name. Each total shows "on hand", "short" (red) or "not in inventory", and the badge counts the shortages.
- One card per flavor shows its source (**Formulation**, **Base recipe** or **AI estimate**), the ingredients, and **Production tracking** blanks for the product type, for example "Infused flower wt" or "Kief used" for pre-rolls. Anything you type in those blanks prints on the worksheet. It is not saved with the plan.
- The worksheet PDF has one page per flavor: the license, plan number, date, SKU and flavor, target units, required ingredients with a "Lot / tag used" blank, the production tracking blanks, Batch # and METRC tag blanks, and operator and manager signature lines.

### Work with saved plans
The **Plans** tab lists every plan for the license with its number, planned date, product, flavors × units, the batches made from it and the status: **Planned**, **In production**, **Completed** or **Cancelled**. The tab label counts the open plans, and the Dashboard shows a "Production plans" card.

![Plans list with planned, in-production, completed and cancelled plans](shots/prod_planner_plans.png)

1. Click **Open** on a plan to see its results again, with the batches made from it on each flavor card.
2. Click **Start batch** on a flavor card. Hendrix opens the Batch Tracker on that product type with **+ New Batch** already filled with the SKU and flavor. A **Planned** plan moves to **In production**.
3. When the plan is done, click **Mark completed** (shown while the plan is In production).
4. To cancel a plan, click **Cancel plan**, enter the **Reason** and confirm with **Cancel plan**.

![Cancel a plan: a reason is required](shots/prod_planner_cancel.png)

> **Hendrix checks:**
> - A plan cannot be saved without at least one calculated flavor ("Calculate the plan first (no flavors).").
> - Plans are numbered automatically and are never deleted. Cancel them with a reason instead ("A reason is required to cancel a plan."). Only Full access can cancel ("Only Full access can cancel a plan.").
> - Once production has started, the amounts cannot change: "Production has started on this plan. Cancel it and make a new plan to change the amounts."
> - A completed or cancelled plan cannot be changed.
> - The SKU must belong to the license's state. Saving, status changes and cancellations go to the Audit Trail.

### Tips
- Save the plan before you start batches. The plan then shows which batches came from it.
- If an ingredient shows "not in inventory", check that the lot's item name in Receiving matches the recipe name, for example "THCA" and "THCA isolate".

## Batch Tracker
The Batch Tracker is the batch production record for the 8 Black Fox product types. It holds the batch number, SKU and flavor, every input and output with its METRC tag, built-in weight checks, R&D and mandatory testing status, attachments and a signature. It is the core traceability record an inspector asks for.

**Where:** left menu → Batch Tracker. Batches belong to the license picked at the top. **Who:** View can see, view and print batches and export CSV. Edit can create batches and **Continue** a batch (fill in blank fields only). Full can **Edit** filled values with a reason and **Void** batches. Seeing the formulation card on the form needs View on the Formulation Bank.
**CSQ:** 1.8, 2A.10.1, 2A.12.1, 2A.12.9, 3A.1.19, 3A.2.3, 3B.1.1, 3B.1.2, 3B.1.4, 3B.1.6, 3B.1.12, 3B.2.2, 3C.1.1, 3C.1.2, 3C.1.4, 3C.1.10, 3C.2.1, 3C.2.2, 3C.2.3, 3C.2.6, 4A.4, 4A.8, 5.4.3

![Batch Tracker, Pre-Rolls tab: status, METRC progress, system checks, test and line clearance badges](shots/prod_batches_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new pre-roll run starts | Pre-Rolls tab → **+ New Batch** (or **Start batch** from a Production Planner plan). |
| The next shift continues a batch | **Continue** on the batch. Fill in the blank fields and click **Save**. |
| A filled-in weight was wrong | Someone with Full access → **Edit** → change the value → enter the **Reason for change** → **Save changes**. |
| A batch was entered twice | Full access → **Void** → enter the reason. |
| The final package tag is ready for state testing | **Submit for testing** on the batch card. |
| A system check shows UNDER WEIGHT | Investigate. Click **Deviation** on the batch to report it to QMS. |
| The line must be cleared before the run | **Line clearance** on the batch (needs Line Clearance access). |
| An inspector asks for batch records for a period | Set **From** / **To**, then **Print / PDF** or **CSV**. |

### Read the batch list
- The tabs across the top are the 8 batch types. Hendrix remembers the last one you used.
- Use the search box (it searches every field), the **From** / **To** dates and **Clear**. **CSV** exports the list. **Print / PDF** prints up to 200 full records.
- The summary bar shows the number of batches and the date of the last one.
- Each card shows the batch number, the status (or **Void**), the date and operator, a **METRC x/y** badge (how many "Recorded on METRC?" boxes are ticked), and the SKU and flavor. Below that come the system checks (PASS, UNDER WEIGHT or OVER WEIGHT), test status badges, the line clearance badge (**Line cleared · LC-…** or **No line clearance**) and, when a HACCP plan covers the batch type, a **CCP x/y** badge.
- The buttons on a card are **View**, **Deviation**, **Line clearance**, **CCP check**, **Submit for testing**, **Continue** (Edit access), **Edit** and **Void** (Full access). Each one shows only when it applies and you have access.
- If no SKU of the type is switched on for the license, a red banner says so.

### Create a batch record
1. Open the batch type tab and click **+ New Batch**.
2. Fill in the header: batch number, date, operator, SKU and flavor.
3. If you can see formulations, a **Formulation** card shows the recipe for that SKU and flavor. The flavor's own recipe is used if there is one, otherwise the base recipe.
4. Work down the sections. Tick **Recorded on METRC?** after each step is entered in the state system. The label uses your state's tracking system name.
5. Watch the **System Check** panels. They recalculate as you type.
6. Add files with **+ Upload file / photo** (PDF, PNG, JPG, DOCX, XLSX; max 5 MB each).
7. Sign in the **Signature** box and click **Submit & Sign**.

![New Pre-Rolls batch: header, formulation card, inputs and live system checks](shots/prod_batches_form.png)

![End of the form: packaging check, R&D result, mandatory testing, status, attachments and signature](shots/prod_batches_form_end.png)

**Fields on every batch type**

| Field | What to enter | Required |
|---|---|---|
| Batch / Lot Number | For example PR-2026-045. It must be unique under this license (capitals and spaces at the ends are ignored). | Yes |
| Date | Defaults to today | Yes |
| Operator / Personnel | Who ran the batch (defaults to your name) | No |
| SKU | Only switched-on SKUs of this type made under this license are offered. Ethanol Extraction has no SKU. | Yes (except Ethanol Extraction) |
| Flavor | A flavor of the SKU. If the SKU has no flavor list, type it. Hidden for SKUs set to "no flavors". BHO and Ethanol have no flavor. | No |
| Recorded on METRC? | Tick after each step is entered in the state tracking system | No |
| Status | In Progress, QC Hold, Passed, Failed, Completed. Ethanol also has Winterization and Filtration, and BHO has Purging. | Yes (default In Progress) |
| Notes | Any observations or issues | No |
| Attachments | Files or photos, max 5 MB each | No |
| Signature | Your drawn signature, stored with the record | No |

**Sections and fields by batch type**

| Batch type | Sections and fields |
|---|---|
| Ethanol Extraction | **Extraction:** Biomass Tags (add a row per tag with its weight; **+ Add Biomass Tag**), Total Biomass Used (auto), Ethanol Crude METRC #, Ethanol Crude Weight. **Recovery and Decarbing:** Decarbed Crude Tag, Decarbed Crude Weight Produced. **Distillation:** Total Decarbed Crude Used, Total Decarbed Crude Waste, Total Distillate Produced, Distillate METRC Tag. **Batch Yield Quality Check.** Under each weight Hendrix shows the usual amount for a good yield (77%, 20% and 16% of the biomass). |
| BHO Extraction | **Biomass Used:** Biomass Tags, Total Biomass Used (auto). **BHO Crude:** METRC #, Produced. **In Progress** and **Final:** METRC #, Qty, Waste. For a SKU set to "two products", these come as separate THCA and HTE fields. **Yield:** % of biomass for each product and in total. |
| Pre-Rolls | **Infused Flower:** Flower METRC #, Flower Used, the infusion ingredients chosen on the SKU (METRC # and amount used), Infused Flower #, Infused Flower Total WT, check. **Infused Joints:** Infused Flower Used, Waste, Total Joint Filled, Infused Pre Roll METRC Tag, check. **Infused Kiefed Preroll** (only if the SKU has a coating step): pre-rolls used and wasted, Kief METRC #, Kief QTY Used, Total Kiefed Infused Joints, its METRC #, check. **Final Packaging:** joints used and wasted, Total Jar Packaged, Final Packaged Tag #, packaging check, R&D 1, R&D 2, Mandatory Testing. |
| Cartridges | **Source Oil / Distillate:** Source Batch #, Input Oil Weight, Amount Terpene Added. **Primed Oil:** Total Weight, METRC #, Used, R&D Test, R&D Test 2, check. **Packaged:** Total Cart Packaged, its METRC #, Mandatory Test. |
| Gummies | **Gummy Mixture Batch:** Distillate METRC #, Distillate Used, Batch Weight, Gummy Mixture METRC #. **Production Batch (Eaches):** Mixture Used (auto), Mixture Waste, Total Gummies Produced, METRC #. **Sugared Gummies:** Gummies Used, Waste before sugaring, Total Sugar Coated (auto), METRC #, R&D Test, R&D Test 2. **Final Packaging:** Sugar Coated Used and Waste, Total Packaged Gummies (auto), Final Packaged Gummies METRC#, Mandatory Testing, gummy weight check. |
| Infused Flower | **Infused Flower:** flower and each infusion input with METRC # and amount, Infused Flower METRC Tag, Total WT, check, R&D Test, R&D Test 2. **Filling & Packaging** (unlocks once an R&D test is Passed): Infused Flower Used, Total Bags Filled, Waste, Final Packaging METRC Tag, validation, Mandatory Testing. |
| Moon Rocks | Base Flower METRC# and Weight, Hash Oil METRC# and Used, Kief METRC# and Used, Total Moon Rocks Produced, Final METRC Tag#. |
| Snow Caps | Base Flower METRC# and Weight, Kief METRC# and Used, Total Snow Caps Produced, Final METRC Tag#. |

**R&D and mandatory testing:** R&D results are **Passed** / **Failed** buttons. **R&D 2** appears only after R&D 1 is marked Failed. On Pre-Rolls and Infused Flower, **Mandatory Testing** appears only after an R&D test is Passed. Mandatory testing values are Not Submitted, Submitted, Passed or Failed.

**System checks** compare what you entered with what the SKU's settings predict, with a ±10% tolerance:

| Check | How it is worked out |
|---|---|
| Infused / Ground flower weight | Sum of all inputs vs. Infused Flower Total WT |
| Joints | Infused flower used ÷ grams per joint vs. Total Joint Filled |
| Kiefed / Diamond coated joints | Infused flower used (plus kief for Diamond) ÷ grams after coating vs. total coated joints |
| Packaging (pre-rolls) | Joints going to packaging ÷ joints per package vs. Total Jar Packaged |
| Primed oil (cartridges) | Input oil + terpene vs. Primed Oil Total Weight |
| Gummy weight | (Mixture used ÷ grams per gummy) ÷ gummies per package vs. Total Packaged Gummies |
| Packaging (infused flower) | Infused flower used ÷ unit size vs. Total Bags Filled |
| Ethanol yield | Distillate ÷ biomass: 16–19% VERY GOOD, 13–16% GOOD, 10–13% BAD, 7–10% VERY BAD, otherwise OUT OF RANGE |

More units than expected shows **UNDER WEIGHT** (red). Fewer units shows **OVER WEIGHT**. The results are saved on the record and shown on the batch card.

> **Hendrix checks:**
> - Batch / Lot Number, Date and (except Ethanol) SKU are required.
> - The batch number must be unique under the license, ignoring capitals and spaces at the ends: "That batch / lot number is already used under this license."
> - The SKU must be switched on, of the same type, in the same state and made under this license. The flavor must belong to that SKU. The database enforces this ("That SKU is switched off (it needs a formulation).", "That SKU is not made under this license.").
> - The SKU and flavor names on the record always come from Products.
> - Every batch belongs to one state and one license and can never be moved.

### Continue a batch (Edit access)
1. Click **Continue** on the batch. The form opens with the message "Continue this batch: fill in the blank fields."
2. Fill in the blank fields. Fields that already have a value are locked, marked "Already entered — locked".
3. You can still change the status, the R&D and mandatory testing results, and add biomass tag rows and attachments.
4. Click **Save**. The Audit Trail records "Filled in blank fields".

> **Hendrix checks:** for anyone without Full access, Hendrix refuses to change a filled value: 'Only blank fields can be filled in. "…" already has a value; ask someone with Full access to change it.' Biomass tag rows and attachments already on the batch cannot be removed or changed.

### Change a filled value (Full access)
1. Click **Edit** on the batch.
2. Change the values.
3. Enter the **Reason for change**. It is saved permanently in the Audit Trail.
4. Click **Save changes**.

> **Hendrix checks:** a change by Full access needs a reason ("A reason for the change is required."). The batch type, signature, creator and creation time can never change. A voided batch cannot be changed.

### View, print and void
- **View** shows the full batch record: license header, every field, check results, attachments, submitted by, signature and, if you have View on the Audit Trail, the **Change history (audit trail)** with old → new values and reasons. Click **Print / PDF** to print it.
- **Void** (Full access) opens **Void batch**. Enter the **Reason for voiding** and click **Void entry**. The batch stays on file, crossed out, with your name, the time and the reason. A void cannot be undone.

![Batch record view with the change history at the bottom](shots/prod_batches_view.png)

> **Hendrix checks:** batch records are never deleted ("Batch records cannot be deleted. Void the batch with a reason instead."). Only Full access can void, a reason is required, and voiding cannot change anything else on the record.

### Submit a batch for testing
When the final package tag is filled in (for example **Final Packaged Tag #** on pre-rolls, **Total Cart Packaged METRC#** on cartridges or **Distillate METRC Tag** on ethanol), a **Submit for testing** button appears, if you have Edit on Testing. Click it and confirm the tags. Hendrix creates one Testing record per final tag with the status **Submitted**, and a **Test: Submitted** badge appears on the batch.

> **Hendrix checks:** only the final package tag goes to mandatory testing, never crude, in-progress or source tags. A batch that is already submitted is refused ("This batch was already submitted for testing.").

### Tips
- Set up the SKU's production settings in Products first. The system checks use them.
- Use **Start batch** from a saved plan so the plan shows the batch.

## Testing
Testing tracks every mandatory lab test per final package tag: submission, lab, result, the stored COA and a reading of the COA by Hendrix AI. It is the evidence that product was tested and passed before release.

**Where:** left menu → Testing. Records belong to the license picked at the top. **Who:** View can see records, open COAs and the analysis, and print compliance stickers (with View on Compliance Stickers). Edit can create records, submit batches from the Batch Tracker, upload, replace and re-read COAs, and update records that are not final. Full can change a final result (Passed / Failed) with a reason and void records.
**CSQ:** 1.8, 1.10, 2A.10.1, 2A.10.4, 2A.12.8, 2A.12.9, 3A.2.2, 3B.1.1, 3B.2.2, 3C.1.1, 3C.2.3, 5.4.3

![Testing: status tabs with counts, category badges and the actions per record](shots/prod_testing_list.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A batch's final package is sampled by the lab | Batch Tracker → **Submit for testing**, or Testing → **+ New test record**. |
| The lab emails the COA | **Upload COA** on the record. Hendrix stores the file and reads it. |
| The COA tag does not match | Read the **Tag mismatch** warning. Confirm it is the right COA before accepting a result. |
| The lab retracts a result | Full access → **Update** → change the status → give the reason. |
| A test fails | Click **Deviation** on the record. Put the batch on hold in Hold and Release. |
| You keep a retention sample | **Update** → fill in the retention sample fields. |
| Labels are needed for a passed batch | **Compliance Sticker** on the record. |

### Read the Testing page
- Tabs: **All**, **Pending**, **Submitted**, **Passed**, **Failed**, **Retest**, each with its count (voided records are not counted).
- Search by batch, SKU, flavor, tag, lab or notes. Filter by category (CONCENTRATES, FLOWER/TRIM, PRE ROLLS, EDIBLES, VAPES), or click **Refresh**.
- Each record shows the batch number, the status badge (or **Void**), the category, the SKU and flavor, the package tag with its label, sample tag, lab, submitted and result dates, THC and CBD %, result notes, notes and the retention sample. A **Tag mismatch** badge appears when the COA's tag differs.
- Buttons: **COA** (open the stored file), **Show analysis** / **Hide analysis**, **Upload COA** / **Replace COA**, **Re-read COA**, **Compliance Sticker**, **Update**, **Deviation** (on Failed or Retest) and **Void**.

### Create a test record
1. Click **+ New test record**.
2. Pick the **Batch**. Hendrix fills the package tag from the batch's final tag. If the batch has more than one final tag (BHO THCA and HTE), pick it from the list.
3. Fill in the other fields and click **Create**.

![New test record, filled in for a resample](shots/prod_testing_new.png)

| Field | What to enter | Required |
|---|---|---|
| Batch | A batch of this license that is not void, or "No batch (type the details)" | Yes (or type the batch number) |
| Batch number, Product type, SKU, Flavor | Shown only when no batch is picked | Batch number: yes, if no batch is picked |
| Package tag tested | The final package tag. If the batch has none yet, the box says "This batch has no final package tag yet". | Yes |
| Sample tag | The tag of the sample taken | No |
| Lab | The testing lab | No |
| Status | Pending or Submitted | Yes (default Pending) |
| Notes | Free text | No |

> **Hendrix checks:** each batch and tag can have only one live test record ("That batch and tag already has a test record."). Tags are compared ignoring spaces, dashes and capitals. A linked batch must be from the same license and not void. The batch number, type, SKU and flavor are copied from the batch and cannot be changed later.

### Upload and read the COA
1. Click **Upload COA** and choose the PDF or photo.
2. Hendrix stores the file privately and sends it to Hendrix AI, which reads the lab name and license number, report date, sample tag, overall result, potency, each test category (pesticides, microbials, mycotoxins, heavy metals, residual solvents, foreign matter, moisture / water activity) with its analytes, and terpenes.
3. Hendrix fills Result THC % and Result CBD %, plus the lab, lab license # and sample tag if they were empty.
4. Then it acts on the result:
   - If the COA tag does not match the record's package or sample tag, the status is **not** changed. A note "Tag mismatch: …" is added, and the message says "COA read, but the tag does not match — status left unchanged."
   - If the result is not final yet and the COA says Pass, the record is marked **Passed**. If it says Fail, it is marked **Failed**.
   - If the result was already final, the status is not changed.
5. Click **Show analysis** to see the overall result, potency bars, each category with its analytes, and the terpenes.

![COA analysis: overall result, lab and COA tag, potency and test categories](shots/prod_testing_analysis.png)

Use **Re-read COA** to read the stored file again. If the AI is not set up, Hendrix keeps the file and says "AI reading is not set up yet … Enter the results with Update."

> **Hendrix checks:** COA files are stored privately. A stored file can never be overwritten or deleted. **Replace COA** adds a new file, and the change is logged as "COA replaced".

### Update a test record
1. Click **Update**.
2. Change the fields (see the table below) and click **Save**.

![Update test: changing a final result needs a reason](shots/prod_testing_update.png)

| Field | What to enter | Required |
|---|---|---|
| Status | Pending, Submitted, Passed, Failed or Retest. On a final record (Passed / Failed), only Full access sees the other options. | Yes |
| Lab, Lab license #, Package tag, Sample tag | As on the COA | No |
| Result THC %, Result CBD % | Numbers from the COA | No |
| Result notes | For example the failing analyte | No |
| Quantity kept / Where it is kept / Keep until | The retention (reserve) sample: for example "2 units", "Retention cabinet B", a date | No |
| Notes | Free text | No |
| Reason for changing a final result | Shown when you change Passed or Failed to another status | Yes, in that case |

> **Hendrix checks:**
> - Changing a final result needs Full access ("Changing a final result (Passed) needs Full access to Testing.") and a reason ("A reason is required to change a final result."). The database enforces both.
> - Hendrix stamps the submitted date when a record becomes Submitted, and the result date when it becomes Passed or Failed.
> - Records are never deleted. **Void** (Full access) needs a reason, and a voided record cannot be changed.
> - Elsewhere in Hendrix: a batch with a Failed test and no later Passed test cannot be released in Hold and Release or shipped in Shipping.

### Tips
- Keep the sample tag on the record. It prints on the compliance sticker as the "Testing Tag#".
- If the COA says Pass but a different tag, do not override the status until QA has confirmed the COA.

## Compliance Stickers
Compliance Stickers holds the label template for each SKU (and flavor) under a license, and prints the compliance stickers for a tested batch on Avery label sheets. Potency comes straight from the COA. Every print is logged, which shows an inspector what was printed, for which tag, how many and by whom.

**Where:** left menu → Compliance Stickers to manage templates. Print from Testing → **Compliance Sticker** on a record that has a COA analysis. Templates belong to the license picked at the top. **Who:** View can print stickers. Edit can add, import and change templates. Full can delete templates.
**CSQ:** 1.10, 2A.12.7, 2A.12.8, 3C.2.6, 4A.3, 5.4.2

![Label templates grouped by SKU, with approval number, servings and weight](shots/prod_stickers_templates.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| A new SKU or flavor goes to market | Compliance Stickers → **+ New template**. |
| You set up a new license from the Black Fox catalog | **Import Black Fox templates**. Only SKUs and flavors that exist in Products are imported. |
| An ingredient or allergen changes | **Edit** on the template → change **Active and other ingredients** / **Allergen declaration** → **Save template**. |
| A batch passed testing and needs labels | Testing → **Compliance Sticker** → set the count → **Download PDF**. |
| The labels print off-center | In the sticker window: **Alignment test sheet**, then adjust **Shift right / Shift down**. |
| A part-used label sheet is in the printer | Set **Start at position** to the first free label. |

### Add or edit a label template
1. Click **+ New template** (or **Edit** on a template card).
2. Fill in the fields below. A **Preview with sample results** shows how the label will look and warns if the text is too long.
3. Click **Save template**.

![Edit label template: approval number, servings, weight, ingredients, allergens and warning](shots/prod_stickers_editor.png)

| Field | What to enter | Required |
|---|---|---|
| SKU | A SKU of this state | Yes |
| Flavor | One flavor, or "Any flavor" | No |
| Template name | Leave blank to name it "[SKU] — [flavor]" | No |
| Label sheet | Avery 94202 — 1" x 4", 20 per sheet | Yes (default) |
| Layout | Standard (paragraphs) or Three columns | Yes (default Standard) |
| Product approval number | The state product approval number, for example M00002721406 | No (flagged as missing when printing) |
| Servings / doses per package | For example 10 | No (needed for mg per serving) |
| Weight | Package weight, for example 3g | No (needed for mg per serving) |
| Instruction and length of effect | As it should print | No |
| Active and other ingredients | Exactly as it should print | No (flagged as missing when printing) |
| Allergen declaration (CSQ 2A.12.7) | For example "Contains: milk, soy". Leave blank if none. It prints after the ingredients as "ALLERGENS: …". | No |
| Warning | The required warning text | No |
| Product information heading, Approval number label, Test results heading | Under **Change heading wording (for other states)**. Defaults: MARIJUANA PRODUCT INFORMATION, MARIJUANA PRODUCT APPROVAL NUMBER, TEST RESULTS (mg/serving): | No |

> **Hendrix checks:** a license can have only one template per SKU and flavor ("This SKU / flavor already has a template under this license."). "Any flavor" counts as one. The flavor must belong to the SKU, and the SKU to the same state. Template changes go to the Audit Trail. A card with no ingredients shows a **No ingredients** badge.

### Print compliance stickers
1. In Testing, click **Compliance Sticker** on a record that has a COA analysis.
2. Hendrix picks the template that matches the SKU and flavor, otherwise the SKU's "Any flavor" template. If there is none, choose one from the list.
3. Set **Labels to print** and **Start at position (1-20)**.
4. First time on a printer: click **Alignment test sheet**, print it on plain paper at 100% / "Actual size" (never "Fit to page"), and hold it over a label sheet against the light. Adjust **Shift right (in)** and **Shift down (in)** until the boxes sit inside the labels. Hendrix remembers the shift on this computer.
5. Check the preview and any red warnings, then click **Download PDF** and print it at actual size.
6. The print is logged and appears under **Print log for this tag**.

![Sticker window: template, count, position, alignment and the print log for this tag](shots/prod_stickers_print.png)

| Field | What to enter | Required |
|---|---|---|
| Template | Picked automatically, can be changed | Yes |
| Labels to print | Number of labels (default 20) | Yes |
| Start at position | First label on the sheet, 1 to 20 | Yes (default 1) |
| Shift right (in) / Shift down (in) | Printer offset in inches, for example 0.03 | No |
| Outlines in preview | Shows the label outlines in the preview only. They are never printed. | No |

![The printed stickers: ingredients, product information, cannabinoid mg per serving from the COA, approval number and warning](shots/prod_stickers_sheet.png)

**What prints on each sticker**
- Active and Other Ingredients, followed by the allergen declaration
- Servings/Doses Per Package and Weight (from the template)
- Best If Used By: one year after the COA report date (or the result date)
- Produced By: the license number
- Tested By: the lab's license number from the COA (or Lab license # on the record)
- Testing Tag#: the record's sample tag
- Cannabinoid profile in mg per serving for Delta-9-THC, Delta-9-THCa, CBD, CBDa, CBN, THCV, CBDV and Delta-8-THC. Each is worked out as COA % × package weight (g) × 1000 ÷ servings, or ND when the COA does not report it.
- Instruction and length of effect, the product approval number and the warning

> **Hendrix checks:**
> - Before you print, Hendrix lists anything missing: approval number, ingredients, sample testing tag, Tested By (lab license #) or cannabinoid results. It also warns when the text is too long for a 1" label.
> - Every download is logged with the batch, tag, SKU, flavor, template, count, start position and who printed it. The count must be between 1 and 5000.
> - Print log entries can never be changed or deleted ("Sticker print records cannot be changed or deleted.").

### Tips
- Put the sample tag and lab license # on the test record before printing. Otherwise those lines print empty.
- Shorten the ingredients or warning if Hendrix says the text does not fit.

## Cultivation
Cultivation keeps the grow records for cultivation (CUL) licenses: grow areas, plant batches from propagation to cure, nutrient and crop protection applications, scouting, harvest, drying and curing. It traces every plant batch back to its clone or seed lot and blocks a harvest inside a pesticide's pre-harvest interval.

**Where:** left menu → Cultivation. The menu item only appears when the license at the top is a cultivation license (its operation is set to Cultivation, or its number starts with CUL, or its type mentions cultivation, grow or nursery). **Who:** View can see all records. Edit can add and edit grow areas (including switching an area off) and plant batches, and record nutrients, crop protection, scouting, stage moves, harvest, drying, curing and notes. Full can void records and destroy plant batches. The picklists also need View on Receiving (lots) and on Chemicals and SDS (approved inputs).
**CSQ:** 3A.1.1, 3A.1.2, 3A.1.3, 3A.1.5, 3A.1.7, 3A.1.8, 3A.1.12, 3A.1.13, 3A.1.14, 3A.1.15, 3A.1.16

![Cultivation: summary cards and the active plant batches, one on pre-harvest hold](shots/prod_cultivation_batches.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You set up a new room, greenhouse or field | **+ Grow area**. |
| Clones arrive and are planted | Receive them in Receiving first, then **+ Plant batch** with the clone lot. |
| You feed the plants | Open the batch → **Nutrients**. |
| You spray for mites | Open the batch → **Crop protection**, with the rate, re-entry and pre-harvest intervals from the label. |
| The weekly IPM walk-through | Open the batch → **Scouting**. |
| Plants move from veg to flower | Open the batch → **Stage / move**. |
| Harvest day | Open the batch → **Harvest** (wet weight and METRC harvest tag). |
| Plants are hung, then cured | **Drying** (room conditions), then **Cured (dry weight)**. |
| A batch must be destroyed | Full access → **Destroy** (reason and method). |
| The inspector asks for spray records | **Applications** tab → **Print application records**. |

### Read the Cultivation page
- Summary cards: **Active plant batches** (with plants growing), **Harvest on hold (PHI)**, **Harvests (30 days)**, **Applications (7 days)** and, if you have outdoor or greenhouse areas, **Site risk assessment due** (yearly).
- Tabs:
  - **Plant batches** (filter: Active batches, Done and destroyed, All) shows the batch number and METRC tag, cultivar and source, plants, stage, area, planted date, and the harvest column (**Not before [date]** while a pre-harvest interval runs, or the wet and dry weights).
  - **Grow areas** shows the type, canopy, limits, irrigation and water, and the site risk assessment date.
  - **Applications** is every nutrient and crop protection record that is not void, with product, EPA number, rate, REI / PHI and who applied it. **Print application records** prints it.
  - **Approved inputs** lists the nutrients, pesticides and other inputs approved in Chemicals and SDS with grade, EPA #, SDS and storage. This is your nutrient and crop protection plan.
- The Dashboard shows a Cultivation card with plants growing, batches drying or curing, and batches on pre-harvest hold.

### Add a grow area
1. Click **+ Grow area**.
2. Fill in the fields below and click **Save**. To change an area later, click **Edit** on the Grow areas tab.

![Grow areas with limits, irrigation, water source and the greenhouse risk assessment date](shots/prod_cultivation_areas.png)

| Field | What to enter | Required |
|---|---|---|
| Name | For example Flower Room 2, Field A | Yes |
| Type | Indoor grow room, Greenhouse, Outdoor field, Mother room, Clone / propagation, Dry room, Cure room, Trim room | Yes (default Indoor) |
| Canopy (sq ft) | Number | No |
| Temperature / humidity / airflow limits | For example 68-80 °F, 40-60% RH | No |
| Irrigation / fertigation system, Water source | Grow areas only | No |
| Land use history and neighboring land | Outdoor and greenhouse only | No |
| Risk assessed on (yearly) | Date of the site risk assessment, not in the future (outdoor and greenhouse) | No |
| Risk assessment | Topography, animals, run-off, controls, toilets / handwashing | Yes, if a risk date is entered |
| Active | Shown when editing. Untick to switch the area off. | - |

> **Hendrix checks:** grow areas can only be added to a cultivation license ("Cultivation records are only for cultivation (CUL) licenses."). A risk date without a description is refused ("Describe the site risk assessment."). An area that has grow records cannot be deleted. Switch it off instead. A risk assessment older than a year is flagged **Due**.

### Start a plant batch
1. Click **+ Plant batch** (you need at least one grow area).
2. Fill in the fields below and click **Save**. Hendrix numbers the batch PB-YYYY-### and starts it in **Propagation**.

| Field | What to enter | Required |
|---|---|---|
| Cultivar / strain | For example Gelato | Yes |
| Plants | Number of plants, 1 or more | Yes |
| Planted on | Date, not in the future. Fixed after saving. | Yes (default today) |
| Propagation material from | A received clone / seed lot, Our own mother plants, or Our own seeds. Fixed after saving. | Yes |
| Lot (Receiving) | An accepted clone / seed lot of this license | Yes, for a received lot |
| Mother plant batch | A growing plant batch | Yes, for own mothers |
| Seed source | Free text | No |
| Grow media lot | An accepted lot, for example coco coir | No |
| Media (treated / reused?) | For example "New coco, pre-washed" | No |
| METRC plant batch tag | The state plant batch tag | No |
| Starts in area | An active grow area | No |
| Notes | Free text | No |

> **Hendrix checks:** propagation material must come from an accepted lot of this license ("Propagation material must come from an accepted lot of this license."). The planting date cannot be in the future. After saving, the stage, area, harvest data and weights change only through grow records ("Stage, area, harvest and weights change through the grow records."). Plant batches are never deleted. Destroy them with a reason. A done or destroyed batch is closed.

### Record grow work on a plant batch
Click **Open** on a batch. The window shows the stage, plants, area, planted date, source, media and tag, a red banner while a pre-harvest interval runs, the action buttons and every record (voided ones crossed out).

![Plant batch PB-2026-021 with its records and the pre-harvest interval warning](shots/prod_cultivation_batch.png)

Which buttons you see depends on the stage:
- **Nutrients**, **Crop protection**, **Scouting** and **Stage / move**: while the batch is growing (propagation, vegetative, flowering).
- **Harvest**: when it is vegetative or flowering.
- **Drying**: when it is drying.
- **Cured (dry weight)**: when it is drying or curing.
- **Note**, **Edit** and **Print label** (a plant label with cultivar, number, plants, source, planted date and METRC tag): while the batch is active.
- **Destroy**: Full access only.

Every record form has **Date** (not in the future and not before planting; default today) and **Done by** (**Applicator** for crop protection, required). Then:

| Record | Fields | Effect on the batch |
|---|---|---|
| Nutrients | Approved nutrient / amendment (Chemicals), Received lot used (one of the two is required), **Amount / rate** (required), Method | Logged in Applications |
| Crop protection | **Approved pesticide (Chemicals)**, **Rate (label)**, Method, **Re-entry (hours)**, **Pre-harvest (days)**, Target pest / disease, Photos / files | Sets the earliest harvest date |
| Scouting | **What was seen (pests, disease, plant health)**, Photos / files | - |
| Stage / move | Stage (Vegetative, Flowering, or stage unchanged), Move to area | Changes the stage and / or area |
| Harvest | **Wet weight (g)**, Waste weight (g), **Harvest batch tag (METRC)**, Hung in (dry room), Notes, Photos / files | Stage becomes Drying |
| Drying | **Room conditions**, Moved to (cure room) | Stage becomes Curing |
| Cured (dry weight) | **Final dry weight (g)**, Waste weight (g), Conditions | Stage becomes Done |
| Note | **Note** | - |
| Destroy (Full) | **Reason and how it was destroyed (waste log / METRC)** | Stage becomes Destroyed |

Fields in **bold** are required.

![Crop protection: approved pesticide with EPA number, label rate, re-entry and pre-harvest intervals](shots/prod_cultivation_crop.png)

![Harvest form blocked inside the pre-harvest interval](shots/prod_cultivation_harvest.png)

> **Hendrix checks:**
> - Only chemicals approved in Chemicals and SDS can be applied. Crop protection must use one whose purpose is "Pesticide / crop protection" ("Crop protection must use a pesticide approved in the Chemical register."). The product name and EPA number are copied from the register.
> - Lots used must be accepted lots of this license.
> - Crop protection needs the re-entry interval (hours) and the pre-harvest interval (days) from the label.
> - **Pre-harvest interval:** the earliest harvest is the latest application date plus its PHI, over every crop protection record that is not void. Hendrix refuses an earlier harvest: "Too early to harvest: the pre-harvest interval of a crop protection application ends on [date]." Voiding an application recalculates the date.
> - Only a vegetative or flowering batch can be harvested. Drying and curing need the harvest first ("Record the harvest first."). Wet and dry weights must be above 0.
> - Grow records cannot be edited. Void them and record them again. Only Full access can void, only nutrient, crop protection, scouting and note records can be voided, and a reason is required. Stage, harvest, drying, curing and destruction records cannot be voided. Record a correction note instead.
> - Every plant batch, area and record is in the Audit Trail.

### Tips
- Approve nutrients and pesticides in Chemicals and SDS (with their SDS and EPA number) before you need them. They will not appear in the forms otherwise.
- Receive clones, seeds and grow media in Receiving so the plant batch can be traced to its lot.
