"""
cricket_rnn
===========
Predict cricket matches by using recurrent neural networks(RNNs) to simulate
ball-by-ball data.

More detailed information on how to use the code as well as examples of outputs
are available in the GitHub repository `cricket-rnn-predictions
<https://github.com/ncr121/cricket-rnn-predictions>`_.

Available subpackages
---------------------
- ``loaders``
    Read JSON data from `Cricsheet <https://cricsheet.org>`_ and `Cricinfo <https://www.espncricinfo.com/>`_
- `framework`
    Core framework that runs ball-by-ball data to generate player and match statistics
- `dashboard`
    Front-end visualisation of match scorecards using `Dash <https://dash.plotly.com/>`_
- `simulation`
    Simulate matches being played for real or artifical players
- `neural_network`
    Build a recurrent neural network(RNN) to predict real matches (in development)

"""

TEAM_TYPES = [
    'international',
    'club'
]

MATCH_FORMATS = [
    'Test',
    'ODI',
    'T20'
]
NATIONS = {
    'England': 1,
    'Australia': 2,
    'South Africa': 3,
    'West Indies': 4,
    'New Zealand': 5,
    'India': 6,
    'Pakistan': 7,
    'Sri Lanka': 8,
    'Bangladesh': 25,
}
TEST_NATION_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 25]
TEST_NATIONS = [nation for nation, nation_id in NATIONS.items() if nation_id in TEST_NATION_IDS]

CLUB_COMPETITIONS = [
    'IPL',
    'HND'
]

MATCH_TYPES = MATCH_FORMATS + CLUB_COMPETITIONS
