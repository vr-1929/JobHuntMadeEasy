"""
Job App OS - Streamlit frontend.

Three pages:
  - New Application: paste a job description, run the full AI pipeline
    (keyword extraction -> gap analysis -> resume tailoring -> cover letter),
    and save it for review. (Automated job search - Phase 2 - isn't built
    yet, so this is the manual entry point for now.)
  - Review Queue: see tailored resume + cover letter per application,
    approve or skip before actually applying.
  - Dashboard: track status across all applications.
"""
import os
import sys

# Streamlit runs this file as `frontend/app.py`, which puts only the
# `frontend/` folder on sys.path — not the project root where `backend/`
# lives. Add the root explicitly so `from backend...` imports resolve
# regardless of the working directory Streamlit was launched from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import datetime

from backend.db import init_db, get_session
from backend.models import MasterProfile, Application
from backend.crud import (
    get_master_profile,
    get_applications_pending_review,
    get_all_applications,
    update_application_status,
)
from backend.ai.keyword_extraction import extract_keywords
from backend.ai.gap_analysis import analyze_gaps
from backend.ai.resume_tailoring import tailor_resume
from backend.ai.cover_letter import generate_cover_letter
from backend.resume.compile import compile_tailored_resume

st.set_page_config(page_title="Job App OS", page_icon="\U0001F4BC", layout="wide")

# Make sure tables exist (safe to call repeatedly).
init_db()


def _compute_match_score(gap_analysis: dict) -> float:
    """Simple match score: % of required keywords matched or truthfully reworded."""
    matched = len(gap_analysis.get("matched", []))
    reword = len(gap_analysis.get("missing_reword", []))
    flagged = len(gap_analysis.get("missing_flagged", []))
    total = matched + reword + flagged
    if total == 0:
        return 0.0
    return round((matched + reword) / total * 100, 1)


def _keyword_names(items: list) -> list:
    """Gap analysis returns list of dicts; pull just the keyword names for storage."""
    return [item.get("keyword", str(item)) if isinstance(item, dict) else str(item) for item in items]


# ---------------------------------------------------------------------------
# Page: New Application
# ---------------------------------------------------------------------------
def page_new_application():
    st.title("New Application")
    st.caption(
        "Automated job search (Phase 2) isn't built yet, so paste a job "
        "description below to run it through the tailoring pipeline manually."
    )

    db = get_session()
    profile = get_master_profile(db)
    if not profile:
        st.error(
            "No master resume found in the database. Run `python test_pipeline.py` "
            "once first to seed your master resume, then reload this page."
        )
        db.close()
        return

    with st.form("new_application_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company name*")
            role_title = st.text_input("Role title*")
            job_url = st.text_input("Job posting URL", placeholder="https://...")
        with col2:
            source = st.selectbox(
                "Source", ["manual", "adzuna", "usajobs", "remotive", "greenhouse", "lever"]
            )
            location_type = st.selectbox("Location type", ["remote", "onsite", "hybrid"])
            location_text = st.text_input("Location", placeholder="e.g. Remote (US), New York, NY")

        job_description = st.text_area("Job description*", height=300)

        submitted = st.form_submit_button("Generate Tailored Application", type="primary")

    if submitted:
        if not company_name or not role_title or not job_description:
            st.error("Company name, role title, and job description are required.")
            db.close()
            return

        try:
            with st.status("Running tailoring pipeline...", expanded=True) as status:
                status.write("Extracting keywords from job description...")
                keywords = extract_keywords(job_description, role_title, company_name)
                status.write(f"\u2713 Extracted {len(keywords)} keywords")

                status.write("Running gap analysis against your master resume...")
                gap_analysis = analyze_gaps(keywords, profile.resume_latex, job_description)
                status.write(
                    f"\u2713 {len(gap_analysis.get('matched', []))} matched, "
                    f"{len(gap_analysis.get('missing_reword', []))} to reword, "
                    f"{len(gap_analysis.get('missing_flagged', []))} flagged"
                )

                status.write("Tailoring resume (this can take 10-20s)...")
                tailored_latex = tailor_resume(
                    profile.resume_latex, job_description, gap_analysis, role_title, company_name
                )
                status.write(f"\u2713 Resume tailored ({len(tailored_latex)} chars)")

                status.write("Generating cover letter...")
                cover_letter = generate_cover_letter(
                    company_name, role_title, job_description, profile.resume_latex
                )
                status.write("\u2713 Cover letter generated")

                # Save first (without PDF path) so nothing is lost if compile fails.
                new_app = Application(
                    master_profile_id=profile.id,
                    company_name=company_name,
                    role_title=role_title,
                    job_url=job_url or "manual-entry",
                    job_description_raw=job_description,
                    source=source,
                    location_type=location_type,
                    location_text=location_text,
                    status="reviewed",
                    match_score=_compute_match_score(gap_analysis),
                    keywords_matched=_keyword_names(gap_analysis.get("matched", [])),
                    keywords_missing_added=_keyword_names(gap_analysis.get("missing_reword", [])),
                    keywords_missing_flagged=_keyword_names(gap_analysis.get("missing_flagged", [])),
                    tailored_resume_latex=tailored_latex,
                    tailored_cover_letter=cover_letter,
                )
                db.add(new_app)
                db.commit()
                db.refresh(new_app)

                status.write("Compiling tailored resume to PDF...")
                pdf_path = compile_tailored_resume(tailored_latex, new_app.id, company_name)
                if pdf_path:
                    new_app.tailored_resume_pdf_path = pdf_path
                    db.commit()
                    status.write(f"\u2713 PDF compiled: {pdf_path}")
                else:
                    status.write(
                        "\u26a0 PDF compilation failed — you can still review the "
                        "LaTeX/text in the Review Queue and retry later."
                    )

                status.update(label="Done! Check the Review Queue tab.", state="complete")

            st.success(
                f"Application for {role_title} at {company_name} is ready for review "
                "(see the Review Queue page)."
            )
        except Exception as e:
            st.error(f"Pipeline failed: {e}")

    db.close()


