"""
LaTeX compilation wrapper.
Compiles LaTeX resume to PDF using pdflatex or tectonic.
"""
import os
import shutil
import subprocess
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Where we preserve the .tex/.log of any failed compile for debugging,
# since the working temp directory gets deleted right after.
FAILED_DEBUG_DIR = os.path.join("backend", "resume", "templates", "failed")


def _run_latex_command(args, cwd, timeout=90):
    """Run a LaTeX compiler command and kill it cleanly on timeout."""
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=creationflags,
    )

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
            proc.communicate(timeout=10)
        except Exception:
            pass
        raise


def _cleanup_temp_dir(temp_dir: str) -> None:
    """Remove temp artifacts safely."""
    try:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.warning(f"Failed to clean temp directory {temp_dir}: {e}")


def _preserve_failed_artifacts(temp_dir: str, output_filename: str) -> None:
    """
    Copy the .tex source and .log file out of the temp directory into a
    permanent debug folder before it gets wiped, so a failed compile leaves
    something behind to actually inspect.
    """
    try:
        os.makedirs(FAILED_DEBUG_DIR, exist_ok=True)
        for ext in (".tex", ".log"):
            src = os.path.join(temp_dir, f"{output_filename}{ext}")
            if os.path.exists(src):
                dst = os.path.join(FAILED_DEBUG_DIR, f"{output_filename}{ext}")
                shutil.copy(src, dst)
                logger.info(f"Preserved failed compile artifact: {dst}")
    except Exception as e:
        logger.warning(f"Failed to preserve debug artifacts: {e}")


def _log_pdflatex_failure(stdout: str, stderr: str, temp_dir: str, output_filename: str) -> None:
    """
    Surface the actual reason pdflatex failed. pdflatex's most useful error
    detail usually lands in its .log file (in the output directory) rather
    than in stdout/stderr, so check both.
    """
    log_path = os.path.join(temp_dir, f"{output_filename}.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            tail = "".join(lines[-40:])
            logger.error("pdflatex .log tail (last 40 lines):\n%s", tail)
        except Exception as e:
            logger.warning(f"Could not read pdflatex log file: {e}")

    if stdout:
        logger.error("pdflatex stdout (last 2000 chars):\n%s", stdout[-2000:])
    if stderr:
        logger.error("pdflatex stderr (last 2000 chars):\n%s", stderr[-2000:])


def compile_latex_to_pdf(
    latex_content: str,
    output_filename: str,
    output_dir: str = "backend/resume/templates",
) -> Optional[str]:
    """
    Compile LaTeX content to PDF.
    Tries pdflatex first, falls back to tectonic if not available.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{output_filename}.pdf")
    temp_dir = tempfile.mkdtemp(prefix=f"{output_filename}_", dir=None)

    try:
        tex_file = os.path.join(temp_dir, f"{output_filename}.tex")

        try:
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)
        except Exception as e:
            logger.error(f"Failed to write LaTeX file: {e}")
            return None

        try:
            result_code, stdout, stderr = _run_latex_command(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
                temp_dir,
                timeout=90,
            )
            pdf_temp = os.path.join(temp_dir, f"{output_filename}.pdf")

            # pdflatex's exit code is unreliable: packages like rerunfilecheck
            # (pulled in by hyperref) return rc=1 just to say "run me again for
            # correct outlines/refs" even when the PDF compiled successfully.
            # So we check for the actual PDF file rather than trusting rc alone.
            if result_code != 0 and not os.path.exists(pdf_temp):
                logger.warning(f"pdflatex failed (rc={result_code}), no PDF produced")
                _log_pdflatex_failure(stdout, stderr, temp_dir, output_filename)
                _preserve_failed_artifacts(temp_dir, output_filename)
                logger.warning("Trying tectonic as fallback")
                return _compile_with_tectonic(latex_content, output_filename, output_dir, temp_dir, tex_file)
            elif result_code != 0:
                logger.info(
                    f"pdflatex returned rc={result_code} but a PDF was produced "
                    "(likely a harmless rerun/outline warning) — continuing."
                )

            # Second pass (common for LaTeX to resolve references/counters,
            # and required to clear the rerunfilecheck warning above).
            result_code2, stdout2, stderr2 = _run_latex_command(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
                temp_dir,
                timeout=90,
            )
            if result_code2 != 0 and not os.path.exists(pdf_temp):
                logger.warning(f"pdflatex second pass failed (rc={result_code2}), no PDF exists")
                _log_pdflatex_failure(stdout2, stderr2, temp_dir, output_filename)

            if os.path.exists(pdf_temp):
                shutil.copy(pdf_temp, output_path)
                logger.info(f"✓ PDF compiled with pdflatex: {output_path}")
                return output_path
            else:
                # No PDF from either pass — preserve artifacts before giving up.
                _preserve_failed_artifacts(temp_dir, output_filename)
                logger.error("pdflatex did not produce a PDF on either pass")
                return None

        except FileNotFoundError:
            logger.warning("pdflatex not found, trying tectonic")
            return _compile_with_tectonic(latex_content, output_filename, output_dir, temp_dir, tex_file)
        except subprocess.TimeoutExpired:
            logger.error("pdflatex timed out")
            _preserve_failed_artifacts(temp_dir, output_filename)
            return None
        except Exception as e:
            logger.error(f"pdflatex error: {e}")
            _preserve_failed_artifacts(temp_dir, output_filename)
            return None

    finally:
        _cleanup_temp_dir(temp_dir)

    return None


def _compile_with_tectonic(
    latex_content: str,
    output_filename: str,
    output_dir: str,
    temp_dir: str,
    tex_file: str,
) -> Optional[str]:
    """Compile using tectonic as fallback."""
    try:
        result_code, stdout, stderr = _run_latex_command(
            ["tectonic", tex_file],
            temp_dir,
            timeout=90,
        )
        if result_code != 0:
            logger.error(f"tectonic failed: {stderr}")
            _preserve_failed_artifacts(temp_dir, output_filename)
            return None

        pdf_temp = os.path.join(temp_dir, f"{output_filename}.pdf")
        if os.path.exists(pdf_temp):
            output_path = os.path.join(output_dir, f"{output_filename}.pdf")
            shutil.copy(pdf_temp, output_path)
            logger.info(f"✓ PDF compiled with tectonic: {output_path}")
            return output_path

    except FileNotFoundError:
        logger.error("tectonic not found. Install with: pip install tectonic or apt-get install tectonic")
    except subprocess.TimeoutExpired:
        logger.error("tectonic timed out")
    except Exception as e:
        logger.error(f"tectonic error: {e}")

    return None


def compile_master_resume(master_resume_latex: str) -> Optional[str]:
    """Compile master resume as a sanity check."""
    return compile_latex_to_pdf(
        master_resume_latex,
        "master_resume",
        "backend/resume/templates"
    )


def compile_tailored_resume(
    tailored_resume_latex: str,
    application_id: int,
    company_name: str,
) -> Optional[str]:
    """Compile tailored resume for a specific application."""
    sanitized_company = company_name.replace(" ", "_").replace("/", "_")[:30]
    filename = f"app_{application_id}_{sanitized_company}"
    return compile_latex_to_pdf(
        tailored_resume_latex,
        filename,
        "backend/resume/templates"
    )
