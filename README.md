# cricket-rnn-predictions
Predict cricket matches by using recurrent neural networks(RNNs) to simulate
ball-by-ball data.

Disclaimer: The prediction aspect of this library is currently in development.
However, there are still a lot of other useful features to process raw JSON
data into match objects with statistics and to visualise scorecards.

## About
Framework for converting ball-by-ball data for cricket matches in order to
display detailed match and player statistics. The processed data is also used
to generate discrete distributions based on different match scenarios.

Current features:
- Process JSON data into `Match`, `Inning`, `Over`, `Ball` and `Player` objects
- View detailed statistics and scorecards for existing matches
- Simulate fictitious matches using real data and hard-coded weights
- (in development) Predict future matches by using recurrent neural
networks(RNNs) to optimise the weights

## Description
# Overview
This project was inititally started to simulate cricket matches by assigning a
discrete distribution to every ball in order to randomly choose the outcome: 0,
1, 2, 3, 4, 6 or W. An inning is then played out until all 10 wickets have
fallen. This simplistic approach is the core idea that the entire model is
built upon.

# Features
For the match to be as realistic as possible, the probabilities need to be
chosen such that they are consistent with actual run rates and averages, so
real ball-by-ball data should be considered. However, using a single vector
of probabilites for every ball in a match is not feasible since match
conditions change constantly.

For example, the probability of a wicket falling is much higher when a tail
ender is batting compared to an opener. Also, the probability of a four or six
being hit is much higher towards the end of an inning (in an ODI or T20). There
are many other factors like pace vs spin, powerplays, etc that dictate that
every ball should have its own unique probability vector.

Trends in cricket matches:
- Average team score varies per inning
- Average team score varies based on venue
- Batting performance depends on batting position
- Batting performance rate differs for pace vs spin
- Set batters are less likely to get out

These are just some of the general trends being considered. The important part
is converting an idea of what takes place in a match into a meaningul feature.

# Weights
Currently the weights are manually calibrated to ensure the scores of simulated
matches are realistic. A recurrent neural newtowk(RNN) architechture is in
development to optimise the weights.

## Data
Disclaimer: This library is not intended for commercial use.

# Cricsheet
This project is only possible because of [Cricsheet](https://cricsheet.org),
which is an amazing website that provides accurate ball-by-ball data for
international and club matches since 2003.

# Cricinfo
Additionally, some further information is obtained from
[Cricinfo](https://www.espncricinfo.com) by web scraping. This is mostly
player data, e.g. batting style, bowling style, if the player is a keeper.

## Installation
To clone this repository, run the following command:

```bash
git clone https://github.com/ncr121/cricket-rnn-predictions.git
```

## Usage
Download JSON data from Cricsheet:

```python
>>> from cricket_rnn.loaders import download_json_data
>>> download_json_data()
Downloading Test matches
Downloading ODI matches
Downloading T20 matches
```

View a master list of all downloaded matches:
```python
>>> from cricket_rnn.loaders import read_master_list
>>> master_list = read_master_list()
```

From there, valid match IDs can be found and an individual match can be run:
```python
>>> from cricket_rnn.framework import run_match
>>> mat = run_match(mat_id=1249875)
```

Match and inning statistics are stored in the following class properties:
```python
>>> # match summary
>>> summary = mat.summary
>>> # first inning batting scorecard
>>> bat_card = inn[0].bat_card
>>> # second inning bowling scorecard
>>> bowl_card = inn[1].bowl_card
```