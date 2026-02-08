import requests
import random
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

USERS = ["user_1", "user_2", "user_fraud"]
LOCATIONS = ["Bangalore", "Mumbai", "Delhi"]
MERCHANTS = ["Amazon", "Flipkart", "Zomato", "Swiggy"]

def generate_transaction(user_id: str):
    """Generate realistic + risky transactions"""

    if user_id == "user_fraud":
        amount = random.choice([7000, 9000, 12000])  # risky
        location = random.choice(LOCATIONS)
    else:
        amount = random.randint(100, 3000)
        location = "Bangalore"

    payload = {
        "user_id": user_id,
        "amount": amount,
        "merchant": random.choice(MERCHANTS),
        "category": "E_COMMERCE",
        "location": location,
        "device_id": f"device_{random.randint(1,3)}"
    }

    res = requests.post(f"{BASE_URL}/transaction/", json=payload)
    return res.json()


def assess_risk(transaction_id: str):
    res = requests.get(f"{BASE_URL}/risk/{transaction_id}")
    return res.json()


def run_simulation(rounds=10):
    print("\n🚀 Starting SentinelPay Traffic Simulation\n")

    for i in range(rounds):
        user = random.choice(USERS)
        txn = generate_transaction(user)

        txn_id = txn["transaction_id"]
        risk = assess_risk(txn_id)

        print(f"🧾 TXN {i+1}")
        print(f"User: {user}")
        print(f"Risk Score: {risk['risk_score']}")
        print(f"Risk Level: {risk['risk_level']}")
        print(f"Reasons: {risk['reasons']}")
        print("-" * 50)

        time.sleep(1)


if __name__ == "__main__":
    run_simulation(rounds=15)
