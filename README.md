
# SAP--Project
# 📊 SAP SD Order-to-Cash (O2C) Analytics Project

## 👩‍💻 Author

**J Neha**
B.Tech CSE | KIIT University
Roll No: 2305703

---

## 📌 Project Overview

This project simulates the **SAP SD Order-to-Cash (O2C) process** using Python and builds an **end-to-end analytics pipeline** for business insights.

It replicates real SAP data flow across:

* Sales Orders
* Deliveries
* Billing
* Revenue Analytics

---

## 🧠 Problem Statement

SAP systems store O2C data across multiple tables (VBAK, VBAP, LIKP, VBRK), making:

* Cross-module analysis complex
* SLA tracking difficult
* Real-time reporting limited

This project solves it using **Python-based analytics simulation**.

---

## ⚙️ Tech Stack

* Python 3.11
* Pandas
* NumPy
* Matplotlib

---

## 🏗️ Architecture

1. Data Generation (SAP-like tables)
2. Data Processing (joins & transformations)
3. KPI Calculation
4. Dashboard Visualization

---

## 📊 Key KPIs

* Total Order Value: ₹89.06 Cr
* Billed Revenue: ₹78.81 Cr
* Unbilled AR Exposure: ₹10.25 Cr
* Avg Lead Time: 14.5 days
* On-Time Delivery Rate: 22.7%

---

## 🔍 Key Insights

* ⚠️ Severe SLA breach (only 22.7% on-time)
* ⚠️ ₹10.25 Cr revenue stuck in pipeline
* ⚠️ High dependency on LAPTOP product (>40%)

---

## 🧾 SAP Tables Used

| Table | Description        |
| ----- | ------------------ |
| VBAK  | Sales Order Header |
| VBAP  | Sales Order Items  |
| LIKP  | Delivery           |
| VBRK  | Billing            |

---

## 🔗 SAP Transactions Covered

* VA01 – Create Sales Order
* VL06O – Delivery Monitor
* VF05 – Billing List
* MC9 – Revenue Report

---

## 📁 Project Files

* 📄 Project Report (DOCX/PDF)
* 🐍 Python Code
* 📊 Visualizations
* 📷 SAP Screenshots

---

## 🚀 How to Run

```bash
pip install pandas numpy matplotlib
python main.py
```

---

## 📈 Future Enhancements

* Predictive SLA Breach using ML
* SAP HANA Integration
* Real-time dashboard (Power BI / Tableau)

---

## 📌 Conclusion

This project proves that **enterprise SAP analytics can be replicated using Python**, enabling faster and cost-effective decision-making.

---

⭐ If you like this project, give it a star!
