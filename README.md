# Capsim Capstone Forecaster
## What it does
Forecast based on December customer survey score based on the principle below. It does not caclucate customer survey score.

> [3.2 Estimating the Customer Survey Score](http://ww3.capsim.com/guides/capstone_harvard2011/the-guide/3-the-customer-survey-score034f.html)
The customer survey score drives demand for your product in a segment. Your demand in any given month is your score divided by the sum of the scores. For example, if your product’s score in April is 20, and your competitors’ scores are 27, 19, 21, and 3, then your product’s April demand is:
20/(20+27+19+21+3) = 22%
Assuming you had enough inventory to meet demand, you would receive 22% of segment sales for April.

It will be a great starting point for your forecast. You have to take your decisions and your assumpitons on the competitors' decisions into considertation.

## How to use
1. Get your html version of courier. You can get it from report tab on your web decision spreadsheet.
1. Place your html courier in `courier` directory.
1. To scrape data out of yoru courier, run
```
python scrape.py
```
and input the name of your html courier wihtout extension. For exmpale, if your file name is `round0.html`,
```
Enter file name to scrape (w/o .html):
round0
```
and you can see scraped data in `data.csv` in `output` direcotry.
1. To forecast based on December survey score, run
```
python forecast.py
```
and input the name of your html courier wihtout extension. For exmpale, if your file name is `round0.html`,
```
Enter html file name you got data from (w/o .html):
round0
```
and you can see forecasted data in `forecast.csv` in `output` direcotry.