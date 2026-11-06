# CampusPocket Pro — Deployment Bundle

## Run locally
1. Install Python 3.10 or newer.
2. Run: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`

## Streamlit Community Cloud
1. Create a GitHub repository and upload these four files to its root.
2. In Streamlit Community Cloud, create an app from that repository.
3. Set the main file path to `app.py`.
4. Deploy.

## Authentication and data persistence
The app includes a local JSON/file fallback and an optional Supabase authentication/data path.
For a real multi-user public deployment, configure `SUPABASE_URL` and `SUPABASE_KEY` in the deployment secrets and create the required `expenses` table with row-level security policies. The local JSON and CSV fallback is not a durable or secure production database on ephemeral cloud hosting.
