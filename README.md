<div align="center">

# 📇 Automated Digital Business Card Generator

<p><strong>A high-performance Static Site Generator (SSG) that converts structured JSON datasets into responsive, dynamic digital business cards with vCard automation.</strong></p>

[![Status](https://img.shields.io/badge/Status-Active-3ddc84?style=for-the-badge)](https://github.com/Kahaan83/digital-cards)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Deployment](https://img.shields.io/badge/Deployment-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

<img src="assets/preview.png" alt="Digital Business Card Preview" width="600" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.3);" />

<br /><br />

</div>

---

## 🚀 Overview

Managing digital identity pages for teams or businesses often leads to tedious maintenance and repetitive HTML templating. 

This project solves that by acting as an **automation engine**:
Instead of manually coding HTML for individual profiles, a Python-driven static-site generator parses a centralized dataset (`data.json`) and programmatically generates an optimized, uniquely themed web card for each individual—complete with QR code modal popups and direct downloadable `.vcf` contact cards.

---

## ✨ Key Features

- **⚡ Custom Static Site Generation (SSG):** Transforms clean JSON records into lightweight, zero-dependency HTML5/CSS3 pages.
- **🧠 Incremental MD5 Build Intelligence:** Computes MD5 checksum fingerprints for templates and records (`build_state.json`). If a profile hasn't changed, the script automatically skips rebuilding it to optimize deployment times.
- **📱 vCard 3.0 Automation:** Programmatically produces compatible `.vcf` contact cards that download and import into iOS Contacts and Android Contacts with one click.
- **🎨 Dynamic Brand Theming:** Automatically adapts CSS variables (accent hues, button shadows, interactive states) based on each user's unique brand hex code.
- **🔗 Smart Asset Resolution:** Intelligently resolves image formats (`.jpg`, `.png`, `.webp`) from local source paths to prevent broken image references.
- **🌊 Modern Mobile-First UX:** Tailored for smartphone screens with waterfall animations, smooth modal interactions, and touch-friendly targets.

---

## 🛠️ Project Structure

```bash
digital-cards/
├── build.py           # The SSG Engine: Data parsing, hashing, & generation
├── data.json          # The Database: User profiles, theme colors, and social links
├── template.html      # The Blueprint: Semantic HTML shell & CSS design system
├── build_state.json   # Incremental Memory: Stores hashes to skip redundant builds
├── photos/            # Source profile photos and avatar images
├── public/            # The Output: Production-ready static builds (deployable to Vercel)
│   ├── kahaan/
│   │   └── index.html
│   └── contact.vcf
└── assets/            # Showcase images and documentation assets
```

---

## ⚙️ How It Works

```
┌─────────────────┐       ┌─────────────────┐
│    data.json    │   +   │  template.html  │
└────────┬────────┘       └────────┬────────┘
         │                         │
         └───────────► ◄───────────┘
                       │
          [ MD5 Hash State Comparison ]
          ├── Unchanged? ──► Skip Rebuild
          └── Modified?  ──► Inject Data + Generate .vcf
                       │
                       ▼
          ┌─────────────────────────┐
          │     public/<user>/      │
          │  Production Static HTML │
          └─────────────────────────┘
```

1. **Input:** Reads user configurations from `data.json` and layout tokens from `template.html`.
2. **Hashing:** Calculates an MD5 hash of each profile record and compares it with `build_state.json`.
3. **Template Compilation:** For modified profiles, injects name, title, contact methods, and theme colors into the template.
4. **Asset Export:** Generates matching vCard (`.vcf`) files and exports everything to `public/`.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kahaan83/digital-cards.git
   cd digital-cards
   ```

2. **Add or edit profiles in `data.json`:**
   ```json
   {
     "id": "alex",
     "name": "Alex Mercer",
     "position": "Hardware Engineer",
     "phone": "+1234567890",
     "email": "alex@example.com",
     "theme_color": "#2563eb",
     "photo_url": "alex.jpg"
   }
   ```

3. **Run the build engine:**
   ```bash
   python build.py
   ```
   *Console output:*
   ```text
   [BUILD] Hashing templates and records...
   [NEW] Building profile for Alex Mercer -> public/alex/index.html
   [SKIP] Profile 'kahaan' is unchanged.
   [SUCCESS] Build complete in 0.04s.
   ```

4. **Deploy:**
   Connect the repository to **Vercel** or **Cloudflare Pages** targeting the `public/` directory for automatic deployment on git push.

---

## 🔮 Roadmap

- [ ] **Cloud Storage Sync:** Add automated image uploads to Cloudinary or AWS S3.
- [ ] **QR Code Image Generation:** Embed SVG QR codes directly into downloadable cards for print/NFC tags.
- [ ] **Web UI Dashboard:** Simple browser-based editor to modify `data.json` without touching code directly.

---

## 👤 Author

**Kahaan Shah**
- Portfolio: [kahaanshah.in](https://kahaanshah.in)
- GitHub: [@Kahaan83](https://github.com/Kahaan83)
- LinkedIn: [linkedin.com/in/kahaan-shah-842095334](https://www.linkedin.com/in/kahaan-shah-842095334/)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
