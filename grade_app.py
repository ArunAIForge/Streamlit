"""Student grade tracker (Streamlit only, single file).

Run with:  streamlit run grade_app.py

Bootstrap 5 is loaded from a CDN, so the page needs internet access to get the
full styling. Without it the app still works, just with plainer styling.
"""

from html import escape

import streamlit as st

# Grading scale: (minimum mark, grade), checked from the top down.
# If your Day 2 scale is different, change only this list.
GRADE_SCALE = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

# Bootstrap contextual colour used for each grade badge / progress bar.
GRADE_COLOURS = {"A": "success", "B": "primary", "C": "info", "D": "warning", "F": "danger"}


def get_grade(mark: float) -> str:
    """Return the letter grade for a whole-number mark between 1 and 100."""
    for minimum, grade in GRADE_SCALE:
        if mark >= minimum:
            return grade
    return "F"


def remove_selected() -> None:
    """Remove the student chosen in the selectbox."""
    idx = st.session_state.get("remove_idx")
    if idx is not None and 0 <= idx < len(st.session_state.students):
        removed = st.session_state.students.pop(idx)
        st.toast(f"Removed {removed['Name']}", icon="🗑️")
    st.session_state.remove_idx = None
    st.session_state.confirm_clear = False


def clear_all() -> None:
    """Two-step clear: the first click arms it, the second click wipes the list."""
    if st.session_state.get("confirm_clear"):
        st.session_state.students = []
        st.session_state.remove_idx = None
        st.session_state.confirm_clear = False
        st.toast("All students cleared", icon="🧹")
    else:
        st.session_state.confirm_clear = True


def disarm_clear() -> None:
    """Changing the selection cancels a pending 'clear all'."""
    st.session_state.confirm_clear = False


st.set_page_config(page_title="Grade App", page_icon="📝", layout="wide")

