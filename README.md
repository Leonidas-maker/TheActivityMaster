# TheActivityMaster

Welcome to the **TheActivityMaster** repository! This project focuses on creating a versatile and user-friendly mobile application tailored for dance schools and clubs. It is designed to streamline daily operations, from course bookings and member management to event planning and detailed analytics.

---

## 📋 Features

### Core Functionalities

- **Course Management**: Create, update, and manage courses with detailed information such as schedules, trainers, available spots, and skill levels.
- **Online Booking System**: Real-time course bookings with automatic confirmations, waitlist management, and availability tracking.
- **Member Management**: Comprehensive profile handling including membership details, payment history, and personal data management.
- **Event Planning**: Organize workshops, special events, and manage registrations automatically.
- **Mobile Optimization**: A fully responsive native mobile app featuring push notifications and offline support.
- **Analytics & Reports**: In-depth insights into attendance, revenue, and course performance metrics.

### Start Script Functionality

In addition to manual deployment steps, **TheActivityMaster** includes a powerful start script that automates several critical tasks:

- **Pre-Installation Checks**:  
  - Installs required Python packages (e.g., `rich`, `faker`, `requests`, `pandas`, `openpyxl`).
  - Verifies that necessary tools such as Docker, Node.js, and npm are installed.

- **Deployment Modes**:  
  The script offers multiple deployment modes to fit your development needs:
  - **Full Deployment**:  
    - Starts the Docker stack (pulls images, builds, and runs containers).
    - Waits until the backend is ready.
    - Creates test data (users, clubs, programs, memberships, and bookings) to simulate a real environment.
    - Optionally restarts the Docker stack after test data has been set up.
  - **Start Services Only**:  
    - Launches the backend and frontend services without creating new test data.
  - **Prepare Environment**:  
    - Sets up the test environment (including test data creation) and then stops the Docker containers, allowing you to inspect the generated data before fully launching the app.

- **Additional Functionalities**:  
  - **Log Streaming**: Automatically streams backend logs in a separate terminal window for real-time monitoring.
  - **Frontend Launch**: Opens the Expo-based frontend in a new terminal on your chosen platform (iOS or Android).
  - **Cleanup Option**: Provides a Docker cleanup routine to remove containers, images, and volumes, ensuring a fresh environment on demand.
  - **Cross-Platform Support**: The script is designed to work on Windows, macOS, and Linux with appropriate terminal commands.

By using the start script, you can easily start, monitor, and manage your entire development environment with one command—no need for separate terminal sessions for each service!

⚠️ Note: If you encounter error messages when running the startup script, please execute it again. Due to the multithreaded deployment of the test data, the backend's stdout may not have fully flushed yet, causing the script to miss essential backend authentication data. Re-running the script typically resolves this issue.

---

## 🛠️ Tech Stack

### Mobile

- **Framework**: React Native (Expo)
  
### Backend

- **Framework**: FastAPI
- **Database**: MariaDB (with Async SQLAlchemy)  
- **Cache**: Redis

---

## 📈 Objectives

1. Address the unique operational requirements of dance schools and clubs.
2. Enhance efficiency and user experience with streamlined course, member, and event management.
3. Maintain high standards for data security and compliance (e.g., GDPR).

---

## 📂 Folder Structure

```
project-root/
├── client/             # Mobile application (React Native)
├── server/             # Backend implementation (FastAPI, database models, etc.)
├── misc/               # Miscellaneous files and documentation
├── start_script.py     # Start script to setup, run, and manage the environment
└── README.md           # Project overview (this file)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **MariaDB**
- **Docker**
- **Node.js & npm**

### Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://gitlab.com/themastercollection/TheActivityMaster.git
   ```
2. **Backend Setup:**
   - Navigate to the `server` directory:
     ```bash
     cd server
     ```
   - Create a virtual environment and activate it:
     ```bash
     python -m venv env
     source env/bin/activate  # For Windows: .\env\Scripts\activate
     ```
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Configure your database connection in the `.env` file.
   - Run the backend:
     ```bash
     uvicorn main:app --reload
     ```

3. **Frontend Setup:**
   - Navigate to the `client` directory:
     ```bash
     cd client
     ```
   - Install dependencies and start the development server:
     ```bash
     npm install
     npm npx expo run:{ios, android}
     ```

---

## 🚀 Using the Start Script

For a streamlined development process, you can start the entire environment using the provided start script. This script will:

1. **Install Required Dependencies**:  
   Automatically install Python packages and verify that Docker, Node.js, and npm are available.

2. **Check Prerequisites & Clean Up**:  
   Run pre-installation checks and offer an option to perform a Docker cleanup if needed.

3. **Deploy the Backend & Frontend**:  
   Start the Docker stack for your backend services, wait until the backend is fully operational, and then launch the Expo-based mobile app in a new terminal window.

4. **Create Test Data (Optional)**:  
   In "full" or "prepare" deployment modes, the script populates your environment with test users, clubs, programs, memberships, and bookings for simulation and testing purposes.

5. **Real-Time Log Streaming**:  
   Open a separate terminal window to stream backend logs for live monitoring during development.

6. **User-Friendly Command Prompts**:  
   Follow interactive prompts to choose the deployment mode and your target Expo platform (iOS or Android).

To run the start script, simply navigate to the project root and execute:

```bash
./start_script.py
```

Follow the on-screen prompts to select your desired deployment options.

---

## 🧑‍💻 Contributors

- **Andreas Schütz**: Backend Developer (Python, FastAPI, MariaDB)
- **Leon Sylvester**: Frontend Developer (React Native, NativeWind)

---

## 📄 License

This project is licensed under a modified MIT License. Commercial use of unmodified or minimally modified copies is prohibited without prior written permission. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute and provide feedback to help improve this application further! Happy coding! 🚀