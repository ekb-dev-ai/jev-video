# Jev requests

The request files from the Jev video, and a small client to send them. Jev is TypeSafe's System One model: it reads some text, answers from a list you wrote, and says how sure it is.

## Files

| Request | File |
| --- | --- |
| The desk note | `demos/01-desk-note.json` |
| The telescope card | `demos/06-telescope-ready.json` |
| The dome motor and the bench | `demos/07-dome-note.json` |
| Cocoa, then the planted line | `demos/02a-cocoa-clean.json`, then `demos/02b-cocoa-planted.json` |
| The failing picture test | `demos/03-bug-triage.json` |
| The agent trace | `demos/04-agent-guardrail.json` |
| The claim beside the log | `demos/05-claim-versus-log.json` |

Each file is the body of `POST https://api.typesafe.ai/v1/systemone`: a `model`, a `state` (the text), and `questions`.

## Try it

No key: paste any file from `demos/` into the [TypeSafe playground](https://console.typesafe.ai/playground).

With a key:

```bash
cp .env.example .env     # paste your key after TYPESAFE_API_KEY=  (git ignores .env)
python3 try_jev.py                              # the desk note
python3 try_jev.py demos/05-claim-versus-log.json
python3 try_jev.py demos/05-claim-versus-log.json --raw   # also print the full reply
```

Python 3, no packages. Numbers can move from run to run and between model versions. Believe your own pile of examples over any single run.
