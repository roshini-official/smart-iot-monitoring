# 🗑️ SmartBin – IoT-Based Smart Waste Monitoring System

### ♻️ Smart Waste Management Through Intelligent Fill-Level Monitoring

**Technologies:** 🐍 Python · 📊 Streamlit · 🌐 Flask · 🗄️ SQLite · 📈 Plotly

---

## 🌱 Project Overview

SmartBin is an IoT-based smart waste monitoring system designed to monitor waste-bin fill levels and identify bins that require collection. It provides an interactive dashboard to visualize bin status, review historical readings, and support more efficient waste collection.

The current version uses simulated sensor readings to demonstrate the monitoring process and includes a Flask API for future integration with physical sensors.

## ✨ Key Features

- 📊 **Interactive Dashboard** — Displays bin fill percentages and current status.
- 🗑️ **Multiple Bin Monitoring** — Monitors bins assigned to different locations.
- 🚨 **Fill-Level Alerts** — Highlights bins that are nearly full or require collection.
- 🔄 **Automatic Dashboard Refresh** — Periodically refreshes the displayed information.
- 💾 **Persistent Data Storage** — Stores sensor readings in an SQLite database.
- 📈 **Historical Data Visualization** — Displays fill-level trends using interactive charts.
- 📥 **CSV Export** — Allows recorded data to be exported for further analysis.
- 🔌 **Flask API** — Provides an endpoint for receiving sensor readings.
- 🧪 **Simulation Mode** — Demonstrates the monitoring workflow without physical hardware.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| 🐍 Python | Application logic and data processing |
| 📊 Streamlit | Interactive monitoring dashboard |
| 🌐 Flask | Sensor data API |
| 🗄️ SQLite | Persistent data storage |
| 🐼 Pandas | Data handling and analysis |
| 📈 Plotly | Interactive data visualization |

## 📂 Project Structure

```text
smart-iot-monitoring/
├── app.py
├── sensor_receiver.py
├── requirements.txt
├── README.md
└── .gitignore
```

- `app.py` — Implements the monitoring dashboard.
- `sensor_receiver.py` — Provides the Flask API for sensor readings.
- `requirements.txt` — Lists the required Python libraries.
- `README.md` — Contains project documentation.
- `.gitignore` — Specifies files Git should ignore.

The SQLite database is created locally by the application when needed.

## 🚀 Installation and Setup

### 📌 Prerequisites

- Python 3.x
- pip package manager
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/roshini-official/smart-iot-monitoring.git
cd smart-iot-monitoring
```

### 2️⃣ Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3️⃣ Run the Dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal to access the dashboard.

### 4️⃣ Run the Sensor Receiver

Open another terminal in the project directory and execute:

```bash
python sensor_receiver.py
```

The API can receive sensor readings from external devices when they are configured to send requests in the expected format.

## ⚙️ Current Implementation

The current application demonstrates waste-bin monitoring through simulated sensor readings. It stores readings locally, displays bin status, visualizes historical data, and provides a Flask API for sensor data submission.

**Note:** Physical sensor readings are not yet implemented. The dashboard's simulated readings are intended for demonstration, and actual hardware integration remains a future enhancement.

## 🔮 Future Enhancements

- 📡 Integrate an ESP32 microcontroller and an ultrasonic distance sensor.
- 📏 Collect actual waste-bin distance measurements.
- 🔔 Add automated notifications for bins requiring collection.
- 📱 Develop a mobile-friendly monitoring interface.
- 🌍 Expand monitoring to additional waste collection locations.

## 🎯 Project Objective

To demonstrate how IoT concepts, data visualization, and persistent storage can be combined to build a smart waste monitoring solution that supports timely collection and more efficient waste management.

---

### ♻️ Smart Monitoring. Smarter Waste Management.
