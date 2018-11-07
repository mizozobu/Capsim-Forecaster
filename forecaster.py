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
  def __init__(self, name, pfmn, size, price, MTBF, age, awrns, accss):
    self.name = name
    self.pfmn = pfmn
    self.size = size
    self.price = price
    self.MTBF = MTBF
    self.age = age
    self.awrns = awrns
    self.accss = accss
    self.score = -1
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
  
  def calculateScore(self):
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
        pricePenalty = (p.price - self.price['high']) * 0.2
      elif p.price <= self.price['low']:
        pricePenalty = (self.price['low'] - p.price) * 0.2
      else:
        pricePenalty = 0

      if reliabilityPercentile > 0:
        reliabilityPenalty = 0
      elif p.MTBF >= self.MTBF['high']:
        reliabilityPenalty = (p.MTBF - self.MTBF['high']) / 1000 * 0.2
      elif p.MTBF <= self.MTBF['low']:
        reliabilityPenalty = (self.MTBF['low'] - p.MTBF) / 1000 * 0.2

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
  
#
# scraping
#
import bs4 as bs
import math

print('Enter file name to analyze (w/o .html):')
file = '{}.html'.format(input())

print('Enter A/R days:')
AR = int(input())

with open(file, 'r', encoding='utf-8') as f:
  source= f.read()

soup = bs.BeautifulSoup(source, 'lxml')

#
# constants
#
indexMap = {'Traditional': 64, 'LowEnd': 79, 'HighEnd': 94, 'Performance': 109, 'Size': 124}
ageOffset = {'Traditional': 2, 'LowEnd': 5, 'HighEnd': 3, 'Performance': 2.5, 'Size': 2.5}
ARPenalty = {'90': 0.00, '60': 0.01, '30': 0.07, '0': 0.40}

#
# segment
#
segments = []
for segmentName, index in indexMap.items():
  try:
    lastDemand = int(soup.find_all('table')[index - 3].find_all('tr')[1].find_all('td')[1].text.strip().replace(',', ''))
    growth = float(soup.find_all('table')[index - 2].find_all('td')[1].text.strip()[:-1]) * 0.01
    
    segmentTrs = soup.find_all('table')[index].find_all('tr')
    parsedName = segmentTrs[0].find('center').text.strip().split(' ')[:-3]
    sname = "".join(parsedName)
    for x in range(2, 6):
      elem = segmentTrs[x].find_all('td')
      sweight = int(elem[3].text.strip()[:-1]) * 0.01
      val = elem[2]
      if elem[1].text.strip() == 'Reliability':
        parsedMTBF = val.text[4:].split('-')
        sminMTBF = int(parsedMTBF[0])
        smaxMTBF = int(parsedMTBF[1])
        sMTBFWeight = sweight
      elif elem[1].text.strip() == 'Age':
        sage = float(val.text.split(' = ')[1])
        sageWeight = sweight
      elif elem[1].text.strip() == 'Price':
        parsedPrice = val.text[1:].split(' - ')
        sminPrice = float(parsedPrice[0])
        smaxPrice = float(parsedPrice[1])
        spriceWeight = sweight
      elif elem[1].text.strip() == 'Ideal Position':
        parsedPosition = val.text.split(' ')
        spfmn = float(parsedPosition[1])
        ssize = float(parsedPosition[3])
        spositionWeight = sweight
      else:
        print('Error occurred in parsing segment')
    
    segment = Segment(sname, lastDemand, growth, spfmn, ssize, spositionWeight, sage, sageWeight, smaxPrice, sminPrice, spriceWeight, smaxMTBF, sminMTBF, sMTBFWeight)
  
  except Exception as e:
    print('Error occurred in parsing segment')
    print(e)
  
  #
  # products in segment
  #
  try:
    products = soup.find_all('table')[index + 4].find_all('tr')
    for i in range(1, len(products)):
      productTds = products[i].find_all('td')
      pname = productTds[0].text.strip()
      ppfmn = float(productTds[5].text.strip())
      psize = float(productTds[6].text.strip())
      pprice = float(productTds[7].text.strip()[1:])
      pMTBF = int(productTds[8].text.strip())
      page = float(productTds[9].text.strip())
      pawrns = int(productTds[11].text.strip()[:-1]) * 0.01
      paccss = int(productTds[13].text.strip()[:-1]) * 0.01

      product = Product(pname, ppfmn, psize, pprice, pMTBF, page, pawrns, paccss)
      segment.products.append(product)

    print('finished reading product data in {} segment.'.format(segment.name))
    segments.append(segment)

  except Exception as e:
    print('Error occurred in parsing product.')
    print(e)

# 
# forecast calculation
# 
try:
  for segment in segments:
    segment.calculateNextDemand()
    segment.calculateScore()
    segment.calculatTotalScore()
    segment.calculateShare()
    segment.calculateTotalShare()
    segment.calculateForecast()
    segment.calculateTotalForecast()
  
except Exception as e:
  print('Error occurred in calculation.')
  print(e)

# 
# write to csv
# 
import csv

try:
  f = open('forecast.csv', 'w', encoding='UTF-8')
  writer = csv.writer(f, lineterminator='\n')
  for segment in segments:
    writer.writerow([segment.name])
    writer.writerow(['Last Year', 'Growth', 'This Year'])
    writer.writerow([segment.lastDemand, segment.growth, segment.nextDemand])
    writer.writerow(['Product', 'Survey Score', 'Share', 'Forecast'])
    for product in segment.products:
      writer.writerow([product.name, product.score, product.share, product.forecast])
    writer.writerow(['Total', segment.totalScore, segment.totalShare, segment.totalForecast])
    writer.writerow([''])
    writer.writerow([''])
except Exception as e:
  print('Error occurred in exporting to csv.')
  print(e)
