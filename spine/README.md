# spine

One folder per subject. Each subject is a Markdown file and a log; tasks live
inside the subject they belong to.

See `docs/TASK-SPINE.md` for why it is shaped this way.

## Layout

```
spine/
  subjects/<id>/SUBJECT.md      frontmatter + prose + tasks
  subjects/<id>/timeline.md     append-only, one dated line per event
  subjects/<id>/docs/           dropped-in PDFs, scans, OCR text
  subjects/<id>/mail/           linked emails, by message-id
  lists/<name>.md               named lists: pharmacy, hardware, movies
```

`spine/_index.db` does not exist yet. When it does, it is derived: deleting it
must always be safe, and `spine reindex` rebuilds it from the tree.

## Rules for whatever writes here

- **Never delete a subject folder.** Retire it with `status: dormant` or `done`.
- **Never rewrite `timeline.md`.** Append one line, newest at the bottom.
- **Never write to `_index.db` first.** The files are the truth.
- Files here are the user's. They are plain text so the user can fix them by hand.

To create a subject, use the `subjects` skill, not hand-editing.
