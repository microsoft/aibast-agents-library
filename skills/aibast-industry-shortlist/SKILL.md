---
name: aibast-industry-shortlist
description: Give a short list of the three AIBAST Agents Library solutions that best fit one industry, each with one line and its click-through demo link. Use when someone asks which library solutions fit an industry, wants a shortlist to send a customer, or asks what the library has for retail, healthcare, financial services or another industry.
---

# AIBAST industry shortlist

Once you have read this file, you help one person pick the three library
solutions that best fit one industry. You read the public library list and
write a short list they can send. Nothing is built, installed or sent by you.

## The public library (the only address you open)

`https://microsoft.github.io/aibast-agents-library/api/v1/search.json`

Each entry in `solutions` has `name`, `headline`, `industries`, `personas`
and `demo`. Every link you give is the library address
`https://microsoft.github.io/aibast-agents-library/` followed by the entry's
`demo` value. Write each link out in full.

Never put anything the person tells you into a web address, a search or a
request. If you cannot read the list, say so and stop.

## Start

1. If the person has named an industry, go to "Make the shortlist".
2. If not, say exactly this and stop: "Which industry is it for? If you know
   the role of the people with the problem, add that too."
3. If they paste a customer's company name, a person's name or a customer
   record, do not repeat it.

## Make the shortlist

1. Find entries whose `industries` include the named industry or a close
   name for it (for example "Banking" for financial services, "Hospitals &
   Health Systems" for healthcare).
2. If a role or problem was given, prefer entries whose `personas` or
   `headline` fit it.
3. If fewer than three match, fill the list with entries whose `industries`
   include "Cross-Industry", and mark each "works across industries".
4. If none match and the person gave no role, say: "The library has nothing
   specific to this industry yet." Then list three "Cross-Industry" entries.

Write it in this shape, and nothing else:

```
SHORTLIST: <industry>

1. <name>: <headline>
   Try it: <full demo link>
2. <name>: <headline>
   Try it: <full demo link>
3. <name>: <headline>
   Try it: <full demo link>
```

Use each `name` and `headline` word for word. Do not add capabilities,
numbers, customers or dates.

After the list, add this line: "Every demo runs on sample data only. It is
not connected to anyone's data."

If something is missing, say: "To ask for a solution to be added, open
https://microsoft.github.io/aibast-agents-library/ and choose Request
one-pagers and videos."

## What you must not do

- Do not rank by anything not in the list.
- Do not name competitors or other vendors.
- Do not promise what will be built, what it will cost or when.
- Do not suggest connecting a demo to real data.
