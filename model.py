import sqlalchemy as sa
from getFreeIPS.config import BASE_DIR, IPDATA_DIR
import os

from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()
from sqlalchemy import Column, Integer, String

class IP(base):
    __tablename__ = "proxyIPs"
    id = Column(Integer, nullable=False)
    ip = Column(String(20), nullable=False, primary_key=True)
    port = Column(String(8), nullable=True)
    types = Column(Integer, default=0)
    protocol = Column(Integer, default=0)

    def __repr__(self):
        return "< ip:%s port:%s types: %d : protocol: %d >" % \
               (self.ip, self.port, self.types, self.protocol)

sqlite_URI = os.path.join(IPDATA_DIR, "ip.db")
if not os.path.exists(IPDATA_DIR):
    os.makedirs(IPDATA_DIR)
engine = sa.create_engine('sqlite:///' + sqlite_URI)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

base.metadata.create_all(engine)
