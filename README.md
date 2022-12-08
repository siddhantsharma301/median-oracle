# Making Uniswap's price oracle more outlier-resistant

## Problem with Uniswap's TWAP oracle
Currently, Uniswap uses a Time-Weighted Average Price (TWAP) oracle, with v2 using arithmetic mean and v3 using geometric mean. This leads to risks related to the security of TWAP oracles, since arithmetic and geometric mean are affected by outlier price values:
- Attackers can use a one-block attack to manipulate the price by a large amount and use the manipulated price for tasks such as borrowing from lending protocol
- With Ethereum’s recent move to proof-of-stake and sophisticated MEV systems like Flashbots, attackers can use multi-block attacks to manipulate price for multiple blocks

## Our Solution

### Improve Euler Finance's implementation of a median oracle
- Grow ring size functionality: Allows median oracle to follow same oracle API as Uniswap V3 TWAP
- Price oscillations around ticks: When an oracle oscillates around two ticks constantly, there is no need to add more items to ring buffer (to reduce gas usage). We implemented this change to make the median oracle more gas efficient in this scenario

### Implement a Winsorized TWAP oracle for Uniswap v3
- What is a winsorized oracle: price ticks are “capped” if the difference between the new and current tick is too high
- Winsorized oracle makes it harder to do PoS oracle attacks (through flash loans, for example)
- More difficult + expensive to manipulate price significantly across several blocks
- Must manipulate oracle for 30 consecutive blocks to increase price by 20% (source: [Uniswap Blog](https://uniswap.org/blog/uniswap-v3-oracles#what-else-can-be-done))

## Evaluating our Solution

### Improvements to Euler Finance's median oracle
To test our improvement regarding price oscillations, we ran the oracle on a price dataset which repeatedly oscillated between two quantized prices, and then measured the gas usage in our improved oracle vs. the existing median oracle. We found that the improved median oracle is ~96.7% more gas-efficient than the existing median oracle when run on oscillating prices:

<img width="464" alt="image" src="https://user-images.githubusercontent.com/22297592/205815286-39c9bd52-ab7d-4b8f-a678-f78d2bf3a438.png">

### Winsorized TWAP oracle
We simulated a flash loan attack on historical Uniswap price data and ran the existing v3 TWAP oracle as well as our Winsorized TWAP oracle. To evaluate success, we measured the average deviation between the oracle price and the underlying price without the flash loan attack at each time step. This evaluates the degree to which each oracle is affected by the attack.

We found that the Winsorized TWAP oracle is ~24% more resistant to price outliers than existing TWAP oracle in Uniswap v3:

<img width="502" alt="image" src="https://user-images.githubusercontent.com/22297592/205815436-16a116f5-2151-4166-be64-0bbcc652b325.png">

## Possible Next Steps
- Improve Uniswap V3 TWAP gas efficiency and Winsorizing Uniswap V3 TWAP gas efficiency: very gas inefficient compared to Euler Finance's median oracle
- Exploring other outlier-resistant measures of average for price oracles (examples include harmonic mean and robust statistics)
