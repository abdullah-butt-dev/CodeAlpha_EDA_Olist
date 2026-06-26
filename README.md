# 🛒 Olist Intelligence – E‑Commerce Analytics Dashboard

> **Interactive, production‑grade dashboard** that transforms 100K+ orders from Brazil’s largest e‑commerce platform into actionable business insights.

🔗 **Live Demo:** [olist-intelligence.streamlit.app](https://olist-intelligence.streamlit.app/)

---

## 📸 Dashboard Preview

| Overview | Revenue & Growth |
|----------|------------------|
| ![Overview](images/dashboard-overview.png) | ![Revenue](images/revenue-tab.png) |

| Products | Delivery & Satisfaction | Sellers |
|----------|------------------------|---------|
| ![Products](images/products-tab.png) | ![Delivery](images/delivery-tab.png) | ![Sellers](images/sellers-tab.png) |

---

## 📌 Overview

This project delivers a **full‑stack analytics solution** for the Olist Brazilian E‑Commerce dataset.  
It merges 9 raw CSV files into a single clean data model, then surfaces **real‑time KPIs**, **dynamic filtering**, and **5 interactive tabs** covering:

- Revenue & growth trends  
- Product category performance  
- Delivery logistics & customer satisfaction  
- Seller segmentation & risk  
- Customer retention & RFM analysis  

Built with **Streamlit** and **Plotly**, the dashboard is fully responsive and designed for both desktop and mobile.

---

## 🚀 Key Features

- **Live, filterable dashboard** – adjust date range, state, or product category; all charts update instantly.
- **7‑card KPI row** – total revenue, order volume, on‑time rate, average review, etc.
- **Multi‑tab layout** – each tab dives deep into a specific business domain.
- **Interactive visualisations** – bar charts, histograms, scatter plots, heatmaps, and pie charts.
- **Seller performance quadrant** – identify stars, hidden gems, and at‑risk sellers.
- **Delivery speed vs. satisfaction** – shows a clear negative correlation beyond 21 days.
- **Repeat‑rate analysis** – highlights a critical retention gap (only ~3% of customers reorder).

---

## 📊 Data Source

- **Olist Brazilian E‑Commerce Dataset** – [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
- 9 interconnected tables: orders, customers, products, sellers, payments, reviews, etc.
- Cleaned and merged into a single `olist_master_clean.csv` (included in `/data`).

---

## 🛠️ Tech Stack

- **Python 3.9+**  
- **Streamlit** – interactive web app framework  
- **Pandas** & **NumPy** – data wrangling & aggregation  
- **Plotly Express / Graph Objects** – interactive plotting  
- **CSS** – custom styling with mobile‑first responsive breakpoints  

---
