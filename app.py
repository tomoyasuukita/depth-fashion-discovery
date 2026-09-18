import streamlit as st
import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path

from recommendation_engine_v02 import recommend, ENT, REL, BY_NAME

try:
    from supabase import create_client
except Exception:
    create_client = None


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="DEPTH — Japanese Fashion Discovery",
    page_icon="↘",
    layout="wide"
)

BASE = Path(__file__).parent
LOG = BASE / "behavior_log.csv"

LOG_FIELDS = [
    "ts_utc",
    "session_id",
    "event",
    "source",
    "campaign",
    "selected",
    "mode",
    "entity",
    "depth"
]


# =========================================================
# QUERY PARAMS
# =========================================================

def qp(name, default="direct"):
    v = st.query_params.get(name, default)
    return v[0] if isinstance(v, list) else v


# =========================================================
# SESSION
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "source" not in st.session_state:
    st.session_state.source = qp("src", "direct")

if "campaign" not in st.session_state:
    st.session_state.campaign = qp("campaign", "none")

if "logged_session" not in st.session_state:
    st.session_state.logged_session = False


# =========================================================
# SUPABASE
# =========================================================

@st.cache_resource
def get_supabase():
    if create_client is None:
        return None, "supabase library could not be imported"

    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key), None

    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def log_event(event, selected="", mode="", entity="", depth=""):

    row = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": st.session_state.session_id,
        "event": event,
        "source": st.session_state.source,
        "campaign": st.session_state.campaign,
        "selected": "|".join(selected)
        if isinstance(selected, list)
        else selected,
        "mode": mode,
        "entity": entity,
        "depth": depth
    }

    db, db_error = get_supabase()

    if db_error:
        st.error(f"Supabase connection error: {db_error}")

    if db is not None:
        try:
            db.table("depth_events").insert(
                row,
                returning="minimal"
            ).execute()
            return

        except Exception as e:
            st.error(
                f"Supabase insert error: {type(e).__name__}: {e}"
            )

    # Local fallback
    try:
        new = not LOG.exists()

        with LOG.open(
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=LOG_FIELDS
            )

            if new:
                writer.writeheader()

            writer.writerow(row)

    except Exception as e:
        st.error(
            f"Local log error: {type(e).__name__}: {e}"
        )


if not st.session_state.logged_session:
    log_event("session_start")
    st.session_state.logged_session = True


# =========================================================
# DEPTH TASTE WORLDS
# ---------------------------------------------------------
# 画像はブランド商品を意味しない。
# ブランドの世界観 / Taste を表現するVisual。
# =========================================================

TASTE_WORLDS = {

    "MILITARY": {
        "label": "MILITARY / UTILITY / TOKYO",
        "image":
            "https://images.unsplash.com/photo-1523398002811-999ca8dec234"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Uniforms, utility, workwear and the quieter side of Tokyo street."
    },

    "QUIET": {
        "label": "QUIET / MATERIAL / REFINED",
        "image":
            "https://images.unsplash.com/photo-1594938298603-c8148c4dae35"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Material, proportion and restraint over obvious branding."
    },

    "TECHNICAL": {
        "label": "TECHNICAL / OUTDOOR / URBAN",
        "image":
            "https://images.unsplash.com/photo-1551632811-561732d1e306"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Outdoor function translated into everyday urban clothing."
    },

    "HERITAGE": {
        "label": "HERITAGE / VINTAGE / CRAFT",
        "image":
            "https://images.unsplash.com/photo-1542272604-787c3835535d"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Old garments, craft, patina and reinterpretations of the familiar."
    },

    "CONTEMPORARY": {
        "label": "TOKYO / CONTEMPORARY / BALANCE",
        "image":
            "https://images.unsplash.com/photo-1523381210434-271e8be1f52b"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Modern Tokyo clothing built around proportion, balance and everyday use."
    },

    "EXPERIMENTAL": {
        "label": "CHARACTER / LAYERING / UNEXPECTED",
        "image":
            "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126"
            "?auto=format&fit=crop&w=1200&q=85",
        "description":
            "Familiar references pushed somewhere stranger and more personal."
    }
}


# =========================================================
# ENTITY → TASTE WORLD
# =========================================================

