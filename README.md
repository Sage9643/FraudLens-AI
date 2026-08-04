
<p align="center">
  <img src="./frontend/src/assets/branding/logo-github-banner.png" alt="FraudLens AI Banner" width="100%">
</p>



<p align="center">

<img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white"/>

<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white"/>

<img src="https://img.shields.io/badge/XGBoost-ML-orange?style=flat-square"/>

<img src="https://img.shields.io/badge/SHAP-XAI-purple?style=flat-square"/>

<img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white"/>

<img src="https://img.shields.io/badge/Tailwind-CSS-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white"/>

<img src="https://img.shields.io/badge/Vercel-Frontend-black?style=flat-square&logo=vercel"/>

<img src="https://img.shields.io/badge/Render-Backend-46E3B7?style=flat-square&logo=render&logoColor=black"/>



</p>
---


> An end-to-end Explainable Fraud Detection Platform built using **React, FastAPI, XGBoost, SHAP, and SQLite**. FraudLens AI enables users to analyze financial transactions, understand model predictions through explainable AI, process datasets in bulk, and monitor fraud trends through interactive dashboards.

---

### 🚀 Live Application

Link:-  https://fraudlens-ai-nu.vercel.app/


### 📖 Overview

FraudLens AI is a full-stack machine learning application designed to demonstrate how a fraud detection model can be integrated into a complete software system rather than existing only as a trained model.

The platform combines machine learning, explainable AI, data persistence, analytics, and visualization into a unified application. Every prediction goes beyond simply classifying a transaction as **Fraud** or **Legitimate** by providing:

- Fraud probability
- Confidence score
- Risk classification
- SHAP-based feature explanations
- Recommended action
- Persistent prediction history

The application supports both **single transaction analysis** through manual input and **batch fraud detection** through CSV uploads.

---

###  🎯 Problem Statement

Financial fraud detection systems often rely on machine learning models that produce accurate predictions but provide little insight into *why* a transaction has been classified as fraudulent.

FraudLens AI addresses this by combining prediction with explainability and analytics. Instead of acting as a black-box classifier, the platform allows users to understand the reasoning behind every prediction while maintaining a searchable history of previous analyses.

---

###  🚀 Features

#### 1. Single Transaction Prediction

Users can manually enter transaction details through the web interface.

For every transaction, the application:

- Validates the input
- Runs inference using the trained XGBoost model
- Predicts whether the transaction is fraudulent
- Computes fraud probability
- Calculates model confidence
- Assigns a fraud risk tier
- Generates SHAP explanations
- Produces a recommended action
- Stores the prediction in the database

---

#### 2. Fraud Probability

Instead of returning only a binary prediction, the system provides the probability that a transaction is fraudulent.

Example:

```
Prediction: Fraud

Fraud Probability: 94.8%
```

This allows users to understand how strongly the model supports its decision.

---

#### 3. Confidence Score

Each prediction includes a confidence score that reflects the certainty of the model.

This helps distinguish highly confident predictions from predictions that lie close to the decision boundary.

---

#### 4. Risk Tier Classification

FraudLens AI converts prediction probabilities into operational risk categories.

| Risk Tier | Description |
|------------|-------------|
| 🟢 Low | Very low fraud likelihood |
| 🟡 Medium | Suspicious, monitor closely |
| 🟠 High | Requires manual review |
| 🔴 Critical | Immediate investigation recommended |

Risk tiers make it easier to prioritize transactions during analysis.

---

#### 5. Recommended Actions

Based on the prediction and associated risk level, the application generates an appropriate recommendation.

Examples include:

- Approve transaction
- Monitor transaction
- Review manually
- Block transaction

This demonstrates how prediction results can be translated into business decisions.

---

#### 6. Explainable AI (SHAP)

Every prediction is accompanied by SHAP-based explanations.

The explainability module identifies:

- Features that increased fraud probability
- Features that decreased fraud probability
- Relative feature importance
- Contribution of each feature toward the final prediction

This enables users to understand why a transaction was classified as fraudulent instead of relying solely on a probability score.

