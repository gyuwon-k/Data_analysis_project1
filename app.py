from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


TARGET_COLUMN = "A_Ngmark"
GOOD_LABEL = "양품"
DEFECT_LABEL = "불량"
DESIGN_PROMPT_PATH = Path(__file__).with_name("DESIGN_PROMPT.md")
DISPLAY_NAMES = {
    "A_Ngmark": "양불구분",
    "A_Cushion_Position": "쿠션위치",
    "A_Max_Injection_Speed": "최대사출속도",
    "A_Average_Back_Pressure": "평균배압",
    "A_Barrel_Temperature_3": "배럴온도3",
    "A_Barrel_Temperature_4": "배럴온도4",
    "A_Hopper_Temperature": "호퍼온도",
    "A_Mold_Temperature_1": "금형온도1",
    "A_Mold_Temperature_2": "금형온도2",
    "S_Inj_Velocity_04": "사출속도4",
    "S_Inj_Pressure_01": "사출압력1",
    "S_Inj_Pressure_04": "사출압력4",
    "S_Inj_Position_01": "사출거리1",
    "S_Hid_Time_01": "보압시간1",
    "S_Suckback_Position_02": "강제후퇴위치2",
    "S_Barrel_Temperature_02": "히터온도2",
    "VALUE1": "금형상판온도",
    "VALUE2": "금형하판온도",
    "VALUE3": "호퍼온도(외부)",
    "VALUE4": "호퍼수분율",
    "VALUE5": "현장온도",
}