# ---------- Styling: Bootstrap 5 (CDN) + custom CSS ----------
st.markdown(
    """
<style>
@import url("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css");

/* Keep Streamlit's own look where Bootstrap's reset would interfere */
.stApp { background: #f4f6fb; }
.block-container { padding-top: 2rem; max-width: 1200px; }
.stApp, .stApp p, .stApp label { font-family: "Segoe UI", system-ui, sans-serif; }
header[data-testid="stHeader"] { background: transparent; }

/* Hero banner */
.ga-hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: #fff; border-radius: 1rem; padding: 1.6rem 2rem; margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px rgba(79, 70, 229, .25);
}
.ga-hero h1 { font-size: 1.9rem; font-weight: 700; margin: 0; color: #fff; }
.ga-hero p { margin: .3rem 0 0; opacity: .9; color: #fff; }

/* Section cards */
.ga-section-title { font-weight: 600; font-size: 1.15rem; color: #1f2937; margin-bottom: .6rem; }
div[data-testid="stForm"] {
    background: #fff; border: 0; border-radius: 1rem; padding: 1.4rem;
    box-shadow: 0 4px 14px rgba(15, 23, 42, .08);
}
div[data-testid="stForm"] label p { color: #374151; font-weight: 500; }
div[data-testid="stFormSubmitButton"] button,
.stButton button {
    border-radius: .6rem; font-weight: 600; transition: transform .1s ease;
}
div[data-testid="stFormSubmitButton"] button {
    width: 100%; background: #4f46e5; color: #fff; border: 0; padding: .6rem 1rem;
}
div[data-testid="stFormSubmitButton"] button:hover { background: #4338ca; color: #fff; transform: translateY(-1px); }

/* Metrics as cards */
div[data-testid="stMetric"] {
    background: #fff; border-radius: 1rem; padding: 1rem 1.2rem;
    border-left: 5px solid #4f46e5; box-shadow: 0 4px 14px rgba(15, 23, 42, .08);
}
div[data-testid="stMetricLabel"] p { color: #6b7280; font-weight: 600; }
div[data-testid="stMetricValue"] { color: #111827; }

/* Student table */
.ga-card { background: #fff; border-radius: 1rem; padding: 1rem 1.2rem;
           box-shadow: 0 4px 14px rgba(15, 23, 42, .08); }
.ga-table { margin-bottom: 0; color: #1f2937; }
.ga-table th { font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; color: #6b7280; }
.ga-table .progress { height: .5rem; min-width: 90px; }
.ga-badge { font-size: .95rem; padding: .45em .8em; border-radius: .6rem; }
.ga-empty { text-align: center; color: #6b7280; padding: 2.2rem 1rem; }
.ga-empty .ga-emoji { font-size: 2.4rem; }

/* ---------- Remove section: interactive colours ---------- */
.st-key-remove_zone {
    background: #fff; border-radius: 1rem; padding: 1.1rem 1.3rem; margin-top: 1rem;
    border: 2px solid #e5e7eb; box-shadow: 0 4px 14px rgba(15, 23, 42, .06);
    transition: border-color .25s ease, box-shadow .25s ease, background .25s ease;
}
.st-key-remove_zone:hover { border-color: #fca5a5; }
.ga-zone-title { font-weight: 600; color: #b91c1c; margin-bottom: .6rem; }

/* Remove button: soft red -> solid red on hover -> darker on press */
.st-key-remove_btn button {
    background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca;
    transition: background .2s ease, color .2s ease, transform .1s ease, box-shadow .2s ease;
}
.st-key-remove_btn button:hover:not(:disabled) {
    background: #ef4444; color: #fff; border-color: #ef4444;
    box-shadow: 0 6px 16px rgba(239, 68, 68, .35); transform: translateY(-1px);
}
.st-key-remove_btn button:active:not(:disabled) { background: #b91c1c; transform: translateY(0); }
.st-key-remove_btn button:disabled { background: #f3f4f6; color: #9ca3af; border-color: #e5e7eb; }

/* Clear all button: grey -> amber on hover */
.st-key-clear_btn button {
    background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb;
    transition: background .2s ease, color .2s ease, transform .1s ease;
}
.st-key-clear_btn button:hover { background: #f59e0b; color: #fff; border-color: #f59e0b; transform: translateY(-1px); }

/* Table row that is about to be removed */
.ga-table tr.ga-row-selected > * {
    background: #fee2e2 !important; color: #991b1b;
    animation: ga-pulse 1.2s ease-in-out infinite;
}
@keyframes ga-pulse { 50% { background: #fecaca !important; } }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="ga-hero">
  <h1>📝 Student Grade App</h1>
  <p>Add students, see their grades instantly and keep an eye on class performance.</p>
</div>
""",
    unsafe_allow_html=True,
)

# The student list lives in session_state so it survives reruns.
if "students" not in st.session_state:
    st.session_state.students = []
st.session_state.setdefault("confirm_clear", False)

form_col, result_col = st.columns([1, 2], gap="large")

# ---------- Add student form ----------
with form_col:
    st.markdown('<div class="ga-section-title">➕ Add a student</div>', unsafe_allow_html=True)
    with st.form("add_student_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Alice Johnson")
        mark = st.number_input(
            "Mark (whole number, 1 - 100)",
            min_value=1,
            max_value=100,
            value=None,
            step=1,
            format="%d",
            placeholder="e.g. 85",
            help="Only whole numbers from 1 to 100 are accepted.",
        )
        submitted = st.form_submit_button("Add student")

    if submitted:
        clean_name = name.strip()
        if not clean_name:
            st.error("Please enter a student name.")
        elif mark is None:
            st.error("Please enter a mark.")
        elif not isinstance(mark, int) or not 1 <= mark <= 100:
            # Safety net: the input already limits the value to whole numbers 1 - 100.
            st.error("Mark must be a whole number between 1 and 100.")
        else:
            st.session_state.students.append(
                {"Name": clean_name, "Mark": mark, "Grade": get_grade(mark)}
            )
            st.toast(f"Added {clean_name} ({mark:g})", icon="✅")

    # Grade scale reference
    with st.expander("Grading scale"):
        upper = 100
        for minimum, grade in GRADE_SCALE:
            st.markdown(
                f'<span class="badge text-bg-{GRADE_COLOURS[grade]}">{grade}</span> '
                f"&nbsp;{max(minimum, 1)} – {upper}",
                unsafe_allow_html=True,
            )
            upper = minimum - 1