---

#### 7. Batch Prediction

The platform supports fraud analysis for entire datasets through CSV uploads.

For every uploaded dataset, the application:

- Validates the uploaded file
- Processes each transaction individually
- Generates predictions
- Computes fraud probabilities
- Assigns risk tiers
- Produces recommended actions
- Stores batch results
- Generates downloadable prediction reports

This allows users to evaluate large numbers of transactions using the same prediction pipeline.

---

#### 8. Prediction History

Every manually analyzed transaction is stored in the database.

The history module enables users to:

- Browse previous predictions
- Search prediction records
- Review fraud probabilities
- Inspect explanations
- Revisit previous analyses

This creates a persistent audit trail of all processed transactions.

---

#### 9. Analytics Dashboard

The dashboard aggregates prediction data into meaningful insights.

It provides visual summaries such as:

- Total predictions
- Fraud vs legitimate transactions
- Fraud rate
- Risk distribution
- Confidence distribution
- Prediction trends over time

Rather than displaying individual predictions, the dashboard offers an overview of system activity.

---

#### 10. Batch History

Every uploaded CSV is recorded after processing.

For each processed batch, the application stores:

- Batch ID
- Upload timestamp
- Number of processed transactions
- Fraud count
- Legitimate count
- Fraud rate
- Processing duration
- Model version

This allows previously processed datasets to be reviewed without rerunning inference.

---

### 🧠 Machine Learning Pipeline

For every transaction, the following workflow is executed:

```
Transaction Input
        │
        ▼
Input Validation
        │
        ▼
Model Inference (XGBoost)
        │
        ▼
Fraud Prediction
        │
        ▼
Fraud Probability
        │
        ▼
Confidence Score
        │
        ▼
Risk Tier Assignment
        │
        ▼
SHAP Explainability
        │
        ▼
Recommended Action
        │
        ▼
Database Storage
        │
        ▼
Dashboard & History
```

---

### 🏗️ System Architecture

```
                   React + Vite
                         │
                    Axios API Calls
                         │
                    FastAPI Backend
                         │
        ┌────────────────┴────────────────┐
        │                                 │
 Prediction Service              Analytics Service
        │                                 │
        ├───────────────┐                 │
        │               │                 │
   XGBoost Model    SHAP Engine           │
        │               │                 │
        └───────────────┴─────────────────┘
                        │
                  SQLite Database
```

---

### 📂 Project Structure

```
FraudLens-AI
│
├── frontend/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   └── utils/
│
├── backend/
│   ├── api/
│   ├── database/
│   ├── services/
│   ├── schemas/
│   ├── utils/
│   └── models/
│
└── model_artifacts/
```

---

### 🛠 Tech Stack

#### Frontend

- React
- Vite
- Tailwind CSS
- Axios
- Lucide React

####  Backend

- FastAPI
- Python
- SQLite
- Pydantic

####  Machine Learning

- XGBoost
- SHAP
- Scikit-learn
- Pandas
- NumPy

####  Deployment

- Vercel (Frontend)
- Render (Backend)

---

### 🌐 API Modules

The backend exposes REST APIs for:

- Health Monitoring
- Single Transaction Prediction
- Explainability
- Dashboard Analytics
- Prediction History
- Batch Prediction
- Batch History

---

### 📈 Current Scope

The current implementation supports:

- Manual transaction prediction
- Batch CSV prediction
- Explainable AI
- Prediction history
- Batch history
- Dashboard analytics
- Downloadable batch reports
- REST-based backend architecture

The application currently **does not ingest live financial transaction streams** or perform continuous real-time monitoring. It is designed as an end-to-end fraud analysis platform demonstrating prediction, explainability, analytics, and persistence within a modular software architecture.

---

### 🔮 Future Scope

Potential future enhancements include:

- Migration from SQLite to PostgreSQL for higher concurrency
- Role-based authentication and authorization
- Containerized deployment
- Model version management
- Automated model retraining pipeline
- Real-time transaction ingestion
- Distributed batch processing
- Advanced monitoring and alerting

---
