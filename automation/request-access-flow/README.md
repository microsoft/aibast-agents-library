# Request access flow

Turns a submission on [the request form](../../request-info.html) into SharePoint
access, automatically, for Microsoft-internal requesters. External requesters go
to a person instead.

This directory is the recipe and its settings shape. It holds no tenant values:
the site URL, the group and the owner mailbox live in `settings.local.json`,
which is gitignored, because this repository is public.

## The problem this has to solve first

The form asks the requester to type their work email. **A typed address proves
nothing.** Anyone can type `someone@microsoft.com`. A flow that grants access
because the typed domain matched is an open door, and it is the obvious way to
build this.

So the flow does not look at the domain. It looks the address up in the
directory, and it acts on what the directory returns:

1. The typed address is used for **one** thing: a directory lookup.
2. If the lookup fails, nobody is granted anything and a human is emailed.
3. If the lookup succeeds, the grant is made against the **object id the
   directory returned**, and the confirmation mail goes to the **address the
   directory returned**.

That last rule is what makes a spoofed submission harmless. If someone types a
colleague's address, the colleague, a real Microsoft employee, receives access
and the mail. The person who submitted the form gets nothing and learns nothing.
The failure mode is a confused colleague, not a leak.

A directory lookup proves the address belongs to a real account in the tenant.
It does not prove the submitter is that person. Nothing available at form-submit
time can prove that, which is why the grant and the notification both follow the
directory rather than the form.

## What it grants

Membership in one group, and nothing else. Do not grant per-item sharing links,
and do not grant anything above read.

- The group is a security group whose only privilege is **read** on the internal
  library.
- Membership is the whole access model, so revoking is one removal in one place.
- The flow never touches site permissions, sharing settings or ownership.

## Prerequisites

| What | Why |
| --- | --- |
| A security group with read access to the internal library | The unit of access. Create it first; the flow only adds members. |
| A Power Automate connection for Microsoft Forms | Reads the submission. |
| A connection for Office 365 Users | Does the directory lookup. |
| A connection for Microsoft Entra ID (shown as Azure AD) | Adds the member. Needs rights to write group membership. |
| A connection for Office 365 Outlook | Sends both mails. |
| An owner mailbox | Where external and failed requests land. |

Run the flow under a service account that owns the group, not under a person.
When a person leaves, a flow owned by them stops.

## Build it

Create a cloud flow in the same environment as the form owner. Each step below
gives the connector, the action as the designer names it, and the exact
expression to paste.

**1. Trigger — Microsoft Forms, "When a new response is submitted"**

Pick the request form. The form id is the `id` parameter in the form URL on
`request-info.html`.

**2. Microsoft Forms, "Get response details"**

Form id: the same form. Response id: `Response Id` from the trigger.

**3. Compose, named `Requested address`**

```
@trim(toLower(outputs('Get_response_details')?['body/<email question id>']))
```

Replace `<email question id>` with the question id for the work-email field.
The designer shows it when you pick the field from the dynamic content list.
Trimming and lower-casing here means every later step compares the same thing.

**4. Office 365 Users, "Get user profile (V2)", named `Resolve in the directory`**

User (UPN): `@outputs('Requested_address')`

Then open the action's settings and **configure run after** so the next step
runs on both success and failure. Without this the flow stops on a lookup miss,
which is exactly the case you most need to handle.

**5. Condition, named `Is this a real account`**

```
@equals(actions('Resolve_in_the_directory')?['status'], 'Succeeded')
```

**If yes:**

**5a. Microsoft Entra ID, "Add user to group"**

- Group id: `@parameters('accessGroupId')`
- User id: `@body('Resolve_in_the_directory')?['id']`

Use the object id the lookup returned. Do not use the form answer here. This is
the line that decides whether the flow is safe.

**5b. Office 365 Outlook, "Send an email (V2)", named `Tell the employee`**

- To: `@body('Resolve_in_the_directory')?['mail']`
- Subject: `Your AIBAST internal library access is ready`
- Body: the library link, what is in it, and who to contact to have access
  removed.

The recipient is the directory address, never `outputs('Requested_address')`.

**If no:**

**5c. Office 365 Outlook, "Send an email (V2)", named `Ask a human`**

- To: `@parameters('ownerMailbox')`
- Subject: `Access request needs review`
- Body: the submitted name, the typed address, the solutions requested and the
  stated purpose, plus a line saying the lookup did not resolve.

No grant happens on this branch. That is the point of the branch.

**6. Turn on the flow's run history retention and leave it on.**

Every grant should be answerable six months later.

## Settings

Copy `settings.example.json` to `settings.local.json` and fill it in. That file
is gitignored. Nothing in it belongs in this repository.

## Test it before you trust it

Run all four cases and confirm the result, not the flow's green tick:

| Case | Submit | Expected |
| --- | --- | --- |
| Real internal account | Your own work address | You are added to the group and receive the mail. |
| Plausible but fake | `not-a-real-person@microsoft.com` | No grant. The owner mailbox gets a review mail. |
| External requester | A personal address | No grant. The owner mailbox gets a review mail. |
| Already a member | Your own address again | The flow succeeds and does not duplicate or error. |

Check case two by looking at the group membership afterwards, not by reading the
run history. A flow can report success and still have granted nothing, or
granted the wrong thing.

## What this deliberately does not do

- It does not remove access. Removal stays manual and deliberate.
- It does not grant write, ownership or site permissions.
- It does not create the group, so a misconfigured flow cannot invent a new
  access boundary.
- It does not email the submitted address. Ever.
