# deploy/ — what runs on the VM

Everything in this folder is either **tracked config** or **gitignored secrets**.
Check which before you touch it.

| File | Committed? | What it is |
|---|---|---|
| `docker-compose.yml` | yes | The Hermes container: pinned image, data bind mount, no published ports |
| `.env.example` | yes | Variable names only, no values |
| `.env` | **no** (gitignored) | The real values. Never leaves the machine/VM |
| `data/` | **no** | Hermes' own state (`/opt/data`): config, sessions, memory, skills it writes |

## First bring-up on the VM

Run as the non-root `hermes` user; `/srv/hermes` is owned by it.

```bash
# 1. Layout. Never root-owned: the container runs as $HERMES_UID.
sudo install -d -o hermes -g hermes -m 750 /srv/hermes
cd /srv/hermes

# 2. Config from the repo (or `git clone` it here).
#    docker-compose.yml comes from this folder; .env is created here, not copied
#    if it already holds values.
cp docker-compose.yml /srv/hermes/
cp .env.example /srv/hermes/.env          # only if .env doesn't exist yet
chmod 600 /srv/hermes/.env

# 3. Fill in the blanks. Values are typed here and nowhere else.
#    HERMES_UID / HERMES_GID must match the `hermes` user:  id -u hermes; id -g hermes
$EDITOR /srv/hermes/.env

# 4. Up. First run pulls the pinned image.
docker compose up -d
docker compose logs -f --tail=50
```

Then check it's alive: message the bot from Telegram and expect a reply. A
container that is `Up` but silent usually means a bad `TELEGRAM_BOT_TOKEN`, or
your numeric id missing from `TELEGRAM_ALLOWED_USERS`.

## Day-to-day

```bash
docker compose ps
docker compose logs -f --tail=100        # follow
docker compose exec hermes hermes --version
docker compose exec hermes hermes setup  # provider/model/Telegram, if needed
docker compose restart
```

### Secrets: the profile `.env` is the only source (multiplexing)

