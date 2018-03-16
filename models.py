from sqlalchemy import Column, LargeBinary,Integer,BigInteger, String, DateTime, Numeric, ForeignKey
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

now=datetime.now()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uname = Column(String(50), unique=True)
    phoneNumber = Column(BigInteger, unique=True)
    email = Column(String(120), unique=True)
    pwd = Column(String(120) )
    dateofBirth = Column(String(120))
    storedCash=Column(Integer())
    usersid = relationship("Utrack",  backref="users")

    
    

    def __init__(self, uname=None, phoneNumber=None, email=None, pwd=None, dateofBirth=None, height=None, weight=None,storedCash=None):
        self.uname=uname
        self.phoneNumber=phoneNumber
        self.email=email
        self.pwd=pwd
        self.dateofBirth=dateofBirth
        self.height=height
        self.weight=weight
        self.storedCash=storedCash

    def __repr__(self):
        return '<User %r>' % (self.uname)

class Utrack(Base):
    __tablename__='trackuser'
    id=Column(Integer, primary_key=True)
    uid=Column(Integer, ForeignKey("users.id"))
    height=Column(Integer())
    weight=Column(Integer())
    datechanged=Column(String())
    #usern = relationship("User",  back_populates="trackusers")
    

    def init(self, height, wegth, datechanged=None):
        self.uid=uid
        self.height=height
        self.weight=weight
        if datechanged is None:
            self.datechanged=datetime.utcnow()
        else:
            self.datechanged=datechangeds

    def __repr__(self):
        return'<Utrack %r>'%(self.uid)


class Product(Base):
    __tablename__='products'
    id = Column(Integer, primary_key=True)
    productname = Column(String(50))
    productImage = Column(String, unique=True)
    cost = Column(Integer())


    def __init__(self, productname=None, productImage=None,cost=None):
        self.productname=productname
        self.productImage=productImage
        self.cost=cost
        

    def __repr__(self):
        return '<Product %r>' % (self.productname)

