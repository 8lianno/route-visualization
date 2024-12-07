# Route Visualization Dashboard 🚗 🗺️

A powerful Streamlit-based dashboard for visualizing route data using Kepler.gl. This dashboard supports multiple data formats and provides an interactive map visualization with customizable styles.

## Features

- 📊 Support for multiple data formats:
  - Khatkesh (polyline encoded paths)
  - Argus (base64 encoded routes)
  - Sheyda (direct lat/lng coordinates)
- 🗺️ Interactive Kepler.gl map visualization
- 📈 Real-time metrics:
  - Total points
  - Unique rides
  - Average points per ride
- 🎨 Color-coded routes by data source
- 🎯 Auto-centering on routes
- 📋 Data preview table

## Installation

1. Clone the repository:
```bash
git clone repository_url
cd route-visualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the dashboard:
```bash
streamlit run dashboard.py
```

2. Open your browser at `http://localhost:8501`

3. Select your data source type and upload a CSV file:

### Data Format Requirements

#### Khatkesh Format
CSV file must contain:
- `ride_id`: Unique identifier for each ride
- `ride_path`: Polyline encoded path string

Example:
```csv
ride_id,ride_path
10555152398,ocevdA_lincBo@gAw@_AgAg@...
```

#### Argus Format
CSV file must contain:
- `ride_id`: Unique identifier for each ride
- `route`: Base64 encoded polyline string

Example:
```csv
ride_id,route
12345,Y3pkfkV5fHBgST8/fkBAPz90...
```

#### Sheyda Format
CSV file must contain:
- `lat`: Latitude coordinates
- `lng`: Longitude coordinates
- `ride_id` (optional): Will be set to 1 if not provided

Example:
```csv
lat,lng,ride_id
35.770035,51.348133,1
35.770157,51.348843,1
```

## Features in Detail

### 1. Data Processing
- Khatkesh: Decodes polyline format with proper coordinate scaling
- Argus: Handles base64 decoding followed by polyline decoding
- Sheyda: Direct lat/lng coordinate processing

### 2. Visualization
- Line-based route visualization
- Color coding:
  - Khatkesh routes: Red
  - Argus routes: Green
  - Sheyda routes: Blue
- Automatic viewport centering on routes
- Configurable line thickness and opacity

### 3. Metrics
- Real-time calculation of:
  - Total number of points in the route
  - Number of unique rides
  - Average points per ride

## Dependencies

- streamlit==1.29.0
- pandas==2.1.3
- plotly==5.18.0
- numpy==1.26.2
- streamlit-keplergl==0.3.0
- keplergl==0.3.2
- polyline==2.0.1

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Kepler.gl](https://kepler.gl/) for the amazing visualization capabilities
- [Streamlit](https://streamlit.io/) for the web framework
- [Polyline](https://pypi.org/project/polyline/) for route decoding
