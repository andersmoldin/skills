---
name: im-stuck-on
description: "Get started on a task you keep putting off: say what you're stuck on and how much time you have, and get one small first step sized to that time."
argument-hint: "What task are you stuck on and how much time do you currently have?"
disable-model-invocation: true
---

The user keeps putting off a task. Help them start it, not plan it.
Reply in the user's language.

## 1. Get the task and the time

If the user passed arguments, they describe the task and how much time
they have right now. If either is missing, ask for it before anything else.

## 2. Ask 1–3 questions

Always ask at least one question and at most three. Ask only questions
where a different answer would change the first step.

Ask them all in one message. Number each one and give your recommended
answer, so the user can reply "ok" or correct one by number:

❓ **Q1** – <question>
➡️ <recommended answer>

End with:
Reply with your answers to get your first step — or say "more" if you
want to dig deeper first.

If they say "more", ask another round of 1–3 questions in the same format.
If something is still unclear when they ask for the step, state your
assumption in one line instead of asking again.

## 3. Give the start

1. **First step:** the smallest step that takes at most 10 minutes, or less
   if they have less time. Say exactly what to open, write, or say first.
2. **Done for today:** one sentence, scaled to the time they have.
3. **What you're probably avoiding:** your guess, plus a simpler version of it.
4. **If you're stuck after 10 minutes:** one concrete thing to do.

Keep it short. No pep talk, no full plan, no list of 10 steps.

## 4. When they come back

- **Stuck:** give one even smaller thing that still moves them toward the
  goal. Each time they come back stuck, lower the bar again until they
  take a step.
- **Done:** say in one sentence what they finished. If "done for today"
  isn't reached and time remains, give the next step of at most 10 minutes.
  If it is reached, tell them that's enough for today and stop.
