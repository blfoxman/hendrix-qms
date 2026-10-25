# Video 07 · Production Line Map for managers. Captions use the text as written; speech uses SAY.
NARR = [
    ('i1', "Hendrix QMS training, video seven: the Production Line Map, for managers."),
    ('i2', "In a few minutes: how to read the map, why a batch stopped, the wall display, and access for executives."),

    # What the map shows
    ('w1', "The Line Map is a live subway map of production, for general managers and executives. Open it from the top of the Modules menu."),
    ('w2', "Every batch of the license picked at the top sits at its real station, from plan to shipment. The cards count the batches in production, moving, and stopped, with the longest stop. Then the batches at the lab, what shipped in the last three days, and who's on the floor, from the Time Clock."),

    # Reading lines and colors
    ('r1', "Each line is a product type: here Pre-Rolls, Cartridges and Gummies. Its stations are Planned, Line clearance, and then the sections of that product's batch record."),
    ('r2', "Every line then joins the shared trunk: Lab testing, QC release, Labels and Shipped."),
    ('r3', "The legend explains the colors. Gold, or the line color, means moving. Red means stopped. Dashed is waiting at the lab, outlined is a plan that hasn't started, and grey is shipped."),

    # Why a batch stopped
    ('y1', "Nobody marks a stop by hand. Hendrix stops a batch by itself, when its records show a problem. Click a red batch to see why."),
    ('y2', "This gummy batch has a CCP cooking temperature out of limits, waiting for a second person to verify it. The box names the source record, the owner, how long it's been stopped, and what clears it."),
    ('y3', "A batch can have more than one reason. This cartridge batch's line clearance wasn't cleared, and it has had no update for hours. Below, its journey shows each station, and where it stopped."),
    ('y4', "This pre-roll batch is stopped by equipment: the cone filler is past its calibration date. Maintenance owns it, and a passing calibration clears it."),
    ('y5', "Click Open Equipment to go straight to the module behind the stop, where the cone filler shows its overdue calibration."),

    # Stops right now
    ('s1', "Stops right now lists every stop, longest first. Each one names the record that stopped it, and its owner. Click a stop to open its batch."),
    ('s2', "When several batches share a station, the map shows one marker, like 2 batches at Lab testing. Click it, and pick the batch you want. This one is on hold: its potency is over the label claim."),
    ('s3', "A batch at the lab whose test is still pending or submitted is waiting, not stopped. Click Stops only to dim every batch that's moving."),

    # Wall display
    ('v1', "Click Wall display to put the map full screen, on an office or floor TV. It refreshes every minute, so the screen always shows the line as it is now."),

    # Access for executives
    ('e1', "Executives only need View on the Line Map. Here, Morgan is signed in with Line Map access, and nothing else. The menu shows the Line Map, and the Dashboard shows its card."),
    ('e2', "Morgan sees the whole map, and every reason for a stop, without access to the modules behind it."),
    ('e3', "The Open buttons only appear for modules a person can open, so Morgan sees none. And the map never shows costs or files."),

    # Dashboard card and idle time
    ('d1', "On the Dashboard, the Line map card counts the stopped batches, and names the longest stop. Open line map takes you straight to the map."),
    ('d2', "A batch also stops when it goes too long without an update. Admins set those hours in Settings, under Line Map. The default is 4."),
    ('d3', "Hendrix checks: the hours must be from 1 to 72, so zero is refused. Enter 6, and click Save settings."),

    ('z1', "That's the Production Line Map, and the full Hendrix QMS training series. For every station and every stop reason, see Chapter 7 of the Hendrix QMS User Manual, under Line Map."),
    ('z2', "Thank you for watching."),
]
SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('SKU', 'S K U'), ('HACCP', 'hassip'),
       ('read only', 'read-only'), ('1 to 72', 'one to seventy-two'), ('2 batches', 'two batches'), ('is 4.', 'is four.'),
       ('Enter 6', 'Enter six'), ('Pre-Rolls', 'pre-rolls')]