# ---------- Results ----------
with result_col:
    students = st.session_state.students

    if students:
        marks = [s["Mark"] for s in students]
        average = sum(marks) / len(marks)

        m1, m2, m3 = st.columns(3)
        m1.metric("Class average", f"{average:.1f}")
        m2.metric("Highest", f"{max(marks):g}")
        m3.metric("Lowest", f"{min(marks):g}")

    st.markdown(
        f'<div class="ga-section-title" style="margin-top:1.2rem;">'
        f'📋 Students <span class="badge rounded-pill text-bg-secondary">{len(students)}</span></div>',
        unsafe_allow_html=True,
    )

    if not students:
        st.markdown(
            '<div class="ga-card ga-empty"><div class="ga-emoji">🎓</div>'
            "<div><strong>No students yet</strong></div>"
            "<div>Use the form on the left to add your first student.</div></div>",
            unsafe_allow_html=True,
        )
    else:
        rows = ""
        selected_idx = st.session_state.get("remove_idx")
        for i, s in enumerate(students, start=1):
            colour = GRADE_COLOURS[s["Grade"]]
            row_class = "ga-row-selected" if selected_idx == i - 1 else ""
            rows += (
                f"<tr class='{row_class}'><td>{i}</td>"
                f"<td class='fw-semibold'>{escape(s['Name'])}</td>"
                f"<td>{s['Mark']:g}"
                f"<div class='progress mt-1'><div class='progress-bar bg-{colour}' "
                f"style='width:{s['Mark']}%'></div></div></td>"
                f"<td><span class='badge ga-badge text-bg-{colour}'>{s['Grade']}</span></td></tr>"
            )
        st.markdown(
            "<div class='ga-card'><div class='table-responsive'>"
            "<table class='table table-hover align-middle ga-table'>"
            "<thead><tr><th>#</th><th>Name</th><th>Mark</th><th>Grade</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div></div>",
            unsafe_allow_html=True,
        )

        # Manage entries
        armed = st.session_state.confirm_clear
        if armed:
            # Turn the whole zone red while "clear all" is waiting for confirmation.
            st.markdown(
                "<style>.st-key-remove_zone { border-color: #dc2626 !important;"
                " background: #fef2f2 !important; }"
                ".st-key-clear_btn button { background: #dc2626 !important; color: #fff !important;"
                " border-color: #dc2626 !important; animation: ga-pulse-btn 1s infinite; }"
                "@keyframes ga-pulse-btn { 50% { box-shadow: 0 0 0 6px rgba(220,38,38,.25); } }"
                "</style>",
                unsafe_allow_html=True,
            )

        with st.container(key="remove_zone"):
            st.markdown('<div class="ga-zone-title">🗑️ Remove students</div>', unsafe_allow_html=True)
            selected = st.selectbox(
                "Student to remove",
                options=list(range(len(students))),
                index=None,
                placeholder="Choose a student…",
                format_func=lambda i: f"{i + 1}. {students[i]['Name']} ({students[i]['Mark']:g})",
                key="remove_idx",
                on_change=disarm_clear,
            )

            if armed:
                st.markdown(
                    '<div class="alert alert-danger py-2 mb-2">⚠️ This will delete '
                    f"<strong>all {len(students)}</strong> students. Click the red button again to confirm.</div>",
                    unsafe_allow_html=True,
                )
            elif selected is not None:
                chosen = students[selected]
                st.markdown(
                    '<div class="alert alert-warning py-2 mb-2">You are about to remove '
                    f"<strong>{escape(chosen['Name'])}</strong> "
                    f"({chosen['Mark']:g}, grade {chosen['Grade']}).</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="alert alert-light py-2 mb-2 border">Pick a student to highlight their row.</div>',
                    unsafe_allow_html=True,
                )

            remove_col, clear_col = st.columns(2)
            remove_col.button(
                "Remove selected",
                key="remove_btn",
                use_container_width=True,
                disabled=selected is None,
                on_click=remove_selected,
            )
            clear_col.button(
                "⚠️ Confirm clear all" if armed else "Clear all",
                key="clear_btn",
                use_container_width=True,
                on_click=clear_all,
            )