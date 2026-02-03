#!/usr/bin/env python3

# ESTANDAR
import subprocess
import os
import sys
from pathlib import Path

# Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def compile_latex_to_pdf(tex_file_path):
    """Compile the given LaTeX file to PDF using pdflatex."""
    tex_file = Path(tex_file_path)
    output_dir = tex_file.parent

    if not tex_file.exists():
        print(f"Error: The file {tex_file_path} does not exist")
        return False

    try:
        # Change to output directory
        original_dir = os.getcwd()
        os.chdir(output_dir)

        # Compile LaTeX to PDF
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
            capture_output=True,
            text=True,
            timeout=60,
        )

        os.chdir(original_dir)

        if result.returncode == 0:
            pdf_name = tex_file.stem + ".pdf"
            print(f"PDF generated successfully: {output_dir / pdf_name}")
            return True
        else:
            print(f"Error compiling {tex_file.name}:")
            print(result.stdout)
            return False

    except FileNotFoundError:
        print("Error: pdflatex is not installed. Please install MiKTeX or TeX Live")
        return False
    except subprocess.TimeoutExpired:
        print(f"Error: Compilation of {tex_file.name} took too long")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Compile all LaTeX files in the project"""
    reports_dir = Path(__file__).parent / "src" / "reports" / "output"

    tex_files = list(reports_dir.glob("report_*.tex"))

    if not tex_files:
        print("No report_*.tex files found")
        return

    print(f"Found {len(tex_files)} LaTeX files to compile:")
    for tex_file in tex_files:
        print(f"  - {tex_file.name}")

    print("\nCompiling files...")
    results = []
    for tex_file in tex_files:
        success = compile_latex_to_pdf(tex_file)
        results.append((tex_file.name, success))

    print("\n" + "=" * 60)
    print("COMPILATION SUMMARY:")
    print("=" * 60)
    for name, success in results:
        status = "Successful" if success else "Failed"
        print(f"{name}: {status}")


if __name__ == "__main__":
    main()
