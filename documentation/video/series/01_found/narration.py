# Video 01 - Setting up and running Hendrix. (key, text): captions use the text, speech uses SAY.
NARR = [
    # ---- Introduction (title card)
    ('t1', "Hendrix QMS training, Video 01: Setting up and running Hendrix."),
    ('t2', "This video covers the Dashboard, States and Licenses, the Rulebook, Standards, Team and Access, Roles, the Audit Trail, Settings, and Import. Most of these pages are for admins and managers, but everyone starts the day on the Dashboard."),

    # ---- Dashboard
    ('d1', "The Dashboard is your home page. But first, you need an account. On the sign-in screen, click Create an account, and enter your full name, your work email and a password."),
    ('d2', "Hendrix checks: the password must be at least 8 characters. And a new account can't open any page until an admin approves it on Team and Access."),
    ('d3', "Once you're approved, go back to Sign in. Enter your email and password, and click Sign in."),
    ('d4', "At the top, pick the State, and then the License you're working in. Hendrix remembers your choice on this computer."),
    ('d5', "Everything you record belongs to the license chosen at the top. A record can never be moved to another state or license later, so check it before you start."),
    ('d6', "The first row shows the state's regulator and governing code, the active license, and the state rulebook."),
    ('d7', "Below that, every module you can open has its own card, with a headline number and a link. Red means something is overdue, missing or failed. Green means all clear."),
    ('d8', "The Quality standard card shows the CSQ target level and the progress for this license. When you're finished, or you leave a shared computer, click Sign out."),

    # ---- States and Licenses
    ('l1', "States and Licenses is where the company's states and licenses are set up. Every record belongs to one license, and every license belongs to one state. Only a system admin can change this page."),
    ('l2', "To add a license, click Add license under the right state. Enter the facility name, the license number and the license type."),
    ('l3', "The Operation decides which CSQ standards apply. On Automatic, Hendrix reads the number and the type. A number starting with MAN makes it Manufacturing, so it follows the Manufacturing and Extraction standards."),
    ('l4', "Click Save. The new license is listed with its CSQ standards, and it's now in the License list at the top."),
    ('l5', "When a license stops operating, click Deactivate rather than Delete. It leaves the License list at the top, but its records stay."),
    ('l6', "Hendrix checks: you can't delete a state that still has licenses. Delete or move its licenses first."),
    ('l7', "Tip: set each license's operation before you adopt the CSQ standard."),

    # ---- Rulebook
    ('r1', "Each state has its own Rulebook with the state's cannabis rules. Open Missouri Rulebook from the left menu, click Upload rules PDF, and choose the official rules PDF from the state website."),
    ('r2', "Hendrix reads every page and opens a review window: the file, the number of pages, the rule format it found, and seven rules found. New and changed rules are ticked for you."),
    ('r3', "Check each title and category. Click Text to read the rule word for word, as it came from the PDF."),
    ('r4', "Hendrix checks: nothing is saved until you click Import, and a scanned PDF with no readable text is refused. Click Import 7 rules."),
    ('r5', "The PDF is listed under Source PDFs, marked latest. To add a company rule by hand, click Add rule. Fill in the category, the citation and the title, and save."),
    ('r6', "Every change to a rule is kept in the Audit Trail. Tip: during an inspection, type in the search box to find a rule fast."),

    # ---- Standards (CSQ)
    ('s1', "Standards holds the CSQ standard clause by clause, and records how each license meets each clause. When no standard is loaded yet, someone with Full access clicks Add CSQ Standards."),
    ('s2', "Hendrix adds 130 clauses, each linked to the Hendrix records that prove it. Next, with the right license picked at the top, click Adopt for this license."),
    ('s3', "The standards follow from the license's operation. Choose the target level, here Level 2, cGMP plus HACCP. Set the status to Audit scheduled, and enter the certification body and the audit date."),
    ('s4', "Click Adopt standard. The page now shows the operational alerts, the license's target and status, and the percent complete."),
    ('s5', "To record how you meet a clause, open it, and click Record conformance."),
    ('s6', "Hendrix checks: a clause can only be marked Not applicable with a written justification."),
    ('s7', "Here, the clause is met. Set the status to Conforming, name the owner, and write the document reference and the evidence an auditor will look for. Then save."),
    ('s8', "When the auditor arrives, click Inspector view. The page becomes read only. Every clause opens with its evidence and live records, and the edit buttons are hidden."),

    # ---- Team and Access
    ('m1', "Team and Access is where a system admin approves new people, and decides what they can see and change. New accounts wait at the top."),
    ('m2', "Click Approve. Tick one or more roles, here Team Member. To keep someone at one license, untick All licenses, and tick their license."),
    ('m3', "Custom access overrides the roles for this one person. Here, Jordan gets View only on the Batch Tracker. Then click Approve."),
    ('m4', "The table now shows Jordan's roles, licenses and custom access. When someone leaves, click Manage and untick Approved. Their records and history stay."),
    ('m5', "Hendrix checks: you can't remove your own approval or admin rights, and Hendrix always needs at least one system admin."),
    ('m6', "Tip: give access through roles, and use custom access only for exceptions."),

    # ---- Roles
    ('o1', "Roles are access templates, like Production Lead or Compliance Officer. Each role carries a View, Edit or Full level for every module. On a new system, click Add Black Fox roles to start from twelve job titles."),
    ('o2', "Each card shows how many people hold the role, its duties, its requirements, and its access. A role without requirements is flagged, because CSQ asks for them."),
    ('o3', "To change a role, click Edit, and fill in the requirements for the job: certifications, education, experience and training."),
    ('o4', "Then set the access per module. Here, Sanitation gets Edit on Chemicals and SDS. View means see records. Edit means create and add. Full means change filled-in records with a reason, void and delete."),
    ('o5', "Click Save role. Hendrix checks: only a system admin can create or change roles, each role name must be unique, and every change is kept in the Audit Trail."),

    # ---- Audit Trail
    ('a1', "The Audit Trail is the permanent history of every change in Hendrix. Each row shows when, who, the area and the record, the action, the old and new values, and the reason."),
    ('a2', "Type in the search box to find a person, a record or a reason."),
    ('a3', "Or filter by area, for example Batch record. Here, an input weight was changed from 800 to 812, with the reason written at the time."),
    ('a3b', "Set the period, from the last 24 hours to all time. Missouri only is ticked by default. Untick it to see the changes from every state. Changes to log entries and batch records, and every void, need a reason, and the reason is stored here."),
    ('a4', "Hendrix checks: every change is written by the database itself, and nobody, not even an admin, can change or delete the audit trail. Click Export CSV to hand the list to an inspector."),

    # ---- Settings
    ('e1', "Settings are kept per license, for the license chosen at the top. On General, enter the business details printed on every record: the legal name, the name you do business as, the address, the phone and the email."),
    ('e2', "Upload the logo for badges, kiosks and printouts. The preview shows the header and footer every printout will carry."),
    ('e3', "Time clock holds the break limits. On Facility logs, set how many days a log can go without an entry before it's flagged. Here, the Sanitation Log must be filled in every day."),
    ('e4', "On the Line Map tab, set how many hours a batch in production can go without an update, before the Line Map shows it as stopped. The default is four hours."),
    ('e5', "Hendrix checks: it must be between 1 and 72 hours, so zero is refused."),
    ('e6', "Enter six hours, and click Save settings. Hendrix confirms the settings are saved for Black Fox, and every change is kept in the Audit Trail."),

    # ---- Import (Excel / Sheets)
    ('i1', "Import brings your existing lists from Excel or Google Sheets into Hendrix: suppliers, equipment, chemicals, products, complaints, risks and the org chart. First, pick what you're importing, here Equipment."),
    ('i2', "Then choose the spreadsheet file, or paste cells copied from Google Sheets. Hendrix picks the sheet and finds the header row."),
    ('i3', "Click Match with AI to let the AI match the columns, and translate values, like Mixer into Production. Check every field."),
    ('i4', "In the preview, read the badges and the Check column. Hendrix checks: a row with a required column empty is not imported, and a row already in Hendrix is skipped, so importing the same file twice adds nothing."),
    ('i5', "Click Import 2 rows. Every row is saved to the license at the top, with the same rules and Audit Trail as a record typed by hand."),

    # ---- Wrap-up (end card)
    ('w1', "That's Video 01. Next: Video 02, the Quality system, with deviations and CAPAs, complaints, internal audits, SOPs and training."),
    ('w2', "For every field and every check, see the Hendrix QMS User Manual, chapter two: Setting up and running Hendrix. Thank you for watching."),
]

SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('SKU', 'S K U'), ('CSV', 'C S V'), ('HACCP', 'hassip'),
       ('read only', 'read-only'), ('800 to 812', 'eight hundred to eight hundred twelve'), ('cGMP', 'C G M P'),
       ('starting with MAN', 'starting with M A N'), ('SDS', 'S D S'), ('SOPs', 'S O Pees'), ('with AI', 'with A I'), ('the AI', 'the A I'),
       ('Import 7 rules', 'Import seven rules'), ('Import 2 rows', 'Import two rows'), ('Video 01', 'video one'), ('Video 02', 'video two')]
