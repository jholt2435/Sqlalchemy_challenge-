# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine =create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables

base = automap_base()
base.prepare(autoload_with = engine )
# Save references to each table
measurement = base.classes.measurement
station = base.classes.station 

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Home():
    return """
     <p>Welcome!</p>
     <p> These are the routes to navigate my app <p>
     <ol>
     <li>/api/v1.0/precipitation</li>
     <li>/api/v1.0/stations</li>
     <li>/api/v1.0/tobs<li>
     <li>/api/v1.0/start/<start><li>
     <li>/api/v1.0/start_end/<start>/<end><li>
"""
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of measurement data including the date, and precipitation"""
    # Query precipitation data for the past year 
    
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    precipitation_data_final_year = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).\
        order_by(measurement.date).all()

    session.close()

    measurements_by_date = []
    for date, prcp in precipitation_data_final_year:
        measurements_by_date_dict = {"date": date, "prcp": prcp}
        measurements_by_date.append(measurements_by_date_dict)
        
    return jsonify(measurements_by_date)

@app.route("/api/v1.0/stations")
def stations():

    #Start session 
    session = Session(engine)

    #Query for identifying all station names 
    stations = session.query(station.station).all()

    # Add all station Ids to a list 
    
    station_list = [{"station": station} for station, in stations]
    # Return the list of stations as JSON
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Start session
    session = Session(engine)

    """Return a JSON list of temperature observations for the previous year"""
    # Establish the date range starting one year ago 
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations for only the most active station= 'USC00519281' within only the last year 
    temperature_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= one_year_ago).\
        order_by(measurement.date).all()

    # Close the session
    session.close()

    # Convert the query results into a list of dictionaries with date and tobs(temp) as keys and dates for most active station and temp for most active station as values 
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    # Return the list of temperature observations as JSON
    return jsonify(temperature_list)
@app.route("/api/v1.0/start/<start>")
def temperature_stats_start(start):
    #Return Min, max and avg for chosen date to the end of the timeframe 
    try:
        # Convert start date string to a date user can enter with following format 
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Query to get Min.max and avg within chosen range 
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start_date).all()

    # Extract results into a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    
    return jsonify(temperature_stats)


@app.route("/api/v1.0/start_end/<start>/<end>")
def temperature_stats_start_end(start, end):
    #Return Min, Max and Avg for range from chosen start date to chosen end date
    try:
        # Convert start and end date strings to datetime objects
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Query to get Min.max and avg within chosen range 
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start_date, measurement.date <= end_date).all()

    # Extract results into a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)
