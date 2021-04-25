def intersecting(a, b):
    # A.X1 < B.X2 & A.X2 > B.X1 & A.Y1 < B.Y2 & A.Y2 > B.Y1
    return a[0][0] < b[1][0] and a[1][0] > b[0][0] and a[0][1] < b[1][1] and a[1][1] > b[0][1] 