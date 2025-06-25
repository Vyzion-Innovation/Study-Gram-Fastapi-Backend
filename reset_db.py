# reset_db.py

from app.utils.db_cleaner import clear_all_data

if __name__ == "__main__":
    clear_all_data()
    print("✅ All data cleared successfully.")
