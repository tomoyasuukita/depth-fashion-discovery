import streamlit as st
import csv, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from recommendation_engine_v02 import recommend, ENT, REL, BY_NAME
try:
    from supabase import create_client
except Exception:
    create_client = None

st.set_page_config(page_title="DEPTH — Japanese Fashion Discovery", page_icon="↘", layout="wide")

BASE=Path(__file__).parent
LOG=BASE/"behavior_log.csv"
LOG_FIELDS=["ts_utc","session_id","event","source","campaign","selected","mode","entity","depth"]

def qp(name, default="direct"):
    v=st.query_params.get(name,default)
    return v[0] if isinstance(v,list) else v

if "session_id" not in st.session_state:
    st.session_state.session_id=str(uuid.uuid4())
if "source" not in st.session_state:
    st.session_state.source=qp("src","direct")
if "campaign" not in st.session_state:
    st.session_state.campaign=qp("campaign","none")
if "logged_session" not in st.session_state:
    st.session_state.logged_session=False

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
    row={
        "ts_utc":datetime.now(timezone.utc).isoformat(),
        "session_id":st.session_state.session_id,
        "event":event,
        "source":st.session_state.source,
        "campaign":st.session_state.campaign,
        "selected":"|".join(selected) if isinstance(selected,list) else selected,
        "mode":mode,"entity":entity,"depth":depth
    }
db, db_error = get_supabase()

if db_error:
    st.error(f"Supabase connection error: {db_error}")

if db is not None:
    try:
        result = db.table("depth_events").insert(row).execute()
        st.success(f"Supabase event saved: {event}")
        return
    except Exception as e:
        st.error(
            f"Supabase insert error: {type(e).__name__}: {e}"
        )
    # Local fallback for development only; Community Cloud storage is not persistent.
    try:
        new=not LOG.exists()
        with LOG.open("a",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=LOG_FIELDS)
            if new:w.writeheader()
            w.writerow(row)
    except Exception:
        pass

if not st.session_state.logged_session:
    log_event("session_start")
    st.session_state.logged_session=True

IMG={
"WTAPS":"https://images.unsplash.com/photo-1523398002811-999ca8dec234?auto=format&fit=crop&w=1000&q=80",
"DESCENDANT":"https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=1000&q=80",
"A.PRESSE":"https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=1000&q=80",
"meanswhile":"https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=80",
"nanamica":"https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?auto=format&fit=crop&w=1000&q=80",
"THE NORTH FACE PURPLE LABEL":"https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1000&q=80"}
FALLBACK="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1000&q=80"

st.markdown("""<style>
:root{--acid:#caff00;--ink:#0d0d0d;--paper:#f2f0e9}.stApp{background:var(--paper);color:var(--ink)}
.block-container{max-width:1240px;padding-top:1.5rem;padding-bottom:5rem}h1{font-size:clamp(4rem,9vw,8rem)!important;line-height:.82!important;letter-spacing:-.06em!important}
h2,h3{letter-spacing:-.045em}.k{font-size:.67rem;letter-spacing:.18em;text-transform:uppercase}.rule{border-top:1px solid #111;margin:1.2rem 0 1.8rem}
.acid{background:var(--acid);display:inline-block;padding:.08rem .34rem}.cardtitle{font-size:2rem;font-weight:650;letter-spacing:-.05em;margin:.25rem 0}
div[data-testid="stImage"] img{filter:saturate(.7);border-radius:0}div[data-testid="stButton"] button{border-radius:0;border:1px solid #111;background:#111;color:white;width:100%}
div[data-testid="stButton"] button:hover{background:var(--acid);color:#111}div[data-testid="stMultiSelect"] span[data-baseweb="tag"]{background:var(--acid);color:#111}
</style>""",unsafe_allow_html=True)

st.markdown("<div class='k'>DEPTH / INDEPENDENT FASHION DISCOVERY FROM JAPAN</div><div class='rule'></div>",unsafe_allow_html=True)
a,b=st.columns([1.15,.85],gap="large")
with a:
    st.title("GO\nDEEPER.")
    st.write("Start with what you know. Discover what you didn't know to search for.")
    st.markdown("<span class='acid'>DISCOVER ↘</span>",unsafe_allow_html=True)
