#
# scraping
#
import bs4 as bs
import os
import math
import model

Segment = model.Segment
Product = model.Product 

print('Enter file name to scrape (w/o .html):')
file = '{}.html'.format(input())

with open(os.path.join('courier', file), 'r', encoding='utf-8') as f:
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
      score = int(productTds[14].text.strip())

      product = Product(pname, ppfmn, psize, pprice, pMTBF, page, pawrns, paccss, score)
      segment.products.append(product)

    print('finished reading product data in {} segment.'.format(segment.name))
    segments.append(segment)

  except Exception as e:
    print('Error occurred in parsing product.')
    print(e)

# 
# write to csv
# 
import csv

try:
  f = open(os.path.join('output', 'data.csv'), 'w', encoding='UTF-8')
  writer = csv.writer(f, lineterminator='\n')
  for s in segments:
    writer.writerow([s.name])
    writer.writerow(['name', 'pfmn', 'size', 'price', 'MTBF', 'age', 'awrns', 'accss', 'score'])
    for p in s.products:
      writer.writerow([p.name, p.pfmn, p.size, p.price, p.MTBF, p.age, p.awrns, p.accss, p.score])
    writer.writerow([''])

except Exception as e:
  print('Error occurred in exporting to csv.')
  print(e)
