# StudyGram 🎓

**StudyGram** is a student management platform built using **FastAPI** and **PostgreSQL**, designed to efficiently manage student records, mock tests, attendance, transactions, and fee reports.

---

## 🚀 Features

- ✅ **Student Management**
  - Add, update, list, and delete student records
  - Filter students by type (PTE, Demo, Regular, IELTS)
  - Track admission details and batch fees

- 🧪 **Mock Test Management**
  - Add test results for speaking, writing, listening, reading
  - Auto-calculates overall scores
  - New or existing student selection with validation

- 📅 **Attendance Tracking**
  - Record and view daily student attendance
  - Filter by date and student
  - Monthly attendance summaries

- 💰 **Transaction & Fee Reports**
  - Add fee payments per student with specific month
  - View pending fees per student for last month
  - Summarized transaction history

- 📊 **Reporting APIs**
  - Students with **pending fees for the last month**
  - Overall earnings by month
  - Payment summary report

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Auth:** JWT-based Authentication
- **Pagination:** FastAPI Pagination
- **Validation:** Pydantic

---

## 📂 Project Structure


---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/studygram.git
   cd studygram
## Setup Instructions

### 1. Create a virtual environment

```bash
python -m venv venv

source .venv/bin/activate

pip install -r requirements.txt

##run migrations 

alembic upgrade head

## to run 
uvicorn app.main:app --reload

## to run on server continously

nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 & 
setup github action to auto deploy