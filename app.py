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


# =========================================================
# BASE / LOG
# =========================================================

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

        client = create_client(url, key)

        return client, None

    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def log_event(event, selected="", mode="", entity="", depth=""):
    row = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": st.session_state.session_id,
        "event": event,
        "source": st.session_state.source,
        "campaign": st.session_state.campaign,
        "selected": "|".join(selected) if isinstance(selected, list) else selected,
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
                f"Supabase insert error: "
                f"{type(e).__name__}: {e}"
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
            f"Local log error: "
            f"{type(e).__name__}: {e}"
        )


# Session start tracking
if not st.session_state.logged_session:
    log_event("session_start")
    st.session_state.logged_session = True


# =========================================================
# DEPTH VISUAL LIBRARY
# ---------------------------------------------------------
# MVPではブランド公式商品画像を直接転載せず、
# ブランドのTasteに近いeditorial visualを使用。
# =========================================================

IMG = {

    # -----------------------------------------------------
    # STREET / MILITARY
    # -----------------------------------------------------

    "WTAPS":
        "https://images.unsplash.com/photo-1523398002811-999ca8dec234?auto=format&fit=crop&w=1000&q=80",

    "NEIGHBORHOOD":
        "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1000&q=80",

    "DESCENDANT":
        "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=1000&q=80",

    "C.E":
        "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=80",

    "UNDERCOVER":
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80",


    # -----------------------------------------------------
    # TOKYO CONTEMPORARY
    # -----------------------------------------------------

    "nonnative":
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1000&q=80",

    "Graphpaper":
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1000&q=80",

    "FreshService":
        "https://images.unsplash.com/photo-1496217590455-aa63a8350eea?auto=format&fit=crop&w=1000&q=80",

    "UNIVERSAL PRODUCTS.":
        "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=1000&q=80",

    "N.HOOLYWOOD":
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1000&q=80",


    # -----------------------------------------------------
    # MINIMAL / REFINED
    # -----------------------------------------------------

    "AURALEE":
        "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?auto=format&fit=crop&w=1000&q=80",

    "COMOLI":
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1000&q=80",

    "CIOTA":
        "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?auto=format&fit=crop&w=1000&q=80",

    "blurhms":
        "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=1000&q=80",

    "ATON":
        "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=1000&q=80",

    "YOKE":
        "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1000&q=80",

    "ssstein":
        "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=1000&q=80",


    # -----------------------------------------------------
    # UTILITY / TECHNICAL
    # -----------------------------------------------------

    "nanamica":
        "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?auto=format&fit=crop&w=1000&q=80",

    "DAIWA PIER39":
        "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1000&q=80",

    "and wander":
        "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1000&q=80",

    "meanswhile":
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=80",

    "TEATORA":
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1000&q=80",

    "THE NORTH FACE PURPLE LABEL":
        "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1000&q=80",


    # -----------------------------------------------------
    # HERITAGE / CRAFT
    # -----------------------------------------------------

    "orSlow":
        "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=1000&q=80",

    "KAPITAL":
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=1000&q=80",

    "Kaptain Sunshine":
        "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=1000&q=80",

    "A.PRESSE":
        "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=1000&q=80",

    "MAATEE&SONS":
        "https://images.unsplash.com/photo-1610652492500-ded49ceeb378?auto=format&fit=crop&w=1000&q=80",


    # -----------------------------------------------------
    # CHARACTER / EXPERIMENTAL
    # -----------------------------------------------------

    "Needles":
        "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1000&q=80",

    "Engineered Garments":
        "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?auto=format&fit=crop&w=1000&q=80",

    "SOUTH2 WEST8":
        "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=1000&q=80",

    "ANCELLM":
        "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=1000&q=80",
}


# ---------------------------------------------------------
# Fallback visuals
# 未登録entityが出ても全て同じ画像にはしない
# ---------------------------------------------------------

FALLBACKS = [
    "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?auto=format&fit=crop&w=1000&q=80",

    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=1000&q=80",

    "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?auto=format&fit=crop&w=1000&q=80",

    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=1000&q=80",

    "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=1000&q=80",

    "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=1000&q=80",
]


def entity_image(name):
    """
    Entityごとの画像を返す。
    登録済みなら専用画像、
    未登録ならentity名から安定的にfallbackを割り当てる。
    """

    if name in IMG:
        return IMG[name]

    index = sum(ord(c) for c in name) % len(FALLBACKS)

    return FALLBACKS[index]


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
        margin:.25rem 0;
    }

    div[data-testid="stImage"] img{
        filter:saturate(.7);
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
    st.image(
        entity_image("WTAPS"),
        use_container_width=True
    )


# =========================================================
# 01 / YOUR TASTE
# =========================================================

choices = [
    e["name"]
    for e in ENT
    if e["type"] in ("brand", "shop", "line")
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
# RECOMMENDATION
# =========================================================

if selected:

    r = recommend(
        selected,
        extra or None
    )

    current_signature = (
        tuple(selected),
        tuple(sorted(extra))
    )

    if (
        st.session_state.get("last_selected")
        != current_signature
    ):

        log_event(
            "recommendation_view",
            selected
        )

        st.session_state.last_selected = current_signature


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


    for col, (mode, item, copy) in zip(
        cols,
        cards
    ):

        with col:

            name = item["name"]

            st.image(
                entity_image(name),
                use_container_width=True
            )

            st.markdown(
                f"""
                <div class='k'>{mode}</div>
                <div class='cardtitle'>{name}</div>
                """,
                unsafe_allow_html=True
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


    for col, (name, relation_type) in zip(
        rabbit_cols,
        names[:3]
    ):

        with col:

            st.image(
                entity_image(name),
                use_container_width=True
            )

            st.markdown(
                f"**{name}**"
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
# SIDEBAR / TRAFFIC SOURCE
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
