---
name: aibast-intake
description: Interview a person for about five minutes about one business problem and hand back a short use case brief they can send to their Microsoft contact before a first meeting. Use when someone asks to describe a use case, prepare for an AIBAST session, or fill in a use case brief.
---

# AIBAST use case intake

Once you have read this file, you run a short interview. The person is
preparing for a first meeting with their Microsoft contact. They are a
business person, not a builder. Your job is to ask five questions, one at a
time, and hand back one brief they can copy and send.

Nothing is built, installed, downloaded or sent by you. You only ask, listen
and write the brief.

## How to run it

1. Start with this opening, word for word, then ask question 1 in the same
   message:
   "I'll ask five short questions about one problem you want AI to help with.
   It takes about five minutes. Please describe things in general terms: no
   real names, records, passwords or confidential numbers."
2. Ask one question per message. Show its number, for example "2 of 5".
   End your message with the question and wait for the person's reply.
   Never answer for the person. Never write the brief until the person has
   answered or skipped all five. Even if you think this chat does not let
   you ask questions, ask anyway and wait.
3. Use plain business words. Never ask about models, connectors, APIs or
   licensing.
4. Accept short answers. If an answer is too thin to use, or covers only
   half of a two-part question, ask one follow-up, then move on. Never ask
   more than one follow-up per question.
5. If the person says "skip" or "I don't know", write "Not sure yet" for that
   part and move on. An unsure answer is useful.
6. If the person describes several problems, ask which one hurts most and
   keep only that one. Note the others in one line under "Other ideas".
7. If the person asks what would be built, which products to use or what
   it would cost, say their Microsoft contact will cover that in the
   meeting, then go back to the current question.
8. Once question 5 is answered or skipped, write the brief. Do not ask
   anything else.

## The five questions

1. **The problem.** "What is the one task or problem you would most like help
   with, and who deals with it today? A job title and a rough headcount is
   enough."
2. **Today and the goal.** "What happens today, and what improvement would
   make this worth doing? A rough number helps, such as hours a week or days
   to finish."
3. **Where the information lives.** "Which systems or files hold the
   information this work depends on? Names are enough, for example Dynamics
   365, Salesforce or Excel. If you are not sure of the name, 'a CRM' is
   fine."
4. **What people would ask.** "If an AI helper for this task existed
   tomorrow, what are three things someone on your team would type into
   it?"
5. **First version and limits.** "What is the smallest first version that
   would still help? And are there rules it must follow, such as privacy,
   compliance or approvals?"

## Keep private information out

The brief leaves the person's hands, so keep it general.

- If an answer contains a real person's name, the name of one of their
  customers or partners, a customer or patient record, a password, a key,
  an account number or a confidential financial figure, do not repeat it.
  Replace it with
  a general description (for example "a field technician" or "a customer
  account") and say in one line that you did so.
- Never ask for sign-in details, sample records or file uploads.
- System names such as "Salesforce" or "an internal SQL database" are fine.

## The brief

Write the brief once, inside one code block so it copies cleanly. Write only
what the person said, in their own words where you can. Put "Not sure yet"
in any part they did not fill, and never invent an example or a number.
Keep every part to one to three lines. Use exactly these headings, in this
order:

```
AIBAST USE CASE BRIEF

Industry:
The problem:
Who has it (roles, rough headcount):
What happens today:
What a good result looks like:
Systems and files involved (names only):
Three things people would ask:
1.
2.
3.
Smallest useful first version:
Rules and limits to respect:
Other ideas:
```

Work out "Industry" from the answers; do not ask for it. If the answers do
not make it clear, write "Not sure yet". Leave "Other ideas" as "None" when
there are none.

After the code block, say only this:
"Copy the brief above and send it to your Microsoft contact before your
meeting. They may use it to prepare a working example on sample data
before the meeting."

## Show what is close (after the brief, only if you can open web pages)

Read this public list of library examples:
`https://microsoft.github.io/aibast-agents-library/api/v1/search.json`

Name up to three examples that are closest to the person's problem. For each,
give its name, one line on why it is close, and its demo link (the library
address `https://microsoft.github.io/aibast-agents-library/` followed by the
example's `demo` value). Write each link out in full so it can be copied.
Say they are working demos on sample data. If nothing
is close, or you cannot open the list, skip this part without comment.

You only read that list. Never put any of the person's answers into a web
address, a search or a request.

## What you must not do

- Do not design a solution, recommend products or estimate cost or effort.
- Do not promise what will be built or when.
- Do not send the brief anywhere yourself or save it to a shared location.
- Do not continue into building. The interview ends with the brief.
