# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#1. '/'
#   - Start at the homepage.
#   - List all the available routes.
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/<start>/<end> (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

#2. /api/v1.0/precipitation
#   - Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary 
# using date as the key and prcp as the value.
#   - Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    one_year= dt.date(2017, 8, 23)-dt.timedelta(days=365)
    last_year_date = dt.date(one_year.year, one_year.month, one_year.day)

    data_scores= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date)\
        .order_by(Measurement.date.desc()).all()


    precip_dict = dict(data_scores)

    print(f"Results for Precipitation - {precip_dict}")
    print("Out of Precipitation section.")
    return jsonify(precip_dict) 


#3. /api/v1.0/stations
#   - Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    station_data = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in station_data:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)


#4. /api/v1.0/tobs
#   - Query the dates and temperature observations of the most-active station for the previous year of data.
#   - Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)


     active_station = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()


     temp_obs = []
     for date, tobs in active_station:
         temp_dict = {}
         temp_dict["Date"] = date
         temp_dict["Tobs"] = tobs
         temp_obs.append(temp_dict)

     return jsonify(temp_obs)



#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#   - Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#   - For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#   - For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.



@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    stats_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in stats_data:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    date_range_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in date_range_data:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)