# Academic Relay

> A centralized academic resource platform that connects students and faculty through a single, organized system.

Academic Relay is a web-based academic resource management platform designed to bridge the gap between faculty and students by bringing essential academic information and resources together in one place.

The project was built from my own experience as a student, with the goal of making commonly needed academic resources easier to access, manage, and share.

---

## 🌐 Live Demo

**[Visit Academic Relay](https://academic-relay.onrender.com)**

> The application is deployed online as a working prototype.

---

## 🎯 Problem

Academic information is often distributed across different platforms, groups, messages, and physical notices. Students may have to search through multiple sources to find something as simple as a timetable, assignment, circular, study material, or marks update.

Academic Relay aims to provide a centralized platform where students can access these resources while faculty can manage and share academic information more efficiently.

---

## ✨ Features

### 🔐 Authentication

- Student and faculty login
- Secure password hashing
- Password reset through email
- Secure, time-limited password reset links
- Role-based access to academic functionality

### 🎓 Student Features

- Access academic resources from a centralized dashboard
- View circulars and announcements
- Access timetables
- View assignments
- Access notes and study materials
- View marks and academic information
- Access previous-year papers and other shared resources

### 👨‍🏫 Faculty Features

- Manage academic resources
- Upload and share study materials
- Manage assignments
- Publish academic information
- Share resources with students

### 📚 Academic Resource Management

Academic Relay brings different types of academic resources together, including:

- Circulars
- Timetables
- Assignments
- Notes & study materials
- Marks

---

## 🛠️ Tech Stack

### Backend

- Python
- Flask

### Frontend

- HTML5
- CSS3
- JavaScript

### Database

- PostgreSQL
- Supabase

### Storage & Services

- Supabase Storage
- Mailjet API

### Deployment

- Render

---

## 🏗️ Architecture

At a high level, Academic Relay follows a client-server architecture:

```text
                    ┌─────────────────────┐
                    │      Students       │
                    │      & Faculty      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Academic Relay    │
                    │      (Flask)        │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │ PostgreSQL │ │  Supabase  │ │  Mailjet   │
          │  Database  │ │   Storage  │ │    API     │
          └────────────┘ └────────────┘ └────────────┘
```

---

## 🔑 Password Reset Flow

Academic Relay implements a secure password recovery workflow:

```text
Forgot Password
       │
       ▼
Enter Email Address
       │
       ▼
Generate Secure Token
       │
       ▼
Store Token Hash
       │
       ▼
Send Reset Link via Mailjet
       │
       ▼
User Opens Reset Link
       │
       ▼
Create New Password
       │
       ▼
Password Updated
       │
       ▼
Login with New Password
```

Reset tokens are:

- Cryptographically generated
- Stored as SHA-256 hashes
- Time-limited
- Single-use
- Invalidated after successful password reset

---

## 🔒 Security

The project includes several security-focused implementations:

- Passwords are stored using secure password hashing.
- Password reset tokens are generated using cryptographically secure randomness.
- Only token hashes are stored in the database.
- Reset links expire after a limited period.
- Reset tokens can only be used once.
- Password reset responses avoid revealing whether an email address belongs to an account.
- Sensitive credentials are stored using environment variables rather than being committed to the repository.

---

## 🚀 Deployment

Academic Relay is deployed using Render with:

- Flask application server
- PostgreSQL/Supabase database
- Supabase Storage for file management
- Mailjet HTTPS API for transactional emails

Production configuration and sensitive credentials are managed through environment variables.

---

## 📌 Project Status

**Working Prototype — Deployed**

The current version provides the core academic resource management functionality along with authentication and password recovery.

The project is primarily developed as a practical academic and portfolio project and can be extended with additional features over time.

---

## 💡 Why I Built This

Academic Relay started from a simple observation: students often have to look across multiple places to find academic information they need.

Instead of treating each resource separately, I wanted to build a single platform that could bring these resources together and make them easier to access.

Building Academic Relay also gave me practical experience working with:

- Web application development
- Backend development with Flask
- Relational databases
- Authentication
- File storage
- REST APIs
- Cloud deployment
- Environment configuration
- Building and debugging a real-world application

---

## 👨‍💻 Author

**Syed Rizwan**

Computer Science Engineering Student  
Chaitanya Bharathi Institute of Technology (CBIT)

Interested in:

Data Science • Artificial Intelligence • Analytics • Software Development

---

## ⭐ Acknowledgement

Academic Relay is a personal project developed as part of my journey of learning software development and building practical solutions to real-world problems.
