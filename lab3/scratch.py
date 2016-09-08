def  factorialRemainder(n):
    if n == 1:
        return 1
    count = factorialRemainder(n-1)
    factorial = 1
    for next in xrange(n):
        if next != 0:
            factorial *= next
    if factorial%n == n-1:
        count += 1
    return count



print factorialRemainder(12)