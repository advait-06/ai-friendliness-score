import streamlit as st
from main import (
    fetch_site,
    extract_ai_text,
    signal_ratio,
    js_dominance,
    detect_walls,
    heading_structure,
    score_accessibility,
    score_speed,
    score_signal_ratio,
    score_js_dependency,
    score_structure,
    lost_points_report,
    fix_suggestions
)
from datetime import datetime

def build_txt_report(url, total_score, losses, fixes, ai_text):
    lines = []
    lines.append("AI WEBSITE READABILITY REPORT")
    lines.append("=" * 30)
    lines.append(f"URL: {url}")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"AI Readability Score: {total_score} / 100")
    lines.append("")
    lines.append("POINTS LOST:")
    for k, v in losses.items():
        if v > 0:
            lines.append(f"- {k}: -{v} points")
    lines.append("")
    lines.append("RECOMMENDED FIXES:")
    if fixes:
        for f in fixes:
            lines.append(f"- {f}")
    else:
        lines.append("- No major fixes required.")
    lines.append("")
    lines.append("AI VIEW (EXTRACTED TEXT):")
    lines.append("-" * 30)
    lines.append(ai_text.strip() if ai_text.strip() else "[No AI-readable text found]")
    return "\n".join(lines)

st.set_page_config(page_title="AI Website Readability Scanner")

st.title("🤖 AI Website Readability Scanner")
st.write("See your website the way AI agents see it.")

url = st.text_input("Enter website URL")

if st.button("Scan Website") and url:
    data = fetch_site(url)
    ai_text = extract_ai_text(data["html"])
    ratio = signal_ratio(data["html"], ai_text)
    js_info = js_dominance(data["html"])
    heading_info = heading_structure(data["html"])

    accessibility = score_accessibility(data["status_code"])
    speed = score_speed(data["time_taken"])
    signal = score_signal_ratio(ratio)
    js_score = score_js_dependency(js_info["script_count"])
    structure = score_structure(
        heading_info["h1_count"],
        heading_info["h2_count"]
    )

    scores = {
        "Accessibility": accessibility,
        "Speed": speed,
        "Signal Quality": signal,
        "JavaScript Dependency": js_score,
        "Structure": structure
    }

    total_score = accessibility + speed + signal + js_score + structure

    st.subheader("AI Readability Score")
    st.metric("Score", f"{total_score} / 100")

    st.divider()
    st.subheader("🧠 What AI Sees vs What Humans See")

    col1, col2 = st.columns(2)

    # ------------------------
    # HUMAN VIEW
    # ------------------------
    with col1:
        st.markdown("### 👀 Human View")

        st.markdown(
            f"""
            <iframe 
                src="{url}" 
                width="100%" 
                height="400px" 
                style="border:1px solid #444; border-radius:8px;">
            </iframe>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "⚠️ Some websites block iframe embedding (e.g. Facebook, Google). "
            "If the page does not load here, it is intentionally restricted."
        )

        st.markdown(
            f"[🔗 Open website in new tab]({url})",
            unsafe_allow_html=True
        )

    # ------------------------
    # AI VIEW
    # ------------------------
    with col2:
        st.markdown("### 🤖 AI View (Extracted Text)")
        if ai_text.strip():
            st.text_area(
                label="AI-readable content",
                value=ai_text[:5000],
                height=400
            )
        else:
            st.warning("AI could not extract meaningful text from this page.")

    losses = lost_points_report(scores)

    st.subheader("Points Lost")
    for k, v in losses.items():
        if v > 0:
            st.write(f"- {k}: -{v} points")

    fixes = fix_suggestions(
        ratio,
        js_info["script_count"],
        heading_info["h1_count"],
        heading_info["h2_count"],
        data["time_taken"]
    )

    st.subheader("Recommended Fixes")
    for f in fixes:
        st.write("✔", f)

    st.divider()
    st.subheader("📄 Download Report")

    report_text = build_txt_report(
        url=url,
        total_score=total_score,
        losses=losses,
        fixes=fixes,
        ai_text=ai_text
    )

    st.download_button(
        label="⬇️ Download AI Readability Report (.txt)",
        data=report_text,
        file_name="ai_readability_report.txt",
        mime="text/plain"
    )