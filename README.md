Here is the full, complete Markdown code. You can copy the entire block below and paste it directly into your `README.md` file.

```markdown
# 📇 Automated Digital Business Card Generator

> A custom-built Static Site Generator (SSG) that automates the creation of responsive, high-performance digital profile sites from raw JSON data.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Built%20With-Python%203-blue)
![Vercel](https://img.shields.io/badge/Deployment-Vercel-black)

## 🚀 Overview

This project is not just a website; it is an **automation engine**. Instead of manually coding HTML for individual employees, I engineered a Python script that parses a central dataset (`data.json`) and programmatically generates a unique, fully-featured website for every user.

It features an **Incremental Build System** (using MD5 hashing) that optimizes deployment times by only rebuilding profiles that have actually changed, similar to how React or Next.js handles virtual DOM updates.

## ✨ Key Features

* **⚡ Custom Static Site Generation (SSG):** Converts structured JSON data into pure HTML5/CSS3 pages.
* **🧠 Incremental Build Intelligence:** Uses MD5 fingerprinting to track state (`build_state.json`). If a user's data hasn't changed, the script skips rebuilding their site to save resources.
* **📱 vCard 3.0 Automation:** Programmatically generates `.vcf` contact files that work across iOS and Android.
* **🎨 Dynamic Brand Theming:** The template adapts CSS variables (buttons, highlights) based on the specific brand color defined in the dataset.
* **🔗 Smart Asset Management:** Automatically detects and resolves image file extensions (`.jpg` vs `.png`) to prevent broken links.
* **🌊 Advanced UI/UX:** Features "Waterfall" CSS animations and mobile-first responsive design.

## 🛠️ Project Structure

```bash
├── build.py           # The Engine: Main logic script
├── data.json          # The Database: User profiles and settings
├── template.html      # The Blueprint: HTML/CSS design
├── build_state.json   # The Memory: Stores hashes for incremental builds
├── photos/            # Source images (local storage)
└── public/            # Output folder (Generated sites go here)

```

## ⚙️ How It Works

1. **Input:** The script reads `data.json` and `template.html`.
2. **Hashing:** It calculates a unique hash for the template and each user profile.
3. **Comparison:** It checks `build_state.json` to see if the hash differs from the previous run.
4. **Generation:**
* Injects data into the HTML template.
* Generates the QR code modal logic.
* Creates the downloadable `contact.vcf` file.


5. **Output:** Saves the optimized files to the `public/` directory, ready for Vercel deployment.

## 🚀 Quick Start

### Prerequisites

* Python 3.x
* Git

### Installation

1. **Clone the repo:**
```bash
git clone [https://github.com/yourusername/digital-cards.git](https://github.com/yourusername/digital-cards.git)
cd digital-cards

```


2. **Add your data:**
Edit `data.json` to add a new profile:
```json
{
  "id": "john",
  "name": "John Doe",
  "position": "Software Engineer",
  "phone": "+919876543210",
  "email": "john@example.com",
  "theme_color": "#2563eb",
  "photo_url": "john.jpg"
}

```


3. **Run the Build Engine:**
```bash
python build.py

```


*Output:* `🔄 Rebuilt John Doe`
4. **Deploy:**
```bash
git push origin main

```



## 🔮 Future Roadmap

* [ ] **Cloud Integration:** Move image storage to AWS S3/Cloudinary for scalability beyond 1GB.
* [ ] **Database Migration:** Transition from `data.json` to a PostgreSQL database for managing 1,000+ users.
* [ ] **Admin Dashboard:** Build a React frontend to allow users to edit their own profiles without touching JSON.

---

*Built with ❤️ by Kahaan Shah*

```

```