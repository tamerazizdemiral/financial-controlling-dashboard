import csv, random
from pathlib import Path
from datetime import date
random.seed(42)
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data';D.mkdir(exist_ok=True)
def write(name, fields, rows):
 with (D/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
centers=[('CC10','Sales'),('CC20','Operations'),('CC30','IT'),('CC40','Administration')]
products=[('P10','Software','Digital'),('P20','Consulting','Services'),('P30','Support','Services')]
write('cost_centers.csv',['CostCenterID','CostCenterName'],[dict(zip(['CostCenterID','CostCenterName'],x)) for x in centers])
write('products.csv',['ProductID','ProductName','ProductGroup'],[dict(zip(['ProductID','ProductName','ProductGroup'],x)) for x in products])
actual=[];budget=[]
for year in (2024,2025):
 for month in range(1,13):
  period=f'{year}-{month:02d}-01'
  for cc,_ in centers:
   for pid,_,_ in products:
    base={'P10':18000,'P20':12000,'P30':8000}[pid]*{'CC10':1.2,'CC20':0.9,'CC30':0.7,'CC40':0.4}[cc]
    season=1+0.08*(month-6)/6
    growth=1.08 if year==2025 else 1
    rev=round(base*season*growth*random.uniform(.88,1.12),2)
    cost=round(rev*random.uniform(.55,.82),2)
    budget_rev=round(base*season*growth*1.02,2)
    budget_cost=round(budget_rev*.67,2)
    actual.append(dict(Date=period,CostCenterID=cc,ProductID=pid,Revenue=rev,Costs=cost))
    budget.append(dict(Date=period,CostCenterID=cc,ProductID=pid,BudgetRevenue=budget_rev,BudgetCosts=budget_cost))
write('actuals.csv',['Date','CostCenterID','ProductID','Revenue','Costs'],actual)
write('budget.csv',['Date','CostCenterID','ProductID','BudgetRevenue','BudgetCosts'],budget)
print('Generated',len(actual),'actual and',len(budget),'budget rows')
