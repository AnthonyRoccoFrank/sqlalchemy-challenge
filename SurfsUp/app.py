import numpy as np
import datetime as dt
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
   f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2010-01-01<br/>"
        f"/api/v1.0/start/2010-01-01/end/2017-08-23"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():

    most_recent_date = dt.date(2017, 8, 23)
    one_year_prior = most_recent_date - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_prior).all()

    session.close()

     # Convert list of tuples into dictionary
    p_dict = dict(precipitation)
    return jsonify(p_dict)

@app.route("/api/v1.0/stations")
def stations():

     stations = session.query(station.station).all()

     session.close()

      # Convert list of tuples into normal list
     all_stations = list(np.ravel(stations))

     return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
     descending_station = session.query(measurement.station, func.count(measurement.id)).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()
     most_active = descending_station[0][0]
     most_recent_date = dt.date(2017, 8, 23)
     one_year_prior = most_recent_date - dt.timedelta(days=365)
     waihee = session.query(measurement.date, measurement.tobs).\
     filter(measurement.station == most_active).filter(measurement.date >= one_year_prior).all()

     session.close()

     waihee_dict = dict(waihee)
     return jsonify(waihee_dict)

@app.route('/api/v1.0/start/<start>')
def start_date(start):

     temperature = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
         filter(measurement.date >= start).all()

     session.close()

     all_temperatures = []
     for tmin, tmax, tavg in temperature:
         temperature_dict = {}
         temperature_dict["Min"] = tmin
         temperature_dict["Max"] = tmax
         temperature_dict["Avg"] = tavg
         all_temperatures.append(temperature_dict)

     return jsonify(all_temperatures)

@app.route('/api/v1.0/start/<start>/end/<end>')
def start_end(start, end):

      temperature = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
         filter(measurement.date >= start).\
         filter(measurement.date <= end).all()

      session.close()
    
      all_temperatures = []
      for min, max, avg in temperature:
         temperature_dict = {}
         temperature_dict["Min"] = min
         temperature_dict["Max"] = max
         temperature_dict["Avg"] = avg
         all_temperatures.append(temperature_dict)

      return jsonify(all_temperatures)

if __name__ == "__main__":
    app.run(debug=True)