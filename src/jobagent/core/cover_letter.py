"""Compile a cover letter text file into a PDF."""

from __future__ import annotations

from pathlib import Path


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters in plain text."""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text


def text_to_pdf(
    cover_text: str,
    output_dir: Path,
    name: str = "Wong See Siang, Jordan",
    contact: str = "(+65) 9048 1857 | jorwong5@gmail.com | linkedin.com/in/jorwong",
) -> Path:
    """Compile cover letter text into a PDF using a LaTeX template.

    Args:
        cover_text: Plain text body of the cover letter.
        output_dir: Directory to save the PDF.
        name: Name for the header.
        contact: Contact line for the header.

    Returns:
        Path to the generated PDF.
    """
    from jobagent.core.latex_compiler import compile_latex

    template_path = Path(__file__).parent / "cover_letter_template.tex"
    template = template_path.read_text()

    # Split paragraphs and wrap in LaTeX
    paragraphs = [p.strip() for p in cover_text.strip().split("\n\n") if p.strip()]
    body_latex = "\n\n".join(_escape_latex(p) for p in paragraphs)

    latex = template.replace("HEADING_NAME", name)
    latex = latex.replace("HEADING_CONTACT", contact)
    latex = latex.replace("BODY_CONTENT", body_latex)

    tex_path = output_dir / "cover_letter.tex"
    tex_path.write_text(latex)

    pdf_path = compile_latex(tex_path, output_dir)
    return pdf_path


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compile a cover letter text file to PDF"
    )
    parser.add_argument(
        "cover_letter_txt",
        help="Path to cover_letter.txt",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: same as input file)",
    )
    args = parser.parse_args()

    txt_path = Path(args.cover_letter_txt).resolve()
    if not txt_path.exists():
        print(f"Error: {txt_path} not found")
        raise SystemExit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else txt_path.parent
    cover_text = txt_path.read_text()

    try:
        pdf = text_to_pdf(cover_text, output_dir)
        print(f"PDF generated: {pdf}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
