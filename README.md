# Amdari Project 1 — From Manual Identity Admin to Automated, Auditable Onboarding (Entra ID + Graph)

## The story (why this project existed)

Amdari had already migrated to Microsoft cloud identity (Microsoft Entra ID + Microsoft 365 with P1 licensing), but the day-to-day work of identity administration still looked like “old IT”:

> Despite the platform migration, day-to-day identity administration remains manual, performed individually by IT administrators.

That meant onboarding a single employee could take **2–3 hours**, and the quality of access depended on who handled the request and how busy they were that day.

At the same time, the security posture wasn’t keeping up with the platform:
- MFA enforcement was inconsistent
- legacy authentication was still possible
- Conditional Access wasn’t configured
- Identity Protection wasn’t configured
- admin privileges were standing (always-on), with no Just-In-Time model
- audit reporting was hard and manual

Management’s concerns were very direct:
> delayed onboarding, inconsistent provisioning, excessive administrative effort, weak privileged-access controls, and limited audit visibility.

So the assignment wasn’t to “install Entra.” It was to **close gaps** and produce an operational identity system that was:
- faster
- standardized
- secure by default
- auditable

---

## What I was asked to deliver (the mission)

This engagement had measurable objectives (not vibes):

1. **Onboard 100 users** across **five departments** within a two-week window.
2. Reduce provisioning time from **2–3 hours per user** to **under 5 minutes** per user.
3. Automate onboarding end-to-end using **Python + Microsoft Graph**:
   - account creation
   - attributes + manager
   - group assignment
   - license assignment (P1)
4. Validate HR CSV input **before** creating anything:
   - required fields
   - duplicates
   - email formats
   - department mapping
5. Enforce modern security controls:
   - MFA enforcement
   - block legacy authentication
   - staged Conditional Access rollout
6. Turn privileged access into a governed system:
   - **PIM eligible roles**
   - **Zero standing Global Admin**
   - **JIT activation** (time-bound, MFA, justification, approval)
7. Implement **license governance**:
   - automated assignment
   - inventory reporting
   - identify unused licenses
   - reclamation workflow
8. Produce **audit-ready reports** and map controls to frameworks:
   - Microsoft Zero Trust
   - CIS Controls v8
   - CIS Azure Foundations Benchmark
   - NIST CSF
   - ISO 27001 (Access Control domain)

---

## Step-by-step: what I did and how I did it

### Step 1 — I documented the current-state risks (so we fixed the right problems)
Before touching configuration, I wrote down the operational and security reality in plain language (and aligned it to what management was already worried about):

- Manual account creation: **2–3 hours** per employee
- Manual group + license assignment: error-prone
- No consistent baseline onboarding standard
- MFA inconsistent across user population
- Legacy auth allowed
- No Conditional Access policies
- Standing admin privilege (no JIT / no PIM)
- No Identity Protection policies (risk signals not acted on)
- Audit reporting = manual pain
- No license inventory/utilization/reclamation process

This became the baseline for measuring improvement.

---

### Step 2 — I built a clean IAM foundation (groups, Administrative Units, RBAC)
To prevent onboarding from becoming a “one-off script,” I set up structure first:

- **Department security groups** (Finance, HR, Operations, IT, Security)
- **Dynamic groups** where needed (attribute-based membership)
- **Administrative Units** to delegate administration by department boundary
- A least-privilege **RBAC model** mapped to job functions (e.g., Helpdesk vs Security Reader vs User Admin)

The goal: once onboarding runs, the identity lands in the correct boundaries automatically.

---

### Step 3 — I implemented Conditional Access in a staged rollout (not “big bang”)
Because Conditional Access can break access if rushed, I treated it like a deployment:
- staged policies
- careful scope
- enforcement of MFA
- explicit blocking of legacy auth paths
- aligned to “how and from where access is granted”

This directly addressed:
- inconsistent MFA enforcement
- legacy authentication protocols bypassing modern controls
- lack of policy controls around access conditions

---

### Step 4 — I configured Identity Protection (risk-based detection + remediation)
The project required more than “MFA everywhere.” It required detection and response:

- enabled **user risk** and **sign-in risk** policies
- configured automated remediation paths (e.g., require secure actions when risk is high)
- ensured risky sign-ins (impossible travel / leaked credentials patterns) were not ignored

This directly addressed:
- “risky sign-ins undetected”
- “no automated remediation when compromise indicators appear”

---

### Step 5 — I removed standing privilege using PIM + Just-In-Time access
One of the most important security outcomes: **no always-on power accounts.**

So I:
- converted privileged roles to **PIM eligible assignments**
- implemented **Just-In-Time activation** with:
  - time-bound access (default 1 hour, max 2 hours)
  - MFA
  - justification
  - approval workflows (where required)

Outcome: privileged access became **governed and auditable**, not assumed.

---

