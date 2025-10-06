
l1 = [[[1, 2, 3, 4], [2,3,4,5,6]]]
l2 = [[[4,5,6,7], [2,5,7,9]]]

sdx = []

sdx.append(l1[0][0])
sdx.append(l2[0][0])

dx = [x for sublist in sdx for x in sublist]

print(dx)