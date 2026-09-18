DEPTH / SF-002 — MVP v0.4

What changed:
- Persistent behavior logging to Supabase.
- Local CSV remains only as a development fallback.
- Streamlit secrets are used; keys are not hard-coded.
- Source/campaign attribution remains enabled.

One-time setup:
1. Create a free Supabase project.
2. Open SQL Editor and run supabase_setup.sql.
3. Copy Project URL and Publishable/anon key.
4. In Streamlit Community Cloud > App settings > Secrets, add:
   [supabase]
   url = "..."
   key = "..."
5. Deploy app.py from GitHub.

Tracked events:
session_start / recommendation_view / explore_click /
rabbit_hole_click / find_it_click

Security:
The included SQL enables RLS and permits anonymous INSERT only.
Public visitors are not granted SELECT/UPDATE/DELETE on analytics events.
Never commit real secrets to GitHub.
