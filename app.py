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


# ============================================================
# PAGE
# ============================================================

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
    "depth",
]


# ============================================================
# QUERY PARAMS
# ============================================================

def qp(name, default="direct"):
    v = st.query_params.get(name, default)
    return v[0] if isinstance(v, list) else v


# ============================================================
# SESSION
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "source" not in st.session_state:
    st.session_state.source = qp("src", "direct")

if "campaign" not in st.session_state:
    st.session_state.campaign = qp("campaign", "none")

if "logged_session" not in st.session_state:
    st.session_state.logged_session = False

if "saved_entities" not in st.session_state:
    st.session_state.saved_entities = []

if "focus" not in st.session_state:
    st.session_state.focus = None

if "detail_entity" not in st.session_state:
    st.session_state.detail_entity = None


# ============================================================
# SUPABASE
# ============================================================

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
        "selected": "|".join(selected)
        if isinstance(selected, list)
        else selected,
        "mode": mode,
        "entity": entity,
        "depth": depth,
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

            w = csv.DictWriter(
                f,
                fieldnames=LOG_FIELDS
            )

            if new:
                w.writeheader()

            w.writerow(row)

    except Exception as e:

        st.error(
            f"Local log error: {type(e).__name__}: {e}"
        )


# ============================================================
# FIRST SESSION EVENT
# ============================================================

if not st.session_state.logged_session:

    log_event("session_start")

    st.session_state.logged_session = True


# ============================================================
# ENTITY HELPERS
# ============================================================

IDMAP = {
    e["entity_id"]: e
    for e in ENT
}


def get_entity(name):

    if not name:
        return None

    return BY_NAME.get(name.lower())


def entity_depth(name):

    e = get_entity(name)

    if not e:
        return ""

    return e.get("discovery_depth", "")


# ============================================================
# VISUAL SYSTEM
# ============================================================
#
# IMPORTANT:
#
# These are VISUAL MOOD images.
# They are NOT official product photography.
#
# The objective is:
#
#   "Does this image make the visitor understand
#    the world of the entity before reading?"
#
# ============================================================


VISUALS = {

    "WTAPS": {
        "image":
            "https://images.unsplash.com/photo-1523398002811-999ca8dec234"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "MILITARY / UTILITY / TOKYO",
        "note":
            "Uniforms, utility and the quieter side of Tokyo street.",
    },

    "DESCENDANT": {
        "image":
            "https://images.unsplash.com/photo-1523398002811-999ca8dec234"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "MILITARY / UTILITY / TOKYO",
        "note":
            "Relaxed utility, uniforms and everyday Tokyo street.",
    },

    "nonnative": {
        "image":
            "https://images.unsplash.com/photo-1506629082955-511b1aa562c8"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "UTILITY / TRAVEL / URBAN",
        "note":
            "Everyday clothing shaped by movement, utility and city life.",
    },

    "nanamica": {
        "image":
            "https://images.unsplash.com/photo-1551632811-561732d1e306"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "TECHNICAL / OUTDOOR / CITY",
        "note":
            "Outdoor function translated into calm everyday clothing.",
    },

    "THE NORTH FACE PURPLE LABEL": {
        "image":
            "https://images.unsplash.com/photo-1551632811-561732d1e306"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "TECHNICAL / JAPAN / OUTDOOR",
        "note":
            "A Japanese lens on outdoor utility and everyday design.",
    },

    "1LDK": {
        "image":
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "TOKYO / CONTEMPORARY / BALANCE",
        "note":
            "A Tokyo point of view connecting quiet contemporary labels.",
    },

    "UNIVERSAL PRODUCTS.": {
        "image":
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "EVERYDAY / BASIC / TOKYO",
        "note":
            "Ordinary wardrobe pieces refined through proportion and detail.",
    },

    "Graphpaper": {
        "image":
            "https://images.unsplash.com/photo-1490481651871-ab68de25d43d"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "MINIMAL / VOLUME / TOKYO",
        "note":
            "Clean forms, generous volume and contemporary restraint.",
    },

    "A.PRESSE": {
        "image":
            "https://images.unsplash.com/photo-1594938298603-c8148c4dae35"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "HERITAGE / VINTAGE / CRAFT",
        "note":
            "Old garments, craft, patina and reinterpretations of the familiar.",
    },

    "meanswhile": {
        "image":
            "https://images.unsplash.com/photo-1529139574466-a303027c1d8b"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "TECHNICAL / UTILITY / URBAN",
        "note":
            "Function and construction designed for everyday movement.",
    },

    "NEIGHBORHOOD": {
        "image":
            "https://images.unsplash.com/photo-1520975954732-35dd22299614"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "MOTOR / MILITARY / TOKYO",
        "note":
            "Motor culture, military references and Tokyo street identity.",
    },

    "COMOLI": {
        "image":
            "https://images.unsplash.com/photo-1523381210434-271e8be1f52b"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "QUIET / MATERIAL / JAPAN",
        "note":
            "Quiet clothing built around material, ease and everyday life.",
    },

    "AURALEE": {
        "image":
            "https://images.unsplash.com/photo-1496217590455-aa63a8350eea"
            "?auto=format&fit=crop&w=1200&q=82",
        "world":
            "MATERIAL / REFINED / QUIET",
        "note":
            "Material-first clothing with refined proportions and restraint.",
    },

}


