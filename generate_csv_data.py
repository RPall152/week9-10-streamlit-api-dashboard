import pandas as pd
import random
from datetime import datetime, timedelta

DATA_DIR = "DATA"
N = 1000  # number of rows per CSV

# -----------------------------
# COMMON VALUES
# -----------------------------
SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES_INCIDENTS = ["Open", "In Progress", "Resolved", "Closed"]
INCIDENT_TYPES = ["Phishing", "Malware", "Misconfiguration", "DDoS", "Insider Threat"]

USERS = ["it_admin", "cyber_admin", "data_scientist", "analyst1", "analyst2"]

TICKET_PRIORITIES = ["Low", "Medium", "High", "Critical"]
TICKET_STATUSES = ["Open", "Assigned", "In Progress", "Resolved", "Closed"]


def random_date(start_days_ago=365):
    start = datetime.now() - timedelta(days=start_days_ago)
    return start + timedelta(days=random.randint(0, start_days_ago),
                             seconds=random.randint(0, 86400))


# =====================================================
# 1️⃣ CYBER INCIDENTS
# =====================================================
incidents = []

for i in range(N):
    incidents.append({
        "incident_id": f"INC-{1000+i}",
        "timestamp": random_date().strftime("%Y-%m-%d %H:%M:%S"),
        "incidents_type": random.choice(INCIDENT_TYPES),
        "severity": random.choice(SEVERITIES),
        "category": random.choice(INCIDENT_TYPES),
        "status": random.choice(STATUSES_INCIDENTS),
        "description": f"Synthetic incident description #{i}"
    })

df_incidents = pd.DataFrame(incidents)
df_incidents.to_csv(f"{DATA_DIR}/cyber_incidents.csv", index=False)


# =====================================================
# 2️⃣ DATASETS METADATA
# =====================================================
datasets = []

for i in range(N):
    datasets.append({
        "dataset_id": f"DS-{1000+i}",
        "name": f"Dataset_{i}",
        "rows": random.randint(500, 1_000_000),
        "columns": random.randint(5, 50),
        "uploaded_by": random.choice(USERS),
        "upload_date": random_date(700).strftime("%Y-%m-%d")
    })

df_datasets = pd.DataFrame(datasets)
df_datasets.to_csv(f"{DATA_DIR}/datasets_metadata.csv", index=False)


# =====================================================
# 3️⃣ IT TICKETS
# =====================================================
tickets = []

for i in range(N):
    created = random_date(300)
    resolved_hours = random.randint(1, 240)

    tickets.append({
        "ticket_id": f"TCK-{2000+i}",
        "priority": random.choice(TICKET_PRIORITIES),
        "description": f"Synthetic IT ticket #{i}",
        "status": random.choice(TICKET_STATUSES),
        "assigned_to": random.choice(USERS),
        "created_at": created.strftime("%Y-%m-%d"),
        "resolution_time_hours": resolved_hours
    })

df_tickets = pd.DataFrame(tickets)
df_tickets.to_csv(f"{DATA_DIR}/it_tickets.csv", index=False)


print("✅ Generated 1000 rows for EACH CSV file.")
print("📁 Files saved in DATA/ folder.")