`multiplex_profiles` is on. Under multiplexing, **every** credential — platform
tokens, allowlists, and provider API keys — is resolved from the profile's own
`.env`, i.e. `/opt/data/.env` in the container, `/srv/hermes/data/.env` on the
host. It deliberately does **not** fall back to the container's process
environment (upstream #64674, and #72348 for allowlists), so one profile can
never borrow another's credential.

Consequence: a value that exists **only** in `/srv/hermes/.env` (the
`env_file` for the container) is invisible to the gateway — even though
`docker compose exec hermes env` prints it happily. `docker compose exec` reads
the real process env; the platform layer does not.

This bites three separate ways, and the failure messages do not mention
multiplexing:

| Missing from `data/.env` | Symptom |
|---|---|
| `TELEGRAM_BOT_TOKEN` | log: `telegram is enabled but no profile ... provided a bot credential` → platform **not served**, messages silently ignored |
| `TELEGRAM_ALLOWED_USERS` | log: `Blocked unauthorized user <id>` → user is dropped **silently**, no error to sender |
| `DEEPSEEK_API_KEY` *(model provider)* | reply: `⚠️ I couldn't connect to the AI model service` → agent falls back to Nous and prompts `/login` |

**Keep these keys in both files**:

| File | Purpose |
|---|---|
| `/srv/hermes/.env` | `env_file` for the container; tooling, `docker compose` |
| `/srv/hermes/data/.env` | profile secret store — **this is what the gateway reads** |

`data/.env` ships with its keys **commented out**. Uncommenting a line without
adding a value is worse than leaving it commented: it registers an **empty
string**, which shadows the real value and produces the same failure. Either
set a real value or leave the line commented. When editing, check the **value
length**, not just that the key is present.

Provider keys are not all templated — `DEEPSEEK_API_KEY` has no placeholder
line at all, so it must be appended.

Ownership matters: `data/.env` must stay `hermes:hermes 600`. Editing it with a
root-owned editor leaves an artifact the agent cannot rewrite, and a skill file
written that way appears as a `root:root` directory (a failed curator patch
looks exactly like a stray backup directory).

Verify — check each layer separately, because they fail independently:

```bash
# 1. Platform connected?
docker compose exec hermes sh -c "grep -o 'telegram[^}]*}' /opt/data/gateway_state.json"

# 2. Which keys can the profile scope actually see?
docker compose exec hermes bash -lc '
  cd /opt/hermes
  PY=$(ls -d /opt/data/installs/*/environments/*/venv/bin/python | head -1)
  "$PY" - <<"PY"
from gateway.platforms._shared import platform_gate_env
for k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_USERS", "DEEPSEEK_API_KEY"):
    v = platform_gate_env(k)
    print(f"{k}: len={len(v)} " + (v[:6] + "..." if v else "EMPTY/MISSING"))
PY'
```

Expect a non-trivial `len` for each. A provider key can be present and still be
rejected, so confirm it with a real call rather than trusting the variable:

```bash
docker compose exec hermes bash -lc '
  cd /opt/hermes
  PY=$(ls -d /opt/data/installs/*/environments/*/venv/bin/python | head -1)
  "$PY" - <<"PY"
import json, urllib.request
from gateway.platforms._shared import platform_gate_env
k = platform_gate_env("DEEPSEEK_API_KEY")
req = urllib.request.Request("https://api.deepseek.com/chat/completions",
    data=json.dumps({"model": "deepseek-chat",
                     "messages": [{"role": "user", "content": "say PONG"}],
                     "max_tokens": 8}).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + k})
with urllib.request.urlopen(req, timeout=45) as r:
    print("OK:", json.loads(r.read())["choices"][0]["message"]["content"].strip())
PY'
```

Use an interpreter that can import the gateway (`ruamel.yaml` must resolve).
`/opt/hermes/.venv/bin/python` does **not** — that venv serves the STT extra,
not the agent runtime.

After fixing anything here, `docker compose restart` (safe; does not destroy
the STT install).


## Updating Hermes

Deliberate, two-step, with a rollback that's one line:

1. Read the release notes.
2. Edit `HERMES_IMAGE` in `.env` to the new tag, then `docker compose pull && docker compose up -d`.
3. To roll back: put the old tag back and repeat step 2. The data directory is untouched by image changes.

## Local speech-to-text (voice notes)

Telegram voice notes are transcribed on the VM by `faster-whisper`. No API key,
no third party, audio never leaves the machine.

The Docker image does **not** ship `faster-whisper` (it is an opt-in extra), and
`hermes tools post-setup faster_whisper` **does not work on this image**: it
installs the package into a separate environment under
`/opt/data/installs/.../venv`, while the launcher runs `/opt/hermes/.venv`. The
hook reports success, but `import faster_whisper` still fails. Install it by
copying the package closure into the gateway venv:

```bash
docker compose exec hermes bash -lc '
  set -e
  SRC="$(ls -d /opt/data/installs/*/environments/*/venv/lib/python3.14/site-packages | head -1)"
  DST=/opt/hermes/.venv/lib/python3.14/site-packages
  for p in faster_whisper ctranslate2 ctranslate2.libs onnxruntime flatbuffers \
           av av.libs huggingface_hub hf_xet tokenizers numpy numpy.libs \
           filelock fsspec tqdm yaml; do
    [ -e "$SRC/$p" ] && [ ! -e "$DST/$p" ] && cp -a "$SRC/$p" "$DST/" || true
  done
  for d in "$SRC"/{faster_whisper,ctranslate2,onnxruntime,av,huggingface_hub}-*.dist-info; do
    [ -e "$d" ] && [ ! -e "$DST/$(basename "$d")" ] && cp -a "$d" "$DST/" || true
  done
  /opt/hermes/.venv/bin/python -c "import faster_whisper; print(faster_whisper.__version__)"
'
```

Then restart and verify Hermes itself agrees:

```bash
docker compose restart
# Generate 3s of test audio, then transcribe it through Hermes' own entry point.
docker compose exec hermes bash -lc '
  ffmpeg -nostdin -y -f lavfi -i "sine=frequency=440:duration=3" \
    -ar 16000 -ac 1 /tmp/stt_test.wav 2>/dev/null
  /opt/hermes/.venv/bin/python -c "
import sys; sys.path.insert(0, \"/opt/hermes\")
from tools.transcription_tools import transcribe_audio
print(transcribe_audio(\"/tmp/stt_test.wav\"))"
'
```

Expect `{'success': True, 'transcript': '', 'provider': 'local'}`. An empty
transcript is correct here — a sine tone is not speech and the VAD filter drops
it. What the check proves is that Hermes **routed to `local`** and the model
loaded. Pass a real voice recording to see actual words.

**This is lost on every container recreate** — `docker compose pull`, but also a
plain `docker compose down && docker compose up -d`, and even
`docker compose up -d --force-recreate`. `/opt/hermes` is baked into the image
and replaced whenever the container is recreated, taking the copied packages
with it. `docker compose restart` is safe; anything that recreates the container
is not.

Re-run the install block afterwards, or use the checked-in helper, which is
idempotent and re-links only what is missing:

```bash
scp deploy/relink_stt.sh root@<vm>:/srv/hermes/data/relink_stt.sh
docker compose exec hermes sh /opt/data/relink_stt.sh
```

The model cache is kept on the persistent volume via `HF_HOME=/opt/data/cache/huggingface`
(set in `docker-compose.yml`), so a recreate does not re-download the model.
Without that variable `faster-whisper` falls back to `~/.cache/huggingface`
*inside* the container, which is discarded on recreate.

Config (`/srv/hermes/data/config.yaml`):

| Key | Value | Notes |
|---|---|---|
| `stt.enabled` | `true` | Off by default |
| `stt.provider` | *(omitted)* | Auto-detects `local` once importable |
| `stt.local.model` | `base` | ~150 MB, ~390 MB RAM. `small` is more accurate, ~2× RAM |
| `stt.language` | `en` | Force, or `""` to auto-detect |

Memory: `base` peaks around 390 MB RSS, which fits the 4 GB VM. `small` is a
reasonable upgrade; `medium`/`large-v3` are not for this box. The VM has **no
swap**, so a large model can OOM the gateway.

## The spine (subjects)

Markdown only, nothing derived, no `triage.py` involvement. Laying it down is
additive and safe: if it goes wrong, delete `/srv/hermes/data/spine` and nothing
else is affected.

### Install

The repo is the source of truth for our skills; the VM should not hold a copy
that can drift. Register `skills/` as an **external skill directory** once:

```yaml
# /srv/hermes/data/config.yaml  (in the container: /opt/data/config.yaml)
skills:
  external_dirs:
    - /opt/data/repo/skills      # wherever the checkout is mounted, see below
```

The checkout has to be inside the data volume or readable from the container —
`/srv/hermes/data/repo` is the simple choice, and it is covered by the backup.
Paths support `${VAR}` substitution, so `- ${SKILLS_REPO}/skills` also works.

```bash
# On the VM, from the repo checkout.
git clone <repo> /srv/hermes/data/repo     # or rsync the checkout there
chown -R hermes:hermes /srv/hermes/data/repo

# The spine tree: an empty skeleton plus the rules. No data is copied in.
install -d -o hermes -g hermes -m 750 /srv/hermes/data/spine/subjects
install -d -o hermes -g hermes -m 750 /srv/hermes/data/spine/lists
cp spine/README.md /srv/hermes/data/spine/README.md
chown hermes:hermes /srv/hermes/data/spine/README.md

docker compose restart      # safe: reloads skills, does not recreate
```

External dirs are rescanned on restart, so a `git pull` plus a restart is the
whole update path for skills. Notes from the upstream docs that matter here:

- **Precedence** is `project → ~/.hermes/skills (here: /opt/data/skills) → skills.create_dir → external_dirs`. A stale copy of `subjects` in `/opt/data/skills/` would **shadow** the repo version and be logged as shadowed. If a change does not take effect, look for a duplicate there first.
- **External dirs are not read-only.** If `/opt/data/repo` is writable by the
  container user, the agent's `skill_manage` can edit files in the checkout. That
  is acceptable here (it is a git checkout, so `git diff` shows any change), but
  do not sync it back blindly.


### Verify

```bash
# The skill is discovered from the external dir, not a copy.
docker compose exec hermes hermes skills list | grep subjects
docker compose exec hermes ls /opt/data/repo/skills/subjects/

# The validator runs, and finds nothing yet.
docker compose exec hermes /opt/hermes/.venv/bin/python \
  /opt/data/repo/skills/subjects/validate.py
# expect: exit 2, "no subjects in /opt/data/spine/subjects"
```

Then the real test, from Telegram:

1. "Create a subject for the house" — expect a proposed name, then a folder.
2. "Add: get the geyser checked, due next Friday"
3. "What's due?"
4. On the VM: `find /srv/hermes/data/spine -type f` shows `SUBJECT.md` and
   `timeline.md`, and the validator now exits 0.

Failure to check first: a container that runs but the bot says it cannot write.
That is almost always ownership — the files must be owned by `hermes`, because
the container runs as `$HERMES_UID`.

```bash
ls -la /srv/hermes/data/spine/subjects/
# anything root-owned is the bug:
sudo chown -R "$(id -u hermes):$(id -g hermes)" /srv/hermes/data/spine
```

### Rollback

```bash
rm -rf /srv/hermes/data/spine                  # take a copy of this first
$EDITOR /srv/hermes/data/config.yaml           # delete the skills.external_dirs entries
docker compose restart
```

Remove the `external_dirs` lines by hand rather than with `sed`: the `skills:`
block may hold other settings (`create_dir`, skill config) that a range delete
would take with it.

Nothing else changes. `triage.py` and the labels are untouched by this deploy.

## Backup

`/srv/hermes/data` is the only thing worth backing up, and **it contains API
keys plus the bot's memory**, so encrypt the backup.

```bash
docker compose stop hermes
sudo tar -C /srv/hermes -czf /var/backups/hermes-$(date +%F).tgz data
docker compose start hermes
```

Restoring is the reverse, before `docker compose up -d`.

## Security notes

- **No `ports:` in the compose file, deliberately.** The Telegram gateway polls
  outward, so the bot accepts no inbound connections. Reach the VM over NetBird.
- `.env` is mode `600` and gitignored. If a key ever lands in git, rotate it;
  removing the commit is not enough.
- Never run this as root, and never mount the Docker socket into it.
