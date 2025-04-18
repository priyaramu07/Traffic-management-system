# Traffic-management-system
## Project Description

The **Traffic Management System** is designed to detect and track vehicles in real-time across four lanes using OpenCV. The system monitors traffic flow in each lane, counts the number of vehicles moving forward and backward, and stores this data in a MySQL database. A Streamlit dashboard is used to visualize the real-time traffic data and provide dynamic traffic light control suggestions based on the vehicle counts in each lane.

The project aims to enhance traffic management systems by optimizing traffic light control and providing insights into traffic density across multiple lanes.

## Features

- **Vehicle Detection:** Detects and tracks vehicles across four lanes in real-time.
- **Vehicle Counting:** Counts the number of vehicles moving forward and backward in each lane.
- **Database Integration:** Stores the vehicle count data in a MySQL database.
- **Streamlit Dashboard:** Visualizes vehicle counts in real-time and offers dynamic traffic light control suggestions.
- **Manual Traffic Light Control:** Allows for manual override of traffic light states through the dashboard.

## Requirements

Before running the project, ensure you have the following installed:

- Python 3.x
- OpenCV (`opencv-python` and `opencv-python-headless`)
- MySQL Connector (`mysql-connector-python`)
- Streamlit (`streamlit`)
- Numpy (`numpy`)

## Installation Instructions

Follow these steps to get the project up and running:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/traffic-management-system.git

2. Navigate to the project folder:
cd traffic-management-system

3. Install the required Python packages:
pip install -r requirements.txt

4. Set up the MySQL database:
Run the SQL script from the sql_code.txt file to create the multi_vehicle_data database and the lane_vehicle_count table.

Usage Instructions
1. Run the vehicle detection script:
This script processes the video files for each lane and counts the number of vehicles moving forward and backward.
python multi_vehicle_counter.py

2. Launch the Streamlit dashboard:
The Streamlit dashboard provides a visual interface for monitoring the traffic data in real-time and controlling the traffic lights dynamically.
python -m streamlit run Home.py

3. Video Files:
Ensure that the required video files (lane1.mp4, lane2.mp4, lane3.mp4, lane4.mp4) are present in the project folder. These videos simulate traffic in each lane.

4. Traffic Light Suggestions:
The dashboard will show real-time data with the vehicle count for each lane and suggest dynamic traffic light control based on the current traffic density.

Database Setup
The MySQL database is used to store the vehicle count data for each lane.

Data is inserted into the lane_vehicle_count table every 10 seconds with the following fields:

lane1_fwd, lane1_bwd: Forward and backward vehicle counts for Lane 1.
lane2_fwd, lane2_bwd: Forward and backward vehicle counts for Lane 2.
lane3_fwd, lane3_bwd: Forward and backward vehicle counts for Lane 3.
lane4_fwd, lane4_bwd: Forward and backward vehicle counts for Lane 4.
