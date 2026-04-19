"""Set up application directory, copy master resume for tailoring, and compile PDF."""

from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path


def setup_application(
    master_resume_path: str | Path,
    job_description: str,
    company: str,
    role: str,
    output_base: str | Path = "applied",
) -> Path:
    """Set up an application directory with master resume copy and JD.

    Args:
        master_resume_path: Path to the master resume .tex file.
        job_description: The job description text.
        company: Company name (used for directory).
        role: Role name (used for directory).
        output_base: Base directory for applied jobs.

    Returns:
        Path to the output directory.
    """
    master_resume_path = Path(master_resume_path).resolve()

    company_dir = re.sub(r"[^\w\-]", "-", company.lower()).strip("-")
    role_dir = re.sub(r"[^\w\-]", "-", role.lower()).strip("-")

    output_dir = Path(output_base).resolve() / company_dir / role_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy master resume as starting point
    tex_path = output_dir / "resume.tex"
    shutil.copy2(master_resume_path, tex_path)
    print(f"Copied resume to: {tex_path}")

    # Save JD
    jd_path = output_dir / "jd.txt"
    jd_path.write_text(
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Date: {date.today().isoformat()}\n\n"
        f"{job_description}"
    )
    print(f"Saved JD: {jd_path}")

    return output_dir


def compile_application(output_dir: str | Path) -> None:
    """Compile resume and cover letter (if present) to PDF.

    Args:
        output_dir: The application directory.
    """
    from jobagent.core.latex_compiler import compile_latex

    output_dir = Path(output_dir).resolve()

    # Compile resume
    resume_tex = output_dir / "resume.tex"
    if resume_tex.exists():
        pdf = compile_latex(resume_tex, output_dir)
        print(f"Resume PDF: {pdf}")

    # Compile cover letter if text exists
    cover_txt = output_dir / "cover_letter.txt"
    if cover_txt.exists():
        from jobagent.core.cover_letter import text_to_pdf

        cover_text = cover_txt.read_text()
        pdf = text_to_pdf(cover_text, output_dir)
        print(f"Cover letter PDF: {pdf}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Set up and compile a job application"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup command
    setup = subparsers.add_parser(
        "setup", help="Set up application directory with resume copy and JD"
    )
    setup.add_argument(
        "--resume",
        default="master-resume.tex",
        help="Path to master resume .tex file (default: master-resume.tex)",
    )
    setup.add_argument("--company", required=True, help="Company name")
    setup.add_argument("--role", required=True, help="Role title")
    setup.add_argument(
        "--jd",
        help="Path to JD file (reads from stdin if omitted)",
    )
    setup.add_argument(
        "--output-dir",
        default="applied",
        help="Base output directory (default: applied/)",
    )

    # compile command
    compile_cmd = subparsers.add_parser(
        "compile", help="Compile resume.tex and cover_letter.txt to PDF"
    )
    compile_cmd.add_argument(
        "app_dir", help="Path to the application directory"
    )

    args = parser.parse_args()

    if args.command == "setup":
        if args.jd:
            jd = Path(args.jd).read_text()
        else:
            import sys

            print("Paste the job description (Ctrl+D when done):")
            jd = sys.stdin.read()

        if not jd.strip():
            print("Error: empty job description")
            raise SystemExit(1)

        output_dir = setup_application(
            master_resume_path=args.resume,
            job_description=jd,
            company=args.company,
            role=args.role,
            output_base=args.output_dir,
        )
        print(f"\nReady! Edit {output_dir}/resume.tex then run:")
        print(f"  python3 -m jobagent.core.resume_tailor compile {output_dir}")

    elif args.command == "compile":
        try:
            compile_application(args.app_dir)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Error: {e}")
            raise SystemExit(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
