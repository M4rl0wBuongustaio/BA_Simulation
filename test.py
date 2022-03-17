from resources import product_batch

p1 = product_batch.ProductBatch(5, 0, 2)
p2 = product_batch.ProductBatch(6, 1, 3)
p3 = product_batch.ProductBatch(8, 2, 4)
p4 = product_batch.ProductBatch(7, 3, 5)

stock = [p3, p1, p2]

for value in stock:
    print('Production date: ' + str(value.get_production_date()))

stock.sort(key=lambda pb: pb.get_production_date(), reverse=False)
stock.append(p4)
print('\n')
for value in stock:
    print('Production date: ' + str(value.get_production_date()))

i = -1
while len(stock) > 0:
    stock.remove(stock[i])
    print(stock)