# Different fallbacks.
# This prevents every unknown entity showing exactly the same image.

FALLBACK_IMAGES = [

    "https://images.unsplash.com/photo-1445205170230-053b83016050"
    "?auto=format&fit=crop&w=1200&q=82",

    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"
    "?auto=format&fit=crop&w=1200&q=82",

    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b"
    "?auto=format&fit=crop&w=1200&q=82",

    "https://images.unsplash.com/photo-1441986300917-64674bd600d8"
    "?auto=format&fit=crop&w=1200&q=82",

    "https://images.unsplash.com/photo-1483985988355-763728e1935b"
    "?auto=format&fit=crop&w=1200&q=82",

]


def stable_fallback(name):

    if not name:
        return FALLBACK_IMAGES[0]

    index = sum(
        ord(c)
        for c in name
    ) % len(FALLBACK_IMAGES)

    return FALLBACK_IMAGES[index]


def visual_for(name):

    if name in VISUALS:
        return VISUALS[name]

    e = get_entity(name)

    if e:

        axes = [
            ("STREET", float(e.get("street", 0))),
            ("MINIMAL", float(e.get("minimal", 0))),
            ("UTILITY", float(e.get("utility", 0))),
            ("HERITAGE", float(e.get("heritage", 0))),
            ("TECHNICAL", float(e.get("technical", 0))),
            ("MILITARY", float(e.get("military", 0))),
        ]

        axes.sort(
            key=lambda x: x[1],
            reverse=True
        )

        world = " / ".join(
            x[0]
            for x in axes[:3]
        )

    else:
        world = "JAPAN / DISCOVERY / INDEPENDENT"

    return {
        "image": stable_fallback(name),
        "world": world,
        "note":
            "A visual mood for discovery — not official product photography.",
    }


# ============================================================
# NEW / JUST ADDED
# ============================================================
#
# MVP:
# Keep this explicit.
#
# Later:
# move to Supabase / graph metadata and automate updates.
#
# ============================================================

NEW_ENTITIES = {
    "A.PRESSE": "NEW",
    "meanswhile": "JUST ADDED",
    "THE NORTH FACE PURPLE LABEL": "DEEP CUT",
}


def new_badge(name):

    return NEW_ENTITIES.get(name)


# ============================================================
# RELATIONSHIP HELPERS
# ============================================================

