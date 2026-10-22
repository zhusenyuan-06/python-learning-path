#for i in range(1,11):
 #   print(i)

#total = 0
#i = 1
#while i<=100:                 # 条件：i 不超过多少就继续？
 #   total = total + i    # 把当前 i 加进总和（也可写 total += i）
  #  i = i + 1               # 让 i 前进，否则永远卡在 1 → 死循环（易错点①）
#print(total)



#num = [3,7,2,9,5]

#for i in num:
 #   if i > 5:
  #      print(i)



#t = 0
#while True:
 #   n = int(input('输入数字：'))
 #   if n ==0:
  #      break
   # t = t + n
#print(t)


a = [12, 5, 8, 20, 3]
max_val = a[0]        # 先假设第 1 个最大（注意：别写 0！）
for x in a:
    if x > max_val:   # 来了个更大的
        max_val = x                          # 填：让谁当新擂主？
print(max_val)
