import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import uuid

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = 'data/raw'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_departments():
    depts = [
        {'department_id': 'ENG', 'name': 'Engineering'},
        {'department_id': 'SALES', 'name': 'Sales'},
        {'department_id': 'MKTG', 'name': 'Marketing'},
        {'department_id': 'PROD', 'name': 'Product'},
        {'department_id': 'HR', 'name': 'Human Resources'}
    ]
    return pd.DataFrame(depts)

def generate_headcount_plan():
    plans = []
    for dept in ['ENG', 'SALES', 'MKTG', 'PROD', 'HR']:
        for year in [2022, 2023, 2024]:
            for month in range(1, 13):
                period = f"{year}-{month:02d}"
                plans.append({
                    'department_id': dept,
                    'fiscal_period': period,
                    'planned_headcount': random.randint(10, 100),
                    'planned_hires': random.randint(0, 5)
                })
    return pd.DataFrame(plans)

def generate_employees(departments_df):
    employees = []
    for _ in range(300):
        start_date = fake.date_between(start_date='-3y', end_date='today')
        is_active = random.random() > 0.15
        end_date = None if is_active else start_date + timedelta(days=random.randint(30, 700))
        employees.append({
            'employee_id': str(uuid.uuid4())[:8],
            'name': fake.name(),
            'department_id': random.choice(departments_df['department_id']),
            'title': fake.job(),
            'start_date': start_date,
            'end_date': end_date,
            'status': 'Active' if is_active else 'Terminated'
        })
    return pd.DataFrame(employees)

def generate_funnel_data(departments_df):
    requisitions = []
    candidates = []
    applications = []
    stage_events = []
    offers = []
    
    stages = ['Applied', 'Recruiter Screen', 'Hiring Manager Interview', 'Onsite', 'Offer', 'Hired']
    sources = ['LinkedIn', 'Referral', 'Company Website', 'Agency', 'Indeed']
    
    for i in range(100):
        req_id = f"REQ-{1000+i}"
        open_date = fake.date_between(start_date='-2y', end_date='today')
        is_closed = random.random() > 0.2
        close_date = open_date + timedelta(days=random.randint(15, 120)) if is_closed else None
        
        requisitions.append({
            'req_id': req_id,
            'title': fake.job(),
            'department_id': random.choice(departments_df['department_id']),
            'status': 'Closed' if is_closed else 'Open',
            'open_date': open_date,
            'close_date': close_date,
            'target_hire_date': open_date + timedelta(days=60)
        })
        
        # 10 to 50 apps per req
        num_apps = random.randint(10, 50)
        for _ in range(num_apps):
            cand_id = str(uuid.uuid4())[:8]
            app_id = str(uuid.uuid4())[:8]
            apply_date = open_date + timedelta(days=random.randint(1, 30))
            if apply_date > datetime.now().date():
                continue
                
            candidates.append({
                'candidate_id': cand_id,
                'name': fake.name(),
                'email': fake.email(),
                'source': random.choices(sources, weights=[40, 20, 20, 10, 10])[0]
            })
            
            applications.append({
                'application_id': app_id,
                'req_id': req_id,
                'candidate_id': cand_id,
                'apply_date': apply_date
            })
            
            # Determine how far they got
            max_stage_idx = random.choices(range(len(stages)), weights=[50, 20, 10, 10, 5, 5])[0]
            
            curr_date = apply_date
            for stage_idx in range(max_stage_idx + 1):
                stage = stages[stage_idx]
                curr_date += timedelta(days=random.randint(1, 7))
                
                status = 'Pass' if stage_idx < max_stage_idx else random.choice(['Fail', 'In Progress'])
                
                stage_events.append({
                    'event_id': str(uuid.uuid4())[:8],
                    'application_id': app_id,
                    'stage_name': stage,
                    'event_date': curr_date,
                    'status': status
                })
                
                if stage == 'Offer':
                    offer_status = random.choices(['Accepted', 'Declined'], weights=[70, 30])[0]
                    offers.append({
                        'offer_id': str(uuid.uuid4())[:8],
                        'application_id': app_id,
                        'offer_date': curr_date,
                        'status': offer_status,
                        'accepted_date': curr_date + timedelta(days=random.randint(1,3)) if offer_status == 'Accepted' else None,
                        'amount': random.randint(80000, 150000)
                    })
    
    return (pd.DataFrame(requisitions), pd.DataFrame(candidates), 
            pd.DataFrame(applications), pd.DataFrame(stage_events), pd.DataFrame(offers))

def main():
    print("Generating synthetic data...")
    deps = generate_departments()
    hcp = generate_headcount_plan()
    emps = generate_employees(deps)
    reqs, cands, apps, events, offers = generate_funnel_data(deps)
    
    # Save to CSV
    deps.to_csv(f"{OUTPUT_DIR}/departments.csv", index=False)
    hcp.to_csv(f"{OUTPUT_DIR}/headcount_plan.csv", index=False)
    emps.to_csv(f"{OUTPUT_DIR}/employees.csv", index=False)
    reqs.to_csv(f"{OUTPUT_DIR}/requisitions.csv", index=False)
    cands.to_csv(f"{OUTPUT_DIR}/candidates.csv", index=False)
    apps.to_csv(f"{OUTPUT_DIR}/applications.csv", index=False)
    events.to_csv(f"{OUTPUT_DIR}/stage_events.csv", index=False)
    offers.to_csv(f"{OUTPUT_DIR}/offers.csv", index=False)
    
    print(f"Data generated successfully in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
