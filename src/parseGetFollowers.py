from operator import itemgetter, attrgetter

filename = 'results.txt'

f = open(filename, 'r')
count = 0
num_followers = 1
friends = []

for line in f:
    if count == 0:
        num_followers = int(line)
        count += 1
    else:
        friend = map(int, line.replace(' ', '').split(':'))
        friend[1] /= float(num_followers)
        friends.append((friend[0], friend[1]))

f.close()

friends = sorted(friends, key=itemgetter(1, 0), reverse=True)
for i in range(5):
    print friends[i]
