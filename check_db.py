from database import get_db
import models
from sqlalchemy import func, text

db = next(get_db())

try:
    print("1. Checking User table...")
    count = db.query(models.User).count()
    print(f"User count: {count}")

    print("2. Checking Policy table...")
    count = db.query(models.Policy).count()
    print(f"Policy count: {count}")

    print("3. Checking UserAction table...")
    # This will fail if table doesn't exist
    count = db.query(models.UserAction).count()
    print(f"UserAction count: {count}")

    print("4. Testing Hot Policies Query...")
    hot_policies_data = db.query(
        models.UserAction.policy_id, 
        func.count(models.UserAction.id).label("count")
    ).group_by(models.UserAction.policy_id).order_by(func.count(models.UserAction.id).desc()).limit(5).all()
    print(f"Hot policies data: {hot_policies_data}")

    print("5. Testing Regional Query...")
    user_regions = db.query(models.User.region, func.count(models.User.id)).group_by(models.User.region).all()
    print(f"User regions: {user_regions}")

    print("All checks passed!")

except Exception as e:
    print(f"ERROR: {e}")
