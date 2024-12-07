import streamlit as st
import pandas as pd
import numpy as np
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
import json
import polyline
import base64

# Set page config
st.set_page_config(
    page_title="Route Analysis Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Add title and description
st.title("🚗 Route Analysis Dashboard")
st.markdown("### Visualize and analyze route data")

# Sidebar for file upload and data source selection
st.sidebar.header("Data Input")

# Data source selection
data_source = st.sidebar.radio(
    "Select Data Source",
    ["Khatkesh", "Argus", "Sheyda"],
    help="Choose the type of data you're uploading"
)

# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type="csv",
    help="Upload your route data CSV file"
)

def decode_base64_route(encoded_str):
    """Decode base64 encoded route string"""
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        st.warning(f"Error decoding base64: {str(e)}")
        return None

def process_khatkesh_data(df):
    """Process Khatkesh format data with proper polyline decoding"""
    if 'ride_path' not in df.columns:
        st.error("The file doesn't contain the required 'ride_path' column for Khatkesh data.")
        return None
    
    paths_df = pd.DataFrame(columns=['lat', 'lng', 'ride_id'])
    
    for _, row in df.iterrows():
        try:
            encoded_polyline = row['ride_path']
            # Remove leading "0 " if present
            if encoded_polyline.startswith("0 "):
                encoded_polyline = encoded_polyline[2:]
            
            # Decode the polyline
            decoded_route = polyline.decode(encoded_polyline)
            
            # Create points DataFrame with proper scaling
            points_df = pd.DataFrame(decoded_route, columns=['lat', 'lng'])
            points_df['lat'] = points_df['lat'] / 10  # Scale latitude
            points_df['lng'] = points_df['lng'] / 10  # Scale longitude
            points_df['ride_id'] = row['ride_id']
            
            paths_df = pd.concat([paths_df, points_df], ignore_index=True)
        except Exception as e:
            st.warning(f"Error processing ride_id {row['ride_id']}: {str(e)}")
            continue
            
    return paths_df

def process_argus_data(df):
    """Process Argus format data"""
    if 'route' not in df.columns or 'ride_id' not in df.columns:
        st.error("The file doesn't contain required columns: route, ride_id")
        return None
    
    paths_df = pd.DataFrame(columns=['lat', 'lng', 'ride_id'])
    
    for _, row in df.iterrows():
        try:
            # Decode base64 route
            decoded_route = decode_base64_route(row['route'])
            if decoded_route:
                # Decode the polyline
                points = polyline.decode(decoded_route)
                points_df = pd.DataFrame(points, columns=['lat', 'lng'])
                points_df['ride_id'] = row['ride_id']
                paths_df = pd.concat([paths_df, points_df], ignore_index=True)
        except Exception as e:
            st.warning(f"Error processing ride_id {row['ride_id']}: {str(e)}")
            continue
    
    return paths_df

def process_sheyda_data(df):
    """Process Sheyda format data"""
    required_cols = ['lat', 'lng']
    if not all(col in df.columns for col in required_cols):
        st.error(f"The file doesn't contain all required columns: {', '.join(required_cols)}")
        return None
    
    # Add ride_id if not present
    if 'ride_id' not in df.columns:
        df['ride_id'] = 1
    
    return df[['lat', 'lng', 'ride_id']]

def get_map_center(df):
    """Calculate the center point of all coordinates"""
    return {
        'latitude': df['lat'].mean(),
        'longitude': df['lng'].mean(),
        'zoom': 11
    }

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Process data based on selected source
        if data_source == "Khatkesh":
            processed_df = process_khatkesh_data(df)
        elif data_source == "Argus":
            processed_df = process_argus_data(df)
        else:  # Sheyda
            processed_df = process_sheyda_data(df)
        
        if processed_df is not None and not processed_df.empty:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Total Points",
                    value=len(processed_df)
                )
            with col2:
                st.metric(
                    label="Unique Rides",
                    value=processed_df['ride_id'].nunique()
                )
            with col3:
                st.metric(
                    label="Average Points per Ride",
                    value=f"{len(processed_df) / processed_df['ride_id'].nunique():.1f}"
                )
            
            # Get map center
            center = get_map_center(processed_df)
            
            # Create Kepler map
            map_config = {
                "version": "v1",
                "config": {
                    "visState": {
                        "filters": [],
                        "layers": [
                            {
                                "id": "routes",
                                "type": "line",
                                "config": {
                                    "dataId": "routes",
                                    "label": "Routes",
                                    "color": [255, 0, 0] if data_source == "Khatkesh" else [0, 255, 0] if data_source == "Argus" else [0, 0, 255],
                                    "columns": {
                                        "lat": "lat",
                                        "lng": "lng",
                                        "alt": None
                                    },
                                    "isVisible": True,
                                    "visConfig": {
                                        "opacity": 0.8,
                                        "thickness": 2,
                                        "colorRange": {
                                            "name": "Global Warming",
                                            "type": "sequential",
                                            "category": "Uber",
                                            "colors": ["#5A1846", "#900C3F", "#C70039", "#E3611C", "#F1920E", "#FFC300"]
                                        },
                                        "sizeRange": [0, 10],
                                        "targetColor": None
                                    }
                                }
                            }
                        ]
                    },
                    "mapState": {
                        "bearing": 0,
                        "latitude": center['latitude'],
                        "longitude": center['longitude'],
                        "pitch": 0,
                        "zoom": center['zoom'],
                        "dragRotate": False
                    }
                }
            }
            
            # Create and configure map
            map_1 = KeplerGl(height=600, config=map_config)
            
            # Add data to map
            map_1.add_data(data=processed_df, name="routes")
            
            # Display the map
            st.subheader("Route Visualization")
            keplergl_static(map_1)
            
            # Display data table
            st.subheader("Data Preview")
            st.dataframe(processed_df.head())
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    st.info("Please upload a CSV file to begin visualization.")
