# Machine Learning Poker Bot
### Created by Jason Van Humbeck

Passionate about Machine Learning, AI algorithms, and probability, I wanted to pursue a project at the intersection of all three fields. Since I was a kid, I’ve always been interested in forecasting and probability in board and card games (*nerdy, I know*) — starting with Monopoly and eventually reaching poker.

Poker fascinated me because, more than most other games, winning can be nearly 100% determined by math and probability. This got me thinking: could a Machine Learning algorithm learn to master poker's deterministic side?

---

## 1. Building a Heuristic

- No two poker hands are the same — among 5 players, there are C(52, 7) = 4,481,381,400,000 possible hands. This makes traditional ML algorithms ineffective.
- Standard ML libraries rely on repeated inputs producing consistent outputs. But poker hands are *nearly random*, which blinds the model.
- To solve this, I built a **heuristic** to assign a score or hand ranking, drastically reducing the input space.
- Using hypergeometric distributions, discrete math, and probability, I calculated a hand score (1–~30) based on the likelihood of each hand rank and sub-rank.
    - Example: 2 = Pair; 2.1/13 = Pair of 2s; 2.11/13 = Pair of Queens
- This score is used to represent hand strength and estimate cumulative win probabilities contrasted against the opponents hand, which are then passed into the algorithm.

---

## 2. Recursive Q-Learning Algorithm

- Q-Learning works by simulating game states, taking actions, and updating state values based on long-term rewards.
- But in poker, outcomes aren't immediate — they’re revealed over multiple stages (*pre-flop, flop, turn, river*).
- To handle this, I modified the algorithm to use a **recursive** structure, where the value of a state depends on the *maximum outcome of future states*.
    - Example: If you bet \$20 pre-flop and are destined to lose, the worst case might be losing \$80 (betting every round), while the best case is folding next round for a \$1 loss.
- Game states are represented as **(Hand Score, Opponent Score, Round, Current Bet)**.
- Even with heuristics, the state space is still large — but many states converge to the same future states.
    - e.g., (10.2, 3, 0, 0) → (7.0, 5.4, 1, 10) and (3.3, 5.9, 0, 0) → (7.0, 5.4, 1, 10)
- This overlap lets us recursively share learned knowledge across different paths. To utilize this, we run ~10% of games exploring all options, before only exploring the determined, more promising states.
---

**Notes:**  
- The betting space was simplified to [1, 5, 10, 20, 50, -1 (fold)]. (this can be updated) 
- Training was done against unintelligent, unaggressive agents due to lack of real data and human opponents.  
- Despite this, the bot was able to **40x** its starting money across multiple datasets of 10,000+ games — showcasing its understanding of poker strategy.

---

**Takeaways:**  
- I really enjoyed modifying and implementing the Q-Learning framework - and seeing it *work*. 
- With more time and resources, I’d love to introduce varied agents for better learning and competition (*and eventually test against human players*).  
- I can’t wait to apply these learnings to even more complex ML environments.
