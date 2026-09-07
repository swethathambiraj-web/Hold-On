# Hold On - Modern Social Media Platform

**Hold On** is a photo and video sharing social media web application built with **Django 5**, **Django REST Framework**, and a sleek modern Instagram-style UI (dark and light modes, glassmorphism, Bootstrap 5, and vanilla JavaScript).

---

## ✨ Features

1. **User Accounts & Authentication**
   - Custom `User` model extending `AbstractUser` with bio, profile picture, website link, and private account support.
   - Signup, Login, Logout, Profile editing.
   - Follow & Unfollow system with follow requests approval workflow for private accounts.
   - Followers and Following lists.

2. **Posts & Media Sharing**
   - Multi-photo / carousel uploads with order tracking.
   - Video media support.
   - Caption with automatic hashtag (`#tag`) extraction and tagging.
   - Location tagging.
   - Post detail view, Edit, and Delete (with author authorization).

3. **Interactions**
   - Real-time AJAX Likes with double-tap heart animations.
   - Bookmark / Save posts to a personal collection tab on your profile.
   - AJAX Comments with threaded replies and comment deletion.

4. **Stories (24-Hour Ephemeral Posts)**
   - 24-hour expiring photo stories.
   - Interactive story viewer modal with automated progress timers, next/previous slide controls, and view tracking.

5. **Home Feed & Discovery**
   - Dynamic home feed showing posts from followed users + own posts, sorted newest first.
   - Stories tray at top of the feed with unseen/seen gradient rings.
   - Explore page featuring trending public posts and popular hashtags.
   - Live debounced search for users and hashtags.

6. **Notifications**
   - Instant in-app alerts for likes, comments, follows, follow requests, and messages.
   - Unread badges across sidebar and mobile navigation.

7. **Direct Messaging (1-to-1 Chat)**
   - Inbox with conversation previews and unread indicators.
   - Chat thread with live message polling, image attachments, and instant AJAX delivery.

8. **RESTful API**
   - Complete Django REST Framework API endpoints under `/api/v1/` for:
     - `/api/v1/users/`
     - `/api/v1/posts/`
     - `/api/v1/stories/`
     - `/api/v1/notifications/`
     - `/api/v1/conversations/`
     - `/api/v1/feed/` & `/api/v1/explore/`

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13, Django 5.2, Django REST Framework 3.18
- **Database**: SQLite (default for development) / PostgreSQL ready
- **Frontend**: Django Templates, Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript (Fetch API)
- **Image Processing**: Pillow 12.3
- **Configuration**: python-decouple (.env management)

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` (already configured with local dev defaults):
```bash
cp .env.example .env
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Demo Data (Optional but Recommended)
Populate the database with sample users, multi-photo posts, stories, comments, likes, and messages:
```bash
python manage.py seed_demo_data
```

**Demo Accounts (Password for all is `password123`):**
- `alex_wanderer` (Photographer & adventurer)
- `maya_design` (3D Artist & UI/UX Designer)
- `chef_marco` (Artisanal pasta chef)
- `sophia_code` (AI research engineer)
- `leo_vibes` (Private account demonstration)

### 6. Run the Development Server
```bash
python manage.py runserver 8000
```
Open your browser and visit: `http://127.0.0.1:8000/`

---

## 🧪 Running Automated Unit Tests

```bash
python manage.py test
```

---

## 📂 Project Architecture

```
blue_collar/
├── hold_on/                 # Main Django project settings & root URLs
├── accounts/                # Custom User, Profile, Follow & Auth system
├── posts/                   # Posts, Multi-Image Carousels, Likes, Comments, Hashtags
├── feed/                    # Home Feed, Explore, Search
├── stories/                 # 24-Hour Stories & View tracking
├── notifications/           # Notifications & Context processors
├── messaging/               # 1-to-1 Direct Messaging
├── static/                  # CSS (Dark/Light mode) & JavaScript
├── templates/               # Django HTML templates
├── media/                   # User uploaded images & media
├── requirements.txt         # Project dependencies
├── .env.example             # Environment configuration template
└── README.md
```