st.set_page_config(
    page_title="사출성형 공정 불량 패턴 분석",
    page_icon="◆",
    layout="wide",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --background-deep: #030712;
            --background-base: #070A12;
            --background-elevated: #111827;
            --surface: rgba(17,24,39,0.92);
            --surface-hover: rgba(30,41,59,0.96);
            --foreground: #F8FAFC;
            --muted: #CBD5E1;
            --subtle: #E2E8F0;
            --accent: #7C8CFF;
            --accent-bright: #9AA6FF;
            --border: rgba(226,232,240,0.20);
            --border-hover: rgba(226,232,240,0.34);
            --danger: #ff6171;
            --ok: #63d29a;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(ellipse at top, rgba(30,41,89,0.60) 0%, #070A12 44%, #030712 100%),
                radial-gradient(circle at 18% 22%, rgba(124,140,255,0.17), transparent 34%),
                radial-gradient(circle at 82% 8%, rgba(56,189,248,0.11), transparent 30%),
                linear-gradient(180deg, #070A12 0%, #030712 100%);
            color: var(--foreground);
            font-family: "Inter", system-ui, sans-serif;
        }

        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.026) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.026) 1px, transparent 1px);
            background-size: 64px 64px;
            mask-image: radial-gradient(circle at 50% 0%, black, transparent 76%);
            z-index: 0;
        }

        [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            width: 900px;
            height: 900px;
            left: 50%;
            top: -520px;
            transform: translateX(-50%);
            pointer-events: none;
            background: radial-gradient(circle, rgba(94,106,210,0.24), transparent 62%);
            filter: blur(80px);
            animation: floatGlow 9s ease-in-out infinite;
            z-index: 0;
        }

        @keyframes floatGlow {
            0%, 100% { transform: translateX(-50%) translateY(0) rotate(0deg); }
            50% { transform: translateX(-48%) translateY(24px) rotate(1deg); }
        }

        @media (prefers-reduced-motion: reduce) {
            [data-testid="stAppViewContainer"]::after { animation: none; }
            * { transition: none !important; }
        }

        .main .block-container {
            position: relative;
            z-index: 1;
            max-width: 1440px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(15,23,42,0.99), rgba(17,24,39,0.98)),
                radial-gradient(circle at 10% 0%, rgba(124,140,255,0.16), transparent 36%);
            border-right: 1px solid rgba(124,140,255,0.28);
            backdrop-filter: blur(24px);
            box-shadow:
                inset -1px 0 0 rgba(255,255,255,0.05),
                16px 0 50px rgba(0,0,0,0.20);
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }

        h1, h2, h3 {
            color: var(--foreground);
            letter-spacing: 0;
        }

        p, label, span, div, li {
            color: var(--foreground);
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 34px 34px 28px;
            background:
                linear-gradient(180deg, rgba(17,24,39,0.96), rgba(15,23,42,0.88)),
                radial-gradient(circle at 12% 0%, rgba(124,140,255,0.18), transparent 30%);
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.045),
                0 20px 80px rgba(0,0,0,0.44),
                0 0 100px rgba(94,106,210,0.08);
            margin-bottom: 22px;
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: radial-gradient(circle at 82% 18%, rgba(94,106,210,0.18), transparent 28%);
        }

        .eyebrow {
            color: #aeb4ff;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .hero-title {
            margin: 0;
            max-width: 980px;
            font-size: 46px;
            line-height: 1.08;
            font-weight: 700;
            letter-spacing: 0;
            background: linear-gradient(180deg, #FFFFFF 0%, #DDE7FF 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .hero-copy {
            max-width: 920px;
            margin-top: 14px;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.75;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 22px;
        }

        .metric-card, .note-card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 18px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.078), rgba(255,255,255,0.026));
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.035),
                0 14px 44px rgba(0,0,0,0.34),
                inset 0 1px 0 rgba(255,255,255,0.075);
            transition: border-color 220ms ease-out, transform 220ms ease-out, box-shadow 220ms ease-out;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(15,23,42,0.95));
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 18px 18px 14px;
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.045),
                0 14px 44px rgba(0,0,0,0.32),
                inset 0 1px 0 rgba(255,255,255,0.10);
            min-height: 112px;
        }

        [data-testid="stMetricLabel"] p {
            color: #CBD5E1 !important;
            font-size: 13px !important;
            font-weight: 650 !important;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 30px !important;
            font-weight: 750 !important;
        }

        [data-testid="stMetricDelta"] {
            color: #A7F3D0 !important;
        }

        .metric-card:hover, .note-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-hover);
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.06),
                0 18px 60px rgba(0,0,0,0.44),
                0 0 80px rgba(94,106,210,0.08),
                inset 0 1px 0 rgba(255,255,255,0.1);
        }

        .metric-label {
            color: var(--muted);
            font-size: 12px;
            letter-spacing: 0;
            margin-bottom: 8px;
        }

        .metric-value {
            color: var(--foreground);
            font-size: 27px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: 0;
        }

        .metric-help {
            color: var(--subtle);
            font-size: 12px;
            margin-top: 7px;
        }

        .note-card {
            margin: 12px 0 18px;
            color: var(--muted);
            line-height: 1.7;
        }

        .accent {
            color: #aeb4ff;
            font-weight: 650;
        }

        div[data-testid="stTabs"] button {
            color: var(--muted);
            border-radius: 8px;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--foreground);
            background: rgba(94,106,210,0.16);
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 8px;
            border: 1px solid rgba(94,106,210,0.38);
            background: linear-gradient(180deg, #6872D9, #515bc5);
            color: white;
            box-shadow:
                0 0 0 1px rgba(94,106,210,0.35),
                0 8px 22px rgba(94,106,210,0.24),
                inset 0 1px 0 rgba(255,255,255,0.18);
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: rgba(255,255,255,0.24);
            box-shadow:
                0 0 0 1px rgba(94,106,210,0.45),
                0 10px 30px rgba(94,106,210,0.32),
                inset 0 1px 0 rgba(255,255,255,0.22);
        }

        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: 0 16px 50px rgba(0,0,0,0.25);
            background: #111827 !important;
        }

        [data-testid="stDataFrame"] * {
            color: #F8FAFC;
        }

        [data-testid="stAlert"] {
            background: rgba(17,24,39,0.96);
            color: #F8FAFC;
            border: 1px solid rgba(226,232,240,0.20);
        }

        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"],
        .stNumberInput input {
            border-radius: 8px;
            background-color: #F8FAFC !important;
            border: 1px solid rgba(203,213,225,0.92) !important;
            color: #0F172A !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.92),
                0 8px 24px rgba(0,0,0,0.22);
        }

        .stSelectbox div[data-baseweb="select"] *,
        .stMultiSelect div[data-baseweb="select"] *,
        .stNumberInput input {
            color: #0F172A !important;
        }

        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] div,
        .stMultiSelect div[data-baseweb="select"] span,
        .stMultiSelect div[data-baseweb="select"] div,
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] div,
        div[role="listbox"] div {
            color: #0F172A !important;
        }

        .stMultiSelect [data-baseweb="tag"] {
            background-color: #E0E7FF !important;
            border: 1px solid rgba(124,140,255,0.35) !important;
        }

        .stMultiSelect [data-baseweb="tag"] span {
            color: #111827 !important;
        }

        div[data-baseweb="popover"] {
            background: #F8FAFC !important;
        }

        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] [role="listbox"],
        div[data-baseweb="popover"] [role="option"],
        ul[role="listbox"],
        li[role="option"],
        div[role="option"],
        [data-baseweb="menu"] {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }

        div[data-baseweb="popover"] *,
        ul[role="listbox"] *,
        li[role="option"] *,
        div[role="option"] *,
        [data-baseweb="menu"] * {
            color: #0F172A !important;
            opacity: 1 !important;
        }

        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [role="option"]:hover,
        li[role="option"]:hover,
        div[role="option"]:hover {
            background-color: #E0E7FF !important;
            color: #0F172A !important;
        }

        div[data-baseweb="select"] input::placeholder {
            color: #334155 !important;
            opacity: 1 !important;
        }

        .stSelectbox div[data-baseweb="select"]:hover,
        .stMultiSelect div[data-baseweb="select"]:hover,
        .stNumberInput input:hover {
            border-color: rgba(124,140,255,0.76) !important;
            background-color: #FFFFFF !important;
        }

        .stSelectbox div[data-baseweb="select"]:focus-within,
        .stMultiSelect div[data-baseweb="select"]:focus-within,
        .stNumberInput input:focus {
            border-color: rgba(154,166,255,0.90) !important;
            box-shadow:
                0 0 0 1px rgba(124,140,255,0.42),
                0 0 0 4px rgba(124,140,255,0.16),
                inset 0 1px 0 rgba(255,255,255,0.08) !important;
        }

        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }

        div[data-baseweb="select"] svg {
            color: #0F172A !important;
            fill: #0F172A !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"],
        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] div[data-baseweb="select"] input,
        [data-testid="stSidebar"] .stNumberInput input {
            background-color: #111827 !important;
            color: #F8FAFC !important;
            border-color: rgba(148,163,184,0.34) !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] span,
        [data-testid="stSidebar"] div[data-baseweb="select"] div,
        [data-testid="stSidebar"] div[data-baseweb="select"] svg {
            color: #F8FAFC !important;
            fill: #F8FAFC !important;
        }

        [data-testid="stDataFrame"] {
            font-size: 14px !important;
        }

        [data-testid="stDataFrame"] div {
            font-size: 14px !important;
        }

        .stSlider [data-baseweb="slider"] > div {
            color: #9AA6FF;
        }

        .stRadio div[role="radiogroup"] {
            background: rgba(30,41,59,0.68);
            border: 1px solid rgba(148,163,184,0.22);
            border-radius: 10px;
            padding: 8px 10px;
        }

        @media (max-width: 900px) {
            .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .hero-title { font-size: 34px; }
        }

        @media (max-width: 560px) {
            .metric-grid { grid-template-columns: 1fr; }
            .hero { padding: 24px 20px; }
            .hero-title { font-size: 28px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    csv_path = Path(__file__).with_name("filtered_defect_pattern_data.csv")
    if not csv_path.exists():
        csv_files = sorted(Path(__file__).parent.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("CSV 파일을 찾을 수 없습니다.")
        csv_path = csv_files[0]

    data = pd.read_csv(csv_path, encoding="utf-8-sig")
    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"타깃 컬럼 `{TARGET_COLUMN}`이 없습니다.")
    return data


def numeric_features(data: pd.DataFrame) -> list[str]:
    return [
        column
        for column in data.select_dtypes(include="number").columns.tolist()
        if column != TARGET_COLUMN
    ]


def fmt_int(value: int | float) -> str:
    return f"{int(value):,}"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def display_name(column: str) -> str:
    return DISPLAY_NAMES.get(column, column)


def display_label(column: str) -> str:
    return display_name(column)


def display_condition(condition: str) -> str:
    text = str(condition)
    for original, korean in sorted(DISPLAY_NAMES.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(original, korean)
    return text


def metric_card(label: str, value: str, help_text: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-help">{help_text}</div>
    </div>
    """


def render_metric_grid(cards: list[tuple[str, str, str]]) -> None:
    columns = st.columns(len(cards))
    for column, (label, value, help_text) in zip(columns, cards):
        with column:
            st.metric(label=label, value=value)
            if help_text:
                st.caption(help_text)


def chart_layout(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EDEDEF", family="Inter, system-ui, sans-serif"),
        margin=dict(l=12, r=12, t=44, b=20),
        coloraxis_colorbar=dict(title="불량률"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_layout(
        title_font=dict(size=19, color="#F8FAFC"),
        font=dict(size=14, color="#EDEDEF", family="Inter, system-ui, sans-serif"),
        legend=dict(font=dict(size=13)),
    )
    fig.update_xaxes(title_font=dict(size=15), tickfont=dict(size=13))
    fig.update_yaxes(title_font=dict(size=15), tickfont=dict(size=13))
    return fig


def safe_interval_label(value: object) -> str:
    text = str(value)
    return (
        text.replace("(", "[")
        .replace("]", "]")
        .replace(", ", " ~ ")
        .replace("nan", "NA")
    )


@st.cache_data(show_spinner=False)
def binned_series(
    data: pd.DataFrame,
    column: str,
    bins: int,
    mode: str,
    exact_unique_limit: int,
) -> pd.Series:
    series = data[column]
    nunique = series.nunique(dropna=True)

    if mode == "원값" or nunique <= exact_unique_limit:
        return (display_name(column) + " = " + series.astype("string").fillna("NA")).astype("string")

    if mode == "동일 폭":
        cut = pd.cut(series, bins=bins, duplicates="drop")
    else:
        cut = pd.qcut(series, q=min(bins, max(1, nunique)), duplicates="drop")

    labels = cut.astype("string").map(lambda value: f"{display_name(column)}: {safe_interval_label(value)}")
    return labels.where(~series.isna(), f"{display_name(column)}: NA").astype("string")


def add_metrics(grouped: pd.DataFrame, baseline_rate: float) -> pd.DataFrame:
    result = grouped.copy()
    result["불량률"] = np.where(result["전체"] > 0, result["불량"] / result["전체"] * 100, 0.0)
    result["양품"] = result["전체"] - result["불량"]
    result["평균 대비"] = np.where(baseline_rate > 0, result["불량률"] / baseline_rate, 0.0)
    result["초과 불량"] = result["불량"] - result["전체"] * baseline_rate / 100
    return result.sort_values(["불량률", "불량", "전체"], ascending=False)


@st.cache_data(show_spinner=False)
def build_combo_table(
    data: pd.DataFrame,
    columns: tuple[str, ...],
    bins: int,
    mode: str,
    exact_unique_limit: int,
    min_count: int,
) -> pd.DataFrame:
    baseline_rate = data[TARGET_COLUMN].mean() * 100
    work = pd.DataFrame(index=data.index)
    group_columns = []

    for idx, column in enumerate(columns, start=1):
        group_name = f"조건{idx}"
        work[group_name] = binned_series(data, column, bins, mode, exact_unique_limit)
        group_columns.append(group_name)

    work[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)
    grouped = (
        work.groupby(group_columns, observed=False)[TARGET_COLUMN]
        .agg(전체="size", 불량="sum")
        .reset_index()
    )
    grouped = grouped[grouped["전체"] >= min_count].copy()
    if grouped.empty:
        return grouped
    return add_metrics(grouped, baseline_rate)


@st.cache_data(show_spinner=False)
def find_absolute_rules(data: pd.DataFrame, min_support: int) -> tuple[pd.DataFrame, pd.Series]:
    features = numeric_features(data)
    total_defects = int(data[TARGET_COLUMN].sum())
    rows = []

    for column in features:
        series = data[column]
        for threshold in np.sort(series.dropna().unique()):
            checks = (
                ("<=", series <= threshold),
                ("<", series < threshold),
                (">=", series >= threshold),
                (">", series > threshold),
            )
            for operator, mask in checks:
                total = int(mask.sum())
                if total < min_support:
                    continue
                defects = int(data.loc[mask, TARGET_COLUMN].sum())
                if total and defects == total:
                    rows.append(
                        {
                            "변수": column,
                            "변수명": display_name(column),
                            "방향": "하한 이하" if operator in ("<=", "<") else "상한 이상",
                            "조건": f"{display_name(column)} {operator} {threshold:g}",
                            "연산자": operator,
                            "임계값": float(threshold),
                            "전체": total,
                            "불량": defects,
                            "불량률": 100.0,
                            "전체 불량 중 비중": defects / total_defects * 100 if total_defects else 0,
                            "조건 내 최솟값": float(series[mask].min()),
                            "조건 내 최댓값": float(series[mask].max()),
                        }
                    )

    rules = pd.DataFrame(rows)
    if rules.empty:
        return rules, pd.Series(False, index=data.index)

    rules["방향키"] = rules["연산자"].map({"<=": "low", "<": "low", ">=": "high", ">": "high"})
    rules["포함조건"] = rules["연산자"].isin(["<=", ">="]).astype(int)
    best_rules = (
        rules.sort_values(["변수", "방향키", "전체", "포함조건"], ascending=[True, True, False, False])
        .groupby(["변수", "방향키"], as_index=False)
        .head(1)
        .sort_values("전체", ascending=False)
        .drop(columns=["방향키", "포함조건"])
    )

    union_mask = pd.Series(False, index=data.index)
    for _, row in best_rules.iterrows():
        column = row["변수"]
        threshold = row["임계값"]
        operator = row["연산자"]
        if operator == "<=":
            union_mask |= data[column] <= threshold
        elif operator == "<":
            union_mask |= data[column] < threshold
        elif operator == ">=":
            union_mask |= data[column] >= threshold
        else:
            union_mask |= data[column] > threshold

    return best_rules, union_mask


def filter_data(
    data: pd.DataFrame,
    features: list[str],
    active_filters: list[str],
) -> pd.DataFrame:
    filtered = data.copy()
    for column in active_filters:
        min_value = float(data[column].min())
        max_value = float(data[column].max())
        if min_value == max_value:
            continue
        low, high = st.sidebar.slider(
            column,
            min_value=min_value,
            max_value=max_value,
            value=(min_value, max_value),
            key=f"filter_{column}",
        )
        filtered = filtered[(filtered[column] >= low) & (filtered[column] <= high)]
    return filtered


def table_download(table: pd.DataFrame, file_name: str, label: str = "CSV 다운로드") -> None:
    st.download_button(
        label,
        data=table.to_csv(index=False).encode("utf-8-sig"),
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


def display_table(table: pd.DataFrame) -> pd.DataFrame:
    shown = table.copy()
    for column in ("불량률", "전체 불량 중 비중"):
        if column in shown.columns:
            shown[column] = shown[column].map(lambda value: f"{float(value):.2f}%")
    if "평균 대비" in shown.columns:
        shown["평균 대비"] = shown["평균 대비"].map(lambda value: f"{float(value):.2f}배")
    if "초과 불량" in shown.columns:
        shown["초과 불량"] = shown["초과 불량"].map(lambda value: f"{float(value):.1f}")
    return shown


def render_overview(data: pd.DataFrame, features: list[str], absolute_rules: pd.DataFrame, absolute_mask: pd.Series) -> None:
    total = len(data)
    defects = int(data[TARGET_COLUMN].sum())
    good = total - defects
    defect_rate = defects / total * 100 if total else 0
    absolute_total = int(absolute_mask.sum())
    absolute_defects = int(data.loc[absolute_mask, TARGET_COLUMN].sum()) if absolute_total else 0

    render_metric_grid(
        [
            ("전체 데이터", fmt_int(total), "현재 필터 적용 후 행 수"),
            ("불량", fmt_int(defects), f"양품 {fmt_int(good)}건"),
            ("불량률", fmt_pct(defect_rate), "현재 데이터 기준"),
            ("절대조건 불량", fmt_int(absolute_defects), f"조건 행 {fmt_int(absolute_total)}건"),
        ]
    )

    left, right = st.columns([0.95, 1.05])
    with left:
        counts = pd.DataFrame(
            {
                "검사 결과": [GOOD_LABEL, DEFECT_LABEL],
                "건수": [good, defects],
            }
        )
        fig = px.pie(
            counts,
            names="검사 결과",
            values="건수",
            hole=0.58,
            color="검사 결과",
            color_discrete_map={GOOD_LABEL: "#63d29a", DEFECT_LABEL: "#ff6171"},
            title="양품/불량 구성",
        )
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="rgba(255,255,255,0.12)", width=1)))
        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    with right:
        if not absolute_rules.empty:
            chart_df = absolute_rules.sort_values("전체 불량 중 비중", ascending=True)
            fig = px.bar(
                chart_df,
                x="전체 불량 중 비중",
                y="조건",
                orientation="h",
                color="전체 불량 중 비중",
                color_continuous_scale=["#1a1b25", "#5E6AD2", "#ff6171"],
                title="단일 절대조건의 불량 설명 비중",
                hover_data=["전체", "불량"],
            )
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        else:
            st.info("현재 기준에서 단일 100% 불량 조건이 없습니다.")

    st.info(
        "권장 해석 흐름: 먼저 단일 변수만으로 100% 불량이 되는 절대조건을 분리한 뒤, "
        "남은 데이터에서 1개/2개/3개 변수 조합을 탐색하세요. 이렇게 해야 한 변수의 절대조건이 "
        "조합 효과처럼 보이는 착시를 줄일 수 있습니다."
    )


def render_absolute_rules(data: pd.DataFrame, rules: pd.DataFrame, mask: pd.Series) -> None:
    if rules.empty:
        st.warning("현재 최소 표본 수 기준을 만족하는 단일 100% 불량 조건이 없습니다.")
        return

    covered_total = int(mask.sum())
    covered_defects = int(data.loc[mask, TARGET_COLUMN].sum())
    total_defects = int(data[TARGET_COLUMN].sum())
    remaining = data.loc[~mask]

    render_metric_grid(
        [
            ("절대조건 행", fmt_int(covered_total), "합집합 기준"),
            ("절대조건 불량률", fmt_pct(covered_defects / covered_total * 100), "해당 조건 행 전체"),
            ("전체 불량 설명", fmt_pct(covered_defects / total_defects * 100), f"전체 불량 {fmt_int(total_defects)}건 중"),
            ("잔여 불량률", fmt_pct(remaining[TARGET_COLUMN].mean() * 100), f"잔여 {fmt_int(len(remaining))}건"),
        ]
    )

    st.dataframe(
        display_table(
            rules[
            [
                "변수명",
                "조건",
                "전체",
                "불량",
                "불량률",
                "전체 불량 중 비중",
                "조건 내 최솟값",
                "조건 내 최댓값",
            ]
            ]
        ),
        use_container_width=True,
        height=280,
    )
    table_download(rules, "single_absolute_defect_rules.csv")


def render_single(data: pd.DataFrame, features: list[str], bins: int, mode: str, exact_limit: int, min_count: int) -> None:
    selected = st.selectbox(
        "분석할 변수",
        features,
        index=features.index("VALUE4") if "VALUE4" in features else 0,
        format_func=display_label,
    )
    table = build_combo_table(data, (selected,), bins, mode, exact_limit, min_count)

    if table.empty:
        st.warning("현재 기준을 만족하는 구간이 없습니다. 최소 표본 수를 낮추거나 구간 수를 조정하세요.")
        return

    left, right = st.columns([1.1, 0.9])
    with left:
        plot_df = table.sort_values("불량률", ascending=True).tail(25)
        fig = px.bar(
            plot_df,
            x="불량률",
            y="조건1",
            orientation="h",
            color="불량률",
            color_continuous_scale=["#151722", "#5E6AD2", "#ff6171"],
            hover_data=["전체", "불량", "평균 대비", "초과 불량"],
            title=f"{display_name(selected)} 구간별 불량률",
        )
        fig.add_vline(x=data[TARGET_COLUMN].mean() * 100, line_dash="dot", line_color="#8A8F98")
        st.plotly_chart(chart_layout(fig, 520), use_container_width=True)

    with right:
        labeled = data.copy()
        labeled["검사 결과"] = np.where(labeled[TARGET_COLUMN] == 1, DEFECT_LABEL, GOOD_LABEL)
        fig = px.histogram(
            labeled,
            x=selected,
            color="검사 결과",
            nbins=40,
            barmode="overlay",
            opacity=0.72,
            color_discrete_map={GOOD_LABEL: "#63d29a", DEFECT_LABEL: "#ff6171"},
            title="양품/불량 분포",
        )
        fig.update_xaxes(title_text=display_name(selected))
        fig.update_yaxes(title_text="건수")
        st.plotly_chart(chart_layout(fig, 520), use_container_width=True)

    st.dataframe(display_table(table), use_container_width=True, height=360)
    table_download(table, f"single_{selected}_defect_rate.csv")


def render_pair(data: pd.DataFrame, features: list[str], bins: int, mode: str, exact_limit: int, min_count: int) -> None:
    default_a = "A_Average_Back_Pressure" if "A_Average_Back_Pressure" in features else features[0]
    default_b = "S_Inj_Pressure_04" if "S_Inj_Pressure_04" in features else features[1]
    cols = st.columns(2)
    with cols[0]:
        x_var = st.selectbox("X축 변수", features, index=features.index(default_a), key="pair_x", format_func=display_label)
    with cols[1]:
        y_options = [feature for feature in features if feature != x_var]
        y_var = st.selectbox(
            "Y축 변수",
            y_options,
            index=y_options.index(default_b) if default_b in y_options else 0,
            key="pair_y",
            format_func=display_label,
        )

    table = build_combo_table(data, (x_var, y_var), bins, mode, exact_limit, min_count)
    if table.empty:
        st.warning("현재 기준을 만족하는 2개 변수 조합이 없습니다.")
        return

    heatmap = table.pivot(index="조건2", columns="조건1", values="불량률")
    fig = px.imshow(
        heatmap,
        color_continuous_scale=["#10121a", "#5E6AD2", "#ff6171"],
        aspect="auto",
        title=f"{display_name(x_var)} × {display_name(y_var)} 불량률 히트맵",
        labels=dict(color="불량률"),
    )
    fig.update_traces(
        hovertemplate="X=%{x}<br>Y=%{y}<br>불량률=%{z:.2f}%<extra></extra>"
    )
    st.plotly_chart(chart_layout(fig, 560), use_container_width=True)

    top = table.head(30)
    st.dataframe(display_table(top), use_container_width=True, height=400)
    table_download(table, f"pair_{x_var}_{y_var}_defect_rate.csv")


def render_triple(data: pd.DataFrame, features: list[str], bins: int, mode: str, exact_limit: int, min_count: int) -> None:
    defaults = [
        "A_Average_Back_Pressure",
        "A_Barrel_Temperature_3",
        "S_Inj_Pressure_04",
    ]
    available_defaults = [column for column in defaults if column in features]
    selected = st.multiselect(
        "3개 변수 선택",
        features,
        default=available_defaults if len(available_defaults) == 3 else features[:3],
        max_selections=3,
        format_func=display_label,
    )

    if len(selected) != 3:
        st.info("3개 변수를 선택하면 조합 분석이 표시됩니다.")
        return

    table = build_combo_table(data, tuple(selected), bins, mode, exact_limit, min_count)
    if table.empty:
        st.warning("현재 기준을 만족하는 3개 변수 조합이 없습니다.")
        return

    render_metric_grid(
        [
            ("최고 불량률", fmt_pct(float(table.iloc[0]["불량률"])), str(table.iloc[0]["조건1"])),
            ("최고 조합 건수", fmt_int(int(table.iloc[0]["전체"])), f"불량 {fmt_int(int(table.iloc[0]['불량']))}건"),
            ("평균 대비", f"{table.iloc[0]['평균 대비']:.2f}배", "현재 데이터 평균 대비"),
            ("표시 조합", fmt_int(len(table)), f"최소 {fmt_int(min_count)}건 이상"),
        ]
    )

    c_values = ["상위 조건 자동"] + table["조건3"].drop_duplicates().tolist()
    selected_c = st.selectbox("3번째 변수 조건으로 히트맵 필터링", c_values)
    if selected_c == "상위 조건 자동":
        selected_c = table.iloc[0]["조건3"]

    heat_df = table[table["조건3"] == selected_c]
    heatmap = heat_df.pivot(index="조건2", columns="조건1", values="불량률")
    fig = px.imshow(
        heatmap,
        color_continuous_scale=["#10121a", "#5E6AD2", "#ff6171"],
        aspect="auto",
        title=f"{display_name(selected[2])} 조건: {selected_c}",
        labels=dict(color="불량률"),
    )
    fig.update_traces(
        hovertemplate="조건1=%{x}<br>조건2=%{y}<br>불량률=%{z:.2f}%<extra></extra>"
    )
    st.plotly_chart(chart_layout(fig, 520), use_container_width=True)

    st.dataframe(display_table(table.head(50)), use_container_width=True, height=420)
    table_download(table, "triple_defect_rate_combinations.csv")


def render_data_quality(data: pd.DataFrame, features: list[str]) -> None:
    missing = data.isna().sum().sum()
    duplicates = data.duplicated().sum()
    render_metric_grid(
        [
            ("결측 셀", fmt_int(missing), "전체 데이터 기준"),
            ("중복 행", fmt_int(duplicates), "완전 동일 행"),
            ("분석 변수", fmt_int(len(features)), "숫자형 공정 변수"),
            ("타깃", display_name(TARGET_COLUMN), "0=양품, 1=불량"),
        ]
    )

    summary = (
        data[features]
        .describe()
        .T[["count", "mean", "std", "min", "max"]]
        .reset_index()
        .rename(
            columns={
                "index": "변수",
                "count": "건수",
                "mean": "평균",
                "std": "표준편차",
                "min": "최솟값",
                "max": "최댓값",
            }
        )
    )
    summary["변수"] = summary["변수"].map(display_name)
    st.dataframe(summary, use_container_width=True, height=520)


def main() -> None:
    inject_style()

    data = load_data()
    features = numeric_features(data)

    with st.sidebar:
        st.header("분석 설정")
        min_support_absolute = st.number_input("절대조건 최소 표본 수", min_value=1, max_value=5000, value=100, step=10)
        min_count = st.number_input("조합 최소 표본 수", min_value=1, max_value=5000, value=100, step=10)
        bins = st.slider("구간 수", min_value=3, max_value=20, value=10)
        bin_mode = st.radio("구간화 방식", ["분위수", "동일 폭", "원값"], horizontal=True)
        exact_limit = st.slider("원값 처리 기준", min_value=2, max_value=30, value=12)

        st.divider()
        st.subheader("전역 필터")
        filter_columns = st.multiselect(
            "필터 변수",
            features,
            default=[],
            format_func=display_label,
            help="선택한 변수의 범위를 제한한 뒤 모든 탭을 다시 계산합니다.",
        )

        st.divider()
        exclude_absolute = st.toggle(
            "단일 절대조건 제외 후 조합 분석",
            value=True,
            help="100% 불량을 단독으로 만드는 행을 제거한 뒤 1/2/3 변수 조합을 계산합니다.",
        )

        if DESIGN_PROMPT_PATH.exists():
            with st.expander("디자인 프롬프트"):
                st.caption(f"참조 파일: {DESIGN_PROMPT_PATH.name}")
                st.text(DESIGN_PROMPT_PATH.read_text(encoding="utf-8", errors="replace")[:1400] + "...")

    filtered = filter_data(data, features, filter_columns)
    absolute_rules, absolute_mask = find_absolute_rules(filtered, int(min_support_absolute))
    analysis_data = filtered.loc[~absolute_mask].copy() if exclude_absolute and not absolute_rules.empty else filtered.copy()

    if analysis_data.empty:
        st.error("현재 설정에서는 조합 분석에 사용할 잔여 데이터가 없습니다. 절대조건 제외를 끄거나 필터를 완화하세요.")
        return

    tabs = st.tabs(
        [
            "요약",
            "절대조건",
            "1개 변수",
            "2개 변수",
            "3개 변수",
            "데이터 품질",
        ]
    )

    with tabs[0]:
        st.title("사출성형 공정 불량률 조건 조합 탐색")
        st.write(
            "단일 임계값, 1개 변수 구간, 2개 변수 히트맵, 3개 변수 조합 랭킹을 바꿔가며 "
            "불량률이 급격히 상승하는 조건을 찾는 Streamlit 분석 도구입니다."
        )
        render_overview(filtered, features, absolute_rules, absolute_mask)
        if exclude_absolute and not absolute_rules.empty:
            st.info(
                f"조합 분석은 단일 절대조건 {fmt_int(int(absolute_mask.sum()))}건을 제외한 "
                f"{fmt_int(len(analysis_data))}건 기준으로 계산됩니다."
            )

    with tabs[1]:
        st.caption("절대조건")
        render_absolute_rules(filtered, absolute_rules, absolute_mask)

    with tabs[2]:
        st.caption("1개 변수 분석")
        render_single(analysis_data, features, int(bins), bin_mode, int(exact_limit), int(min_count))

    with tabs[3]:
        st.caption("2개 변수 분석")
        render_pair(analysis_data, features, int(bins), bin_mode, int(exact_limit), int(min_count))

    with tabs[4]:
        st.caption("3개 변수 분석")
        render_triple(analysis_data, features, int(bins), bin_mode, int(exact_limit), int(min_count))

    with tabs[5]:
        st.caption("데이터 품질")
        render_data_quality(filtered, features)


if __name__ == "__main__":
    main()
