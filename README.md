# TheActivityMaster

Welcome to the **TheActivityMaster** repository! This project focuses on creating a versatile and user-friendly mobile application tailored for dance schools and clubs. It aims to streamline daily operations, from course bookings to member management.

---

## 📋 **Features**

### Core Functionalities:

- **Course Management**: Create and manage courses with detailed information (e.g., schedule, trainer, available spots, skill levels).
- **Online Booking System**: Real-time course booking with automated confirmations and availability tracking.
- **Member Management**: Profile management, membership tracking, and payment history.
- **Event Planning**: Organize workshops, special events, and automate registrations.
- **Mobile Optimization**: A native mobile app with features like push notifications.
- **Analytics & Reports**: Insights into attendance, course statistics, and revenue.

---

## 🛠️ **Tech Stack**

### Mobile:

- **Framework**: React Native
- **Backend**: FastAPI
- **Database**: MariaDB with Async SQLAlchemy, Redis (as cache database)

---

## 📈 **Objectives**

1. Address the unique requirements of dance schools and clubs.
2. Enhance operational efficiency through automation.
3. Ensure compliance with data protection standards (e.g., GDPR).

---

## 📂 **Folder Structure**

```
project-root/
├── client/             # Mobile application code (React Native)
├── server/             # Backend implementation (FastAPI, database models, etc.)
├── misc/               # Miscellaneous files and documentation
└── README.md           # Project overview (this file)
```

---

## 🚀 **Getting Started**

### Prerequisites:

- **Python 3.10+**
- **MariaDB**
- **Node.js**

### Steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/club-management-app.git
   ```
2. Navigate to the backend directory and set up the environment:
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate  # For Windows: .\env\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure the database connection in `.env`.
4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```
5. Navigate to the mobile directory to start the mobile development server.
6. Install dependencies and run the app:
   ```bash
   cd mobile
   npm install
   npm start
   ```

---

## 🧑‍💻 **Contributors**

- **Andreas Schütz**: Backend Developer (Python, FastAPI, MariaDB)
- **Leon Sylvester**: Frontend Developer (React Native, NativeWind)

---

## 📄 **License**
This project is licensed under a modified MIT License. Commercial use of unmodified or minimally modified copies is prohibited without prior written permission. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute and provide feedback to make this app even better! 🚀
