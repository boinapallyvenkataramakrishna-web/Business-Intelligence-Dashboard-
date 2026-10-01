
# Business Intelligence Dashboard — Streamlit

## Objective
Build a dynamic BI dashboard with KPI cards, interactive filters, responsive Plotly charts, customer churn analysis, regional market analysis, and checkout A/B-test analysis.

## Supplied data used
- `web_traffic.csv` — 900 sessions
- `customer_churn.csv` — 605 customers
- `regional_market.csv` — 400 regional records
- `checkout_ab_test.csv` — 1,200 visitors

## KPI definitions
- Total Revenue = sum of valid `TotalChargesINR`
- Active Users = customers with `Churn = No`
- Churn % = churned customers / filtered customers
- Avg Ticket Size = Total Revenue / Active Users
  - This is a revenue-per-active-customer proxy because the supplied data does not contain a dedicated order/ticket table.

## Run locally (Windows CMD)
```cmd
cd BI_Dashboard_Streamlit
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally:
`http://localhost:8501`

## Publish a live URL with Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and the four CSV files.
3. Open Streamlit Community Cloud and choose **Create app**.
4. Select your GitHub repository and branch.
5. Set the main file to `app.py`.
6. Deploy.
7. Copy the generated public `streamlit.app` URL for submission.

## Project structure
```
BI_Dashboard_Streamlit/
├── app.py
├── requirements.txt
├── README.md
├── web_traffic.csv
├── customer_churn.csv
├── regional_market.csv
└── checkout_ab_test.csv
```

## Submission proof
Use either:
- Public Streamlit URL after deployment, or
- Screen-record the dashboard walkthrough showing filters and interactive charts.

Recommended walkthrough:
1. Show KPI cards.
2. Change Date Range.
3. Change Region.
4. Change Category / Landing Page.
5. Demonstrate the churn, market, and A/B-test tabs.
6. Show responsive charts and data table.
