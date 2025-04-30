import streamlit as st
import pandas as pd
import geopy.distance

# Sample data: Replace with your actual dataset
agency_data = pd.read_csv('Agency_CAFN.csv')

# Mapping of service types to corresponding column names in the DataFrame
service_column_map = {
    'CSFP': 'Is_CSFP',
    'Children Services': 'Is_Children_Services',
    'Disaster Relief': 'Is_Disaster_Relief',
    'Elderly Services': 'Is_Elderly_Services',
    'Hospitals/Special Facilities': 'Is_Hospitals_Special_Facilities',
    'Meal Services': 'Is_Meal_Services',
    'Other': 'Is_Other',
    'Pantry': 'Is_Pantry',
    'Shelters/Group Homes': 'Is_Shelters_Group_Homes',
    'TEFAP': 'Is_TEFAP'
}

# Function to calculate distance between two points (latitude, longitude)
def calculate_distance(lat1, lon1, lat2, lon2):
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).miles

# Streamlit UI
st.title("Find Nearby Agencies")

# Dropdown to select the agency
agency_names = agency_data['Name'].tolist()  # List of agency names
selected_agency = st.selectbox("Select an Agency", agency_names)

# Get the coordinates of the selected agency
agency_selected = agency_data[agency_data['Name'] == selected_agency].iloc[0]
lat1, lon1 = agency_selected['Latitude'], agency_selected['Longitude']

# Distance threshold input (in miles)
distance_threshold = st.number_input("Enter Distance Threshold (miles)", min_value=1, max_value=100, value=5)

# Multi-select for types of services
service_types = list(service_column_map.keys())  # Extracting service names for the multiselect
selected_services = st.multiselect("Select Services", service_types)

# Button to calculate nearest agencies
if st.button("Find Nearby Agencies"):
    # Calculate the distances from the selected agency to all other agencies
    agency_data['Distance'] = agency_data.apply(
        lambda row: calculate_distance(lat1, lon1, row['Latitude'], row['Longitude']), axis=1
    )

    # Filter the agencies that are within the selected distance threshold
    nearby_agencies = agency_data[agency_data['Distance'] <= distance_threshold]

    # If any services are selected, filter based on those services
    if selected_services:
        # Convert selected services to the corresponding column names
        selected_columns = [service_column_map[service] for service in selected_services]
        
        # Filter based on selected services (columns with value 1)
        nearby_agencies = nearby_agencies[nearby_agencies[selected_columns].eq(1).any(axis=1)]
    
    nearby_agencies = nearby_agencies[nearby_agencies['Name'] != selected_agency]

    # Sort the agencies by distance in ascending order
    nearby_agencies_sorted = nearby_agencies.sort_values(by='Distance', ascending=True)
    # Show the results
    if not nearby_agencies.empty:
        st.write(f"Nearby Agencies within {distance_threshold} miles of {selected_agency} providing selected services:")
        st.dataframe(nearby_agencies_sorted[['Name', 'Distance', 'Address', 'City', 'State', 'ZIP Code'] + selected_columns])
    else:
        st.write(f"No agencies found within {distance_threshold} miles of {selected_agency} with the selected services.")
