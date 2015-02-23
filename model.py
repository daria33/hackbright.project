from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Float, Unicode
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection

#This part connects it to the database? Echo prints sqla calls, autocommit and autoflush will not occur
engine = create_engine("sqlite:///doctors.db", echo=True)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

#Base allows you to model your classes, not totally sure what the rest does here
Base = declarative_base()
Base.query = session.query_property()

geolocator = Nominatim()

#Class declarations 


class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key=True)   
    email = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    zipcode = Column(String(15), nullable=True)

    def __repr__(self):
        return "<user id = %r, email = %s>" % (self.id, self.email)

# Do I need to define how big a Float or an Integer is?

class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    cert = Column(Unicode(50), nullable=True)
    business_name = Column(Unicode (100), nullable=True)
    address = Column(Unicode(250), nullable=False)
    phone_number = Column(Unicode(25), nullable=True)
    recommended_by = Column(Unicode(50), nullable=False)
    gender = Column(Unicode(15), nullable=True)
    lat = Column(Float(50), nullable=True)
    lon = Column(Float(50), nullable=True)
    specialties = Column(Unicode(500), nullable=True)
    

    def __repr__(self):
        return "<Doctor name=%s, Doctor id=%d>" % (self.name, self.id)

#What is the best way to structure the review portion or the rating? How big to make it?

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=False)
    review = Column(String(500), nullable=True)

    user = relationship("User",
            backref=backref("ratings", order_by=id))

    doctor = relationship("Doctor",
            backref=backref("ratings", order_by=id))

    def __repr__(self):
        return "<Rating id = %d, doctor id = %d, user_id = %d, Rating = %d>" % (self.id, self.doctor_id, self.user_id, self.rating)


# End class declarations

def addgeo():
    """ Queries all doctors, gets lat/long for their address, adds them to the db entry"""

    all_doctors = session.query(Doctor).all()

    for doctor in all_doctors:
        address = doctor.address
        location = getgeo(address)
        doctor.lat = location[0]
        doctor.lon = location[1]
        session.add(doctor)

    session.commit()

    return

def getgeo(address):
    """ Return the latitude and longitude in a tuple"""
    location = geolocator.geocode(address, timeout=5)

    return (location.latitude, location.longitude)

def getlonlat():
    """ creates a list of doctors name and their lat/long"""

    all_doctors = session.query(Doctor).all()

    coordinates = []

    for doctor in all_doctors:
        
        longitude = doctor.lon
        latitude = doctor.lat
        name = doctor.name
        address = doctor.address

        #figure out how to structure with additional information
        my_feature = Feature(geometry=Point((longitude, latitude)), properties={"title": name, "Address":address, "marker-color": "#0099CC"})
        coordinates.append(my_feature)
        print my_feature
        

    new_coords = FeatureCollection(coordinates)
    return new_coords




#Main function because I think we need one here? 
def main():
    pass

if __name__ == "__main__":
    main()


