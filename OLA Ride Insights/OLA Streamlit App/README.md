# 🚖 OLA Ride Insights — Streamlit Dashboard

A fully interactive recreation of the OLA Ride Insights Power BI report,
built with Streamlit + Plotly. Dark-themed, multi-page, with live filters.

## Pages
| Page | What you get |
|------|-------------|
| 📊 Overall Analysis | Booking trend, status donut, vehicle bar chart, distance histogram, 6 KPI cards |
| 🚗 Vehicle Type | Per-vehicle scorecards, revenue bars, fare vs distance scatter, success rate |
| 💰 Revenue | Monthly revenue trend, payment method pie, top-15 customers, revenue by vehicle |
| ❌ Cancellation | Customer & driver reason pies, weekly cancellation trend, cancel rate by vehicle |
| ⭐ Ratings | Rating distributions, ratings by vehicle, customer vs driver scatter, trend line |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run ola_dashboard.py
```

Then open http://localhost:8501 in your browser.

## Filters (Sidebar)
- **Date Range** — pick any Jul–Dec 2024 window
- **Booking Status** — toggle Success / Cancelled by Customer / Driver / Not Found
- **Vehicle Type** — filter to specific fleet types
- **Ride Distance** — slider to narrow by km range

All charts update instantly when you change any filter.

## Data
The dashboard generates 20,000 realistic synthetic OLA bookings for
Jul–Dec 2024 (India market), matching the structure of the uploaded .pbix file:
- Vehicle types: Auto, Bike, E-Bike, Mini, Prime Plus, Prime Sedan, SUV
- Payment: Cash, UPI, Credit Card, Debit Card
- Cancellation reasons match OLA's typical categories
