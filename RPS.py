def player(prev_play, opponent_history=[]):
    # Persistent state stored on the function itself.
    if not hasattr(player, "opp"):
        player.opp = []
        player.own = []
        player.scores = {}
        player.last_preds = {}

    # Reset at the start of each match.
    if prev_play == "":
        player.opp = []
        player.own = []
        player.scores = {}
        player.last_preds = {}
    else:
        # Score the predictions made on the previous call.
        for name, pred in player.last_preds.items():
            if pred is not None:
                arr = player.scores.setdefault(name, [])
                arr.append(1 if pred == prev_play else 0)
                if len(arr) > 50:
                    arr.pop(0)

        player.opp.append(prev_play)

    opp = player.opp
    own = player.own
    n = len(opp)
    preds = {}

    def most_common(seq):
        counts = {}
        for x in seq:
            counts[x] = counts.get(x, 0) + 1
        return max(counts, key=counts.get) if counts else None

    # Predict from patterns in the opponent's own moves.
    for k in range(1, 9):
        if n >= k:
            ctx = "".join(opp[-k:])
            next_moves = []
            for i in range(n - k):
                if "".join(opp[i:i + k]) == ctx:
                    next_moves.append(opp[i + k])
            if next_moves:
                preds[f"opp{k}"] = most_common(next_moves)

    # Predict from patterns in our own moves.
    # This handles bots that react to what we play, like kris and abbey.
    m = len(own)
    for k in range(1, 9):
        if m >= k:
            ctx = "".join(own[-k:])
            next_moves = []
            for i in range(m - k):
                if "".join(own[i:i + k]) == ctx and i + k < n:
                    next_moves.append(opp[i + k])
            if next_moves:
                preds[f"own{k}"] = most_common(next_moves)

    # mrugesh-style predictor: counters the most frequent of our last 10 moves.
    if m > 0:
        last_ten = own[-10:]
        frequent = max(set(last_ten), key=last_ten.count)
        ideal_response = {"R": "P", "P": "S", "S": "R"}
        preds["mrugesh"] = ideal_response[frequent]

    # Pick the predictor with the best recent Laplace-smoothed accuracy.
    best_name = None
    best_score = -1.0
    best_count = -1

    for name, pred in preds.items():
        if pred is None:
            continue

        hist = player.scores.get(name, [])
        score = (sum(hist) + 1.0) / (len(hist) + 2.0)
        count = len(hist)

        if score > best_score or (score == best_score and count > best_count):
            best_score = score
            best_count = count
            best_name = name

    if best_name is not None:
        predicted_opponent = preds[best_name]
    else:
        predicted_opponent = prev_play if prev_play else "R"

    counter = {"R": "P", "P": "S", "S": "R"}
    guess = counter[predicted_opponent]

    player.last_preds = preds
    player.own.append(guess)

    return guess