
def check_subset(big, small):
    j = 0
    not_found = 0
    for i in range(0, len(small)):
        found = False
        while j < len(big):
            if big[j] == small[i]:
                found = True
                j += 1
                break
            elif big[j] > small[i]:
                break
            else:
                j += 1
        if found is False:
            not_found += 1
    return not_found


def min_operation_subset_dp(larger_pattern, smaller_pattern, INF=100000000):
    dp = {}
    # Base Case
    for i in range(0, len(larger_pattern) + 1):
        dp[i] = {}
        for j in range(0, len(smaller_pattern) + 1):
            dp[i][j] = INF
    dp[0][0] = 0
    for i in range(1, len(smaller_pattern) + 1):
        dp[0][i] = dp[0][i-1] + len(smaller_pattern[i-1])
    for i in range(1, len(larger_pattern) + 1):
        dp[i][0] = 0
    # Iteration
    for i in range(1, len(larger_pattern) + 1):
        for j in range(1, len(smaller_pattern) + 1):
            value = check_subset(big=larger_pattern[i-1], small=smaller_pattern[j-1])
            if value == 0:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], value + dp[i][j - 1])
    return dp


def conversion(a):
    _str = []
    for i in range(0, len(a)):
        for j in range(0, len(a[i])):
            _str.append(a[i][j])
        _str.append(-1)
    return _str


def number_of_characters(a):
    _sum = 0
    for i in range(0, len(a)):
        _sum += len(a[i])
    return _sum


def subset_distance(a, b):
    print(a)
    print(b)
    num_a = number_of_characters(a)
    num_b = number_of_characters(b)
    INF = num_a + num_b + 10
    dp1 = min_operation_subset_dp(larger_pattern=a, smaller_pattern=b, INF=INF)
    dp2 = min_operation_subset_dp(larger_pattern=b, smaller_pattern=a, INF=INF)
    print(dp1)
    print(dp2)
    if dp1[len(a)][len(b)] <= dp2[len(b)][len(a)]:
        return dp1[len(a)][len(b)]
    else:
        return dp2[len(b)][len(a)]


if __name__ == "__main__":
    a = [[1], [2], [3]]
    b = [[4], [5], [3]]
    print(subset_distance(a,b))