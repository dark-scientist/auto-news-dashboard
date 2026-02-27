import html
import json
import os
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Auto News Intelligence", page_icon="🚗", layout="wide")

# TODO: Replace with proper auth before production
USERS = {
    "auto2026": "demo123",
}

CATEGORY_COLORS = {
    "Industry & Market Updates": "#2563eb",
    "Regulatory & Policy Updates": "#7c3aed",
    "Competitor Activity": "#db2777",
    "Technology & Innovation": "#0891b2",
    "Manufacturing & Operations": "#d97706",
    "Supply Chain & Logistics": "#16a34a",
    "Corporate & Business News": "#dc2626",
    "External Events": "#6b7280",
}

CATEGORY_NAMES = list(CATEGORY_COLORS.keys())


def apply_global_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top right, #e8eefb 0%, #f3f6fc 38%, #f8fafc 100%);
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .element-container {
            margin-bottom: 0.3rem;
        }
        section[data-testid="stSidebar"] {
            width: 220px !important;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 0.4rem 0.6rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        }
        [data-testid="stMetricLabel"] p {
            font-size: 0.75rem;
            color: #475569;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.4rem;
            line-height: 1.2;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.7rem;
        }
        .dashboard-header {
            background: linear-gradient(120deg, #0d1b2a 0%, #1b263b 100%);
            color: #ffffff;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.45rem;
            box-shadow: 0 8px 20px rgba(13, 27, 42, 0.25);
        }
        .dashboard-title {
            margin: 0;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .dashboard-subtitle {
            margin: 0.15rem 0 0;
            font-size: 0.82rem;
            color: #cbd5e1;
        }
        .section-title {
            color: #0f172a;
            font-size: 1.0rem;
            font-weight: 700;
            margin: 0.35rem 0 0.45rem;
        }
        .top-story-card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
            border: 1px solid #e2e8f0;
            padding: 0.65rem;
            margin-bottom: 0.35rem;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            height: 170px;
            display: flex;
            flex-direction: column;
        }
        .top-story-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.13);
        }
        .top-story-title {
            margin: 0;
            font-size: 0.9rem;
            font-weight: 700;
            color: #111827;
            min-height: 2.2rem;
        }
        .top-story-meta {
            color: #475569;
            font-size: 0.75rem;
            margin-top: 0.15rem;
            margin-bottom: 0.35rem;
        }
        .top-story-list {
            list-style-type: disc !important;
            list-style-position: inside;
            padding-left: 1rem;
            margin: 0.15rem 0 0;
        }
        .top-story-list li {
            display: list-item;
            margin-bottom: 0.14rem;
            font-size: 0.75rem;
            color: #334155;
            line-height: 1.3;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .top-story-list a {
            color: #334155;
            text-decoration: none;
            transition: color 0.15s ease, text-decoration-color 0.15s ease;
        }
        .top-story-list a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
        .cluster-reason {
            color: #6b7280;
            font-size: 0.74rem;
            font-style: italic;
            margin-top: 0.12rem;
        }
        .source-pill {
            display: inline-block;
            background: #e2e8f0;
            color: #334155;
            padding: 0.12rem 0.42rem;
            border-radius: 999px;
            font-size: 0.69rem;
            margin-right: 0.22rem;
            margin-bottom: 0.18rem;
        }
        .news-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 0.5rem 0.6rem;
            margin: 0.18rem 0;
            box-shadow: 0 2px 9px rgba(15, 23, 42, 0.07);
            transition: transform 0.16s ease;
        }
        .news-card:hover {
            transform: translateY(-1px);
        }
        .news-title {
            margin: 0;
            font-size: 0.83rem;
            line-height: 1.26;
            font-weight: 650;
        }
        .news-title a {
            text-decoration: none;
            color: #0f172a;
            transition: color 0.15s ease, text-decoration-color 0.15s ease;
        }
        .news-title a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
        .news-meta {
            margin-top: 0.22rem;
            font-size: 0.7rem;
            color: #64748b;
            line-height: 1.35;
        }
        .category-item {
            background: #ffffff;
            border-radius: 10px;
            border-left: 4px solid #2563eb;
            padding: 0.4rem 0.55rem;
            margin-bottom: 0.26rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
            font-size: 0.76rem;
        }
        .trending-item {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.36rem 0.45rem;
            margin-bottom: 0.24rem;
        }
        .trending-title {
            font-size: 0.74rem;
            font-weight: 650;
            color: #111827;
            line-height: 1.25;
        }
        .trending-meta {
            font-size: 0.67rem;
            color: #64748b;
            margin-top: 0.12rem;
        }
        .scrolling-text {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.5rem 0.65rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
            overflow: hidden;
            white-space: nowrap;
        }
        .scrolling-text a {
            color: #1f2937;
            text-decoration: none;
            transition: color 0.15s ease, text-decoration-color 0.15s ease;
        }
        .scrolling-text a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
        .headline-time {
            display: inline-block;
            background: #1e3a8a;
            color: #ffffff;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 650;
            margin-right: 0.45rem;
        }
        .flashing {
            animation: flash 2s infinite;
        }
        @keyframes flash {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.35; }
        }
        .funnel-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.45rem;
            padding: 0.35rem;
            border: 1px solid #dbeafe;
            border-radius: 12px;
            background: #eff6ff;
            box-shadow: 0 2px 10px rgba(37, 99, 235, 0.08);
        }
        .funnel-stage {
            flex: 1;
            text-align: center;
            padding: 0.48rem 0.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.09);
        }
        .funnel-value {
            font-size: 1.1rem;
            font-weight: 750;
            color: #ffffff;
            line-height: 1.2;
        }
        .funnel-label {
            font-size: 0.67rem;
            font-weight: 650;
            color: #ffffff;
            margin-top: 0.05rem;
            opacity: 0.95;
        }
        .funnel-note {
            font-size: 0.61rem;
            color: rgba(255, 255, 255, 0.87);
        }
        .funnel-arrow {
            color: #64748b;
            font-size: 0.95rem;
            font-weight: 700;
            flex: 0;
        }
        .widget-shell {
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.07);
            padding: 0.6rem;
        }
        .login-wrap {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-panel {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
            padding: 1rem 1rem 0.5rem;
            width: 100%;
            max-width: 460px;
        }
        .login-shell {
            text-align: center;
            margin-bottom: 0.6rem;
        }
        .login-logo {
            width: 64px;
            height: 64px;
            margin: 0 auto 0.5rem;
            border-radius: 14px;
            background: linear-gradient(150deg, #3b82f6 0%, #60a5fa 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-weight: 700;
            font-size: 1.25rem;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }
        .login-title {
            margin: 0;
            color: #0f172a;
            font-size: 1.2rem;
            font-weight: 700;
        }
        .login-subtitle {
            margin: 0.2rem 0 0;
            color: #475569;
            font-size: 0.82rem;
        }
        div[data-testid="stForm"] {
            background: #ffffff;
            border-radius: 12px;
            padding: 0.55rem;
            box-shadow: none;
            border: 1px solid #e2e8f0;
        }
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p {
            color: #334155 !important;
        }
        @media (max-width: 1200px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        @media (max-width: 1100px) {
            div[data-testid="stHorizontalBlock"]:has(.top-story-card) > div[data-testid="column"] {
                flex: 1 1 calc(50% - 0.5rem) !important;
                min-width: calc(50% - 0.5rem) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def subtle_hr() -> None:
    st.markdown(
        '<hr style="border:none; border-top:1px solid #e2e8f0; margin:0.5rem 0">',
        unsafe_allow_html=True,
    )


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value)


def safe_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    return "".join(ch for ch in text if ord(ch) < 128 and (ord(ch) >= 32 or ch in "\n\t")).strip()


def parse_datetime(value: str):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None

    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    parse_attempts = [("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d", 10)]
    for fmt, length in parse_attempts:
        try:
            return datetime.strptime(text[:length], fmt)
        except ValueError:
            continue
    return None


def format_run_at(run_at_value) -> str:
    dt = parse_datetime(run_at_value)
    if not dt:
        return "-"
    return dt.strftime("%d %b %Y, %H:%M")


def load_data():
    env_results_path = clean_text(os.getenv("RESULTS_JSON_PATH", ""))
    if env_results_path:
        configured_path = Path(env_results_path).expanduser()
        if configured_path.exists():
            try:
                with configured_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None

    local_path = Path("results.json")
    app_dir_path = Path(__file__).resolve().parent / "results.json"
    results_path = local_path if local_path.exists() else app_dir_path
    if not results_path.exists():
        return None
    try:
        with results_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_categories(data):
    categories = (data or {}).get("categories") or {}
    return categories if isinstance(categories, dict) else {}


def get_story_list(category_payload):
    stories = (category_payload or {}).get("stories") or []
    return stories if isinstance(stories, list) else []


def iter_story_articles(data):
    for category_name, category_payload in get_categories(data).items():
        for story in get_story_list(category_payload):
            for article in story.get("articles") or []:
                if isinstance(article, dict):
                    yield category_name, story, article


def normalize_source(source: str) -> str:
    source_name = clean_text(source) if source is not None else ""
    return source_name if source_name else "Unknown"


def get_date_bounds(data):
    dates = []
    for _, _, article in iter_story_articles(data):
        dt = parse_datetime(article.get("published_at"))
        if dt:
            dates.append(dt.date())
    if not dates:
        return None, None
    return min(dates), max(dates)


def compute_metrics(data):
    stats = (data or {}).get("stats") or {}
    categories = get_categories(data)

    article_sources = set()
    total_articles_from_payload = 0
    for _, _, article in iter_story_articles(data):
        total_articles_from_payload += 1
        article_sources.add(normalize_source(article.get("source")))

    total_input = safe_int(stats.get("total_input"), default=total_articles_from_payload)
    total_auto = safe_int(stats.get("total_automobile"), default=total_articles_from_payload)

    unique_stories = 0
    active_categories = 0
    for category_name in CATEGORY_NAMES:
        category_payload = categories.get(category_name) or {}
        story_count = safe_int(category_payload.get("unique_stories"), default=len(get_story_list(category_payload)))
        total_articles = safe_int(category_payload.get("total_articles"), default=0)
        if total_articles > 0 or story_count > 0:
            active_categories += 1
        unique_stories += story_count

    if unique_stories == 0:
        for category_payload in categories.values():
            unique_stories += len(get_story_list(category_payload))

    return {
        "total_articles": max(total_input, 0),
        "auto_relevant": max(total_auto, 0),
        "categories": active_categories,
        "unique_stories": unique_stories,
        "sources": len(article_sources),
        "last_updated": format_run_at((data or {}).get("run_at")),
    }


def aggregate_sources(data, top_n: int = 10):
    counts = {}
    for _, _, article in iter_story_articles(data):
        source = normalize_source(article.get("source"))
        counts[source] = counts.get(source, 0) + 1

    if not counts:
        return []

    sorted_sources = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top_slots = max(top_n - 1, 1)
    top_sources = sorted_sources[:top_slots]
    tail_sources = sorted_sources[top_slots:]

    other_count = sum(count for _, count in tail_sources)
    normalized_top = []

    for source, count in top_sources:
        if source == "Unknown":
            other_count += count
        else:
            normalized_top.append((source, count))

    if other_count > 0:
        normalized_top.append(("Other", other_count))

    return normalized_top[:top_n]


def get_story_summary(story):
    summary = clean_text(story.get("summary"))
    if summary:
        return summary
    for article in story.get("articles") or []:
        preview = clean_text(article.get("content_preview"))
        if preview:
            return preview
    return "No summary available."


def get_story_sources(story):
    story_sources = story.get("sources") or []
    if story_sources:
        clean_sources = [normalize_source(source) for source in story_sources]
        return sorted(set(clean_sources))

    fallback = []
    for article in story.get("articles") or []:
        fallback.append(normalize_source(article.get("source")))
    return sorted(set(fallback))


def get_story_count(story):
    explicit = safe_int(story.get("story_count"), default=0)
    if explicit > 0:
        return explicit
    return max(len(get_story_sources(story)), 1)


def get_category_totals(category_payload):
    stories = get_story_list(category_payload)
    total_articles = safe_int(category_payload.get("total_articles"), default=0)
    if total_articles == 0:
        total_articles = sum(len(story.get("articles") or []) for story in stories)

    unique_stories = safe_int(category_payload.get("unique_stories"), default=len(stories))
    return total_articles, unique_stories


def get_story_representative_article(story):
    articles = story.get("articles") or []
    if not articles:
        return {}

    for article in articles:
        if article.get("is_representative"):
            return article

    best_article = articles[0]
    best_date = parse_datetime(best_article.get("published_at"))
    best_date_value = best_date.date() if best_date else None
    for article in articles[1:]:
        current_date = parse_datetime(article.get("published_at"))
        current_date_value = current_date.date() if current_date else None
        if current_date_value and (best_date_value is None or current_date_value > best_date_value):
            best_article = article
            best_date = current_date
            best_date_value = current_date_value
    return best_article


def make_clickable_url(url, title: str) -> str:
    cleaned_url = clean_text(url or "")
    if cleaned_url.startswith("http://") or cleaned_url.startswith("https://"):
        return cleaned_url
    return f"https://www.google.com/search?q={quote_plus(clean_text(title))}"


def get_story_link(story):
    representative_article = get_story_representative_article(story)
    title = clean_text(representative_article.get("title")) or clean_text(story.get("representative_title")) or "Untitled"
    url = representative_article.get("url")
    if not url:
        for article in story.get("articles") or []:
            if article.get("url"):
                url = article.get("url")
                break
    return make_clickable_url(url, title)


def get_story_importance_score(story) -> float:
    score = float(get_story_count(story))
    for article in story.get("articles") or []:
        score += safe_float(article.get("auto_score")) * 2.0
        score += safe_float(article.get("category_confidence")) * 2.0
    return score


def collect_ranked_stories(data):
    ranked = []
    for category_name, category_payload in get_categories(data).items():
        for story in get_story_list(category_payload):
            representative_article = get_story_representative_article(story)
            published_dt = parse_datetime(representative_article.get("published_at"))
            title = clean_text(story.get("representative_title")) or "Untitled"
            ranked.append(
                {
                    "category": category_name,
                    "story": story,
                    "title": title,
                    "url": get_story_link(story),
                    "score": get_story_importance_score(story),
                    "published_at": published_dt.date() if published_dt else None,
                }
            )
    ranked.sort(
        key=lambda row: (
            row["score"],
            row["published_at"] if row["published_at"] is not None else datetime.min.date(),
        ),
        reverse=True,
    )
    return ranked


def create_scatter_plot(data, selected_categories):
    fig = go.Figure()
    categories = get_categories(data)
    rng = random.Random(42)

    for category_name in CATEGORY_NAMES:
        if category_name not in selected_categories:
            continue

        stories = get_story_list(categories.get(category_name) or {})
        if not stories:
            continue

        x_positions = []
        y_positions = []
        sizes = []
        hovers = []

        category_index = CATEGORY_NAMES.index(category_name)
        for story in stories:
            story_title = clean_text(story.get("representative_title")) or "Untitled"
            story_summary = get_story_summary(story)
            story_sources = get_story_sources(story)
            story_count = get_story_count(story)

            base_x = (category_index % 3) * 30 + rng.uniform(-10, 10)
            base_y = (category_index // 3) * 30 + rng.uniform(-10, 10)
            x_positions.append(base_x)
            y_positions.append(base_y)
            sizes.append(min(16 + story_count * 7, 58))

            source_preview = ", ".join(story_sources[:4]) if story_sources else "Unknown"
            if len(story_sources) > 4:
                source_preview += f" +{len(story_sources) - 4} more"

            hovers.append(
                f"<b>{html.escape(story_title[:75])}</b><br>"
                f"<b>Category:</b> {html.escape(category_name)}<br>"
                f"<b>Sources ({story_count}):</b> {html.escape(source_preview)}<br>"
                f"<b>Summary:</b> {html.escape(story_summary[:160])}..."
            )

        fig.add_trace(
            go.Scatter(
                x=x_positions,
                y=y_positions,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=CATEGORY_COLORS.get(category_name, "#2563eb"),
                    line=dict(width=1, color="white"),
                    opacity=0.76,
                ),
                name=category_name,
                hovertemplate="%{hovertext}<extra></extra>",
                hovertext=hovers,
                showlegend=True,
            )
        )

    fig.update_layout(
        height=560,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#e2e8f0",
            borderwidth=1,
        ),
        hovermode="closest",
        xaxis=dict(showgrid=True, gridcolor="#e5e7eb", zeroline=False, showticklabels=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb", zeroline=False, showticklabels=False, title=""),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#334155"),
        margin=dict(l=20, r=130, t=15, b=15),
    )
    return fig


def render_pipeline_funnel(metrics):
    total_articles = metrics["total_articles"]
    relevant_articles = metrics["auto_relevant"]
    sources = metrics["sources"]
    stories = metrics["unique_stories"]
    categories_total = len(CATEGORY_NAMES)
    irrelevant_removed = max(total_articles - relevant_articles, 0)
    duplicates_removed = max(relevant_articles - stories, 0)

    st.markdown('<div class="section-title">Pipeline Flow</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="funnel-container">
            <div class="funnel-stage" style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);">
                <div class="funnel-value">{sources}</div>
                <div class="funnel-label">Sources</div>
            </div>
            <div class="funnel-arrow">&#8594;</div>
            <div class="funnel-stage" style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);">
                <div class="funnel-value">{total_articles}</div>
                <div class="funnel-label">Total Articles</div>
            </div>
            <div class="funnel-arrow">&#8594;</div>
            <div class="funnel-stage" style="background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);">
                <div class="funnel-value">{relevant_articles}</div>
                <div class="funnel-label">Relevant Articles</div>
                <div class="funnel-note">-{irrelevant_removed} irrelevant</div>
            </div>
            <div class="funnel-arrow">&#8594;</div>
            <div class="funnel-stage" style="background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 100%);">
                <div class="funnel-value">{stories}</div>
                <div class="funnel-label">Stories</div>
                <div class="funnel-note">-{duplicates_removed} duplicates</div>
            </div>
            <div class="funnel-arrow">&#8594;</div>
            <div class="funnel-stage" style="background: linear-gradient(135deg, #93c5fd 0%, #dbeafe 100%);">
                <div class="funnel-value" style="color:#1e3a8a;">{categories_total}</div>
                <div class="funnel-label" style="color:#1e3a8a;">Categories</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_headline_ticker(data):
    st.markdown('<div class="section-title">Latest Headlines</div>', unsafe_allow_html=True)
    headlines = []
    for row in collect_ranked_stories(data)[:15]:
        safe_title = html.escape(row["title"][:120])
        safe_url = html.escape(row["url"], quote=True)
        headlines.append(f'<a href="{safe_url}" target="_blank" title="{safe_url}">• {safe_title}</a>')

    if not headlines:
        st.info("No headlines available.")
        return

    headline_text = " &nbsp;&nbsp; ".join(headlines)
    now_text = datetime.now().strftime("%B %d, %Y • %I:%M %p")

    st.markdown(
        f"""
        <div class="scrolling-text">
            <span class="headline-time flashing">LIVE</span>
            <span class="headline-time">{html.escape(now_text)}</span>
            <marquee behavior="scroll" direction="left" scrollamount="5" style="display:inline-block;width:calc(100% - 220px);">
                {headline_text}
            </marquee>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_story_details(story, index: int):
    headline = clean_text(story.get("representative_title")) or "Untitled"
    summary = get_story_summary(story)
    sources = get_story_sources(story)
    story_count = get_story_count(story)

    st.markdown(f"**{index}. {headline}**")
    st.caption(summary)

    if sources:
        pills = "".join(f'<span class="source-pill">{html.escape(source)}</span>' for source in sources)
        st.markdown(pills, unsafe_allow_html=True)

    st.caption(f"Covered by {story_count} sources")

    cluster_reason = clean_text(story.get("cluster_reason"))
    if cluster_reason:
        st.markdown(f'<div class="cluster-reason">Why here: {html.escape(cluster_reason)}</div>', unsafe_allow_html=True)

    subtle_hr()


def render_top_stories_grid(data):
    st.markdown('<div class="section-title">Top Stories</div>', unsafe_allow_html=True)
    categories = get_categories(data)

    for start_idx in range(0, len(CATEGORY_NAMES), 4):
        cols = st.columns(4, gap="small")
        for offset, category_name in enumerate(CATEGORY_NAMES[start_idx : start_idx + 4]):
            with cols[offset]:
                category_payload = categories.get(category_name) or {}
                stories = sorted(get_story_list(category_payload), key=get_story_importance_score, reverse=True)
                top_rows = []
                for story in stories[:3]:
                    title = clean_text(story.get("representative_title")) or "Untitled"
                    url = get_story_link(story)
                    top_rows.append((title, url))

                if not top_rows:
                    top_rows = [("No stories available", "")]

                titles_html = ""
                for title, url in top_rows:
                    safe_title = html.escape(title[:120])
                    if url:
                        safe_url = html.escape(url, quote=True)
                        titles_html += f'<li><a href="{safe_url}" target="_blank" title="{safe_url}">{safe_title}</a></li>'
                    else:
                        titles_html += f"<li>{safe_title}</li>"
                st.markdown(
                    f"""
                    <div class="top-story-card" style="border-top: 3px solid {CATEGORY_COLORS.get(category_name, '#2563eb')};">
                        <p class="top-story-title">{html.escape(category_name)}</p>
                        <ul class="top-story-list">{titles_html}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def build_recent_story_rows(data, selected_range, selected_category):
    rows = []

    for category_name, category_payload in get_categories(data).items():
        if selected_category != "All Categories" and category_name != selected_category:
            continue

        for story in get_story_list(category_payload):
            articles = story.get("articles") or []
            representative_article = articles[0] if articles else {}
            latest_date = None

            for article in articles:
                published_at = parse_datetime(article.get("published_at"))
                if not published_at:
                    continue
                if latest_date is None or published_at.date() > latest_date:
                    latest_date = published_at.date()
                    representative_article = article

            if latest_date and selected_range and len(selected_range) == 2:
                if not (selected_range[0] <= latest_date <= selected_range[1]):
                    continue

            title = clean_text(representative_article.get("title"))
            if not title:
                title = clean_text(story.get("representative_title")) or "Untitled"

            rows.append(
                {
                    "title": title,
                    "category": category_name,
                    "source": normalize_source(representative_article.get("source")),
                    "url": make_clickable_url(representative_article.get("url"), title),
                    "published_at": latest_date,
                }
            )

    rows.sort(key=lambda item: item["published_at"] or datetime.min.date(), reverse=True)
    return rows


def render_recent_news_grid(data):
    st.markdown('<div class="section-title">Latest Articles Feed</div>', unsafe_allow_html=True)

    if "grid_page" not in st.session_state:
        st.session_state.grid_page = 0

    min_date, max_date = get_date_bounds(data)
    if not min_date or not max_date:
        today = datetime.now().date()
        min_date = today
        max_date = today

    filter_col1, filter_col2 = st.columns([1.2, 1], gap="small")
    with filter_col1:
        selected_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter",
        )
    with filter_col2:
        selected_category = st.selectbox(
            "Category",
            options=["All Categories"] + CATEGORY_NAMES,
            index=0,
            key="grid_category_filter",
        )
    filtered_rows = build_recent_story_rows(data, selected_range, selected_category)

    items_per_page = 8
    total_pages = max(1, (len(filtered_rows) + items_per_page - 1) // items_per_page)
    st.session_state.grid_page = max(0, min(st.session_state.grid_page, total_pages - 1))

    start = st.session_state.grid_page * items_per_page
    end = start + items_per_page
    page_rows = filtered_rows[start:end]

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1], gap="small")
    with nav_col1:
        if st.button("Prev", disabled=(st.session_state.grid_page == 0), key="grid_prev", use_container_width=True):
            st.session_state.grid_page -= 1
            st.rerun()
    with nav_col2:
        st.markdown(
            f"<div style='text-align:center;font-size:0.76rem;color:#475569;padding-top:0.35rem;'>"
            f"Page {st.session_state.grid_page + 1}/{total_pages} · {len(filtered_rows)} stories"
            f"</div>",
            unsafe_allow_html=True,
        )
    with nav_col3:
        if st.button(
            "Next",
            disabled=(st.session_state.grid_page >= total_pages - 1),
            key="grid_next",
            use_container_width=True,
        ):
            st.session_state.grid_page += 1
            st.rerun()

    for start_idx in range(0, len(page_rows), 2):
        row_cols = st.columns(2, gap="small")
        for offset, story in enumerate(page_rows[start_idx : start_idx + 2]):
            with row_cols[offset]:
                title = story["title"]
                if len(title) > 110:
                    title = title[:107] + "..."

                category = story["category"]
                category_color = CATEGORY_COLORS.get(category, "#2563eb")
                source_name = story["source"]
                published = story["published_at"].strftime("%d %b %Y") if story.get("published_at") else "Unknown date"

                safe_title = html.escape(title)
                safe_category = html.escape(category)
                safe_source = html.escape(source_name)

                title_html = safe_title
                if story.get("url"):
                    safe_url = html.escape(story["url"], quote=True)
                    title_html = f'<a href="{safe_url}" target="_blank" title="{safe_url}">{safe_title}</a>'

                st.markdown(
                    f"""
                    <div class="news-card">
                        <p class="news-title">{title_html}</p>
                        <div class="news-meta">
                            <span style="color:{category_color};font-weight:700;">&#9679;</span> {safe_category}<br>
                            {safe_source}<br>
                            {published}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    return None


def render_trending_panel(data):
    st.markdown('<div class="section-title">Trending Topics</div>', unsafe_allow_html=True)

    trending = []
    for category_name, category_payload in get_categories(data).items():
        for story in get_story_list(category_payload):
            trending.append(
                {
                    "title": clean_text(story.get("representative_title")) or "Untitled",
                    "category": category_name,
                    "count": get_story_count(story),
                }
            )

    trending.sort(key=lambda row: row["count"], reverse=True)

    for row in trending[:8]:
        safe_title = html.escape(row["title"][:120])
        safe_category = html.escape(row["category"])
        color = CATEGORY_COLORS.get(row["category"], "#2563eb")
        st.markdown(
            f"""
            <div class="trending-item">
                <div class="trending-title">{safe_title}</div>
                <div class="trending-meta"><span style="color:{color};font-weight:700;">&#9679;</span> {safe_category} · {row['count']} sources</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_category_breakdown(data):
    st.markdown('<div class="section-title">Category Breakdown</div>', unsafe_allow_html=True)

    categories = get_categories(data)
    for category_name in CATEGORY_NAMES:
        category_payload = categories.get(category_name) or {}
        total_articles, unique_stories = get_category_totals(category_payload)

        if total_articles == 0 and unique_stories == 0:
            continue

        color = CATEGORY_COLORS.get(category_name, "#2563eb")
        safe_name = html.escape(category_name)

        st.markdown(
            f"""
            <div class="category-item" style="border-left-color:{color};">
                <strong>{safe_name}</strong><br>
                {total_articles} articles · {unique_stories} stories
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_source_chart(data):
    st.markdown('<div class="section-title">Articles by Source</div>', unsafe_allow_html=True)

    aggregated = aggregate_sources(data, top_n=10)
    if not aggregated:
        st.info("No source data available.")
        return

    df_sources = pd.DataFrame(aggregated, columns=["Source", "Articles"])

    bar_colors = ["#2563eb"] * len(df_sources)
    if not df_sources.empty:
        bar_colors[-1] = "#64748b" if df_sources.iloc[-1]["Source"] == "Other" else "#2563eb"

    fig_bar = go.Figure(
        data=[
            go.Bar(
                x=df_sources["Articles"],
                y=df_sources["Source"],
                orientation="h",
                marker=dict(color=bar_colors),
                text=df_sources["Articles"],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Articles: %{x}<extra></extra>",
            )
        ]
    )

    fig_bar.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=5, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis_title="Articles",
        font=dict(size=11, color="#334155"),
    )

    st.plotly_chart(fig_bar, use_container_width=True)


def render_category_pie(data):
    st.markdown('<div class="section-title">Articles by Category</div>', unsafe_allow_html=True)

    rows = []
    for category_name in CATEGORY_NAMES:
        payload = get_categories(data).get(category_name) or {}
        total_articles, _ = get_category_totals(payload)
        if total_articles > 0:
            rows.append((category_name, total_articles))

    if not rows:
        st.info("No category data available.")
        return

    df = pd.DataFrame(rows, columns=["Category", "Articles"])

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["Category"],
                values=df["Articles"],
                hole=0.45,
                marker=dict(colors=[CATEGORY_COLORS.get(cat, "#2563eb") for cat in df["Category"]]),
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>%{value} articles<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        height=310,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scatter_section(data):
    st.markdown('<div class="section-title">Story Scatter Plot Visualization</div>', unsafe_allow_html=True)
    st.caption("Each bubble represents one clustered story. Bubble size maps to source count.")

    available_scatter_categories = [
        category_name
        for category_name in CATEGORY_NAMES
        if get_story_list(get_categories(data).get(category_name) or {})
    ]
    selected_categories = st.multiselect(
        "Cluster Categories",
        options=available_scatter_categories,
        default=available_scatter_categories,
        key="scatter_filter",
    )

    if not selected_categories:
        st.info("Select at least one cluster category to display the plot.")
        return

    fig = create_scatter_plot(data, selected_categories)
    config = {
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
        "toImageButtonOptions": {"format": "png", "filename": "auto_news_scatter"},
    }
    st.plotly_chart(fig, use_container_width=True, config=config)


def render_detailed_stories(data):
    st.markdown('<div class="section-title">Detailed Stories by Category</div>', unsafe_allow_html=True)

    available_categories = [
        category_name
        for category_name in CATEGORY_NAMES
        if get_story_list(get_categories(data).get(category_name) or {})
    ]

    if not available_categories:
        st.info("No story details available.")
        return

    selected_category = st.selectbox(
        "Story Category",
        options=available_categories,
        key="detailed_story_category",
    )

    category_payload = get_categories(data).get(selected_category) or {}
    stories = get_story_list(category_payload)
    total_articles, unique_stories = get_category_totals(category_payload)
    st.caption(f"{total_articles} articles · {unique_stories} stories")

    for index, story in enumerate(stories, 1):
        title = clean_text(story.get("representative_title")) or "Untitled"
        summary = get_story_summary(story)
        sources = get_story_sources(story)
        story_count = get_story_count(story)

        with st.expander(f"Story #{index}: {title} ({story_count} sources)", expanded=False):
            st.info(f"Summary: {summary}")
            st.caption(f"Covered by: {', '.join(sources) if sources else 'Unknown'}")
            subtle_hr()

            articles = story.get("articles") or []
            for article_index, article in enumerate(articles, 1):
                article_title = clean_text(article.get("title")) or "Untitled"
                article_url = make_clickable_url(article.get("url"), article_title)
                source = normalize_source(article.get("source"))
                published = clean_text(str(article.get("published_at") or ""))[:10] or "N/A"

                st.markdown(f"{article_index}. **[{article_title}]({article_url})**")
                st.caption(f"Source: {source} · Published: {published}")


def render_login() -> bool:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.logged_in:
        return True

    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            height: 100%;
            overflow: hidden;
        }
        div[data-testid="stAppViewContainer"] > .main {
            overflow: hidden;
        }
        div[data-testid="stAppViewContainer"] > .main > div {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        div[data-testid="stAppViewContainer"] .block-container {
            max-width: 480px;
            width: 100%;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="login-panel">
            <div class="login-shell">
                <div class="login-logo">AN</div>
                <p class="login-title">Auto News Intelligence</p>
                <p class="login-subtitle">Secure dashboard access</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if USERS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid credentials")

    return False


def main():
    apply_global_css()

    if not render_login():
        return

    with st.sidebar:
        st.markdown(f"Signed in as **{st.session_state.get('user', 'user')}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    data = load_data()
    if data is None:
        st.error("No data found. Ensure results.json is present in streamlit-app/.")
        return

    metrics = compute_metrics(data)
    st.title("Auto News Intelligence Dashboard")
    st.caption(f"Last updated: {metrics['last_updated'] if metrics['last_updated'] != '-' else '—'}")

    subtle_hr()
    render_pipeline_funnel(metrics)
    subtle_hr()
    render_headline_ticker(data)
    subtle_hr()
    render_top_stories_grid(data)
    subtle_hr()
    st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1], gap="medium")
    with left_col:
        render_recent_news_grid(data)
        subtle_hr()
        render_source_chart(data)

    with right_col:
        render_category_pie(data)
        subtle_hr()
        render_category_breakdown(data)

    subtle_hr()
    st.markdown('<div class="widget-shell">', unsafe_allow_html=True)
    render_scatter_section(data)
    st.markdown("</div>", unsafe_allow_html=True)

    subtle_hr()
    st.markdown('<div class="widget-shell">', unsafe_allow_html=True)
    render_detailed_stories(data)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
