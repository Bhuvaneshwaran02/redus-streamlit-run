from matplotlib import pyplot as plt
import pandas as pd
import mysql.connector
import streamlit as st
import plotly.graph_objs as go

# Establish a connection to your MySQL database
cnx = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="abcd",
    database="redbus"
)

# Create a cursor object
cursor = cnx.cursor()

# Create a title for the page
st.title("RedBus Project")

# Create a sidebar container
with st.sidebar:
    st.sidebar.image(r"th.jpg", width=300)
    st.sidebar.markdown("<h1 style='text-align: center'>RedBus Project</h1>", unsafe_allow_html=True)
    st.header("Navigation")
    page = st.selectbox("Choose a page", ["Home", "Bus Routes", "Analysis"])

if page == "Home":
    st.write("Welcome to the Bhuvaneshwaran REDBUS PROJECT!")
    st.subheader("Project Overview")
    st.write("This project aimed to extract relevant data from the Redbus website using Selenium, store the data in MySQL, and present it using Streamlit.")

elif page == "Bus Routes":
    # Query to fetch distinct values for DepartureCity and Destination
    cursor.execute("SELECT DISTINCT DepartureCity FROM bus_detail WHERE DepartureCity IS NOT NULL")
    departure_cities = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT Destination FROM bus_detail WHERE Destination IS NOT NULL")
    destinations = [row[0] for row in cursor.fetchall()]

    # Create dropdowns for Departure City and Destination
    selected_city = st.selectbox("Choose a departure city", departure_cities if departure_cities else ["No data available"])
    selected_destination = st.selectbox("Choose a destination", destinations if destinations else ["No data available"])

    # Manual input for price range
    min_price = st.number_input("Enter minimum price", min_value=0, value=100)
    max_price = st.number_input("Enter maximum price", min_value=min_price, value=1000)

    # Slider for bus rating
    rating_range = st.slider("Select a bus rating range", min_value=0.0, max_value=5.0, value=(3.0, 5.0), step=0.1)

    # Create a selectbox for start time
    time_options = ["Filter Off", "04:00-12:00", "12:00-17:00", "17:00-21:00", "21:00-04:00"]
    selected_time = st.selectbox("Choose a start time range", time_options)

    # Build the SQL query with filters
    query = """
        SELECT *
        FROM bus_detail
        WHERE DepartureCity = %s AND Destination = %s
        AND Price BETWEEN %s AND %s
        AND Bus_Rating BETWEEN %s AND %s
    """
    params = (selected_city, selected_destination, min_price, max_price, rating_range[0], rating_range[1])

    conditions = []

    # Handle Time filter
    if selected_time != "Filter Off":
        if selected_time == "04:00-12:00":
            conditions.append("Start_Time BETWEEN '04:00:00' AND '12:00:00'")
        elif selected_time == "12:00-17:00":
            conditions.append("Start_Time BETWEEN '12:00:00' AND '17:00:00'")
        elif selected_time == "17:00-21:00":
            conditions.append("Start_Time BETWEEN '17:00:00' AND '21:00:00'")
        elif selected_time == "21:00-04:00":
            conditions.append("(Start_Time BETWEEN '21:00:00' AND '23:59:59' OR Start_Time BETWEEN '00:00:00' AND '04:00:00')")

    # Append conditions to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Execute the query
    cursor.execute(query, params)

    # Fetch the results
    matched_values = cursor.fetchall()

    # Check if results are empty
    if not matched_values:
        st.write("No buses found for the selected filters.")
    else:
        # Get the column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Create a DataFrame from the matched values
        df = pd.DataFrame(matched_values, columns=column_names)

        # Display the matched values in a table format
        st.write("Matched Values:")
        st.table(df)

elif page == "Analysis":
    st.subheader("Redbus Data Analysis")

    # Fetch the data from the MySQL table
    query = "SELECT Price, Bus_Rating FROM bus_detail"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=['Price', 'Bus_Rating'])

    # Plot the scatter plot
    fig = go.Figure(data=[go.Scatter(x=df['Price'], y=df['Bus_Rating'], mode='markers')])
    fig.update_layout(title='Scatter Plot of Price vs Bus Rating', xaxis_title='Price', yaxis_title='Bus Rating')

    # Display the plot in the Streamlit app
    st.plotly_chart(fig)

# Close the cursor and connection
cursor.close()
cnx.close()
