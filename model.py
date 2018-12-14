import math

ageOffset = {'Traditional': 2, 'LowEnd': 5, 'HighEnd': 3, 'Performance': 2.5, 'Size': 2.5}
ageOffset = {'Thrift': 3, 'Core': 2, 'Nano': 1, 'Elite': 0}

#
# functions
#
def fitIn100(value):
  if value > 1.00:
    return 1.00
  elif value < 0:
    return 0.00
  else:
    return value

#
# classes
#
class Product:
  def __init__(self, name, pfmn, size, price, MTBF, age, awrns, accss, score=-1):
    self.name = name
    self.pfmn = pfmn
    self.size = size
    self.price = price
    self.MTBF = MTBF
    self.age = age
    self.awrns = awrns
    self.accss = accss
    self.score = score
    self.share = -1
    self.forecast = -1

class Segment:
  def __init__(self, name, lastDemand, growth, pfmn, size, positionWeight, age, ageWeight, maxPrice, minPrice, priceWeight, maxMTBF, minMTBF, MTBFWeight):
    self.name = name
    self.lastDemand = lastDemand
    self.growth = growth
    self.nextDemand = -1
    self.pfmn = {'value': pfmn, 'weight': positionWeight}
    self.size = {'value': size, 'weight': positionWeight}
    self.age = {'value': age, 'weight': ageWeight}
    self.ageOffset = ageOffset[name]
    self.price = {'high': maxPrice, 'low': minPrice, 'weight': priceWeight}
    self.MTBF = {'high': maxMTBF, 'low': minMTBF, 'weight': MTBFWeight}
    self.products = []
    self.totalScore = -1
    self.totalShare = -1
    self.totalForecast = -1
  
  def calculateNextDemand(self):
    self.nextDemand = self.lastDemand * (1 + self.growth)

  def calculatTotalScore(self):
    total = 0
    for p in self.products:
      total += p.score
    self.totalScore = total
  
  def calculateShare(self):
    for p in self.products:
      p.share = p.score / self.totalScore
  
  def calculateTotalShare(self):
    total = 0
    for p in self.products:
      total += p.share
    self.totalShare = total

  def calculateForecast(self):
    for p in self.products:
      p.forecast = p.share * self.nextDemand

  def calculateTotalForecast(self):
    total = 0
    for p in self.products:
      total += p.forecast
    self.totalForecast = total
  