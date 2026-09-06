"""
generate_dataset.py
Generates 4 raw synthetic CSV files for an online skill-certification EdTech platform:
1. users.csv (100,000 rows)
2. enrollments.csv (~150,000 rows)
3. lesson_events.csv (~3,500,000 rows)
4. payments.csv (~60,000 rows)

Built with realistic messiness for downstream SQL cleaning:
- Invalid age values (-1, -3, -5, 0, 999)
- Duplicate enrollment rows
- Inconsistent timestamp formats & null timestamps
"""

import os
import csv
import random
import datetime
import numpy as np

# Set deterministic random seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

OUTPUT_DIR = os.path.join("data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Course Catalog
COURSES = [
    {"course_id": "CRS_PY_101", "category": "programming", "lessons": 8, "price": 99.00},
    {"course_id": "CRS_JS_102", "category": "programming", "lessons": 10, "price": 129.00},
    {"course_id": "CRS_WEB_103", "category": "programming", "lessons": 10, "price": 119.00},
    {"course_id": "CRS_SQL_201", "category": "data_analytics", "lessons": 8, "price": 89.00},
    {"course_id": "CRS_BI_202", "category": "data_analytics", "lessons": 8, "price": 99.00},
    {"course_id": "CRS_DS_203", "category": "data_analytics", "lessons": 10, "price": 149.00},
    {"course_id": "CRS_UX_301", "category": "design", "lessons": 8, "price": 89.00},
    {"course_id": "CRS_FIG_302", "category": "design", "lessons": 6, "price": 79.00},
    {"course_id": "CRS_SEO_401", "category": "marketing", "lessons": 8, "price": 79.00},
    {"course_id": "CRS_DM_402", "category": "marketing", "lessons": 8, "price": 89.00},
    {"course_id": "CRS_AWS_501", "category": "cloud_devops", "lessons": 10, "price": 169.00},
    {"course_id": "CRS_DOCK_502", "category": "cloud_devops", "lessons": 8, "price": 149.00},
]

COUNTRIES = ["US", "IN", "GB", "CA", "DE", "FR", "BR", "AU"]
COUNTRY_WEIGHTS = [0.38, 0.26, 0.11, 0.08, 0.07, 0.04, 0.03, 0.03]

CHANNELS = ["organic", "paid_ad", "social", "referral"]
CHANNEL_WEIGHTS = [0.35, 0.30, 0.20, 0.15]

CATEGORY_BOOST = {
    "cloud_devops": 0.13,
    "programming": 0.10,
    "data_analytics": 0.08,
    "marketing": 0.03,
    "design": 0.00
}

START_DATE = datetime.datetime(2024, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(2024, 12, 31, 23, 59, 59)
TOTAL_DAYS = (END_DATE - START_DATE).days


def generate_users(num_users=100_000):
    print(f"Generating {num_users:,} users...")
    users = []
    
    channels = np.random.choice(CHANNELS, size=num_users, p=CHANNEL_WEIGHTS)
    countries = np.random.choice(COUNTRIES, size=num_users, p=COUNTRY_WEIGHTS)
    experiments = np.random.choice(["control", "treatment"], size=num_users, p=[0.5, 0.5])
    
    # Age distribution: Normal(28.5, 7.8), clipped to [16, 68]
    raw_ages = np.random.normal(loc=28.5, scale=7.8, size=num_users).round().astype(int)
    ages = np.clip(raw_ages, 16, 68)
    
    # Messiness in age: inject ~150 invalid values (-1, -3, -5, 0, 999)
    messy_indices = np.random.choice(num_users, size=150, replace=False)
    invalid_age_choices = [-1, -3, -5, 0, 999]
    for idx in messy_indices:
        ages[idx] = random.choice(invalid_age_choices)
        
    day_offsets = np.random.beta(a=1.2, b=1.0, size=num_users) * TOTAL_DAYS
    second_offsets = np.random.randint(0, 86400, size=num_users)
    
    for i in range(num_users):
        user_id = f"U{i+1:06d}"
        signup_dt = START_DATE + datetime.timedelta(days=float(day_offsets[i]), seconds=int(second_offsets[i]))
        signup_date_str = signup_dt.strftime("%Y-%m-%d")
        
        users.append({
            "user_id": user_id,
            "signup_date": signup_date_str,
            "signup_dt": signup_dt,
            "signup_channel": channels[i],
            "country": countries[i],
            "age": ages[i],
            "experiment_group": experiments[i]
        })
        
    return users


def generate_enrollments_and_events(users):
    print("Generating enrollments, lesson events, and payments...")
    
    enrollment_rows = []
    payments_rows = []
    
    events_filepath = os.path.join(OUTPUT_DIR, "lesson_events.csv")
    
    MESSY_FORMATS = [
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ"
    ]
    
    enrollment_id_counter = 1
    payment_id_counter = 1
    event_id_counter = 1
    
    # Target ~150,000 enrollments across 100,000 users (0-3 courses per user)
    courses_count_dist = [0, 1, 2, 3]
    courses_count_probs = [0.13, 0.42, 0.27, 0.18]
    user_course_counts = np.random.choice(courses_count_dist, size=len(users), p=courses_count_probs)
    
    total_events_written = 0
    null_ts_count = 0
    
    with open(events_filepath, "w", newline="", encoding="utf-8", buffering=4*1024*1024) as f_evt:
        evt_writer = csv.writer(f_evt)
        evt_writer.writerow(["event_id", "enrollment_id", "lesson_number", "event_type", "event_timestamp"])
        
        for user_idx, u in enumerate(users):
            n_courses = user_course_counts[user_idx]
            if n_courses == 0:
                continue
                
            selected_courses = random.sample(COURSES, n_courses)
            u_exp = u["experiment_group"]
            u_signup_dt = u["signup_dt"]
            
            for c_info in selected_courses:
                enrollment_id = f"E{enrollment_id_counter:07d}"
                enrollment_id_counter += 1
                
                # Enrollment date within 0 to 25 days after signup
                enroll_offset_days = int(np.random.exponential(scale=3.2))
                enroll_offset_seconds = random.randint(300, 86400)
                enroll_dt = u_signup_dt + datetime.timedelta(days=enroll_offset_days, seconds=enroll_offset_seconds)
                if enroll_dt > END_DATE:
                    enroll_dt = END_DATE - datetime.timedelta(hours=random.randint(1, 48))
                    
                total_lessons = c_info["lessons"]
                
                # A/B test effect: strictly localized to Onboarding & Lesson 1
                if u_exp == "treatment":
                    prob_bounce = 0.10     # 10% bounce before lesson 1
                    prob_drop_l1 = 0.05    # 5% drop during lesson 1
                else:
                    prob_bounce = 0.16     # 16% bounce before lesson 1
                    prob_drop_l1 = 0.08    # 8% drop during lesson 1
                    
                rand_val = random.random()
                
                if rand_val < prob_bounce:
                    # 0 events generated (bounced enrollment)
                    status = "dropped" if (END_DATE - enroll_dt).days > 30 else "active"
                    enrollment_rows.append({
                        "enrollment_id": enrollment_id,
                        "user_id": u["user_id"],
                        "course_id": c_info["course_id"],
                        "course_category": c_info["category"],
                        "enrollment_date": enroll_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "enrollment_status": status
                    })
                    continue
                    
                # Learner engages with lesson events
                curr_dt = enroll_dt + datetime.timedelta(minutes=random.randint(5, 180))
                
                if rand_val < (prob_bounce + prob_drop_l1):
                    # Learner drops out during Lesson 1
                    max_lesson_reached = 1
                    completed_all = False
                else:
                    # Learner successfully passes Lesson 1 and enters core curriculum.
                    # Downstream completion conditional on reaching Lesson 2 is natural curriculum difficulty
                    # (identical across control & treatment - no artificial compounding)
                    prob_complete_conditional = 0.58
                    if random.random() < prob_complete_conditional:
                        max_lesson_reached = total_lessons
                        completed_all = True
                    else:
                        max_lesson_reached = random.randint(1, total_lessons - 1)
                        completed_all = False
                    
                # Helper function to write event with messiness
                def write_event(eid, les_num, etype, dt):
                    nonlocal event_id_counter, total_events_written, null_ts_count
                    eid_str = f"EVT_{event_id_counter:08d}"
                    event_id_counter += 1
                    
                    if null_ts_count < 50 and random.random() < 0.00003:
                        ts_str = ""
                        null_ts_count += 1
                    elif random.random() < 0.001:
                        fmt = random.choice(MESSY_FORMATS)
                        ts_str = dt.strftime(fmt)
                    else:
                        ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        
                    evt_writer.writerow([eid_str, eid, les_num, etype, ts_str])
                    total_events_written += 1

                passed_quiz_count = 0
                failed_quiz_count = 0

                # Generate events up to max_lesson_reached
                for l_num in range(1, max_lesson_reached + 1):
                    is_last_and_dropped = (l_num == max_lesson_reached) and not completed_all
                    
                    # 1. Lesson started
                    write_event(enrollment_id, l_num, "started", curr_dt)
                    
                    # Multi-session study: ~30% chance learner paused and returned to resume
                    if random.random() < 0.30:
                        curr_dt += datetime.timedelta(hours=random.randint(2, 24))
                        write_event(enrollment_id, l_num, "started", curr_dt)
                        
                    # 2. Mid-lesson practice / Quiz 1 (85% of lessons)
                    if random.random() < 0.85:
                        if random.random() < 0.32:
                            curr_dt += datetime.timedelta(minutes=random.randint(8, 20))
                            write_event(enrollment_id, l_num, "quiz_failed", curr_dt)
                            failed_quiz_count += 1
                            
                        if (not is_last_and_dropped) or (random.random() < 0.50):
                            curr_dt += datetime.timedelta(minutes=random.randint(10, 25))
                            write_event(enrollment_id, l_num, "quiz_passed", curr_dt)
                            passed_quiz_count += 1
                            
                    # 3. Lesson End Challenge / Quiz 2 (70% of lessons)
                    if random.random() < 0.70:
                        if random.random() < 0.28:
                            curr_dt += datetime.timedelta(minutes=random.randint(8, 20))
                            write_event(enrollment_id, l_num, "quiz_failed", curr_dt)
                            failed_quiz_count += 1
                            
                        if (not is_last_and_dropped) or (random.random() < 0.40):
                            curr_dt += datetime.timedelta(minutes=random.randint(10, 25))
                            write_event(enrollment_id, l_num, "quiz_passed", curr_dt)
                            passed_quiz_count += 1
                            
                    # 4. Lesson completed
                    if not is_last_and_dropped:
                        curr_dt += datetime.timedelta(minutes=random.randint(5, 20))
                        write_event(enrollment_id, l_num, "completed", curr_dt)
                        
                    # Advance time to next lesson
                    pace_rand = random.random()
                    if pace_rand < 0.70:
                        curr_dt += datetime.timedelta(days=random.randint(1, 4), hours=random.randint(0, 12))
                    elif pace_rand < 0.90:
                        curr_dt += datetime.timedelta(hours=random.randint(2, 6))
                    else:
                        curr_dt += datetime.timedelta(days=random.randint(5, 10))
                        
                # Pre-exam review for completers (reviewing 1-2 lessons)
                if completed_all and random.random() < 0.55:
                    review_lessons = random.sample(range(1, total_lessons + 1), k=random.randint(1, 2))
                    for r_les in review_lessons:
                        curr_dt += datetime.timedelta(days=random.randint(1, 3))
                        write_event(enrollment_id, r_les, "started", curr_dt)
                        if random.random() < 0.65:
                            curr_dt += datetime.timedelta(minutes=random.randint(10, 20))
                            write_event(enrollment_id, r_les, "quiz_passed", curr_dt)
                            passed_quiz_count += 1
                            
                # Determine enrollment status
                if completed_all:
                    status = "completed"
                else:
                    days_inactive = (END_DATE - curr_dt).days
                    status = "dropped" if days_inactive > 30 else "active"
                    
                enrollment_rows.append({
                    "enrollment_id": enrollment_id,
                    "user_id": u["user_id"],
                    "course_id": c_info["course_id"],
                    "course_category": c_info["category"],
                    "enrollment_date": enroll_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "enrollment_status": status
                })
                
                # Payment conversion for completed enrollments
                # Realistic pricing and willingness to pay by discipline and engagement depth
                if completed_all:
                    prob_pay = 0.18 + CATEGORY_BOOST.get(c_info["category"], 0.0)
                    total_quizzes = passed_quiz_count + failed_quiz_count
                    if total_quizzes > 0:
                        pass_rate = passed_quiz_count / total_quizzes
                        if pass_rate >= 0.85:
                            prob_pay += 0.05
                        elif pass_rate >= 0.70:
                            prob_pay += 0.02
                        else:
                            prob_pay -= 0.02
                    if failed_quiz_count == 0:
                        prob_pay += 0.03
                    prob_pay += random.uniform(-0.03, 0.03)
                    prob_pay = max(0.05, min(0.60, prob_pay))

                    if random.random() < prob_pay:
                        pay_id = f"PAY_{payment_id_counter:06d}"
                        payment_id_counter += 1
                        pay_dt = curr_dt + datetime.timedelta(hours=random.randint(1, 72))
                        if pay_dt > END_DATE:
                            pay_dt = END_DATE - datetime.timedelta(hours=random.randint(1, 12))
                            
                        rand_cert = random.random()
                        if rand_cert < 0.03:
                            cert_issued = "Y "  # Realistic messiness for Phase 1 cleaning
                        elif rand_cert < 0.96:
                            cert_issued = "Y"
                        else:
                            cert_issued = "N"

                        payments_rows.append({
                            "payment_id": pay_id,
                            "enrollment_id": enrollment_id,
                            "amount": f"{c_info['price']:.2f}",
                            "payment_date": pay_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "certification_issued": cert_issued
                        })
                    
            if (user_idx + 1) % 20000 == 0:
                print(f"Processed {user_idx + 1:,} users... Total events written: {total_events_written:,}")
                
    print(f"Total lesson events written: {total_events_written:,}")
    return enrollment_rows, payments_rows


def inject_enrollment_duplicates(enrollments, num_duplicates=200):
    print(f"Injecting {num_duplicates} duplicate enrollment rows for messiness...")
    dup_rows = random.choices(enrollments, k=num_duplicates)
    enrollments_with_dups = enrollments + [dict(r) for r in dup_rows]
    random.shuffle(enrollments_with_dups)
    return enrollments_with_dups


def write_csv(filepath, rows, fieldnames):
    print(f"Writing {len(rows):,} rows to {filepath}...")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    start_time = datetime.datetime.now()
    print("=== Starting Synthetic Data Generation ===")
    
    # 1. Users
    users = generate_users(num_users=100_000)
    users_export = [{
        "user_id": u["user_id"],
        "signup_date": u["signup_date"],
        "signup_channel": u["signup_channel"],
        "country": u["country"],
        "age": u["age"],
        "experiment_group": u["experiment_group"]
    } for u in users]
    
    write_csv(
        os.path.join(OUTPUT_DIR, "users.csv"),
        users_export,
        ["user_id", "signup_date", "signup_channel", "country", "age", "experiment_group"]
    )
    
    # 2. Enrollments & Lesson Events & Payments
    enrollments, payments = generate_enrollments_and_events(users)
    
    # 3. Inject enrollment duplicates
    enrollments_with_dups = inject_enrollment_duplicates(enrollments, num_duplicates=200)
    
    write_csv(
        os.path.join(OUTPUT_DIR, "enrollments.csv"),
        enrollments_with_dups,
        ["enrollment_id", "user_id", "course_id", "course_category", "enrollment_date", "enrollment_status"]
    )
    
    # 4. Payments
    write_csv(
        os.path.join(OUTPUT_DIR, "payments.csv"),
        payments,
        ["payment_id", "enrollment_id", "amount", "payment_date", "certification_issued"]
    )
    
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print(f"\n=== Synthetic Data Generation Complete in {elapsed:.2f}s! ===")
    print(f"Users: {len(users_export):,} rows")
    print(f"Enrollments: {len(enrollments_with_dups):,} rows (including 200 duplicates)")
    print(f"Payments: {len(payments):,} rows")


if __name__ == "__main__":
    main()
