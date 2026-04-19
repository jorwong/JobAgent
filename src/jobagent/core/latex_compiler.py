"""Compile LaTeX files to PDF using tectonic."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def _make_tectonic_compatible(tex_content: str) -> str:
    """Patch pdflatex-only commands for tectonic (XeTeX) compatibility."""
    tex_content = re.sub(
        r"^(\\input\{glyphtounicode\})",
        r"% \1 % pdflatex only",
        tex_content,
        flags=re.MULTILINE,
    )
    tex_content = re.sub(
        r"^(\\pdfgentounicode=1)",
        r"% \1 % pdflatex only",
        tex_content,
        flags=re.MULTILINE,
    )
    return tex_content


def compile_latex(tex_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Compile a .tex file to PDF.

    Args:
        tex_path: Path to the .tex file.
        output_dir: Directory to place the PDF. Defaults to same directory as tex_path.

    Returns:
        Path to the generated PDF.

    Raises:
        FileNotFoundError: If tectonic is not installed or tex file doesn't exist.
        RuntimeError: If compilation fails.
    """
    tex_path = Path(tex_path).resolve()
    if not tex_path.exists():
        raise FileNotFoundError(f"TeX file not found: {tex_path}")

    if not shutil.which("tectonic"):
        raise FileNotFoundError(
            "tectonic is not installed. Install with: brew install tectonic"
        )

    output_dir = Path(output_dir).resolve() if output_dir else tex_path.parent

    # Read, patch for tectonic compatibility, write to a temp file in the same dir
    original = tex_path.read_text()
    patched = _make_tectonic_compatible(original)

    # Work in a temp dir to avoid polluting the source dir with build artifacts
    with tempfile.TemporaryDirectory() as tmp:
        tmp_tex = Path(tmp) / tex_path.name
        tmp_tex.write_text(patched)

        result = subprocess.run(
            ["tectonic", str(tmp_tex)],
            capture_output=True,
            text=True,
            cwd=tmp,
        )

        if result.returncode != 0:
            raise RuntimeError(f"tectonic failed:\n{result.stderr}")

        tmp_pdf = tmp_tex.with_suffix(".pdf")
        if not tmp_pdf.exists():
            raise RuntimeError("PDF was not generated")

        output_dir.mkdir(parents=True, exist_ok=True)
        final_pdf = output_dir / tmp_pdf.name
        shutil.copy2(tmp_pdf, final_pdf)

    return final_pdf


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compile LaTeX to PDF")
    parser.add_argument("tex_file", help="Path to the .tex file")
    parser.add_argument(
        "-o", "--output-dir", help="Output directory (default: same as tex file)"
    )
    args = parser.parse_args()

    try:
        pdf = compile_latex(args.tex_file, args.output_dir)
        print(f"PDF generated: {pdf}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
