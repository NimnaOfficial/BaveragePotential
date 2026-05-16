# 🌩️ Data Storm 7.0 — CODE BLOODED

## Predicting Latent Beverage Demand for Sri Lankan Retail Outlets

### 👥 Team Members

- **Dulan Dhanush** - Lead Data Engineer & Pipeline Architect
- **CODE BLOODED** - Lead Data Scientist & Modeler

### 🎯 Problem Summary

Our objective was to estimate the **Maximum Monthly Purchase Potential (in liters)** for 20,000 traditional trade outlets across 4 Sri Lankan provinces for January 2026. Because historical sales data only shows what an outlet _did_ sell rather than what it _could_ sell, we treated this as a **left-censored demand problem** driven by supply constraints.

### 🏗️ Lakehouse Architecture Overview

We implemented an enterprise-grade data pipeline to ensure complete data hygiene and reproducible feature engineering:

- **🥉 Bronze Layer:** Raw Kaggle dataset ingestion.
- **🥈 Silver Layer:** Parameterized Data Quality (DQ) forensics, anomaly quarantine (rejection logs), and data cleaning.
- **🥇 Gold Layer:** Feature engineering (growth momentum, plateau indicators, constraint proxies) and geographic Point of Interest (POI) data integration via Overpass API.
- **🧠 Modeling:** An ensemble of Peer-Benchmarking and Historical Uplift, capped by strict physical business guardrails.

### 🚀 How to Run the Pipeline

**1. Prerequisites**

```bash
pip install -r requirements.txt
```
