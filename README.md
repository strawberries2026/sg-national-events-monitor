# SG National Events & Leadership Monitor

Version 1.2.0 — Developed by Desmond Song.

Public-information dashboard covering Singapore leadership, ministries, Parliament and publicly announced national events.

## Current capabilities
- Mobile-friendly dark dashboard and clickable navigation
- Search, agency and leader filters for published announcements
- Expandable ministerial and agency announcement groups
- Verified future-event calendar (currently empty until events are individually verified)
- Official social media directories (not a live social media feed)
- Data-file availability, collection timestamps and 24-hour staleness indicators

## Data limitations
The dashboard reads `data/events.json` and `data/verified-events.json`. Loading a file does not prove its upstream source is live, accurate, or complete. Future events must be independently verified from original official announcements before being added. A zero count does not mean no events are scheduled.

Automated collection and social-media ingestion are not yet configured. Do not interpret the dashboard as a real-time operational tracking service.

## GitHub Pages
Settings → Pages → Deploy from a branch → main → /(root).

## Safety
Publicly announced events only. No real-time movement tracking, undisclosed itineraries, or security deployment information. Verify operationally relevant details directly against official sources.
