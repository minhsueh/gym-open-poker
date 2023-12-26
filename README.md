# Open Poker

Welcome to the open-world Poker Simulator, a tool that includes novelty generators for open-world artificial intelligence (Open-world AI). This package relies on the following frameworks:

- [OpenAI Gym](https://github.com/openai/gym): Serving as the infrastructure for simulation environments.
- [Pygame](https://www.pygame.org/): Employed for visualization purposes.


<!---
![alt text](./poker.png)
The poker simulator screenshot.
-->


![alt text](./videos/trim_normal_mode.gif)
The visualization of normal game mode.

![alt text](./videos/trim_debug_mode.gif)
The visualization of debug game mode.


## Getting Started
If you are unfamiliar with poker, these are some references for you as a novice.
- [Wiki](https://en.wikipedia.org/wiki/Poker)
- [Upswingpoker](https://upswingpoker.com/betting-rules/)

Within this software package, the implementation of Limit Texas Hold'em is provided. Some key properties of Limit Texas Hold'em:
- Fixed Betting Limits: The default betting structure is $10/$20. In other words, the small bet is $10 for the first two betting rounds, and the big bet is $20 for the last two betting rounds.
- Number of Raises: Only one bet and up to three raise bets are permissible during each betting round.



### Prerequisites
- Python 3.9 or above

### User Installation
We will publish this package to PyPI soon..

### Development Installation
1. Clone the repository:
```
git clone https://github.com/minhsueh/gym-open-poker.git
```
2. Navigate to the project directory:
```
cd gym-open-poker
```
3. Install the package in editable mode:
```
pip3 install -e .
```
4. Install additional dependencies:
```
pip3 install -r requirements.txt
```

## Authors
- Min-Hsueh Chiu - [GitHub](https://github.com/minhsueh)
- Mayank Kejriwal - [GitHub](https://github.com/mayankkejriwal)

## License
[MIT](https://choosealicense.com/licenses/mit/)