def linked_entities(name):

    e = get_entity(name)

    if not e:
        return []

    entity_id = e["entity_id"]

    results = []

    for r in REL:

        other_id = None

        if r["from_id"] == entity_id:
            other_id = r["to_id"]

        elif r["to_id"] == entity_id:
            other_id = r["from_id"]

        if not other_id:
            continue

        other = IDMAP.get(other_id)

        if not other:
            continue

        results.append({
            "name": other["name"],
            "relation_type": r.get(
                "relation_type",
                "connection"
            ),
            "strength": float(
                r.get(
                    "strength",
                    0
                )
                or 0
            ),
            "evidence": r.get(
                "evidence",
                ""
            ),
        })

    results.sort(
        key=lambda x: x["strength"],
        reverse=True
    )

    return results


def relationship_copy(relation_type, evidence):

    relation_type = (
        relation_type
        or ""
    ).lower()

    evidence = (
        evidence
        or ""
    ).lower()

    if relation_type == "official_relation":
        return "OFFICIAL CONNECTION"

    if relation_type == "house_brand":
        return "HOUSE BRAND"

    if relation_type == "group_context":
        return "OFFICIAL CONTEXT"

    if relation_type == "taste":
        return "TASTE CONNECTION"

    if evidence == "official":
        return "OFFICIAL CONNECTION"

    return "DISCOVERY CONNECTION"


# ============================================================
# SAVE SYSTEM
# ============================================================

def save_entity(name, selected):

    if name not in st.session_state.saved_entities:

        st.session_state.saved_entities.append(name)

        log_event(
            "save_click",
            selected,
            "MY_DEPTH",
            name,
            entity_depth(name)
        )


