# Achievers Wealth Academy, n8n Workflows

This folder holds the n8n automations that sit behind the live `achieverswealth` site forms.

## Files

| File | Purpose |
|---|---|
| `lead-auto-responder.json` | Importable n8n workflow. Webhook trigger, normalizes the form payload, sends TWO emails in parallel (auto-responder to the lead + internal notification to Cherry Jane), responds 200 so the in-page success message fires. |
| `auto-responder-email.html` | Standalone copy of the auto-responder HTML body (the email the lead receives). Edit here first, preview in browser, then paste into the **Send Auto-Responder** node in n8n. |
| `internal-notification-email.html` | Standalone copy of the internal-notification HTML body (the email Cherry Jane receives for every new lead). Edit here first, preview in browser, then paste into the **Send Internal Notification** node in n8n. |

## What this workflow does

When someone submits the contact form on `achieverswealth.com/contact.html`, the site POSTs JSON to:

```
https://n8n.srv1180913.hstgr.cloud/webhook/achievers-wealth-academy-lead
```

The workflow:

1. Receives the JSON payload.
2. Pulls `first_name`, `last_name`, `phone`, `email`, `reason`, `message`, and `submitted_at` into clean variables. Maps the dropdown value into a human phrase (e.g. `become_an_agent` becomes "becoming a licensed agent"). Defaults an empty message to "(none provided)".
3. **In parallel:**
   - Sends a branded auto-responder email from `achieverswealthacademy@gmail.com` back to the submitter.
   - Sends an internal lead-alert email to `achieverswealthacademy@gmail.com` with full lead details, a tappable phone link, and a "Call Now" button. Reply-To is set to the lead's email so hitting Reply in Gmail goes straight to the lead, not back to herself.
4. Returns `{ "ok": true }` with status 200 so `js/main.js` displays the green in-page success message.

## One-time setup

### 1. Create the Gmail OAuth credential

In n8n at `https://n8n.srv1180913.hstgr.cloud`:

1. Credentials, New, **Gmail OAuth2 API**.
2. In Google Cloud Console (Cherry Jane's account, or shared agency project), enable the Gmail API, create an OAuth client (Web), and add `https://n8n.srv1180913.hstgr.cloud/rest/oauth2-credential/callback` as an authorized redirect URI.
3. Paste Client ID and Client Secret into the n8n credential modal.
4. Click **Sign in with Google**, log in as `achieverswealthacademy@gmail.com`, grant the `gmail.send` scope.
5. Save the credential as `CherryJane Gmail`.

### 2. Import the workflow

1. n8n, Workflows, **Import from File**, select `lead-auto-responder.json`.
2. Open the **Send Auto-Responder** node, set the credential field to `CherryJane Gmail` (replaces the `REPLACE_WITH_GMAIL_CREDENTIAL_ID` placeholder).
3. Open the **Send Internal Notification** node and set the credential to the same `CherryJane Gmail` (also has the placeholder).
4. Save the workflow.
5. Toggle **Active** on.

### 3. Sanity test

From a terminal:

```bash
curl -X POST https://n8n.srv1180913.hstgr.cloud/webhook/achievers-wealth-academy-lead \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Lead",
    "phone": "5555555555",
    "email": "YOUR_TEST_INBOX@gmail.com",
    "reason": "become_an_agent",
    "message": "Just testing",
    "consent_transactional": "on",
    "source": "achievers-wealth-academy",
    "page": "/contact.html",
    "submitted_at": "2026-05-12T03:10:00.000Z"
  }'
```

Expect, within 30 seconds:

- HTTP 200 with `{"ok": true}` in the response.
- **In your test inbox:** Subject "Thanks for reaching out, Test", sender "Cherry Jane Okeke <achieverswealthacademy@gmail.com>", body mentioning "becoming a licensed agent".
- **In `achieverswealthacademy@gmail.com`:** Subject "New lead: Test Lead, becoming a licensed agent", sender "Achievers Wealth Leads <achieverswealthacademy@gmail.com>". Hit Reply: the To field should be `YOUR_TEST_INBOX@gmail.com` (NOT herself), thanks to the Reply-To.

### 4. Live form test

Open `contact.html`, fill it out with a real test email, submit. The page should show the green success message. Both emails should arrive: one in the test inbox, one in `achieverswealthacademy@gmail.com`.

## Editing the emails later

**Auto-responder (the email the lead receives):**

1. Edit `auto-responder-email.html` and preview in a browser.
2. Copy the new HTML into the **Send Auto-Responder** node, "Message" field, in n8n.
3. Save the workflow.

**Internal notification (the email Cherry Jane receives):**

1. Edit `internal-notification-email.html` and preview in a browser.
2. Copy the new HTML into the **Send Internal Notification** node, "Message" field, in n8n. Keep the leading `=` sign in the field so n8n treats it as an expression and interpolates `{{ $json.firstName }}` etc.
3. Save the workflow.

If you re-export the workflow from n8n, overwrite `lead-auto-responder.json` so this folder stays the source of truth.

## Reason label map (kept in sync with the contact form dropdown)

| Dropdown value | Email phrase |
|---|---|
| `get_a_quote` | a free insurance quote |
| `become_an_agent` | becoming a licensed agent |
| `whole_life` | Whole Life Insurance |
| `gul` | Guaranteed Universal Life Insurance |
| `final_expense` | Final Expense coverage |
| `rollover` | a retirement rollover |
| `other` | your inquiry |

If you add a new option to the dropdown in `contact.html`, add the matching phrase to the `reasonLabel` expression in the **Normalize Fields** node.

## Out of scope (future workflows)

- Twilio SMS notification to Cherry Jane (email-only this round).
- Per-reason email branching (e.g. licensing leads get a different long-form email with PHP enrollment steps).
- Google Sheet lead log.
- Twilio SMS confirmation to the lead using the `consent_transactional` flag.
- Drip/nurture sequence after the first email.
- CRM push (HubSpot, Pipedrive, etc.).
