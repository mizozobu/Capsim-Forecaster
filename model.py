import math

ageOffset = {'Traditional': 2, 'LowEnd': 5, 'HighEnd': 3, 'Performance': 2.5, 'Size': 2.5}
ARPenalty = {'90': 0.00, '60': 0.01, '30': 0.07, '0': 0.40}

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
  
  def calculateScore(self, AR):
    for p in self.products:
      pricePercentile = fitIn100(1 - (p.price - self.price['low']) / 10)
      reliabilityPercentile = fitIn100((p.MTBF - self.MTBF['low']) / 5000)
      agePercentile = fitIn100(1 - 0.9 * abs(p.age - self.age['value']) / self.ageOffset)
      positionercentile = fitIn100(1 - math.sqrt((p.pfmn - self.pfmn['value']) ** 2 + (p.size - self.size['value']) ** 2) / 4)

      priceScore = self.price['weight'] * pricePercentile * 100
      reliabilityScore = self.MTBF['weight'] * reliabilityPercentile * 100
      ageScore = self.age['weight'] * agePercentile * 100
      positionScore = self.pfmn['weight'] * positionercentile * 100

      if pricePercentile < 0:
        pricePenalty = 0
      elif p.price >= self.price['high']:
        pricePenalty = fitIn100((p.price - self.price['high']) * 0.2)
      elif p.price <= self.price['low']:
        pricePenalty = fitIn100((self.price['low'] - p.price) * 0.2)
      else:
        pricePenalty = 0

      if reliabilityPercentile > 0:
        reliabilityPenalty = 0
      elif p.MTBF >= self.MTBF['high']:
        reliabilityPenalty = fitIn100((p.MTBF - self.MTBF['high']) / 1000 * 0.2)
      elif p.MTBF <= self.MTBF['low']:
        reliabilityPenalty = fitIn100((self.MTBF['low'] - p.MTBF) / 1000 * 0.2)

      totalScore = priceScore + reliabilityScore + ageScore + positionScore
      totalScoreAfterARPenalty = totalScore * (1 - ARPenalty[str(AR)])
      adjustedTotalScoreAfterARPenalty = (totalScoreAfterARPenalty / 10) ** 2
      adjustedTotalScoreAfterARPenaltyAndPromoPenalty = adjustedTotalScoreAfterARPenalty - (1 - p.awrns) / 2 * (1 - p.accss) / 2 * adjustedTotalScoreAfterARPenalty
      p.score = adjustedTotalScoreAfterARPenaltyAndPromoPenalty * (1 - pricePenalty) * (1 - reliabilityPenalty)

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
  