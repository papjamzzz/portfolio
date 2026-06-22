# Portfolio — CLAUDE.md
*Re-entry: Portfolio*

## What This Is
Personal portfolio site for Jeremiah Smith at byjeremiahsmith.ink.
Light UI, warm/organic feeling — contrast to all the dark Creative Konsoles projects.
Port 5576.

## Status
🟢 Live on Railway — byjeremiahsmith.ink

## Architecture
- `app.py`             — Flask server (port 5576)
- `templates/index.html` — Single-page portfolio (hero / projects / about / contact)
- No DB — static + contact form POST → Resend

## Design System
- Background: #F7F8FC
- Surface: #FFFFFF
- Border: #D8DEF0
- Accent: #3D5A80 (navy)
- Muted: #6B7A99
- Font: Inter, weights 400/500/600/700/800/900

## Projects Featured
1. StreamFader — https://stream.creativekonsoles.com
2. Represented — https://represented.creativekonsoles.com
3. Equil — private beta (no link)
4. Melt — https://melt.creativekonsoles.com
5. Soma — in development (no link)

## Contact Form
POST /contact → Resend API → jeremiah3335@gmail.com
Requires RESEND_API_KEY in .env (gracefully degrades if missing)

## Railway Env Vars
- RESEND_API_KEY
- FROM_EMAIL=noreply@byjeremiahsmith.ink

## Port
5576

## GitHub
https://github.com/papjamzzz/portfolio

---
## Last Session (2026-06-22)
- Built from scratch. Full single-page portfolio.
- Design: light UI, cool whites, Inter 900, navy accent.
- 5 project cards with color-coded top stripe accents.
- "Something new" 6th card links to contact.
- About section: personal copy, 2-col layout.
- Contact: Resend form + email + GitHub links.
- Footer with nav links.
- Next: push to GitHub, deploy on Railway, wire byjeremiahsmith.ink DNS.