ENTITY_WORLD = {

    # Military / street
    "WTAPS": "MILITARY",
    "NEIGHBORHOOD": "MILITARY",
    "DESCENDANT": "MILITARY",
    "C.E": "EXPERIMENTAL",
    "UNDERCOVER": "EXPERIMENTAL",

    # Tokyo contemporary
    "nonnative": "CONTEMPORARY",
    "Graphpaper": "CONTEMPORARY",
    "FreshService": "CONTEMPORARY",
    "UNIVERSAL PRODUCTS.": "CONTEMPORARY",
    "N.HOOLYWOOD": "CONTEMPORARY",
    "1LDK": "CONTEMPORARY",

    # Quiet / refined
    "AURALEE": "QUIET",
    "COMOLI": "QUIET",
    "CIOTA": "QUIET",
    "blurhms": "QUIET",
    "ATON": "QUIET",
    "YOKE": "QUIET",
    "ssstein": "QUIET",
    "A.PRESSE": "HERITAGE",
    "MAATEE&SONS": "HERITAGE",

    # Technical
    "nanamica": "TECHNICAL",
    "DAIWA PIER39": "TECHNICAL",
    "and wander": "TECHNICAL",
    "meanswhile": "TECHNICAL",
    "TEATORA": "TECHNICAL",
    "THE NORTH FACE PURPLE LABEL": "TECHNICAL",

    # Heritage
    "orSlow": "HERITAGE",
    "KAPITAL": "HERITAGE",
    "Kaptain Sunshine": "HERITAGE",

    # Character
    "Needles": "EXPERIMENTAL",
    "Engineered Garments": "HERITAGE",
    "SOUTH2 WEST8": "TECHNICAL",
    "ANCELLM": "HERITAGE"
}