### Step 6 — I built the onboarding automation (Python + Microsoft Graph)
This is the engine that solved the “2–3 hours per employee” pain.

The automation flow was designed like a production system:

1. **Input**: HR-provided CSV
2. **Pre-flight validation**:
   - required fields present
   - duplicates detected
   - email format checks
   - department mapping checks
3. **Provisioning** (only after validation passes):
   - create user
   - set attributes + manager
   - add to department groups / dynamic rules
   - assign Entra ID P1 license
4. **Reporting**:
   - onboarding report (success/failure)
   - error report (actionable)
   - license assignment report

This directly addressed:
- delayed onboarding
- inconsistent provisioning
- admin effort
- audit visibility

---

### Step 7 — I added license governance (inventory + reclaim)
Licenses are both a cost problem and a governance problem. I implemented a model for:

- automated license assignment (baseline)
- inventory reporting (who has what)
- unused license identification
- reclaim workflow (reduce waste, improve control)

---

### Step 8 — I closed a governance gap: added an Owner account (accountability + continuity)
During implementation I identified an operational risk: **lack of clear ownership** can make troubleshooting and change control messy.

So I took an explicit governance step:

> Owners can manage membership and settings; having none is a governance risk and makes troubleshooting harder. I added my Admin Account as an Owner.

Why that mattered:
- **Governance & audit**: accountability for changes
- **Operational continuity**: no single-admin dependency
- **Change control**: owners can handle exceptions and approvals

---

## Evidence (screenshots)

> These images are currently linked from my working notes. For GitHub, move them into your repo (e.g., `assets/screenshots/`) and replace the links with relative paths like `![](assets/screenshots/yourfile.png)`.

![](file://%7B%22source%22%3A%22attachment%3Ad1e28fb0-0a42-4cf1-959a-0373e302be3b%3AScreenshot_2026-06-25_151931.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%22c4049353-a3dc-482e-8759-cfdceb78ff02%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3A85fd2130-eace-4901-9713-849cdca541ba%3AScreenshot_2026-07-09_104554.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%222112d594-e772-41e1-8c4c-4b6d206a64a6%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3Af8fde60f-c153-4679-919f-924721b0c1ab%3AScreenshot_2026-07-09_104553.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%22389c27e0-6dfb-4215-b730-39380e389075%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3A2e6e9463-200e-435d-9348-5fb67540c6db%3AScreenshot_2026-07-09_104457.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%221141c665-75f0-4f3c-b038-cdd8ace2434b%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3Afffdb68e-4a32-4e2f-a173-7a8d803902c5%3AScreenshot_2026-07-09_103206.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%220cbd3fb6-db3e-4b53-9ba6-09bc91429c61%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3Aa6b5211e-84c2-4d67-83cc-a4c09d7eb68e%3AScreenshot_2026-07-09_102606.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%2201533634-539c-4fba-b995-6297572a66b0%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3Add2d29c7-fe87-4a49-882e-8f67793d7108%3AScreenshot_2026-07-09_102358.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%223b2741c6-3454-4943-83b6-69e7e679d3c1%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3A40cb1ec6-0c00-4e9b-bbe8-ea97fca63dbd%3AScreenshot_2026-07-09_102110.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%22c859662a-8a33-4da8-a247-f31448779f9b%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)
![](file://%7B%22source%22%3A%22attachment%3A576f2e2f-18eb-45b0-8eca-c50ea9aab801%3AScreenshot_2026-07-09_101914.png%22%2C%22permissionRecord%22%3A%7B%22table%22%3A%22block%22%2C%22id%22%3A%227c22b3ae-b32b-4913-9578-b3969cfa3e0b%22%2C%22spaceId%22%3A%22300e4c7e-c47f-810a-9f17-0003a2002d92%22%7D%7D)

---

## Outcomes (how the project solved management’s worries)

### 1) Delayed onboarding → **Automated onboarding pipeline**
- CSV-driven provisioning with validation
- consistent baseline for every user
- under-5-minute provisioning target

### 2) Inconsistent provisioning → **Standardized IAM model**
- groups, AUs, dynamic rules
- role design by function
- predictable access outcomes

### 3) Excessive admin effort → **Automation + reporting**
- fewer manual steps
- repeatable process
- audit-ready outputs

### 4) Weak privileged controls → **PIM + JIT**
- eligible assignments
- time-bound activation
- MFA + approvals + justification
- no standing Global Admin

### 5) Limited audit visibility → **Built-in reporting + governance**
- onboarding reports
- error reports
- license reports
- traceable privileged activation logs

---

## Documentation deliverables checklist

- [ ] Finalise design documentation, security-configuration docs, and administrative runbooks  
- [ ] Produce the final project report with framework mapping and future-expansion recommendations  
- [ ] Submit your documentation, powerpoint slides and github link to your automation for review by your team lead  
- [ ] Conduct internal lessons-learnt and update the knowledge base  

---

## Repo structure (if publishing on GitHub Pages)
