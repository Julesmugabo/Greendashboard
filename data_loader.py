import pandas as pd
import os
import io

GITHUB_URL = "https://github.com/Julesmugabo/Greendashboard/blob/main/data/Financial_data_-2026_-New.xlsx"
RAW_URL = "https://raw.githubusercontent.com/Julesmugabo/Greendashboard/main/data/Financial_data_-2026_-New.xlsx"
LOCAL_PATH = os.path.join(os.path.dirname(__file__), "data", "Financial_data_-2026_-New.xlsx")


def load_data():
    """Load data from GitHub raw URL, fallback to local file."""
    xl = None

    # Try GitHub raw URL first
    try:
        import requests
        r = requests.get(RAW_URL, timeout=10)
        if r.status_code == 200:
            xl = pd.ExcelFile(io.BytesIO(r.content))
    except Exception:
        pass

    # Fallback to local file
    if xl is None:
        xl = pd.ExcelFile(LOCAL_PATH)

    df_projects = pd.read_excel(xl, sheet_name="Projects")
    df_expenses = pd.read_excel(xl, sheet_name="Expenses")
    df_accounts = pd.read_excel(xl, sheet_name="Accounts")

    # Clean projects
    df_projects.columns = df_projects.columns.str.strip()
    df_projects["Total Budget"] = pd.to_numeric(df_projects["Total Budget"], errors="coerce").fillna(0)
    df_projects["Total Expenses"] = pd.to_numeric(df_projects["Total Expenses"], errors="coerce").fillna(0)
    df_projects["Total Income"] = pd.to_numeric(df_projects["Total Income"], errors="coerce").fillna(0)
    df_projects["Budget Utilization (%)"] = (
        df_projects["Total Expenses"] / df_projects["Total Budget"].replace(0, float("nan")) * 100
    ).fillna(0).round(1)
    df_projects["Net Position"] = df_projects["Total Income"] - df_projects["Total Expenses"]
    df_projects["Remaining Budget"] = df_projects["Total Budget"] - df_projects["Total Expenses"]

    # Clean expenses
    df_expenses.columns = df_expenses.columns.str.strip()
    df_expenses["Amount (RWF)"] = pd.to_numeric(df_expenses["Amount (RWF)"], errors="coerce").fillna(0)
    df_expenses["Date"] = df_expenses["Date"].astype(str).str.strip()
    df_expenses["Month_Num"] = df_expenses["Date"].str.extract(r"-(\d{2})$")[0].astype(int)
    month_map = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
                 "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
                 "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
    df_expenses["Month_Label"] = df_expenses["Date"].str.extract(r"-(\d{2})$")[0].map(month_map)

    return df_projects, df_expenses, df_accounts