def taste_world(name):

    world_key = ENTITY_WORLD.get(
        name,
        "CONTEMPORARY"
    )

    return TASTE_WORLDS[world_key]


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    :root{
        --acid:#caff00;
        --ink:#0d0d0d;
        --paper:#f2f0e9;
        --soft:#777;
    }

    .stApp{
        background:var(--paper);
        color:var(--ink);
    }

    .block-container{
        max-width:1240px;
        padding-top:1.5rem;
        padding-bottom:5rem;
    }

    h1{
        font-size:clamp(4rem,9vw,8rem)!important;
        line-height:.82!important;
        letter-spacing:-.06em!important;
    }

    h2,h3{
        letter-spacing:-.045em;
    }

    .k{
        font-size:.67rem;
        letter-spacing:.18em;
        text-transform:uppercase;
    }

    .rule{
        border-top:1px solid #111;
        margin:1.2rem 0 1.8rem;
    }

    .acid{
        background:var(--acid);
        display:inline-block;
        padding:.08rem .34rem;
    }

    .cardtitle{
        font-size:2rem;
        font-weight:650;
        letter-spacing:-.05em;
        line-height:.95;
        margin:.4rem 0 .6rem;
    }

    .taste{
        font-size:.62rem;
        letter-spacing:.13em;
        text-transform:uppercase;
        color:#555;
        margin-bottom:.4rem;
    }

    .visualnote{
        font-size:.58rem;
        letter-spacing:.12em;
        color:#777;
        text-transform:uppercase;
        margin-top:.3rem;
    }

    div[data-testid="stImage"] img{
        filter:saturate(.55) contrast(.96);
        border-radius:0;
    }

    div[data-testid="stButton"] button{
        border-radius:0;
        border:1px solid #111;
        background:#111;
        color:white;
        width:100%;
    }

    div[data-testid="stButton"] button:hover{
        background:var(--acid);
        color:#111;
    }

    div[data-testid="stMultiSelect"]
    span[data-baseweb="tag"]{
        background:var(--acid);
        color:#111;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class='k'>
    DEPTH / INDEPENDENT FASHION DISCOVERY FROM JAPAN
    </div>
    <div class='rule'></div>
    """,
    unsafe_allow_html=True
)

a, b = st.columns(
    [1.15, .85],
    gap="large"
)

with a:

    st.title("GO\nDEEPER.")

    st.write(
        "Start with what you know. "
        "Discover what you didn't know to search for."
    )

    st.markdown(
        "<span class='acid'>DISCOVER ↘</span>",
        unsafe_allow_html=True
    )

with b:

    hero_world = TASTE_WORLDS["MILITARY"]

    st.image(
        hero_world["image"],
        use_container_width=True
    )

    st.markdown(
        "<div class='visualnote'>VISUAL MOOD / TOKYO UTILITY</div>",
        unsafe_allow_html=True
    )


# =========================================================
# 01 / YOUR TASTE
# =========================================================

choices = [
    e["name"]
    for e in ENT
    if e["type"] in (
        "brand",
        "shop",
        "line"
    )
]

st.markdown(
    """
    <div class='rule'></div>
    <div class='k'>01 / YOUR TASTE</div>
    """,
    unsafe_allow_html=True
)

selected = st.multiselect(
    "Taste",
    choices,
    default=["WTAPS", "1LDK"],
    max_selections=5,
    label_visibility="collapsed"
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    military = st.toggle(
        "MILITARY",
        True
    )

with c2:
    technical = st.toggle(
        "TECHNICAL",
        False
    )

with c3:
    minimal = st.toggle(
        "MINIMAL",
        False
    )

with c4:
    heritage = st.toggle(
        "HERITAGE",
        False
    )


extra = {}

for key, value in [
    ("military", military),
    ("technical", technical),
    ("minimal", minimal),
    ("heritage", heritage)
]:

    if value:
        extra[key] = 100


# =========================================================
# DISCOVERY
# =========================================================

if selected:

    r = recommend(
        selected,
        extra or None
    )

    signature = (
        tuple(selected),
        tuple(sorted(extra))
    )

    if (
        st.session_state.get("last_selected")
        != signature
    ):

        log_event(
            "recommendation_view",
            selected
        )

        st.session_state.last_selected = signature


    # =====================================================
    # 02 / NEXT DISCOVERY
    # =====================================================

    st.markdown(
        """
        <div class='rule'></div>
        <div class='k'>02 / NEXT DISCOVERY</div>
        """,
        unsafe_allow_html=True
    )

    cards = [
        (
            "SAFE",
            r["SAFE"],
            "Familiar enough to trust."
        ),
        (
            "GO DEEPER",
            r["GO_DEEPER"],
            "A familiar thread, taken somewhere less obvious."
        ),
        (
            "SURPRISE ME",
            r["SURPRISE_ME"],
            "The one you probably weren't going to search for."
        )
    ]

    cols = st.columns(3)

    for col, (
        mode,
        item,
        copy
    ) in zip(cols, cards):

        with col:

            name = item["name"]
            world = taste_world(name)

            # Mode
            st.markdown(
                f"<div class='k'>{mode}</div>",
                unsafe_allow_html=True
            )

            # Brand
            st.markdown(
                f"<div class='cardtitle'>{name}</div>",
                unsafe_allow_html=True
            )

            # Taste identity
            st.markdown(
                f"<div class='taste'>{world['label']}</div>",
                unsafe_allow_html=True
            )

            # Mood visual
            st.image(
                world["image"],
                use_container_width=True
            )

            st.markdown(
                "<div class='visualnote'>VISUAL MOOD / NOT PRODUCT IMAGE</div>",
                unsafe_allow_html=True
            )

            st.caption(
                world["description"]
            )

            st.caption(copy)

            if st.button(
                "EXPLORE ↘",
                key=f"x_{mode}_{name}"
            ):

                log_event(
                    "explore_click",
                    selected,
                    mode,
                    name,
                    item.get("depth", "")
                )

                st.session_state.focus = name


    # =====================================================
    # 03 / RABBIT HOLE
    # =====================================================

    focus = st.session_state.get(
        "focus",
        r["GO_DEEPER"]["name"]
    )

    st.markdown(
        """
        <div class='rule'></div>
        <div class='k'>03 / RABBIT HOLE</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"## From {focus}, keep going ↘"
    )

    fe = BY_NAME.get(
        focus.lower()
    )

    idmap = {
        e["entity_id"]: e
        for e in ENT
    }

    linked = []

    if fe:

        for relation in REL:

            if (
                relation["from_id"]
                == fe["entity_id"]
            ):

                linked.append(
                    (
                        relation["to_id"],
                        relation["relation_type"]
                    )
                )

            elif (
                relation["to_id"]
                == fe["entity_id"]
            ):

                linked.append(
                    (
                        relation["from_id"],
                        relation["relation_type"]
                    )
                )


    names = [
        (
            idmap[entity_id]["name"],
            relation_type
        )
        for entity_id, relation_type in linked
        if entity_id in idmap
    ]


    if not names:

        names = [
            (
                "nonnative",
                "taste bridge"
            ),
            (
                "nanamica",
                "next world"
            ),
            (
                "THE NORTH FACE PURPLE LABEL",
                "line / project"
            )
        ]


    rabbit_cols = st.columns(
        min(3, len(names))
    )


    for col, (
        name,
        relation_type
    ) in zip(
        rabbit_cols,
        names[:3]
    ):

        with col:

            world = taste_world(name)

            st.markdown(
                f"**{name}**"
            )

            st.markdown(
                f"<div class='taste'>{world['label']}</div>",
                unsafe_allow_html=True
            )

            st.image(
                world["image"],
                use_container_width=True
            )

            st.caption(
                relation_type.upper()
            )

            if st.button(
                "GO ↘",
                key=f"rh_{name}"
            ):

                log_event(
                    "rabbit_hole_click",
                    selected,
                    "RABBIT_HOLE",
                    name
                )

                st.session_state.focus = name

                st.rerun()


    # =====================================================
    # 04 / FIND IT
    # =====================================================

    st.markdown(
        """
        <div class='rule'></div>
        <div class='k'>04 / FIND IT</div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "Found something worth chasing?"
    )

    if st.button(
        f"FIND {focus.upper()} ↗"
    ):

        log_event(
            "find_it_click",
            selected,
            "FIND_IT",
            focus
        )

        st.success(
            "Interest recorded. "
            "Purchase destinations will be connected "
            "after MVP demand validation."
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "### MVP SOURCE"
    )

    st.caption(
        f"Source: {st.session_state.source}"
    )

    st.caption(
        f"Campaign: {st.session_state.campaign}"
    )

    st.markdown("---")

    st.caption(
        "Example tracked links:"
    )

    st.code(
        "?src=reddit&campaign=wtaps"
    )

    st.code(
        "?src=google&campaign=auralee"
    )

    st.code(
        "?src=instagram&campaign=tokyo"
    )
