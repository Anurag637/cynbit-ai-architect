"""
Revio 2.0 Benchmark Data Generator
Generates realistic multi-location customer review datasets with ground truth attributes.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from src.config import DEFAULT_BRANCHES

# Seed for reproducible benchmark results
random.seed(42)

SEED_REVIEWS: List[Dict] = [
    # Critical Crisis Reviews
    {
        "review_text": "EMERGENCY: Three of us had dinner here last night and woke up with severe food poisoning and vomiting. My brother is admitted to the hospital right now. When I called the store manager, he was completely rude and dismissive. We are reporting this to the food safety authority and filing a police complaint!",
        "star_rating": 1,
        "platform": "Google Maps",
        "branch_index": 0,
        "customer_name": "Rohan Malhotra"
    },
    {
        "review_text": "Absolute fraud! Checked my credit card statement today and discovered an unauthorized charge of Rs. 4,500 that was never on my receipt. The cashier refused to give me a printed invoice. If this is not refunded in 24 hours, my lawyer is taking this to consumer court.",
        "star_rating": 1,
        "platform": "Yelp",
        "branch_index": 1,
        "customer_name": "Meera Sen"
    },
    {
        "review_text": "Horrifying experience with the floor supervisor who used derogatory and abusive language towards my elderly mother when we asked why our order took 55 minutes. We felt completely unsafe and harassed. Never stepping foot here again.",
        "star_rating": 1,
        "platform": "Google Maps",
        "branch_index": 2,
        "customer_name": "Vikramaditya Rathore"
    },
    {
        "review_text": "Found a dead cockroach inside the salad bowl! The waiter took the plate away silently and tried to bring another without even apologizing. Gross hygiene violation. Taking photos to Twitter and local municipal health inspectors.",
        "star_rating": 1,
        "platform": "Zomato",
        "branch_index": 3,
        "customer_name": "Pooja Hegde"
    },

    # High Negative Reviews (Operational Churn Drivers)
    {
        "review_text": "Terrible service. Ordered at 8:15 PM and food arrived stone cold at 9:30 PM. The pasta was raw and completely tasteless. The staff avoided eye contact and ignored our calls. Completely ruined our anniversary dinner.",
        "star_rating": 1,
        "platform": "Google Maps",
        "branch_index": 0,
        "customer_name": "Ananya Sharma"
    },
    {
        "review_text": "Extremely overpriced for the tiny portions they serve. Charging 650 bucks for a basic sandwich that was soggy and stale. Also noticed an extra 15% hidden service fee on the bill that was not mentioned on the menu.",
        "star_rating": 2,
        "platform": "TripAdvisor",
        "branch_index": 1,
        "customer_name": "Karan Mehra"
    },
    {
        "review_text": "Washrooms were completely unhygienic with overflowing water and no soap. The AC was leaking right over our table. Management clearly does not maintain this facility.",
        "star_rating": 2,
        "platform": "Google Maps",
        "branch_index": 4,
        "customer_name": "Tanvi Gupta"
    },
    {
        "review_text": "The delivery took 80 minutes to arrive 3 kilometers away. Food was spilled all over the plastic bag and ice cream was melted water. Rider blamed the kitchen delay.",
        "star_rating": 1,
        "platform": "Zomato",
        "branch_index": 2,
        "customer_name": "Aman Verma"
    },

    # Mixed Reviews
    {
        "review_text": "The food quality and flavours were actually quite delicious, especially the paneer tikka. However, the waiting time of 45 minutes on a Tuesday night was ridiculous. Need better staff training.",
        "star_rating": 3,
        "platform": "Google Maps",
        "branch_index": 0,
        "customer_name": "Siddharth Joshi"
    },
    {
        "review_text": "Great ambience and beautiful interior lighting. But the prices have been hiked by 30% recently while portion sizes shrank. Service was polite but very slow.",
        "star_rating": 3,
        "platform": "Google Maps",
        "branch_index": 3,
        "customer_name": "Neha Kapoor"
    },
    {
        "review_text": "Staff was warm and attentive, but the billing system crashed when we tried to pay via UPI, making us wait 20 minutes just to settle a small bill.",
        "star_rating": 3,
        "platform": "Yelp",
        "branch_index": 1,
        "customer_name": "Deepak Singhal"
    },

    # High Positive Reviews (Brand Advocates)
    {
        "review_text": "Exceptional dining experience! The staff greeted us warmly, our food arrived within 12 minutes hot and bursting with authentic flavor. Special thanks to Rohit at the front desk for great hospitality. 10/10!",
        "star_rating": 5,
        "platform": "Google Maps",
        "branch_index": 0,
        "customer_name": "Aditi Roy"
    },
    {
        "review_text": "Hands down the best branch in Jaipur. Impeccably clean, pristine aesthetic, and the truffle risotto was world-class. Worth every single penny.",
        "star_rating": 5,
        "platform": "TripAdvisor",
        "branch_index": 1,
        "customer_name": "Varun Chawla"
    },
    {
        "review_text": "Super fast turnaround time during peak lunchtime. Professional staff, crisp digital billing with zero fuss, and high food standards. We visit twice every week.",
        "star_rating": 5,
        "platform": "Google Maps",
        "branch_index": 2,
        "customer_name": "Priyanka Nair"
    },
    {
        "review_text": "Stunning rooftop view, relaxing music, and delicious signature drinks. The manager personally checked on every table to make sure we were comfortable. Highly recommended!",
        "star_rating": 5,
        "platform": "Google Maps",
        "branch_index": 3,
        "customer_name": "Rahul Deshmukh"
    },
    {
        "review_text": "Outstanding hygiene protocols and spotless presentation. Portions are generous and ingredients feel farm-fresh. A top-tier experience in Mumbai.",
        "star_rating": 5,
        "platform": "Zomato",
        "branch_index": 4,
        "customer_name": "Sanya Merchant"
    }
]


def generate_benchmark_dataset(count: int = 50) -> List[Dict]:
    """
    Generates an enterprise-scale synthetic dataset combining seed reviews and augmented variants.
    """
    dataset: List[Dict] = []
    base_time = datetime.now() - timedelta(days=30)

    # 1. Include high-signal seed reviews
    for idx, item in enumerate(SEED_REVIEWS):
        branch = DEFAULT_BRANCHES[item["branch_index"] % len(DEFAULT_BRANCHES)]
        review_date = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59)
        )
        dataset.append({
            "id": f"REV-{1000 + idx}",
            "customer_name": item["customer_name"],
            "branch_id": branch["id"],
            "branch_name": branch["name"],
            "branch_city": branch["city"],
            "platform": item["platform"],
            "star_rating": item["star_rating"],
            "timestamp": review_date.isoformat(),
            "review_text": item["review_text"],
            "is_seed": True
        })

    # 2. Augment to target count with diverse variations
    additional_templates = [
        ("The {aspect} was completely unacceptable. Waited {min} mins and got disappointed.", 1, "Speed & Turnaround Time"),
        ("Love coming here! The {aspect} is always consistent, friendly and reliable.", 5, "Customer Service"),
        ("Decent experience overall. {aspect} was great, but the billing was a bit confusing.", 3, "Billing & Transactions"),
        ("Too noisy and tables were not cleaned properly. Needs urgent attention from management.", 2, "Cleanliness & Ambience"),
        ("Incredible value for money. Fresh ingredients, polite team, and seamless checkout.", 5, "Pricing & Value"),
        ("Food was okay, but the AC was not working and staff took ages to take our order.", 2, "Customer Service"),
        ("Quickest lunch spot in the tech park. Courteous staff and great taste.", 5, "Speed & Turnaround Time"),
        ("Overcharged on the bill by Rs. {amt}. Manager was unwilling to rectify. Very disappointing.", 1, "Billing & Transactions"),
        ("Outstanding hospitality by the team! Clean environment and mouth-watering meals.", 5, "Cleanliness & Ambience"),
        ("Average taste, high prices. Don't think it's worth the hype.", 3, "Pricing & Value")
    ]

    names = ["Kavita Shah", "Arjun Reddy", "Sunil Gavaskar", "Ritika Sen", "Manish Paul", "Zoya Akhtar", "Harsh Vardhan", "Smriti Mandhana", "Gaurav Taneja", "Natasha Poonawalla"]
    platforms = ["Google Maps", "Yelp", "Zomato", "TripAdvisor"]

    while len(dataset) < count:
        tmpl, rating, aspect = random.choice(additional_templates)
        branch = random.choice(DEFAULT_BRANCHES)
        text = tmpl.format(
            aspect=aspect.lower(),
            min=random.randint(25, 65),
            amt=random.randint(200, 1200)
        )
        review_date = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59)
        )
        dataset.append({
            "id": f"REV-{1000 + len(dataset)}",
            "customer_name": random.choice(names),
            "branch_id": branch["id"],
            "branch_name": branch["name"],
            "branch_city": branch["city"],
            "platform": random.choice(platforms),
            "star_rating": rating,
            "timestamp": review_date.isoformat(),
            "review_text": text,
            "is_seed": False
        })

    # Sort chronologically (newest first)
    dataset.sort(key=lambda x: x["timestamp"], reverse=True)
    return dataset


def save_dataset_to_file(filepath: Path = Path("data/sample_reviews.json")) -> List[Dict]:
    """Generates and saves the benchmark dataset."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = generate_benchmark_dataset(count=50)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


def load_dataset(filepath: Path = Path("data/sample_reviews.json")) -> List[Dict]:
    """Loads dataset from disk or generates if missing."""
    if not filepath.exists():
        return save_dataset_to_file(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    generated = save_dataset_to_file()
    print(f"Successfully generated {len(generated)} benchmark reviews.")
