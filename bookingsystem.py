from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:geniusraver27@localhost/meeting_room_bookings"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

class BookingRequest(BaseModel):
    room: str
    start_time: datetime
    end_time: datetime

class CoffeeMenu(Base):
    __tablename__ = "coffee_menu"

    id = Column(Integer, primary_key=True, index=True)
    coffee_type = Column(String, index=True)
    price = Column(Integer)
    description = Column(String)

class CoffeeOrder(Base):
    __tablename__ = "coffee_orders"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True)
    coffee_type = Column(String)
    quantity = Column(Integer)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.post("/create_booking")
def create_booking(booking_request: BookingRequest):
    db = SessionLocal()
    booking = Booking(room=booking_request.room, start_time=booking_request.start_time, end_time=booking_request.end_time)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.close()
    return {"id": booking.id, "room": booking.room, "start_time": booking.start_time, "end_time": booking.end_time}

@app.get("/read_booking/{booking_id}")
def read_booking(booking_id: int):
    db = SessionLocal()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    db.close()
    if not booking:
        return {"error": "Booking not found"}
    return {"room": booking.room, "start_time": booking.start_time, "end_time": booking.end_time}

@app.get("/read_all_bookings")
def read_all_bookings():
    db = SessionLocal()
    bookings = db.query(Booking).all()
    db.close()
    return [{"id": b.id, "room": b.room, "start_time": b.start_time, "end_time": b.end_time} for b in bookings]

@app.put("/update_booking/{booking_id}")
def update_booking(booking_id: int, room: str, start_time: str, end_time: str):
    db = SessionLocal()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        db.close()
        return {"error": "Booking not found"}
    booking.room = room
    booking.start_time = start_time
    booking.end_time = end_time
    db.commit()
    db.close()
    return {"status": "updated"}

@app.delete("/delete_booking/{booking_id}")
def delete_booking(booking_id: int):
    db = SessionLocal()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
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
    return [{"id": item.id, "coffee_name": item.coffee_type, "price": item.price, "description": item.description} for item in menu_items]

@app.post("/order_coffee")
def order_coffee(room: str, coffee_type: str, quantity: int):
    db = SessionLocal()
    order = CoffeeOrder(room=room, coffee_type=coffee_type, quantity=quantity)
    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()
    return {"id": order.id, "room": order.room, "coffee_type": order.coffee_type, "quantity": order.quantity}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)