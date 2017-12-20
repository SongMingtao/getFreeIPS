from getFreeIPS.model import session, IP
import random

'''
num is the ip's count that you want
'''
def getfreeipByNum(num):
    return session.query(IP).all()[1:num+1]

def getfreeip():
    return random.choice(session.query(IP).all())

def getfreeipByRange(start, end):
    return session.query(IP).all()[start: end]

from getFreeIPS.config import get_header

