# 🏎️ F1 AI Race Strategy Decision Support System

An AI-powered Formula 1 race strategy application designed to analyze race data, explore tyre strategies, and support data-driven strategic decisions through an interactive dashboard.

## 📌 Overview

The **F1 AI Race Strategy Decision Support System** combines Formula 1 telemetry and race data with data analysis, machine learning, and simulation techniques to explore potential race strategies.

The project aims to make race strategy analysis more accessible through an interactive Streamlit dashboard.

## ✨ Features

- **Formula 1 Data Integration:** Access race and session data using FastF1.
- **Interactive Dashboard:** Explore race strategy information through Streamlit.
- **Data Analysis:** Process and analyze data using Pandas and NumPy.
- **Machine Learning:** Support model-based analysis using scikit-learn, where implemented.
- **Strategy Simulation:** Explore possible strategy outcomes using simulation techniques, where implemented.
- **Data Visualization:** Present insights through interactive charts and visualizations.

## 🛠️ Technology Stack

- Python
- Streamlit
- FastF1
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Plotly
- SciPy
- Joblib

## 📁 Project Structure

The project structure may vary depending on the existing files. Update this section to match your actual folders and modules.

```text
F1 Major Project/
├── src/
│   └── dashboard/
│       └── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "F1 Major Project"
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## ▶️ Run the Application

From the project root, activate your virtual environment and run:

```bash
python -m streamlit run src/dashboard/app.py
```

Streamlit will provide a local URL, usually `http://localhost:8501`, where you can access the dashboard.

## 📊 Data and Models

The application may use Formula 1 session data, processed datasets, trained machine learning models, or simulation outputs.

Ensure any required model files and configuration are available before running the application. Follow the project's data-source terms and any applicable licensing requirements.

## ☁️ Deployment

The application is intended to be deployable on Streamlit Community Cloud.

1. Push the project to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select the repository.
4. Select the correct branch and Streamlit entry-point file.
5. Deploy the application.

Additional configuration may be required if the project relies on local model files, external data, or secrets.

## 🔒 Security

- Do not commit API keys, credentials, or private configuration files.
- Keep virtual environments and Python cache files out of version control.
- Store secrets using Streamlit's secrets management when required.

## 🚧 Project Status

This project is under development. Features and documentation may evolve as the application is tested and prepared for deployment.

## 👤 Author

## Pratham Ahuja

## 📄 License

A license has not yet been specified. Add a license before distributing the project if required.
