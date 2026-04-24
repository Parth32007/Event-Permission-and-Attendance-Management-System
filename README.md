# College Event Management System (CEMS)

A premium, full-featured web application for managing college events, permissions, and student applications. Built with a "Dark Academic" aesthetic, this portal streamlines the workflow between Students, Faculty, and Event Coordinators.

---

## 🌟 Project Overview

CEMS is designed to automate the process of obtaining faculty permission for college events. It replaces traditional paper-based systems with a digital workflow where students can apply for permissions, faculty can review them in real-time, and event coordinators can oversee the entire process.

### 🎭 User Roles

1.  **👨‍🎓 Student**: Discovers upcoming events, submits permission requests to specific faculty members, and tracks application status.
2.  **👨‍🏫 Faculty (Teacher)**: Receives and reviews permission requests from students. Can approve or reject applications with a single click.
3.  **👔 Event Coordinator**: Creates and manages the events calendar. Oversees approved student lists and event analytics.

---

## ✨ Key Features

### 💎 Premium UI/UX
- **Dark Academic Aesthetic**: A cohesive, high-end design using curated color palettes, glassmorphism, and smooth transitions.
- **Responsive Layout**: Fully functional on desktops, tablets, and mobile devices.
- **Micro-animations**: Subtle hover effects and loading states for a polished feel.

### 🔄 Smart Workflow
- **Multi-Faculty Logic**: Students can assign multiple teachers to a single application.
- **Real-Time Sync**: Dashboards auto-refresh to show the latest decisions and new events without page reloads.
- **Approval Lock**: Prevents redundant applications once a student has been approved for an event.
- **Re-application System**: Allows students to re-apply if their previous request was rejected.

### 🧹 Automated Maintenance
- **Event Expiry System**: Events automatically disappear from the student portal once they end (with a 2-minute buffer).
- **Intelligent Cleanup**: Automatically deletes application records once they are both acknowledged by the student and the event has expired/been deleted.

---

## 🛠️ Tech Stack

- **Backend**: [Python](https://www.python.org/) with [Flask](https://flask.palletsprojects.com/)
- **Database**: Flat-file [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) and [JSON](https://www.json.org/) (managed via [Pandas](https://pandas.pydata.org/))
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+)
- **Icons**: [Font Awesome 6](https://fontawesome.com/)
- **Typography**: Google Fonts (Inter, Outfit, Roboto)

---

## 📂 Project Structure

```text
WEB_DESIGNING-updated/
├── app.py                  # Main Flask application and API endpoints
├── database/               # CSV/JSON storage files
│   ├── reg.csv             # User registration data
│   ├── applications.csv    # Student permission requests
│   └── events.json         # Event coordinator data
├── static/                 
│   ├── style.css           # Global design system and component styles
│   └── images/             # UI assets
├── templates/              # HTML Templates
│   ├── index.html          # Login & Registration portal
│   ├── student-dashboard-final.html
│   ├── teacher_portal.html
│   └── event_coordinator_portal.html
├── flask_env/              # Python virtual environment
└── README.md               # You are here!
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd WEB_DESIGNING-updated
   ```

2. **Set up the virtual environment**:
   ```bash
   python -m venv flask_env
   flask_env\Scripts\activate  # On Windows
   source flask_env/bin/activate # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install flask pandas
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the portal**:
   Open your browser and navigate to `http://127.0.0.1:5000`

---

## 📝 Usage Guide

### For Students
- **Login/Register**: Create an account as a "Student".
- **Browse Events**: View all active events on the home tab.
- **Apply**: Select an event, enter faculty emails, and write your message.
- **Track**: Monitor the "Applications" section. Once a decision is made, click "Acknowledge" to clear the notification.

### For Faculty
- **Review**: Log in to see a list of applications assigned to you.
- **Decide**: Use the "Approve" or "Reject" buttons. The student is notified instantly.

### For Event Coordinators
- **Create**: Use the "Event Creation" form to add new events (dates must be in the future).
- **Manage**: Edit or delete events from the "Published Events" grid.
- **Monitor**: Expand any event to see the list of **Approved Students** only.

---

## 🔒 Security & Validation
- **Numeric Passwords**: The system enforces numeric-only passwords for simplicity and consistency.
- **Role-Based Access**: Redirects users to their specific dashboards based on their role stored in the database.
- **Input Validation**: Prevents past-dated events and enforces mandatory fields across all forms.

---

*Developed with ❤️ for College Event Management.*
