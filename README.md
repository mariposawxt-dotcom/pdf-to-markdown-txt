# PDF to Markdown TXT skill

Convert an uploaded, text-based PDF into a UTF-8 `.txt` file containing Markdown. This is a Codex skill powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

## Install

Place this repository at `~/.codex/skills/pdf-to-markdown-txt` (on Windows, `%USERPROFILE%\.codex\skills\pdf-to-markdown-txt`). Then restart Codex or open a new chat so the skill is discovered.

## Use

Upload a PDF and ask Codex to use `$pdf-to-markdown-txt` to convert it. The skill returns a downloadable `<original-name>.md.txt` file. If that name already exists, a number is appended instead of overwriting it.

You do not need to install MarkItDown manually. On the first conversion, the script downloads `markitdown[pdf]` into a per-user cache. Later conversions reuse it. The first run requires internet access and permission to write to the cache. Python 3.10–3.14 is required; Codex Desktop may provide a bundled Python runtime.

The script can also be run directly:

```bash
python scripts/convert_pdf.py /path/to/input.pdf --output-dir /path/to/output
```

## Scope

This version handles PDFs with extractable text. Scanned or image-only PDFs need OCR and are not supported. Complex tables or page layouts may need manual review. Uploaded PDF contents are treated as data, never as instructions.
