# Risk Calculation Service

## Overview

The **Risk Calculation Service** is the final asynchronous worker in the risk assessment pipeline. It acts as the "brain" of the operation, consuming `vulnerability.found` events from Kafka and synthesizing all previously gathered data to produce a final, quantifiable risk score.

Its process is as follows:
1.  Receives a `vulnerability.found` event.
2.  Fetches the corresponding asset's valuation data (SCA scores) from the asset database.
3.  Applies the core risk formulas from the project methodology to calculate:
    -   **Impacto Cuantitativo (IC):** The potential damage a vulnerability could cause to a specific asset.
    -   **Probabilidad Cuantitativa (PC):** The likelihood of the vulnerability being exploited.
    -   **Nivel de Riesgo (NR):** The final risk score, calculated as `NR = IC * PC`.
4.  Persists the calculated risk record to the database.
5.  Publishes a final `risk.calculated` event, which signals to the frontend/dashboard that new results are ready to be displayed.

## Tech Stack

- **Language:** Python 3.11+
- **Messaging:** Apache Kafka
- **Database:** PostgreSQL
- **Containerization:** Docker

## Core Logic: Risk Formulas

This service directly implements the mathematical heart of the methodology:
-   **Impacto Cuantitativo (IC):** Calculated by combining the asset's dimensional CIA scores (`SCA_C`, `SCA_I`, `SCA_D`) with the vulnerability's dimensional impact from its CVSS score.
-   **Probabilidad Cuantitativa (PC):** Calculated using the vulnerability's base severity (`CVSS score`) and a placeholder for the effectiveness of existing controls (`EC`). `PC = (SV / 10) * (1 - EC)`.
-   **Nivel de Riesgo (NR):** The product of the two, `NR = IC * PC`, resulting in a final score from 0 to 10.

## Architecture

This service is a headless worker following **Clean Architecture**:
1.  **Domain:** Defines the `Risk` entity and abstract repository interfaces.
2.  **Application:** Contains the `CalculateRiskUseCase` and the core `RiskFormulaService`.
3.  **Infrastructure:** Provides concrete implementations for the PostgreSQL repositories and Kafka producer. It's unique in that it reads from one database (`asset_db`) and writes to another (`risk_db`).
4.  **Worker:** The main process that runs the Kafka consumer.

## Getting Started

Follow the standard procedure: clone, create a virtual environment, install dependencies, configure your `.env` file, and run `python main.py`.