# ---------------------------------------------------------------------------
# Page: Review Queue
# ---------------------------------------------------------------------------
def page_review_queue():
    st.title("Review Queue")
    st.caption("Approve or skip each tailored application before you actually apply.")

    db = get_session()
    pending = get_applications_pending_review(db)

    if not pending:
        st.info("Nothing waiting for review right now. Add one from the New Application page.")
        db.close()
        return

    for app in pending:
        with st.container(border=True):
            header_col, score_col = st.columns([4, 1])
            with header_col:
                st.subheader(f"{app.role_title} @ {app.company_name}")
                st.caption(
                    f"{app.location_type or '—'} · {app.location_text or '—'} · "
                    f"source: {app.source} · found {app.date_found:%Y-%m-%d}"
                )
            with score_col:
                st.metric("Match", f"{app.match_score:.0f}%")

            with st.expander("Job description"):
                st.text(app.job_description_raw)

            kw_col1, kw_col2, kw_col3 = st.columns(3)
            with kw_col1:
                st.markdown("**Matched**")
                st.write(", ".join(app.keywords_matched) or "—")
            with kw_col2:
                st.markdown("**Reworded (truthful)**")
                st.write(", ".join(app.keywords_missing_added) or "—")
            with kw_col3:
                st.markdown("**Flagged (not added)**")
                st.write(", ".join(app.keywords_missing_flagged) or "—")

            resume_col, letter_col = st.columns(2)
            with resume_col:
                st.markdown("**Tailored resume**")
                if app.tailored_resume_pdf_path and os.path.exists(app.tailored_resume_pdf_path):
                    with open(app.tailored_resume_pdf_path, "rb") as f:
                        st.download_button(
                            "Download tailored resume PDF",
                            f.read(),
                            file_name=os.path.basename(app.tailored_resume_pdf_path),
                            mime="application/pdf",
                            key=f"dl_{app.id}",
                        )
                else:
                    st.warning("PDF not available — showing LaTeX source instead.")
                with st.expander("View tailored LaTeX"):
                    st.code(app.tailored_resume_latex or "", language="latex")

            with letter_col:
                st.markdown("**Cover letter**")
                edited_letter = st.text_area(
                    "Edit before approving if needed",
                    value=app.tailored_cover_letter or "",
                    height=250,
                    key=f"letter_{app.id}",
                    label_visibility="collapsed",
                )

            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("Approve", key=f"approve_{app.id}", type="primary"):
                    app.tailored_cover_letter = edited_letter
                    update_application_status(db, app.id, "approved")
                    st.rerun()
            with btn_col2:
                if st.button("Skip", key=f"skip_{app.id}"):
                    update_application_status(db, app.id, "skipped")
                    st.rerun()
            with btn_col3:
                if app.job_url and app.job_url != "manual-entry":
                    st.link_button("Open job posting", app.job_url)

    db.close()


# ---------------------------------------------------------------------------
# Page: Dashboard
# ---------------------------------------------------------------------------
def page_dashboard():
    st.title("Dashboard")

    db = get_session()
    applications = get_all_applications(db, limit=500)

    if not applications:
        st.info("No applications yet.")
        db.close()
        return

    status_options = [
        "found", "reviewed", "approved", "applied",
        "interviewing", "rejected", "offer", "ghosted", "skipped",
    ]

    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    cols = st.columns(len(status_counts) or 1)
    for col, (status, count) in zip(cols, status_counts.items()):
        col.metric(status.capitalize(), count)

    st.divider()

    filter_status = st.multiselect("Filter by status", status_options, default=[])
    visible = [a for a in applications if not filter_status or a.status in filter_status]

    for app in visible:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{app.role_title}** @ {app.company_name}")
                st.caption(f"{app.source} · {app.location_text or '—'} · match {app.match_score:.0f}%")
            with col2:
                new_status = st.selectbox(
                    "Status", status_options,
                    index=status_options.index(app.status) if app.status in status_options else 0,
                    key=f"status_{app.id}",
                    label_visibility="collapsed",
                )
                if new_status != app.status:
                    update_application_status(db, app.id, new_status)
                    st.rerun()
            with col3:
                st.caption(f"Applied: {app.date_applied:%Y-%m-%d}" if app.date_applied else "Not applied")

    db.close()


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
PAGES = {
    "New Application": page_new_application,
    "Review Queue": page_review_queue,
    "Dashboard": page_dashboard,
}

st.sidebar.title("Job App OS")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
PAGES[selection]()