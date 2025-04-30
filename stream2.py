import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(layout="wide")
st.title("🚓 SecureCheck: Traffic Stops Analytics Dashboard")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="secureccheck"
)

# Function to run SQL queries
def run_query(query):
    return pd.read_sql(query, conn)

# --------------------------- VEHICLE-BASED QUERIES ---------------------------
st.header("🚗 Vehicle-Based (Medium Level)")

vehicle_queries = {
    "Top 10 vehicles involved in drug-related stops": """
        SELECT vehicle_number, COUNT(*) AS stop_count 
        FROM traffic_stops 
        WHERE drugs_related_stop = TRUE 
        GROUP BY vehicle_number 
        ORDER BY stop_count DESC 
        LIMIT 10
    """,
    "Vehicles most frequently searched": """
        SELECT vehicle_number, COUNT(*) AS search_count 
        FROM traffic_stops 
        WHERE search_conducted = TRUE 
        GROUP BY vehicle_number 
        ORDER BY search_count DESC 
        LIMIT 10
    """
}

selected_vehicle_query = st.selectbox("Select a vehicle-related query:", list(vehicle_queries.keys()), key="vehicle")
if st.button("Run Vehicle Query"):
    st.dataframe(run_query(vehicle_queries[selected_vehicle_query]))

# --------------------------- DEMOGRAPHIC QUERIES ---------------------------
st.header("🧍 Demographic-Based (Medium Level)")

demo_queries = {
    "Driver age group with highest arrest rate": """
        SELECT 
            CASE
                WHEN driver_age < 18 THEN 'Under 18'
                WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
                WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                ELSE '60+'
            END AS age_group,
            COUNT(*) AS arrest_count
        FROM traffic_stops
        WHERE is_arrested = TRUE
        GROUP BY age_group
        ORDER BY arrest_count DESC
        LIMIT 1
    """,
    "Gender distribution of drivers by country": """
        SELECT country_name, driver_gender, COUNT(*) AS count
        FROM traffic_stops
        GROUP BY country_name, driver_gender
        ORDER BY country_name, count DESC
    """,
    "Race & gender combo with highest search rate": """
        SELECT driver_race, driver_gender, COUNT(*) AS search_count
        FROM traffic_stops
        WHERE search_conducted = TRUE
        GROUP BY driver_race, driver_gender
        ORDER BY search_count DESC
        LIMIT 1
    """
}

selected_demo_query = st.selectbox("Select a demographic-related query:", list(demo_queries.keys()), key="demo")
if st.button("Run Demographic Query"):
    st.dataframe(run_query(demo_queries[selected_demo_query]))

# --------------------------- TIME & DURATION QUERIES ---------------------------
st.header("🕒 Time & Duration Based (Medium Level)")

time_queries = {
    "Time of day with most traffic stops": """
        SELECT 
            CASE
                WHEN HOUR(stop_time) BETWEEN 5 AND 11 THEN 'Morning (5AM-11AM)'
                WHEN HOUR(stop_time) BETWEEN 12 AND 16 THEN 'Afternoon (12PM-4PM)'
                WHEN HOUR(stop_time) BETWEEN 17 AND 20 THEN 'Evening (5PM-8PM)'
                ELSE 'Night (9PM-4AM)'
            END AS time_period,
            COUNT(*) AS stop_count
        FROM traffic_stops
        GROUP BY time_period
        ORDER BY stop_count DESC
    """,
    "Average stop duration by violation": """
        SELECT violation, 
               AVG(CASE 
                       WHEN stop_duration = '0-15 Min' THEN 7
                       WHEN stop_duration = '16-30 Min' THEN 23
                       WHEN stop_duration = '30+ Min' THEN 45
                       ELSE NULL
                   END) AS avg_duration_minutes
        FROM traffic_stops
        GROUP BY violation
        ORDER BY avg_duration_minutes DESC
    """,
    "Are night stops more likely to lead to arrests?": """
        SELECT 
            CASE
                WHEN (HOUR(stop_time) >= 21 OR HOUR(stop_time) <= 4) THEN 'Night'
                ELSE 'Day'
            END AS time_of_day,
            SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests,
            COUNT(*) AS total_stops,
            ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percentage
        FROM traffic_stops
        GROUP BY time_of_day
        ORDER BY arrest_rate_percentage DESC
    """
}

selected_time_query = st.selectbox("Select a time-related query:", list(time_queries.keys()), key="time")
if st.button("Run Time Query"):
    st.dataframe(run_query(time_queries[selected_time_query]))

