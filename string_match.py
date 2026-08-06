"""
string_match.py
----------------
Detects near-duplicate firm names using LEVENSHTEIN (EDIT) DISTANCE,
implemented from scratch with dynamic programming.

WHY THIS MATTERS FOR FRAUD DETECTION:
Fraudsters sometimes register shell firms with names that are almost
identical to a real firm ("Shreeji Trading Co" vs "Shreeji Traderz Co")
to look like separate legitimate businesses while really being connected.
Exact string matching (==) would miss this completely. Edit distance
catches "close but not identical" names.

EDIT DISTANCE = the minimum number of single-character edits
(insert, delete, substitute) needed to turn string A into string B.
Small distance -> very similar names -> suspicious.
"""


def levenshtein_distance(s1, s2):
    """Classic DP solution.

    dp[i][j] = edit distance between the first i characters of s1
               and the first j characters of s2.

    Base cases:
        dp[i][0] = i   (delete all i characters of s1 to get empty string)
        dp[0][j] = j   (insert all j characters to build s2 from empty)

    Transition:
        if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1]   (chars match, no edit needed)
        else: dp[i][j] = 1 + min(
                dp[i-1][j],     # delete a char from s1
                dp[i][j-1],     # insert a char into s1
                dp[i-1][j-1]    # substitute a char
              )
    """
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    m, n = len(s1), len(s2)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],       # delete
                    dp[i][j - 1],       # insert
                    dp[i - 1][j - 1]    # substitute
                )

    return dp[m][n]


def find_suspicious_name_pairs(firm_names, max_distance=3):
    """Compare every pair of DIFFERENT firm names. If their edit distance is
    small (but not 0 — identical names aren't suspicious, they're the same firm)
    flag them as a possible shell-firm disguise.

    NOTE: this is O(n^2) comparisons for n firms — fine for a resume project
    with a few hundred firms, but worth mentioning as a scaling limitation
    if asked in an interview (could bucket by first letter/length first to
    cut down comparisons).
    """
    unique_names = list(set(firm_names))
    suspicious_pairs = []

    for i in range(len(unique_names)):
        for j in range(i + 1, len(unique_names)):
            name_a, name_b = unique_names[i], unique_names[j]
            distance = levenshtein_distance(name_a, name_b)
            if 0 < distance <= max_distance:
                suspicious_pairs.append({
                    "name_a": name_a,
                    "name_b": name_b,
                    "edit_distance": distance
                })

    return suspicious_pairs
