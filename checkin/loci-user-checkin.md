<!-- CANONICAL SOURCE for the check-in questionnaire.
     build.py (#include-md) generates the 7 Part screens in checkin.html from the
     `## Part N: Title` sections below. Contract per part: intro paragraph(s),
     an optional fenced code block (rendered as a read-only snippet helper), then
     `- ` bullets (each becomes one labeled textarea). Keep that shape or the
     converter output drifts.
     The consent gate, the pulse question, and the closing line are authored in
     checkin.html (page chrome). They are mirrored here for human reading only;
     checkin.html is authoritative for those three. -->

# loci check-in

**How did your palace evolve?**

loci ships as a baseline. It becomes a palace only once you live in it, and
living in it changes it: a room you added, a ritual you bent, a rule you rewrote
because ours did not fit how you think. We cannot see that drift from here, and
it is the most useful thing you could show us. This is the standing channel
between the loci we ship and the loci you actually run. It does not close. Come
back whenever your palace has grown into something we did not predict.

Seven parts. 15-30 minutes depending on how deep you go.

First, the quick one: **how often does your palace actually get opened these days?**
Daily, a few times a week, weekly, or it's been a while. (Lapsed is data too.)

---

## Part 1: Version snapshot

Find your local `Loci/` folder (the setup files, next to your palace). Look for `LOCI-CORE.md` or `PALACE-METHODOLOGY.md` and note the version string. If neither exists, check your README. Read-only, structure only, run from your `Loci/` folder:

```
grep -rhm1 "loci-core version" . --include="*.md" 2>/dev/null
git log --oneline -5 2>/dev/null
```

- If you cloned the repo: paste your `git log --oneline -5`.
- If you set up from templates: roughly when, and what the version string says.
- Scan your palace and setup files. What have you modified or added that wasn't in the original? A list is fine. Directory dump is fine.

---

## Part 2: What's missing

- What do you reach for that isn't there?
- What workaround did you build that should be a core feature?

---

## Part 3: What you changed (the part we read first)

- What modifications did you make to the baseline templates or methodology?
- What drove each change? (The use case, not just the mechanism.)
- Is there anything you invented that now feels load-bearing?

---

## Part 4: Unexpected territory

- Has loci started doing something you didn't plan for?
- What does your palace's rhythm look like in practice? Daily ritual, reactive capture, weekly review?
- Which crystal tier (◇/◈/◆) do you spend the most time in, and have you bent it to a different purpose?

---

## Part 5: You and the AI

- What do you run the palace with (Claude Code, Goose, local models, something else), and has that changed since you set up?
- Does your assistant carry identity across sessions (a name, a voice, working habits it remembers), or does every session start cold?
- Where do you not trust it? What does it get wrong about your palace often enough that you've built a habit around correcting it?

---

## Part 6: Privacy and data

- What's your threat model for your palace? Who specifically shouldn't be able to read it?
- What did you decide to keep out for privacy reasons?
- Have you modified anything because you didn't trust a particular data flow (sync, MCP, cloud AI)?

---

## Part 7: The pitch

- Two sentences: how do you explain what you built to a skeptical friend?
- When did loci stop feeling like a tool and start feeling like a place? (If it hasn't, that's an answer too.)
- What would need to exist before you'd recommend it to someone?

---

**Sending it back:** reply in the thread, or write to themapisnory@tuta.io if any
part shouldn't sit in a channel. Structure over content throughout: directory
shapes, question patterns, workflow descriptions. Nothing from inside your palace
needs to leave it.

We shipped the baseline. You grew the divergence. The divergence is the roadmap.
