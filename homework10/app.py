import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement 
Station = Base.classes.station  


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def main():
    """List all available api routes."""
    return ( 
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>" 
        f"/api/v1.0/<start><br/>" 
        f"/api/v1.0/<start>/<end>"
    )



@app.route("/api/v1.0/precipitation") 
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query 
    precipitation_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    maxdate = precipitation_date[0][0] 
    enddate = datetime.datetime.strptime(maxdate,"%Y-%m-%d") 
    begin = enddate - datetime.timedelta(365)
  
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin).all()
    
    #dictionary
    precip_dict = {}
    for result in precipitation_data:
        precip_dict[result[0]] = result[1]

    return jsonify(precip_dict)
    session.close()

@app.route("/api/v1.0/stations") 
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query 
    stations = session.query(Station).all()
    #dictionary
    empty = [] 
    for station in stations: 
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        empty.append(station_dict)

    return jsonify(empty)
    session.close() 

@app.route("/api/v1.0/tobs")
def tobs():
# Create our session (link) from Python to the DB
    session = Session(engine)
    #query
    tobs_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    maxdate = tobs_query[0][0]
    enddate = datetime.datetime.strptime(maxdate, "%Y-%m-%d")
    begin = enddate - datetime.timedelta(365)

    #get temperature measurements for last year
    results = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin).all()

    #dictionaries 
    empty = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        empty.append(tobs_dict)

    return jsonify(empty)
    session.close() 

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    #query
    date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    maxdate = date[0][0] 

    #temp
    def temps(start_date, end_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temperature = temps(start,maxdate) 
    #dictionary
    empty = []  
    date_dict = {'start_date': start, 'end_date': maxdate}
    empty.append(date_dict)
    empty.append({'Observation': 'TMIN', 'Temperature': temperature[0][0]})
    empty.append({'Observation': 'TAVG', 'Temperature': temperature[0][1]})
    empty.append({'Observation': 'TMAX', 'Temperature': temperature[0][2]})

    return jsonify(empty)
    session.close() 

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    #temp
    def temps(start_date, end_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    temperature = temps(start,end) 

    #dictionary
    empty = []  
    date_dict = {'start_date': start, 'end_date': end}
    empty.append(date_dict)
    empty.append({'Observation': 'TMIN', 'Temperature': temperature[0][0]})
    empty.append({'Observation': 'TAVG', 'Temperature': temperature[0][1]})
    empty.append({'Observation': 'TMAX', 'Temperature': temperature[0][2]})

    return jsonify(empty)
    session.close() 

if __name__ == '__main__':
    app.run(debug=True)