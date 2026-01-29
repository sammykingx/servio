# 🧰 Servio

> A modern platform that connects **local service providers** (e.g., tailors, event planners, makeup artists, laundry services) to **residents** who need their services — fast, easy, and in one place.

![servio app](./docs/images/servio-app.jpg)

Servio allows users to **plan events and projects** by selecting service categories they need, setting budgets, and receiving offers from relevant service providers.  
Providers can **accept, decline, or renegotiate offers**, making it easy to collaborate without manual sourcing.

**Servio is built with a mission**
> To make local talent more discoverable, trusted, and accessible — one booking at a time.
---

## 📚 Table of Contents

- [🧰 Servio](#-servio)
  - [📚 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [🌍 Roadmap](#-roadmap)
  - [🧑‍💻 Tech Stack](#-tech-stack)
  - [🧭 Core Concepts](#-core-concepts)
    - [👤 Users \& Providers](#-users--providers)
    - [🏢 Business Profiles](#-business-profiles)
    - [🧭 Availability](#-availability)
    - [🏡 Unified Address Model](#-unified-address-model)
    - [📝 Event Creation \& Offer Flow](#-event-creation--offer-flow)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Environment Setup](#environment-setup)
    - [Database Migration](#database-migration)
    - [Frontend Setup](#frontend-setup)
  - [🧱 Contributing](#-contributing)
  - [🧩 License](#-license)
  - [❤️ Acknowledgements](#️-acknowledgements)

---

## ✨ Features

- 🔐 **Authentication & Profiles** — secure account system with support for both users and providers.  
- 🏢 **Business Profiles** — service providers can register their businesses, set availability, and offer services.  
- 🗓️ **Smart Booking Flow** — users fill out event/service requirements, and providers are notified in real time.  
- 💬 **Offer System** — providers can accept, decline, or renegotiate offers.  
- 📍 **Unified Address Model** — supports both personal and business addresses with geolocation support.  
- 🕒 **Flexible Availability** — providers can set their working hours for each day of the week.  
- 🧾 **Event Planning** — users can create multi-service events (e.g., catering, photography, laundry) in a single workflow.  
- 💳 **Payment Integration** *(planned)* — secure payment gateway for deposits and settlements.  
- 📊 **Admin Dashboard** — powerful Django admin to manage users, services, and bookings.  

---

## 🏗️ Architecture

Servio is structured as a **modular Django monolith** — logically separated into multiple apps, each responsible for a specific domain.

- **Django backend**: Handles business logic, authentication, and data management.  
- **Tailwind CSS frontend**: For clean, modern, responsive UI.  
- **HTMX (optional)**: Enables lightweight interactivity without full SPA overhead.  
- **PostgreSQL**: Primary database.  


## 🌍 Roadmap

| Phase         | Features                                      | Status            |
|---------------|-----------------------------------------------|-------------------|
| MVP 1         | Core accounts, projects, Escrow, offers               | ✅ In Progress    |
| MVP 2         | Booking flow, services integration             | 🔄 Planned        |
| MVP 3         | Reviews, notifications, chat                  | 🔄 Planned        |
| MVP 4         | Business Mode & analytics                | 🔄 Planned        |


---

## 🧑‍💻 Tech Stack

| Layer            | Technology                                      |
|-------------------|-----------------------------------------------|
| Backend           | [Django](https://www.djangoproject.com/) 🐍    |
| Frontend          | [Tailwind CSS](https://tailwindcss.com/) 🎨   |
| Interactivity     | [HTMX](https://htmx.org/) ⚡                   |
| Database          | PostgreSQL 🐘                                 |
| Auth              | Django Auth (Custom User Model)               |
| Deployment        | Gunicorn + Nginx / Render / Heroku / Docker   |
| Testing           | Pytest + Django Test Framework                |

---

## 🧭 Core Concepts

### 👤 Users & Providers
- Every provider is also a user.
- A user can be:
  - **Client only** (book services)
  - **Provider only** (offer services)
  - **Both** (e.g., a makeup artist who also books photographers)

### 🏢 Business Profiles
- Store **brand name**, **contact info**, **availability**, **service categories**, and **ratings**.

### 🧭 Availability
- Providers define their **working days** and **hours per day** through a dedicated availability model.

### 🏡 Unified Address Model
- Both user and business addresses live in one table.
- `address_type` distinguishes *residential* vs *business*.
- `is_same_as_business` allows reuse of the same location.

### 📝 Event Creation & Offer Flow
1. User creates an event with required service categories.
2. Providers offering those services receive the request.
3. Providers accept / decline / renegotiate.
4. User selects the providers they want.
5. Booking is confirmed.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Node.js (for Tailwind)
- Git

---

### Installation

```bash
# Clone the repository
git clone https://github.com/sammykingx/servio.git
cd servio

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

```

### Environment Setup
Create a `.env` file in the root directory
```
ENVIRONMENT="development" | "production"
SECRET_KEY=your-secret-key

ALLOWED_HOSTS="127.0.0.1, localhost"

# DB CONFIGURATIONS
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""

# EMAIL SETTINGS
EMAIL_BACKEND=""
EMAIL_HOST=""
EMAIL_USERNAME=""
EMAIL_PASSWORD=""
EMAIL_PORT=""
USE_SSL=""
```

### Database Migration
```
python manage.py makemigrations
python manage.py migrate
```

### Frontend Setup

- Install tailwind css
```
npm install tailwindcss @tailwindcss/cli
```

- Generate output
```
# app dev output
npm run dev:app

# prod output
npm run build:app

# landing page dev output
npm run dev:landing

# prod output
npm run build:landing
```

## 🧱 Contributing

- Fork the repository.

- Create your feature branch:
```
git checkout -b feature/amazing-feature
```

- Commit your changes
```
git commit -m "Add amazing feature"
```

- Push to the branch
```
git push origin feature/amazing-feature
```

- Submit a pull request


## 🧩 License

This project is licensed under the MIT License — see the LICENSE


## ❤️ Acknowledgements

- [Django](https://www.djangoproject.com/) - The solid web framework
- [TailwindCSS](https://tailwindcss.com/) - For fast and modern UI development
- [POstgreSQL](https://www.postgresql.org/) - For reliability and scalability.
