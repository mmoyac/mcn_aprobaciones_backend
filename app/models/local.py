from sqlalchemy import Column, Integer, String, SmallInteger
from app.db.base_class import Base


class Local(Base):
    __tablename__ = "loc001"

    Loc_cod = Column(SmallInteger, primary_key=True, nullable=False)
    Loc_des = Column(String(30), nullable=False)
    loc_est = Column(SmallInteger, nullable=False, default=0)
