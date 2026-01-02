# AirCPA

AirCPA is an offline analysis tool for deterministic air traffic
conflict detection based on Closest Point of Approach (CPA)
prediction using historic ADS-B state vector data.

The tool is intended for research, education, and exploratory
safety analysis. It does **not** perform real-time monitoring
or operational air traffic control functions.

<img width="1848" height="848" alt="Screenshot from 2026-01-02 19-03-32-modified" src="https://github.com/user-attachments/assets/37a2c236-5bd2-4101-8504-a474ff058611" />

## Method

AirCPA performs deterministic conflict analysis using a Closest Point of Approach (CPA) model under simplified kinematic assumptions.

For each snapshot of ADS-B state vectors:

- Aircraft motion is assumed to be linear and time-invariant over the selected look-ahead horizon.
- Relative horizontal motion between aircraft pairs is analyzed to compute the time and distance at CPA.
- A conflict is detected if both:
  - horizontal separation at CPA falls below a configurable
    threshold (e.g. 5 NM), and
  - vertical separation at CPA falls below a configurable
    threshold (e.g. 1000 ft).
- Horizontal and vertical separation are evaluated independently.

The analysis is fully deterministic and does not model
aircraft intent, flight plans, sensor uncertainty, or
nonlinear motion. A local Cartesian (flat-earth) approximation
is used for geometric computations.

## Data Source

AirCPA uses ADS-B state vector data from the
[OpenSky Network](https://www.opensky-network.org).

The included example setup analyzes traffic over **Germany**
for **one hour (15:00–16:00 UTC) on 2022-06-27**, chosen to provide
a compact yet sufficiently dense traffic sample for demonstration
purposes.

The same workflow applies to any other OpenSky CSV state vector
dataset with the same schema.

Due to licensing restrictions, raw OpenSky data is **not**
redistributed via this repository.

## Usage

### 1. Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Download and prepare data

From the `data/` directory:

```bash
cd data
./get_data.sh
```

This script downloads the OpenSky dataset, extracts it, and runs a preprocessing step to filter the data for the example scenario.

### 3. Run the application

From the project root:

```bash
streamlit run app.py
```

The application will open in your browser.

## License

### Code License

The source code of this project is licensed under the MIT License.
See the `LICENSE` file for details.

### Data License

This project uses ADS-B state vector data from the OpenSky Network.

The raw data is **not redistributed** via this repository.
Users must download the data themselves and agree to the
OpenSky Network General Terms of Use & Data License Agreement
before using the data.

See `data/LICENSE_OPENSKY.txt` for the full license text.