# --------------------------- VIOLATION-BASED QUERIES ---------------------------
st.header("⚖️ Violation-Based (Medium Level)")

violation_queries = {
    "Violations most associated with search or arrest": """
        SELECT violation, 
               SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests
        FROM traffic_stops
        GROUP BY violation
        ORDER BY searches DESC, arrests DESC
        LIMIT 10
    """,
    "Common violations among drivers under 25": """
        SELECT violation, COUNT(*) AS stop_count
        FROM traffic_stops
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY stop_count DESC
        LIMIT 10
    """,
    "Violations rarely resulting in search or arrest": """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = TRUE OR is_arrested = TRUE THEN 1 ELSE 0 END) AS action_taken
        FROM traffic_stops
        GROUP BY violation
        HAVING action_taken = 0
        ORDER BY total_stops DESC
    """
}

selected_violation_query = st.selectbox("Select a violation-based query:", list(violation_queries.keys()), key="violation")
if st.button("Run Violation Query"):
    st.dataframe(run_query(violation_queries[selected_violation_query]))

# --------------------------- LOCATION-BASED QUERIES ---------------------------
st.header("🌍 Location-Based (Medium Level)")

location_queries = {
    "Countries with highest drug-related stops": """
        SELECT country_name, COUNT(*) AS drug_related_stops
        FROM traffic_stops
        WHERE drugs_related_stop = TRUE
        GROUP BY country_name
        ORDER BY drug_related_stops DESC
    """,
    "Arrest rate by country and violation": """
        SELECT country_name, violation,
               ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percentage
        FROM traffic_stops
        GROUP BY country_name, violation
        ORDER BY arrest_rate_percentage DESC
        LIMIT 20
    """,
    "Countries with most search-conducted stops": """
        SELECT country_name, COUNT(*) AS search_conducted_count
        FROM traffic_stops
        WHERE search_conducted = TRUE
        GROUP BY country_name
        ORDER BY search_conducted_count DESC
        LIMIT 10
    """
}

selected_location_query = st.selectbox("Select a location-based query:", list(location_queries.keys()), key="location")
if st.button("Run Location Query"):
    st.dataframe(run_query(location_queries[selected_location_query]))

# --------------------------- COMPLEX QUERIES ---------------------------
st.header("🧠 Complex Queries (Advanced Level)")

complex_queries = {
    "Yearly Breakdown of Stops and Arrests by Country": """
        SELECT country_name, YEAR(stop_date) AS year, 
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests
        FROM traffic_stops
        GROUP BY country_name, year
        ORDER BY country_name, year
    """,
    "Driver Violation Trends Based on Age and Race": """
        SELECT driver_race, 
               CASE 
                 WHEN driver_age < 18 THEN 'Under 18'
                 WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                 WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
                 WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                 ELSE '60+'
               END AS age_group,
               COUNT(*) AS violation_count
        FROM traffic_stops
        GROUP BY driver_race, age_group
        ORDER BY violation_count DESC
    """,
    "Time Period Analysis of Stops": """
        SELECT 
            YEAR(stop_date) AS year,
            MONTH(stop_date) AS month,
            HOUR(stop_time) AS hour,
            COUNT(*) AS total_stops
        FROM traffic_stops
        GROUP BY year, month, hour
        ORDER BY year, month, hour
    """,
    "Violations with High Search and Arrest Rates": """
        SELECT violation,
               ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100, 2) AS search_rate,
               ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate
        FROM traffic_stops
        GROUP BY violation
        HAVING search_rate > 30 OR arrest_rate > 30
        ORDER BY arrest_rate DESC
    """,
    "Driver Demographics by Country": """
        SELECT country_name, 
               AVG(driver_age) AS avg_age,
               driver_gender,
               driver_race,
               COUNT(*) AS total_drivers
        FROM traffic_stops
        GROUP BY country_name, driver_gender, driver_race
        ORDER BY total_drivers DESC
    """,
    "Top 5 Violations with Highest Arrest Rates": """
        SELECT violation,
               ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)/COUNT(*)*100, 2) AS arrest_rate_percentage
        FROM traffic_stops
        GROUP BY violation
        ORDER BY arrest_rate_percentage DESC
        LIMIT 5
    """
}

selected_complex_query = st.selectbox("Select a complex query:", list(complex_queries.keys()), key="complex")
if st.button("Run Complex Query"):
    st.dataframe(run_query(complex_queries[selected_complex_query]))

# Close connection
conn.close()
