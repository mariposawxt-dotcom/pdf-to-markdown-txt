"""Convert a text-based PDF to a UTF-8 .txt file containing Markdown."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def output_path(source: Path, directory: Path) -> Path:
    stem = source.stem
    candidate = directory / f"{stem}.md.txt"
    number = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{number}.md.txt"
        number += 1
    return candidate


def dependency_cache() -> Path:
    override = os.environ.get("PDF_MD_CACHE_DIR")
    base = Path(override) if override else Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".cache") / "pdf-to-markdown-txt"
    return base.expanduser() / f"py{sys.version_info.major}{sys.version_info.minor}" / "packages"


def run_with_dependency(args: list[str]) -> int:
    if not (3, 10) <= sys.version_info[:2] <= (3, 14):
        print("MarkItDown requires Python 3.10–3.14.", file=sys.stderr)
        return 3
    packages = dependency_cache()
    marker = packages / ".install-complete"
    if not marker.is_file():
        packages.mkdir(parents=True, exist_ok=True)
        print("Installing MarkItDown PDF support for the first run...", file=sys.stderr)
        install = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(packages), "markitdown[pdf]"])
        if install.returncode:
            print("Automatic dependency installation failed; check network access and retry.", file=sys.stderr)
            return install.returncode
        marker.write_text("ready\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(packages) + os.pathsep + environment.get("PYTHONPATH", "")
    return subprocess.call([sys.executable, str(Path(__file__).resolve()), "--internal-run", *args], env=environment)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Input PDF file")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    parser.add_argument("--internal-run", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    source = args.pdf.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        parser.error("Input must be an existing .pdf file")
    with source.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            parser.error("Input does not have a PDF header")

    try:
        from markitdown import MarkItDown
    except ImportError:
        if args.internal_run:
            print("MarkItDown was not available after installation.", file=sys.stderr)
            return 3
        return run_with_dependency(sys.argv[1:])

    try:
        result = MarkItDown(enable_plugins=False).convert_local(str(source))
    except Exception as exc:
        print(f"PDF conversion failed: {exc}", file=sys.stderr)
        return 1

    markdown = result.markdown.strip()
    if not markdown:
        print("No extractable text found. This PDF may be scanned; OCR is not supported.", file=sys.stderr)
        return 2

    directory = args.output_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = output_path(source, directory)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(markdown + "\n")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
