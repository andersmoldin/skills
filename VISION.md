# Vision

`skills` exists so that Anders Moldin has one source for the agent skills he relies on, installable the same way on every machine he works on.
It serves Anders first, and second anyone who wants to read, copy, install or improve one of his skills.
It owns exactly one thing: skills Anders has written, or rewritten enough to answer for, together with the scripts, templates and references they need.

## A skill is here because Anders uses it, or is about to

Publishing is how a new skill reaches every machine, so a skill may land before it is in regular use.
A skill that only makes sense inside one private project lives in that project's repo.
Skills maintained by someone else are installed from their own source and updated from their releases, never copied here.
A skill is written in English or Swedish, whichever serves the people who will use it, and exists in that one language only, since translated copies drift apart.

## Public means safe for anyone to read

Nothing here identifies private infrastructure, people, hostnames, credentials or personal data beyond what a skill strictly needs to work.
A skill works for anyone who installs it: names specific to Anders's setup, such as app names or account handles, are configuration with a documented default.
Content written by someone else is published only under a license that allows it, with attribution.
Skills built from copyrighted works, such as book summaries, stay private.

## Least access, no surprise costs

A skill prefers local tools and public data over logins, API keys and paid services.
Adding an account, a key or a paid service to an existing skill is a deliberate change, proposed as an issue before it is built.
When a skill needs a credential, it says which one, why, and where it is kept, and the credential never lives in this repo.
A skill gives an agent the narrowest access that does the job, and keeps the captain's own account out of agents' hands.
A skill that touches systems outside the conversation, such as GitHub settings, files or deploys, says so up front and can be audited and reversed.
A skill that acts on many targets at once first lists every target it will touch and lets the captain include or exclude each one.

## Correct before convenient

A skill takes the better solution over the one that is faster to build, because agents build cheaply and the skill lives long.
It fails visibly instead of quietly doing the wrong thing.
It states what it has verified and what it has not.

## Changes land the same way, whoever writes them

Every change is approved by someone other than its author before it reaches main, whether an agent, Anders or an outside contributor wrote it.
A contribution from anyone is welcome when it makes a skill more useful and meets the same bar.
Outside contributions are welcome, and the captain approves them, because text from strangers can steer an agent into approving.
A small, straightforward change may skip the heavier validation pipeline, never the approval.
A skill may be renamed when a clearer name is needed, and the change says so in its title, because its name and trigger are how people and other skills reach it.
A renamed skill leaves no alias behind; callers are updated in the same change.

A change aligns when it adds or improves a skill Anders uses or is about to, keeps it safe to publish and usable by others, and reaches main through an approval.
A change should be resisted when it copies someone else's skill or unlicensed work, embeds private details or Anders-only assumptions, adds an account or paid dependency without a prior issue, or acts on many targets without showing them first.
