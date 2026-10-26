# Tasks, security, kiosks and METRC

## My Tasks
My Tasks lists everything waiting for you at the license chosen at the top. Hendrix works the list out from the records and your access every time you open it, so nobody has to assign or tick anything off by hand: when the record is done, the task disappears.

**Where:** left menu → My Tasks (the number shows how many tasks are open), and the **My tasks** card on the Dashboard. **Who:** everyone. Each person only sees what their access allows.
**CSQ:** supports 1.1 (responsibilities), 1.4 (records), 1.6 (CAPA follow-up), 2A.13.2 (training), 2A.10.4 (hold and release)

![My Tasks: overdue first, assigned to you and decisions at your level](shots/sec_tasks.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You start your shift | Open **My Tasks**; work from the top (overdue first) |
| You only want your own assignments | Click the **Waiting for you** card |
| You approve and release | Click the **Your decision** card |
| You want the list on your phone or in your inbox | **Email me this list** |
| A task is done | Open it with **Open**, finish the record; the task disappears on its own |

### What is in the list
| Waiting for you (assigned to you) | Waiting for your decision (needs your access level) |
|---|---|
| SOPs you must read and sign (current version not signed yet) | SOP drafts to approve (Full on SOPs) and SOP reviews due within 30 days |
| Training you need and have not done, or that expires within 30 days | Holds to decide (Full on Hold and Release) |
| CAPAs where you are the responsible person | Lots in quarantine to accept or reject (Full on Receiving) |
| Deviations and audit findings you own | Suppliers waiting for approval (Full) and supplier reviews due (Edit) |
| Complaints you investigate | Changes waiting for approval (Full on Change Control) |
| Risks you own with a review due within 7 days | Calibrations and revalidations due within 14 days (Edit on Equipment) |
| Quality objectives you own that are due within 30 days | Out-of-limit CCP checks not yet verified (Edit on HACCP) |
| Actions given to you in Change Control and Management Review | The next management review when it is due within 30 days |
| Verification activities you are responsible for, due within 7 days | Test results not entered 7 days after the sample went to the lab; deviations without an owner (Full on QMS) |

Each row shows the area, the record, a short detail and the due date: **Overdue** in red, **Due today / tomorrow** in gold. **Open** goes to the module of the record.

Names are matched to your name in Team and Access, without regard to capitals or spaces. Write owners in records exactly as people's names appear in Hendrix.

![The My tasks card on the Dashboard](shots/sec_tasks_card.png)

> **Hendrix checks:**
> - The list is worked out by the database with your own access: you never see records of a license you cannot open, or decisions above your level.
> - "My Tasks is not set up yet - run hendrix_step39.sql" when the database step is missing.

## My account and two-step sign-in
My account is your own page: turn on two-step sign-in, choose whether you get the daily task email, and change your password.

**Where:** click your name at the top right. **Who:** everyone, for their own account.
**CSQ:** supports 1.4 (documentation and recordkeeping); 21 CFR Part 11 benchmark 11.300 (password controls)

![My account: setting up two-step sign-in](shots/sec_account_setup.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| You want to protect your account | **Set up two-step sign-in** |
| The admin made two-step sign-in required for you | You are asked to set it up at your next sign-in |
| You got a new phone | Ask an admin to turn two-step off for you, then set it up again |
| You do not want the daily email | Untick **Email me my task list on work days** |
| Your password may be known to someone | **Change password** |

### Set up two-step sign-in
1. Install an authenticator app on your phone (Google Authenticator, Microsoft Authenticator, 1Password or similar).
2. Click **Set up two-step sign-in**. Scan the QR code with the app, or type the key shown under it.
3. Type the 6-digit code the app shows and click **Turn on two-step sign-in**.

From now on, Hendrix asks for the code after your password every time you sign in, and when you sign records (see Electronic signatures). The badge on the page shows **On** and, when an admin made it compulsory, **Required for your account**.

![Two-step sign-in at sign-in](shots/sec_gate.png)

### Forgot password (temporary password from an admin)
Until password-reset email is set up, a person who forgot their password asks a system admin:
1. Admin: **Team and Access** → **Manage** on the person → **Set a temporary password**. Hendrix suggests a readable one (for example `WPYt-vF8F-Uktn`); **Generate** makes another, or type your own (at least 8 characters). Click **Set password**.
2. Give the temporary password to the person **in person** (not by text or email). Their other open sessions are signed out.
3. The person signs in with it. Hendrix shows **Choose a new password** before anything else opens; they type their own password twice and click **Save my new password**.

The reset is in the Audit Trail ("Password reset by an admin"). Hendrix never stores passwords, only the secure hash kept by the sign-in service. On the sign-in page, **Forgot your password?** tells people to ask an admin.

### Change password
| Field | What to enter | Required |
|---|---|---|
| New password | At least 8 characters | Yes |
| New password again | The same password | Yes |

> **Hendrix checks:**
> - "That code is not correct or has expired. Enter the current 6-digit code from your authenticator app."
> - When two-step sign-in is required, the database gives the person **no access at all** until the code is entered, even if the page is opened another way.
> - Only an admin can turn the requirement off: "Only an admin can turn off two-step sign-in."
> - "Use at least 8 characters." and "The two passwords are not the same."

## Electronic signatures
Approvals, releases and other decisions are electronic signatures. Hendrix asks for your password again before saving them (and your authenticator code when you use two-step sign-in), and keeps each signature for good.

**Where:** appears by itself when you approve, release or sign. **Who:** the person signing.
**CSQ:** supports 1.4 (records and data integrity); 21 CFR Part 11 benchmark 11.50, 11.70, 11.100, 11.200

![Electronic signature: the meaning and the record are shown; the password is your signature](shots/sec_esign.png)

### When it is asked
| Action | Meaning saved with the signature |
|---|---|
| Approve and publish an SOP | Approved and published this SOP |
| Sign an SOP as read | Read and understood this SOP |
| Close a deviation, a risk, an internal audit or a complaint | Closed this deviation / risk / internal audit / complaint |
| Close a CAPA as effective | Verified this CAPA effective and closed it |
| Decide a hold (release, destroy, return, rework) | Decided this hold: released (or the decision taken) |
| Accept or reject a lot | Accepted this lot for use / Rejected this lot |
| Save a final test result | Recorded the final test result: Passed / Failed |
| Approve a supplier | Approved this supplier (with conditions) |
| Approve or close a change | Approved this change / Closed this change after the effectiveness check |
| Sign a management review as held | Signed this management review as held |
| Validate or activate a HACCP plan | Validated this HACCP plan / Approved and activated this HACCP plan |
| Verify a CCP record | Verified this CCP record |

The box shows who is signing, the meaning, the record and the time. Type your password (and the code) and click **Sign**. **Cancel** stops the action: "Signature cancelled - nothing was saved."

Every signature is kept in a permanent signature log with your name and email from the sign-in (never typed), the meaning, the record, the method (password, or password + authenticator) and the server time. It also shows in the Audit Trail.

> **Hendrix checks:**
> - "That password is not correct." - nothing is saved.
> - Signatures cannot be changed or deleted, by anyone: "Electronic signatures are permanent: they cannot be changed or deleted."
> - The signer is always the signed-in person, whatever name is sent.
> - The signature step can be switched off per license (Settings → Security), but auditors expect it on; System Health shows a fail when it is off.

## Security settings and automatic sign-out
Each license chooses whether signatures need the password, and after how many minutes without activity people are signed out.

**Where:** Settings → **Security**. **Who:** Full access on Settings (system admins can always).
**CSQ:** supports 1.4 and 1.9 (product defense); 21 CFR Part 11 benchmark 11.10(d)

![Settings → Security](shots/sec_settings_security.png)

| Field | What to enter | Default |
|---|---|---|
| Ask for the password when signing | Keep ticked | On |
| Sign people out after ... minutes without activity | 0 to 480 (0 = never; kiosks are not affected) | 30 |

One minute before the sign-out, a gold banner warns: "No activity: you will be signed out in 60 s. Move the mouse or press a key to stay signed in." After the sign-out the sign-in page says "You were signed out after 30 minutes without activity."

![The warning one minute before the automatic sign-out](shots/sec_idle.png)

> **Hendrix checks:**
> - "Automatic sign-out must be between 0 and 480 minutes (0 = never)."
> - New licenses start with the secure defaults (password on, 30 minutes).

## Email: daily task list and urgent alerts
Hendrix sends two kinds of email: a daily task list to each person (the same as My Tasks, for every license they work at), and urgent alerts within about 10 minutes when something needs attention now.

**Where:** your inbox; the switch is in My account; admins see the email log in Settings → **Email**. **Who:** everyone gets their own list; alerts go to the people with Full access to the area at that license.
**CSQ:** supports 2A.10.4 (hold and release), 1.6 (CAPA), 1.8 (recalls and withdrawals)

![Settings → Email: is email working, and what was sent](shots/sec_settings_email.png)

### Urgent alerts
| Event | Sent to people with Full access on |
|---|---|
| A hold is placed | Hold and Release |
| A test result is Failed | Testing |
| A deviation is reported (or raised) as critical | QMS (Deviations, CAPA) |
| A complaint is critical | Complaints |
| A real recall or withdrawal is started (not a mock) | Traceability and Recall |

Every email is written to the email log (when, to whom, subject, sent or failed with the reason). An alert that could not be sent stays waiting and is tried again.

### Set-up (once, by the system owner)
1. At resend.com, verify the company email domain and create an API key.
2. In Supabase → Edge Functions, deploy `hendrix-notify.ts` with the name **hendrix-notify** (Verify JWT off).
3. In Edge Functions → Secrets, add `RESEND_API_KEY`, `HX_MAIL_FROM` (for example Hendrix QMS <qms@blackfoxmfg.com>) and `HX_CRON_SECRET` (a long random text).
4. Run the two `cron.schedule` lines at the end of `hendrix_step39.sql`, with the same secret.
5. Test: My Tasks → **Email me this list**.

> **Hendrix checks:**
> - "Email is not set up: add RESEND_API_KEY and HX_MAIL_FROM in Supabase > Edge Functions > Secrets."
> - The schedule can only start the function with the secret; the task list of each person is worked out with that person's own access.
> - System Health warns when no email was ever sent and fails when alerts wait more than 1 hour.

## Kiosks without internet
The time clock, facility log and visitor kiosks keep working when the internet drops. Scans and entries are saved on the tablet with the real time they were made, and sent to Hendrix by themselves when the internet is back.

**Where:** on the kiosk tablets. **Who:** everyone using a kiosk; managers check the kiosk screen for refused items.
**CSQ:** supports 1.4 (contemporaneous records), 1.9 (product defense: who is on site), 2A.3 (sanitation logs), 2A.13.8 (visitors)

![Time clock with no internet: the scan is saved on the tablet](shots/sec_kiosk_offline.png)

### What happens
| Kiosk | Without internet | When the internet is back |
|---|---|---|
| Time clock | "Scan saved on this tablet". The punch keeps the scan time | Punches are added in scan order; late breaks are worked out from the real times; the sign-in sheet marks them **(O)** |
| Facility logs | "Saved on this tablet (no internet)" | The entry is added with the time it was done on the tablet, marked offline |
| Visitors | Sign-in saved on the tablet; sign-out waits for the internet | The visitor's time in is the time they signed in |

A gold bar on the kiosk shows how many entries are waiting, with **Send now**. The kiosk page itself reopens without internet after it has been opened once with internet (the tablet keeps a copy).

If Hendrix does not accept a saved item (for example "Badge not recognized." or the scan is older than 72 hours), a red box lists it on the kiosk so a manager can add it by hand with a reason (Time Clock → **+ Missed punch**). **OK** clears the list.

![A saved scan that Hendrix did not accept](shots/sec_kiosk_refused.png)

> **Hendrix checks:**
> - Each saved item has a one-time id: sending it twice never makes two records.
> - Items older than 72 hours or dated in the future are refused: "Saved more than 72 hours ago: too old to be added automatically. A manager can add it by hand with a reason."
> - The same rules apply as online: active license in that state, valid badge, signature and name on log entries.
> - System Health shows how many offline items arrived in the last 7 days and how many were refused.

## METRC Check
METRC Check compares what METRC says about the license's packages with what Hendrix knows, and lists every difference to fix. It never changes anything in METRC.

**Where:** left menu → METRC Check. **Who:** View sees the checks; Edit uploads the METRC export or reads METRC.
**CSQ:** supports 1.3 (regulatory compliance), 2A.10.1 (traceability), 2A.10.4 (hold and release), 2A.12.9 (testing)

![METRC Check: differences between METRC and Hendrix, most serious first](shots/sec_metrc.png)

### When to use it
| Situation | What you do in Hendrix |
|---|---|
| Weekly, and before an inspection | Export active packages from METRC; **Upload METRC export** |
| METRC keys are set up | **Read from METRC now** |
| A difference is listed | **Open** the record and fix Hendrix or METRC |
| QA signs off the reconciliation | **Print report**, fix, initial and date each line |

### What it finds
| Level | Difference |
|---|---|
| Fix now | On hold in METRC with no open hold in Hendrix, or an open Hendrix hold not on hold in METRC |
| Fix now | Passed in Hendrix but METRC's lab status is not TestPassed |
| Fix | METRC says the test failed while Hendrix has no failed test |
| Fix | Shipped in Hendrix but the package is still active in METRC (transfer not done) |
| Fix | An accepted lot with quantity left in Hendrix that METRC no longer lists |
| Check | The quantity left differs by more than 2% (same unit, g = Grams, ea = Each) |
| Info | Active METRC packages Hendrix does not know at all |

Tags are compared without spaces or dashes, in any case. The METRC export can be CSV or Excel; title rows, quantities like "700 Grams" and dates like 10/18/2026 are understood. Each check is kept; pick an older one from **Check of**.

To read METRC directly, the system owner deploys `hendrix-metrc.ts` (name **hendrix-metrc**, Verify JWT off) and adds the secrets `METRC_VENDOR_KEY` and `METRC_USER_KEYS` (the user key of each license number). Until then, the export upload does the same check.

> **Hendrix checks:**
> - "No tag column found. Use the METRC export of Packages (it has a Tag or Label column)."
> - "You need Edit access to METRC Check at this license."
> - "METRC keys are not set for license ...: ... Until then, upload the METRC export (CSV)."
> - Every upload is in the Audit Trail.

## System Health
System Health checks the installation the way an auditor's Installation Qualification does, and prints the evidence. Nothing is changed.

**Where:** left menu → System Health. **Who:** system admins.
**CSQ:** supports 1.4; this pack's IQ (section 9 of the Validation and Certification Pack)

![System Health](shots/sec_health.png)

| Area | What it checks |
|---|---|
| Database | Every database step 4 to 41 is installed; the database clock agrees with this device |
| Security | Row level security on every table; every record table audited; the audit trail locked; password at every signature; two-step sign-in for admins |
| People | Number of admins (1 to 3); accounts waiting for approval; approved people with no access |
| Files | The private file storage exists and is not public |
| Email | When Hendrix last sent email; alerts waiting more than 1 hour |
| Kiosks | Offline kiosk items received and refused in the last 7 days |
| AI | **Test the AI connection** (one very small paid request) |
| Licenses | Business details, operation and CSQ standard set for each license |

Each line shows ✓ (pass), ! (check) or × (fail) with the fix. **Print IQ evidence** prints the results with sign-off lines for the person who checked and for QA.
