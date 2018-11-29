#
# scraping
#
import bs4 as bs
import csv
import os
import math
import model

Segment = model.Segment
Product = model.Product 

print('Enter html file name you got data from (w/o .html):')
htmlFile = '{}.html'.format(input())
     
with open(os.path.join('courier', htmlFile), 'r', encoding='utf-8') as f:
  source= f.read()

soup = bs.BeautifulSoup(source, 'lxml')

#
# constants
#
indexMap = {'Traditional': 64, 'LowEnd': 79, 'HighEnd': 94, 'Performance': 109, 'Size': 124}

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
    segments.append(segment)

  except Exception as e:
    print('Error occurred in parsing segment')
    print(e)
  
#
# products in segment
#
with open(os.path.join('output', 'data.csv'), 'r', encoding='UTF-8', newline='\n') as file:
  rowsInData = csv.reader(file, delimiter=',')
  currentSegemnt = None
  currentSegemntName = None
  for row in rowsInData:
    try:
      name = row[0]
      pfmn = float(row[1])
      size = float(row[2])
      price = float(row[3])
      MTBF = float(row[4])
      age = float(row[5]) + 1
      awrns = float(row[6])
      accss = float(row[7])
      score = float(row[8])

      product = Product(name, pfmn, size, price, MTBF, age, awrns, accss)
      product.score = score
      currentSegemnt.products.append(product)

    except Exception as e:
      try:
        # segement title row
        currentSegemnt = [s for s in segments if s.name == row[0]][0]

      except Exception as e:
        # blank row and header row
        pass
  
# 
# forecast calculation
# 
try:
  for segment in segments:
    segment.calculateNextDemand()
    # segment.calculateScore()
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
try:
  f = open(os.path.join('output', 'forecast.csv'), 'w', encoding='UTF-8')
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