def unsave_entity(name):

    if name in st.session_state.saved_entities:
        st.session_state.saved_entities.remove(name)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root{
    --acid:#caff00;
    --ink:#0d0d0d;
    --paper:#f2f0e9;
    --muted:#74746f;
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

h2,
h3{
    letter-spacing:-.045em;
}

.k{
    font-size:.67rem;
    letter-spacing:.18em;
    text-transform:uppercase;
}

.rule{
    border-top:1px solid #111;
    margin:1.5rem 0 1.8rem;
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
    line-height:1;
    margin:.3rem 0 .5rem;
}

.world{
    color:#74746f;
    font-size:.68rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    margin-bottom:.6rem;
}

.visualnote{
    color:#666;
    font-size:.78rem;
    line-height:1.5;
}

.badge{
    display:inline-block;
    background:var(--acid);
    color:#111;
    font-size:.58rem;
    letter-spacing:.14em;
    padding:.18rem .35rem;
    margin-bottom:.45rem;
}

.detailbox{
    border:1px solid #111;
    padding:1.4rem;
    margin-top:.8rem;
}

.savedbox{
    border-top:1px solid #111;
    padding-top:1rem;
    margin-top:1rem;
}

div[data-testid="stImage"] img{
    filter:saturate(.72);
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


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class='k'>
DEPTH / INDEPENDENT FASHION DISCOVERY FROM JAPAN
</div>
<div class='rule'></div>
""",
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

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

    hero = visual_for("WTAPS")

    st.image(
        hero["image"],
        use_container_width=True
    )

    st.markdown(
        "<div class='world'>VISUAL MOOD / TOKYO UTILITY</div>",
        unsafe_allow_html=True
    )


# ============================================================
# MY DEPTH
# ============================================================

with st.expander(
    f"MY DEPTH / {len(st.session_state.saved_entities)} SAVED",
    expanded=False
):

    if not st.session_state.saved_entities:

        st.caption(
            "Save discoveries you want to return to."
        )

    else:

        saved_cols = st.columns(
            min(
                3,
                len(st.session_state.saved_entities)
            )
        )

        for col, name in zip(
            saved_cols,
            st.session_state.saved_entities[:3]
        ):

            with col:

                v = visual_for(name)

                st.image(
                    v["image"],
                    use_container_width=True
                )

                st.markdown(
                    f"**{name}**"
                )

                st.caption(
                    v["world"]
                )

                if st.button(
                    "REMOVE",
                    key=f"remove_{name}"
                ):

                    unsave_entity(name)

                    st.rerun()


# ============================================================
# 01 / TASTE
# ============================================================

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
<div class='k'>
01 / YOUR TASTE
</div>
""",
    unsafe_allow_html=True
)

default_taste = [
    x
    for x in ["WTAPS", "1LDK"]
    if x in choices
]

selected = st.multiselect(
    "Taste",
    choices,
    default=default_taste,
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

for k, v in [
    ("military", military),
    ("technical", technical),
    ("minimal", minimal),
    ("heritage", heritage),
]:

    if v:
        extra[k] = 100


# ============================================================
# RECOMMENDATIONS
# ============================================================

if selected:

    r = recommend(
        selected,
        extra or None
    )

    state_signature = (
        tuple(selected),
        tuple(sorted(extra))
    )

    if (
        st.session_state.get("last_selected")
        != state_signature
    ):

        log_event(
            "recommendation_view",
            selected
        )

        st.session_state.last_selected = (
            state_signature
        )


    # ========================================================
    # 02 / NEXT DISCOVERY
    # ========================================================

    st.markdown(
        """
<div class='rule'></div>
<div class='k'>
02 / NEXT DISCOVERY
</div>
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
        ),
    ]


    cols = st.columns(3)


    for col, (
        mode,
        item,
        copy
    ) in zip(
        cols,
        cards
    ):

        with col:

            name = item["name"]

            visual = visual_for(name)

            badge = new_badge(name)

            if badge:

                st.markdown(
                    f"<span class='badge'>{badge}</span>",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"<div class='k'>{mode}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='cardtitle'>{name}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='world'>{visual['world']}</div>",
                unsafe_allow_html=True
            )

            st.image(
                visual["image"],
                use_container_width=True
            )

            st.markdown(
                "<div class='world'>VISUAL MOOD / NOT PRODUCT IMAGE</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='visualnote'>{visual['note']}</div>",
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
                    item.get(
                        "depth",
                        ""
                    )
                )

                log_event(
                    "detail_view",
                    selected,
                    mode,
                    name,
                    item.get(
                        "depth",
                        ""
                    )
                )

                st.session_state.focus = name
                st.session_state.detail_entity = name

                st.rerun()


            if name in st.session_state.saved_entities:

                if st.button(
                    "SAVED ✓",
                    key=f"saved_{mode}_{name}"
                ):

                    unsave_entity(name)

                    st.rerun()

            else:

                if st.button(
                    "SAVE TO MY DEPTH +",
                    key=f"save_{mode}_{name}"
                ):

                    save_entity(
                        name,
                        selected
                    )

                    st.rerun()


    # ========================================================
    # DISCOVERY DETAIL
    # ========================================================

    detail_name = (
        st.session_state.detail_entity
    )

    if detail_name:

        detail_visual = visual_for(
            detail_name
        )

        detail_entity = get_entity(
            detail_name
        )

        st.markdown(
            """
<div class='rule'></div>
<div class='k'>
DISCOVERY DETAIL
</div>
""",
            unsafe_allow_html=True
        )

        left, right = st.columns(
            [1, 1],
            gap="large"
        )

        with left:

            st.image(
                detail_visual["image"],
                use_container_width=True
            )

        with right:

            badge = new_badge(
                detail_name
            )

            if badge:

                st.markdown(
                    f"<span class='badge'>{badge}</span>",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"## {detail_name}"
            )

            st.markdown(
                f"<div class='world'>{detail_visual['world']}</div>",
                unsafe_allow_html=True
            )

            st.write(
                detail_visual["note"]
            )

            if detail_entity:

                st.caption(
                    "DISCOVERY DEPTH / "
                    + detail_entity.get(
                        "discovery_depth",
                        "Explore"
                    ).upper()
                )

                st.caption(
                    "ORIGIN / "
                    + detail_entity.get(
                        "origin",
                        "Japan"
                    ).upper()
                )

            if (
                detail_name
                not in
                st.session_state.saved_entities
            ):

                if st.button(
                    "SAVE TO MY DEPTH ↘",
                    key=f"detail_save_{detail_name}"
                ):

                    save_entity(
                        detail_name,
                        selected
                    )

                    st.rerun()

            else:

                st.markdown(
                    "<span class='acid'>SAVED TO MY DEPTH ✓</span>",
                    unsafe_allow_html=True
                )


    # ========================================================
    # FOCUS
    # ========================================================

    focus = (
        st.session_state.focus
        or r["GO_DEEPER"]["name"]
    )


    # ========================================================
    # 03 / RABBIT HOLE
    # ========================================================

    st.markdown(
        """
<div class='rule'></div>
<div class='k'>
03 / RABBIT HOLE
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        f"## From {focus}, keep going ↘"
    )


    links = linked_entities(
        focus
    )


    # Fallback discovery path
    if not links:

        fallback_names = [
            "nonnative",
            "nanamica",
            "THE NORTH FACE PURPLE LABEL",
        ]

        links = [
            {
                "name": x,
                "relation_type":
                    "taste",
                "strength":
                    50,
                "evidence":
                    "hypothesis",
            }
            for x in fallback_names
            if x.lower() in BY_NAME
            and x != focus
        ]


    # Don't repeat current focus
    links = [
        x
        for x in links
        if x["name"] != focus
    ]


    rabbit_cols = st.columns(3)


    for col, link in zip(
        rabbit_cols,
        links[:3]
    ):

        with col:

            name = link["name"]

            visual = visual_for(
                name
            )

            badge = new_badge(
                name
            )

            if badge:

                st.markdown(
                    f"<span class='badge'>{badge}</span>",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"<div class='cardtitle'>{name}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='world'>{visual['world']}</div>",
                unsafe_allow_html=True
            )

            st.image(
                visual["image"],
                use_container_width=True
            )

            relation_label = (
                relationship_copy(
                    link["relation_type"],
                    link["evidence"]
                )
            )

            st.markdown(
                f"<div class='k'>{relation_label}</div>",
                unsafe_allow_html=True
            )

            st.caption(
                visual["note"]
            )


            if st.button(
                "GO ↘",
                key=f"rh_{focus}_{name}"
            ):

                log_event(
                    "rabbit_hole_click",
                    selected,
                    "RABBIT_HOLE",
                    name,
                    entity_depth(name)
                )

                log_event(
                    "detail_view",
                    selected,
                    "RABBIT_HOLE",
                    name,
                    entity_depth(name)
                )

                st.session_state.focus = name
                st.session_state.detail_entity = name

                st.rerun()


            if (
                name
                not in
                st.session_state.saved_entities
            ):

                if st.button(
                    "SAVE +",
                    key=f"rabbit_save_{focus}_{name}"
                ):

                    save_entity(
                        name,
                        selected
                    )

                    st.rerun()

            else:

                st.caption(
                    "SAVED TO MY DEPTH ✓"
                )


    # ========================================================
    # 04 / FIND IT
    # ========================================================

    st.markdown(
        """
<div class='rule'></div>
<div class='k'>
04 / FIND IT
</div>
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
            focus,
            entity_depth(focus)
        )

        st.info(
            "Interest recorded. "
            "Purchase destinations will be connected "
            "after MVP demand validation."
        )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.markdown(
        """
<div class='rule'></div>
<div class='k'>
START SOMEWHERE
</div>
"""
        ,
        unsafe_allow_html=True
    )

    st.write(
        "Choose a brand, shop or line you already know."
    )


# ============================================================
# RETURN REASON
# ============================================================

st.markdown(
    """
<div class='rule'></div>
<div class='k'>
COME BACK DEEPER
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    "### New connections. New labels. New reasons to keep digging."
)

st.caption(
    "DEPTH is designed to evolve as new Japanese labels, "
    "projects, collaborations and connections are discovered."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "### DEPTH"
    )

    st.caption(
        "Japanese Fashion Discovery"
    )

    st.markdown("---")

    st.markdown(
        f"**MY DEPTH — "
        f"{len(st.session_state.saved_entities)} SAVED**"
    )

    if st.session_state.saved_entities:

        for name in st.session_state.saved_entities:

            st.caption(
                f"↘ {name}"
            )

    else:

        st.caption(
            "Nothing saved yet."
        )

    st.markdown("---")

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
