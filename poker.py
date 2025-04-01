import random
import numpy as np
import copy
import math

CARDS = {i for i in range(8, 60)}

class game:
    def __init__(self,players):
        self.players = players
        self.cards = copy.deepcopy(CARDS)
        self.RawCards = [[],[]]
        self.playerCards = [[],[]]
        self.middle = []
        self.hands = [[] for _ in range(players)]

    def get_card(self):
        selected = random.choice(list(self.cards))
        self.cards.remove(selected)
        return selected

    def hand_power(self,debug=False):
        #print(self.playerCards)
        hands = [self.RawCards[0] + self.RawCards[1], self.RawCards[1]]
        total = 0
        knownNo = [0] * 13
        knownSuit = [0] * 4
        knownRaw = [0] * 52
        knownNo[(self.RawCards[0][0] - 8) % 13] += 1
        knownNo[(self.RawCards[0][1]  - 8) % 13] += 1
        knownSuit[(self.RawCards[0][0] - 8) // 13] += 1
        knownSuit[(self.RawCards[0][1] - 8) // 13] += 1
        knownRaw[(self.RawCards[0][1] - 8)] = 1
        knownRaw[(self.RawCards[0][0] - 8)] = 1
        total1 = ((((self.RawCards[0][0]) - 8) % 13) + (((self.RawCards[0][1]) - 8) % 13))/24
        total2 = 1
        rem = 0

        for hi, hand in enumerate(hands):
            saves = [0] * 8
            solvedBit = [0] * 8
            nos = {}
            nums = [0] * 13
            suits = [0]*4
            value = 0
            cards = len(hand)
            left = 7-cards
            rawHand = [0]*52
            saves[0] = [0,0]
            maxSuit = [0] * 4

            log = ""

            #Pair - 13 - 13
            #Two Pair - 156 + 13 = 169
            #Tripple -


            for card in hand:
                rem += (card/12)
                no = (card-8)%13
                suit = (card-8)//13
                rawHand[card-8] = 1
                nums[no] += 1
                if no not in nos:
                    nos[no] = 1
                else:
                    nos[no] += 1
                #print(suit)
                #print(f"{card} -> {suit}")
                suits[suit] += 1
                maxSuit[suit] = max(maxSuit[suit], no, 2)


            #Quad: Start with one good card and one different. There would then be 50 cards in the deck, and 5 cards left to pull
            #To get the favorable outcome you would need to select 3 more cards from this 50 - leaving 47 cards, and 2 left to draw.
            #Regardless of order that means that there would be (C 47,2) or valid combinations. Or imagine (G, R, G*, G*,G*,_,_).
            #Divide this by total hands



            for card,ammount in nos.items():
                handRankUp = (card / 6)
                handRank = card/12
                if hi == 1:
                    save = hypergeometric(cards, ammount, 2, knownNo[card], 2)
                else:
                    save = hypergeometric(cards, ammount, 2, knownNo[card], 0)

                score = (1 + handRankUp) * save #Pair
                if save == 1:
                    solvedBit[0] = 1
                if score > saves[0][0]:
                    saves[0][1] = max(saves[0][1], saves[0][0])
                    saves[0][0] = score

                else:
                    saves[0][1] = max(saves[0][1], score)
                log += (f'\nPAIR {score}')
                save = 0
                if hi == 1:
                    save = hypergeometric(cards,ammount,3, knownNo[card], 2)

                else:
                    save = hypergeometric(cards, ammount, 3,0, 0)
                score = (6 + handRankUp) * save  # Trips
                saves[2] = max(saves[2], score)
                log += (f'\nTRIP {score}')
                if save == 1:
                    solvedBit[2] = 1



                save = hypergeometric(cards, ammount, 4, knownNo[card],2)
                score = (10 + handRank) * save #Quads
                saves[6] = max(saves[6], score)
                log += (f'\nQUADS {score}')
                if save == 1:
                    solvedBit[6] = 1

                for card2, ammount2 in nos.items():
                    if card2 != card : #Arbitarty check greater than to only count one card
                        handRank = (((card * 12) + card2)/155)

                        if card >= card2 and ammount2 + ammount >= 2:
                            save = pairs_hypergeometric(cards,ammount,ammount2,2,2,knownNo[card], knownNo[card2],2)
                            score = (3 + (handRank*3)) * save #Two Pair

                            saves[1] = max(saves[1],score)
                            if save == 1:
                                solvedBit[1] = 1
                        log += (f'\n2Pair {score}')
                        if (ammount2 + ammount >= 2):
                            save = 0
                            if hi == 1:
                                save = pairs_hypergeometric(cards,ammount,ammount2,3,2, knownNo[card], knownNo[card2],2)
                            else:
                                save = pairs_hypergeometric(cards, ammount, ammount2, 3, 2,0,0, 0)
                            score = (9 + handRank) * save #Full House
                            saves[5] = max(saves[5], score)
                            if save == 1:
                                solvedBit[5] = 1
                        log += (f'\nFULL HOUSE {saves[5]} {save}')

            if hi == 1:
                if solvedBit[0] == 0:
                    saves[0][0] = 0.1167
                elif saves[0][1] == 0:
                    saves[0][1] = 0.1167
                if solvedBit[1] == 0:
                    saves[1] = 0.5248
            last = 0
            known = 0
            for i in range(13):
                if i < 4:
                    last += min(1,nums[i])
                    known += min(1,knownNo[i]) - min(1,nums[i])
                else:
                    plast = last
                    last = max(0,last - min(1,nums[i-5]) + min(1,nums[i]))
                    known = max(0,known + min(1, knownNo[i]) - min(1, nums[i]) - (min(1, knownNo[i-5]) - min(1, nums[i-5])))
                    handRank = (7 + ((i - 4) / 8))
                    if 5-last <= left and last > 1:
                        save = 0
                        if hi == 1:
                            save = run_hypergeometric(cards, last,known,2) #Stright
                        else:
                            save = run_hypergeometric(cards, last, 0,0)  # Stright
                        score = handRank * save
                        saves[3] = max(saves[3], score)

                        if save == 1:
                            solvedBit[3] = 1
            log += (f'\nRUNS {saves[3]}')
            maxsuit, maxindex = max((value, index) for index, value in enumerate(suits))


            if (5 - maxsuit) <= left and maxsuit > 1:
                save = 0
                if hi == 1:
                    save = suit_hypergeometric(cards, last,knownSuit[maxindex],2)
                else:
                    save = suit_hypergeometric(cards, last,0,0)
                if save == 1:
                    solvedBit[4] = 1
                saves[4] = (8 + (maxsuit / 12)) * save  # Suits

            log += (f'\nSUITS {saves[4]}')

            last = 0
            known = 0
            if (5 - maxsuit) <= left and maxsuit > 1:
                barrier = (maxindex * 13) + 4
                for i in range(maxindex * 13, maxindex * 13 + 13):
                    if i < 4:
                        last += min(1,rawHand[i])
                        known += min(1, knownRaw[i]) - min(1, nums[i])
                    else:
                        last = last - rawHand[i-4] + rawHand[i]
                        handRank = (11 + (((i%13)-5) / 8))
                        known = max(0, known + min(1, knownRaw[i]) - min(1, rawHand[i]) - (
                                    min(1, knownRaw[i - 5]) - min(1, rawHand[i - 5])))

                        if 5-last <= left and last > 1:
                            save = 0
                            if hi == 1:
                                save = run_hypergeometric(cards,last,known,True,2)
                            else:
                                save = run_hypergeometric(cards,last,0, True,0)
                            scores = handRank * save
                            saves[7] = max(scores, saves[7])
                            if save == 1:
                                solvedBit[7] = 1
            log += (f'\nRUNS FLUSH {value}')
            for i in range(0,8):
                if i == 7:
                    value += saves[7-i][0] + saves[7-i][1]
                else:
                    value += saves[7-i]
                log += f"\t{value}   {total2}\n"
                if solvedBit[7-i] == 1:
                    break;


            if debug:
                print(log)

            if hi == 0:
                total1 += value
            else:
                total2 = ((0.5 * 52 - rem) / (52 - cards)) + value
                total2 *= (self.players - 1)

        return round(total1,0), round(total2,0)







    def deal(self,i):
        if i == 0:
            for _ in range(2):
                for i in range(self.players):
                    pull = self.get_card()
                    self.hands[i].append(pull)
                    if i == 0:
                        self.identifyCard(pull,0)
            self.burn()
        elif i == 1:
            self.center(3)
        else:
            self.center(1)

        return self.playerCards[0],self.playerCards[1]

    def burn(self):
        self.get_card()


    def identifyCard(self,card,type):
        cardS = card-8
        suit = cardS//13
        if suit == 0:
            cardS = f"{cardS%13}-D"

        elif suit == 1:
            cardS = f"{cardS%13}-C"
        elif suit == 2:
            cardS = f"{cardS%13}-H"
        else:
            cardS = f"{cardS%13}-S"

        if type == 0: #Hand
            self.playerCards[0].append(cardS)
            self.RawCards[0].append(card)
            return
        self.playerCards[1].append(cardS)
        self.RawCards[1].append(card)
        return



    def center(self,n):
        for _ in range(n):
            pull = self.get_card()
            self.middle.append(pull)
            self.identifyCard(pull, 1)
        self.burn()

    def winner(self):
        best = [0] * len(self.hands)
        for a, hand in enumerate(self.hands):
            use = hand + self.middle
            #print(self.hands)
            numbers = []
            suits = []
            sets = [0] * 13
            types = [0] * 4
            pairs = []
            trios = []

            flush = None
            straight = None
            full_House = None
            two_Pair = None
            three = None
            four = None
            pair = None

            numbers = set()
            mycards = []
            for card in use:
                no = (card - 8) % 13
                suit = (card - 8) // 13
                numbers.add(no)
                mycards.append(no)
                suits.append(suit)
                sets[no] += 1
                types[suit] += 1
            streak = 0
            last = None
            #print(sets)
            for i, no in enumerate(sets):
                if no == 4:
                    four = i
                elif no == 3:
                    trios.append(i)
                elif no == 2:
                    pairs.append(i)
                if last is not None and no > 0 and i - last == 1:
                    streak += 1
                else:
                    if streak >= 5:
                        straight = i
                    streak = 0
                last = i
            if streak >= 5:
                straight = i
            for i, no in enumerate(types):
                if no >= 5:
                    flush = []
                    for card in use:
                        num = (card - 8) % 13
                        if (card - 8) // 13 == i:
                            flush.append(num)
                    flush.sort()
                    flush.reverse()
                    diff = 5 - len(flush)
                    flush = flush[diff:]
                    
            if len(pairs) >= 2:
                two_Pair = [pairs[-1], pairs[-2]]
            elif len(pairs) == 1:
                pair = pairs[0]

            if len(trios) > 0:
                three = trios[-1]

            if len(pairs) > 0 and len(trios) > 0:
                full_House = [trios[-1], pairs[-1]]


            if flush is not None and straight is not None:
                use.sort()
                last = None
                streak = 0
                for card in use:
                    if last != None and i - last == 1 and (last - 8) // 13 == (card - 8) // 13:
                        streak += 1
                    else:
                        if streak >= 5:
                            best[a] = [8, (last - 8) // 13]
                        streak = 1
                    last = card
                    best[a] = [8, (last - 8) // 13]
                if streak >= 5:
                    best[a] = [8, (last - 8) // 13]
            if best[a] == 0:
                if four is not None:
                    best[a] = [7, four, max(numbers - {four})]
                elif full_House is not None:
                    best[a] = [6, full_House]
                elif flush is not None:
                    best[a] = [5, flush]
                elif straight is not None:
                    best[a] = [4, straight]
                elif three is not None:
                    best[a] = [3, three, sorted(numbers - {three}, reverse=True)[:2]]
                elif two_Pair is not None:
                    best[a] = [2, two_Pair, max(numbers - {two_Pair[0], two_Pair[1]})]
                elif pair is not None:
                    best[a] = [1, pair, sorted(numbers - {pair}, reverse=True)[:3]]
                else:
                    mycards.sort()
                    mycards.reverse()
                    best[a] = [0, mycards[:5]]

        winners = []
        win = max(best)
        for i, hand in enumerate(best):
            if hand == win:
                winners.append(i)

        return winners


Q = {}  # Q-table
alpha = 0.1  # Learning rate
gamma = 0.99  # Discount factor
epsilon = 1.0  # Exploration rate
epsilon_decay = 0.99995
min_epsilon = 0.01
actions = [1,5, 10, 20,50, -1]  # Call, Raise 1, Raise 10, Raise 20, Fold


def play(players):
    global epsilon
    round = game(players)
    hand, center = round.deal(0)
    state = (round.hand_power(), 0)  # Initial state: (hand, middle cards, bet)
    bet = 1
    reward = 0
    total_reward = 0
    for stage in range(1, 5):  # Betting stages
        if state not in Q:
            Q[state] = {a: random.uniform(0, 0.1) for a in actions}  # Initialize actions for this state
            #print(f' {Q[state]}')
            print("NEW STATE - FOLD")



        # Select action
        if random.uniform(0, 1) < epsilon:
            action = random.choice(actions)  # Explore
        else:
            action = max(Q[state], key=Q[state].get)  # Exploit

        # Perform action
        if action == -1:  # Fold
            reward = -bet  # Penalty for folding
            total_reward += reward
            break
        else:
            bet += action  # Update bet amount
            hand, center = round.deal(stage)

        # Determine reward at the end of the game
        if stage == 4:
            winners = round.winner()
            if 0 in winners:
                reward = bet * 4
            else:
                reward = -bet - max(100,bet * 2)
            total_reward += reward

        # Update Q-table
        next_state = (round.hand_power(), bet, stage)
        if next_state not in Q:
            Q[next_state] = {a: 0 for a in actions}

        Q[state][action] += alpha * (reward + gamma * max(Q[next_state].values()) - Q[state][action])
        state = next_state  # Transition to next state

    # Decay exploration rate
    epsilon = max(min_epsilon, epsilon * epsilon_decay)


# Train the agent


def jaytrain(players, games=100, test=0):
    global epsilon
    print(actions)
    bet = 1



    def test(hands, bet, stage):
        result = 0
        attempts = actions

        state = (hands[stage][0],hands[stage][1] , stage, bet)
        if state in Memo:
            return Memo[state]
        if state not in Q:
            Q[state] = {a: [0,np.empty(0)] for a in actions}
        else:
            if len(Q[state][1][1]) > 10:
                actions_sorted = sorted(Q[state].items(), key=lambda x: x[1][0], reverse=True)
                attempts = (actions_sorted[0][0], actions_sorted[1][0])
        stageResult = float('-inf')
        save = ""
        for action in attempts:
            betting = bet
            if action == -1:
                result = -betting
                stageResult = max(-bet,stageResult)
            else:
                betting += action
                if stage >= 3:
                    result = -betting * 1 #Penalty for False Confidence
                    if 0 in hands[4]:
                        result = betting * 3
                    stageResult = max(stageResult, result)
                else:
                    result = test(hands, betting, stage + 1)
                    stageResult = max(stageResult,result)

            Q[state][action][1] = np.append(Q[state][action][1], result)
            Q[state][action][0] = np.median(Q[state][action][1]) * 0.4 + np.average(Q[state][action][1] * 0.6)
        Memo[state] = stageResult
        return stageResult


    for _ in range(games):
        round = game(players)
        hands = [[0,0]for _ in range (players)]
        for i in range(4):
            round.deal(i)
            power,anti = round.hand_power()
            hands[i][0] = power
            hands[i][1] = anti
        hands[4] = round.winner()
        print(f'{round.playerCards}')
        Memo = {}
        test(hands, bet, 0)

    output = open("QTable.txt", "w")
    for row in Q:
        print(f'{row}')
        for item in Q[row]:
            print(f'\t{item}:{Q[row][item]}')
            output.write(f'{row}\n\t{item}:{Q[row][item]}')
    print("d")

def runBot(games):
    print("RUNNGING BOT\n\n\n")
    global Q, epsilon
    money = 0
    totalBets = 0
    for _ in range(games):
        round = game(5)  # Simulate a game
        bet = 1
        state = None
        fold = False
        for i in range(4):  # Play each stage
            round.deal(i)
            power, anti = round.hand_power()
            state = (power,anti, i, bet)
            print(f"State {round.playerCards}-> {round.hands} | {round.middle} -> {state}")
            if state not in Q:
                print(f"New State {state}")
                Q[state] = {a: [0, np.empty(0)] for a in actions}
                action_key = -1
            else:
                actions = Q[state]
                max_action = max(actions.items(), key=lambda x: x[1][0])
                action_key, (max_value, _) = max_action


            print(f"ON {round.playerCards} || {state} ACTION -> {action_key}")
            # Execute action
            if action_key == -1:
                fold = True
                print("Bot folds")
                break
            else:
                bet += action_key

        # End of game, evaluate results
        totalBets += bet
        if 0 in round.winner() and not fold:
            print(f"BOT WINS {bet * 3}")
            money += bet * 3
        else:
            print(f"BOT LOSES {bet}")
            money -= bet

    print(f"Game finished. Winner: {totalBets}  {money}")


def hypergeometric(selected, ammount, needed, known, totKnown):
    if ammount >= needed:
        return 1
    elif 7 - selected  < 2 - ammount:
        return 0
    try:
        toSelect = 7 - selected
        cardsLeft = 52 - selected - totKnown
        sameRemaining = 4 - ammount - known
        otherRemaining = cardsLeft - sameRemaining - (2 - known)

        value = (math.comb(sameRemaining,needed-ammount) * math.comb(otherRemaining,toSelect-(needed-ammount)))/math.comb(cardsLeft,toSelect)
        return value

    except ValueError:
        return 0

def pairs_hypergeometric(selected, ammount, ammount2, needed, needed2,known, known2, totKnown):

    if ammount >= needed and ammount2 >= needed2:
        return 1
    elif 7 - selected  < 4 - max(2,ammount) - max(2,ammount2):
        return 0
    try:
        toSelect = 7 - selected
        cardsLeft = 52 - selected - totKnown
        sameRemaining = 4 - ammount - known
        sameRemaining2 = 4 - ammount2 - known2
        otherRemaining = cardsLeft - sameRemaining - sameRemaining2 - (2 - known - known2)
        value = (math.comb(sameRemaining,needed-ammount) * math.comb(sameRemaining2,needed2-ammount2) * math.comb(otherRemaining,toSelect-(needed-ammount) - (needed2 - ammount2)))/math.comb(cardsLeft,toSelect)
        return value
    except ValueError:
        return 0

def run_hypergeometric(selected, ammount, known, totKnown, type=False):

    if ammount >= 5:
        return 1
    elif 7 - selected  < 5 - ammount:
        return 0
    try:
        toSelect = 7 - selected
        cardsLeft = 52 - selected - totKnown
        sheild = (ammount/5)**2
        if not type:
            sameRemaining = 20 - (ammount * 4) - known
        else:
            sameRemaining = 5 - ammount - (2-known)
        otherRemaining = 47 - (selected - ammount)
        value = (math.comb(sameRemaining,5-ammount) * math.comb(otherRemaining,2 - (selected - ammount)))/math.comb(cardsLeft,toSelect) * sheild
        #print(f"{math.comb(sameRemaining,5-ammount)} * {math.comb(otherRemaining,2 - (selected - ammount))} ) / {math.comb(cardsLeft,toSelect)} -> {value} * ({ammount}) -> {sheild} = {value * sheild}")
        return value
    except ValueError:
        return 0

def suit_hypergeometric(selected, ammount, known, totKnown):
    if 5 == ammount:
        return 1
    elif 7 - selected  < 5 - ammount:
        return 0
    try:
        toSelect = 7 - selected
        cardsLeft = 52 - selected - totKnown
        sameRemaining = 13 - ammount - known
        otherRemaining = cardsLeft - sameRemaining - (2-known)
        value = (math.comb(sameRemaining, 5 - ammount) * math.comb(otherRemaining, toSelect - (5 - ammount))) / math.comb(
            cardsLeft, toSelect)
        return value
    except ValueError:
        return 0


jaytrain(5,100000)
runBot(10000)
g = game(5)
