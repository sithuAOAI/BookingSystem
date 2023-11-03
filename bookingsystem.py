from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, Date, Interval,Column, Integer, String, DateTime, ForeignKey
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import time, date
from sqlalchemy import Time

#DATABASE_URL = "mysql+pymysql://root:geniusraver27@localhost/meeting_room_bookings"

DATABASE_URL = "mysql+pymysql://bookings_user:password@localhost/meeting_room_bookings"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

Base = declarative_base()


class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"

    room_id = Column(String, primary_key=True, index=True)
    room_name = Column(String)
    building_location = Column(String, default="그랜드빌딩")
    capacity = Column(Integer, default=6)
    tv = Column(String(1), default="N")
    blackboard = Column(String(1), default="N")
    photo_location = Column(String)

class MeetingRoomBooking(Base):
    __tablename__ = "meeting_room_bookings"

    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_subject = Column(String)
    room_id = Column(String, ForeignKey("meeting_rooms.room_id"))
    applicant_name = Column(String)
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    duration = Column(String)
    attendees = Column(Integer)


class BookingRequest(BaseModel):
    booking_subject: str
    room_id: str
    applicant_name: str
    date: date
    start_time: time
    end_time: time
    duration: str
    attendees: int

class CoffeeMenu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    menu_option = Column(String, index=True)
    menu_name = Column(String)
    menu_price = Column(Integer)

class CoffeeOrder(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    coffee_type = Column(String(255))
    num_coffees = Column(Integer)
    order_date = Column(String)
    order_time = Column(Time)
    expected_time = Column(Time)
    booking_id = Column(Integer, ForeignKey("meeting_room_bookings.booking_id"))
    pickup_status = Column(String)

class OrderRequest(BaseModel):
    customer_name: str
    coffee_type: str
    num_coffees: int
    order_date: date
    order_time: time
    expected_time: time
    booking_id: int
    pickup_status: str
    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.get("/meeting_rooms/{room_id}")
def get_meeting_room(room_id: str):
    db = SessionLocal()
    meeting_room = db.query(MeetingRoom).filter(MeetingRoom.room_id == room_id).first()
    db.close()
    if meeting_room is None:
        raise HTTPException(status_code=404, detail="Meeting room not found")
    return meeting_room

@app.get("/all_meeting_rooms")
def get_all_meeting_rooms():
    db = SessionLocal()
    meeting_rooms = db.query(MeetingRoom).all()
    db.close()
    return [{"room_id": m.room_id, "room_name": m.room_name, "building_location": m.building_location, "capacity": m.capacity, "tv": m.tv, "blackboard": m.blackboard, "photo_location": m.photo_location} for m in meeting_rooms]

@app.post("/create_booking")
def create_booking(booking_request: BookingRequest):
    db = SessionLocal()
    booking = MeetingRoomBooking(
        booking_subject=booking_request.booking_subject,
        room_id=booking_request.room_id,
        applicant_name=booking_request.applicant_name,
        date=booking_request.date,
        start_time=booking_request.start_time,
        end_time=booking_request.end_time,
        duration=booking_request.duration,
        attendees=booking_request.attendees
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.close()
    return {"booking_id": booking.booking_id, "booking_subject": booking.booking_subject, "room_id": booking.room_id, "applicant_name": booking.applicant_name, "date": booking.date, "start_time": booking.start_time, "end_time": booking.end_time, "duration": booking.duration, "attendees": booking.attendees}

@app.get("/read_booking/{booking_id}")
def read_booking(booking_id: int):
    db = SessionLocal()
    booking = db.query(MeetingRoomBooking).filter(MeetingRoomBooking.booking_id == booking_id).first()
    db.close()
    if not booking:
        return {"error": "Booking not found"}
    return {"booking_subject": booking.booking_subject, "room_id": booking.room_id, "applicant_name": booking.applicant_name, "date": booking.date, "start_time": booking.start_time, "end_time": booking.end_time, "duration": booking.duration, "attendees": booking.attendees}

@app.get("/read_all_bookings")
def read_all_bookings():
    db = SessionLocal()
    bookings = db.query(MeetingRoomBooking).all()
    db.close()
    return [{"booking_id": b.booking_id, "booking_subject": b.booking_subject, "room_id": b.room_id, "applicant_name": b.applicant_name, "date": b.date, "start_time": b.start_time, "end_time": b.end_time, "duration": b.duration, "attendees": b.attendees} for b in bookings]

@app.get("/available_rooms")
def get_available_rooms(date: date, start_time: time, end_time: time):
    db = SessionLocal()
    bookings = db.query(MeetingRoomBooking).filter(MeetingRoomBooking.date == date).all()
    db.close()
    booked_rooms = [b.room_id for b in bookings if b.start_time <= start_time <= b.end_time or b.start_time <= end_time <= b.end_time]
    available_rooms = db.query(MeetingRoom).filter(MeetingRoom.room_id.notin_(booked_rooms)).all()
    return [{"room_id": r.room_id, "room_name": r.room_name, "building_location": r.building_location, "capacity": r.capacity, "tv": r.tv, "blackboard": r.blackboard, "photo_location": r.photo_location} for r in available_rooms]

@app.put("/update_booking/{booking_id}")
def update_booking(booking_id: int, booking_request: BookingRequest):
    db = SessionLocal()
    booking = db.query(MeetingRoomBooking).filter(MeetingRoomBooking.booking_id == booking_id).first()
    if not booking:
        db.close()
        return {"error": "Booking not found"}
    booking.booking_subject = booking_request.booking_subject
    booking.room_id = booking_request.room_id
    booking.applicant_name = booking_request.applicant_name
    booking.date = booking_request.date
    booking.start_time = booking_request.start_time
    booking.end_time = booking_request.end_time
    booking.duration = booking_request.duration
    booking.attendees = booking_request.attendees
    db.commit()
    db.close()
    return {"status": "updated"}

@app.delete("/delete_booking/{booking_id}")
def delete_booking(booking_id: int):
    db = SessionLocal()
    booking = db.query(MeetingRoomBooking).filter(MeetingRoomBooking.booking_id == booking_id).first()
    if not booking:
        db.close()
        return {"error": "Booking not found"}
    db.delete(booking)
    db.commit()
    db.close()
    return {"status": "deleted"}

@app.get("/coffee_menu")
def get_coffee_menu():
    db = SessionLocal()
    menu_items = db.query(CoffeeMenu).all()
    db.close()
    return [{"id": item.id, "category": item.category, "menu_option": item.menu_option, "menu_name": item.menu_name, "menu_price": item.menu_price} for item in menu_items]

@app.get("/coffee_orders")
def read_coffee_orders():
    db = SessionLocal()
    coffee_orders = db.query(CoffeeOrder).all()
    db.close()
    return coffee_orders


@app.post("/order_coffee")
def order_coffee(order_request: OrderRequest):
    db = SessionLocal()
    order = CoffeeOrder(
        customer_name=order_request.customer_name,
        coffee_type=order_request.coffee_type,
        num_coffees=order_request.num_coffees,
        order_date=order_request.order_date,
        order_time=order_request.order_time,
        expected_time=order_request.expected_time,
        booking_id=order_request.booking_id,
        pickup_status=order_request.pickup_status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()
    return {"id": order.id, "customer_name": order.customer_name,"coffee_type": order.coffee_type,"num_coffees": order.num_coffees, "order_date": order.order_date, "order_time": order.order_time, "expected_time": order.expected_time, "booking_id": order.booking_id, "pickup_status": order.pickup_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

    