with b: st.image(IMG["WTAPS"],use_container_width=True)

choices=[e["name"] for e in ENT if e["type"] in ("brand","shop","line")]
st.markdown("<div class='rule'></div><div class='k'>01 / YOUR TASTE</div>",unsafe_allow_html=True)
selected=st.multiselect("Taste",choices,default=["WTAPS","1LDK"],max_selections=5,label_visibility="collapsed")
c1,c2,c3,c4=st.columns(4)
with c1: military=st.toggle("MILITARY",True)
with c2: technical=st.toggle("TECHNICAL",False)
with c3: minimal=st.toggle("MINIMAL",False)
with c4: heritage=st.toggle("HERITAGE",False)
extra={}
for k,v in [("military",military),("technical",technical),("minimal",minimal),("heritage",heritage)]:
    if v:extra[k]=100

if selected:
    r=recommend(selected,extra or None)
    if st.session_state.get("last_selected") != (tuple(selected),tuple(sorted(extra))):
        log_event("recommendation_view",selected)
        st.session_state.last_selected=(tuple(selected),tuple(sorted(extra)))

    st.markdown("<div class='rule'></div><div class='k'>02 / NEXT DISCOVERY</div>",unsafe_allow_html=True)
    cards=[("SAFE",r["SAFE"],"Familiar enough to trust."),
           ("GO DEEPER",r["GO_DEEPER"],"A familiar thread, taken somewhere less obvious."),
           ("SURPRISE ME",r["SURPRISE_ME"],"The one you probably weren't going to search for.")]
    cols=st.columns(3)
    for col,(mode,item,copy) in zip(cols,cards):
        with col:
            name=item["name"]
            st.image(IMG.get(name,FALLBACK),use_container_width=True)
            st.markdown(f"<div class='k'>{mode}</div><div class='cardtitle'>{name}</div>",unsafe_allow_html=True)
            st.caption(copy)
            if st.button("EXPLORE ↘",key=f"x_{mode}_{name}"):
                log_event("explore_click",selected,mode,name,item.get("depth",""))
                st.session_state.focus=name

    focus=st.session_state.get("focus",r["GO_DEEPER"]["name"])
    st.markdown("<div class='rule'></div><div class='k'>03 / RABBIT HOLE</div>",unsafe_allow_html=True)
    st.markdown(f"## From {focus}, keep going ↘")
    fe=BY_NAME.get(focus.lower())
    idmap={e["entity_id"]:e for e in ENT}; linked=[]
    if fe:
        for x in REL:
            if x["from_id"]==fe["entity_id"]: linked.append((x["to_id"],x["relation_type"]))
            elif x["to_id"]==fe["entity_id"]: linked.append((x["from_id"],x["relation_type"]))
    names=[(idmap[i]["name"],t) for i,t in linked if i in idmap]
    if not names:names=[("nonnative","taste bridge"),("nanamica","next world"),("THE NORTH FACE PURPLE LABEL","line / project")]
    cols=st.columns(min(3,len(names)))
    for col,(name,typ) in zip(cols,names[:3]):
        with col:
            st.image(IMG.get(name,FALLBACK),use_container_width=True)
            st.markdown(f"**{name}**")
            st.caption(typ.upper())
            if st.button("GO ↘",key=f"rh_{name}"):
                log_event("rabbit_hole_click",selected,"RABBIT_HOLE",name)
                st.session_state.focus=name
                st.rerun()

    st.markdown("<div class='rule'></div><div class='k'>04 / FIND IT</div>",unsafe_allow_html=True)
    st.write("Found something worth chasing?")
    if st.button(f"FIND {focus.upper()} ↗"):
        log_event("find_it_click",selected,"FIND_IT",focus)
        st.success("Interest recorded. Purchase destinations will be connected after MVP demand validation.")

with st.sidebar:
    st.markdown("### MVP SOURCE")
    st.caption(f"Source: {st.session_state.source}")
    st.caption(f"Campaign: {st.session_state.campaign}")
    st.markdown("---")
    st.caption("Example tracked links:")
    st.code("?src=reddit&campaign=wtaps")
    st.code("?src=google&campaign=auralee")
    st.code("?src=instagram&campaign=tokyo")
