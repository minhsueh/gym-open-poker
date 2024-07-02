"""
This player wants to stir the pot by making raise count to 1. 
Otherwise, it will not place more betting in the pot.
"""

from action import Action


def make_pre_flop_moves(player, current_gameboard, allowable_actions):

    if current_gameboard["board"].current_bet_count == 0:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.BET in allowable_actions:
            return Action.BET
    elif current_gameboard["board"].current_raise_count < 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.RAISE_BET in allowable_actions:
            return Action.RAISE_BET
    elif current_gameboard["board"].current_raise_count == 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.CALL in allowable_actions:
            return Action.CALL
    else:
        if Action.CHECK in allowable_actions:
            return Action.CHECK

    return Action.FOLD


def make_flop_moves(player, current_gameboard, allowable_actions):
    if current_gameboard["board"].current_bet_count == 0:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.BET in allowable_actions:
            return Action.BET
    elif current_gameboard["board"].current_raise_count < 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.RAISE_BET in allowable_actions:
            return Action.RAISE_BET
    elif current_gameboard["board"].current_raise_count == 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.CALL in allowable_actions:
            return Action.CALL
    else:
        if Action.CHECK in allowable_actions:
            return Action.CHECK

    return Action.FOLD


def make_turn_moves(player, current_gameboard, allowable_actions):
    if current_gameboard["board"].current_bet_count == 0:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.BET in allowable_actions:
            return Action.BET
    elif current_gameboard["board"].current_raise_count < 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.RAISE_BET in allowable_actions:
            return Action.RAISE_BET
    elif current_gameboard["board"].current_raise_count == 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.CALL in allowable_actions:
            return Action.CALL
    else:
        if Action.CHECK in allowable_actions:
            return Action.CHECK

    return Action.FOLD


def make_river_moves(player, current_gameboard, allowable_actions):
    if current_gameboard["board"].current_bet_count == 0:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.BET in allowable_actions:
            return Action.BET
    elif current_gameboard["board"].current_raise_count < 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.RAISE_BET in allowable_actions:
            return Action.RAISE_BET
    elif current_gameboard["board"].current_raise_count == 1:
        if Action.ALL_IN in allowable_actions:
            return Action.ALL_IN
        elif Action.CALL in allowable_actions:
            return Action.CALL
    else:
        if Action.CHECK in allowable_actions:
            return Action.CHECK

    return Action.FOLD


def _build_decision_agent_methods_dict():
    """
    This function builds the decision agent methods dictionary.
    :return: The decision agent dict. Keys should be exactly as stated in this example, but the functions can be anything
    as long as you use/expect the exact function signatures we have indicated in this document.
    """
    ans = dict()
    ans["make_pre_flop_moves"] = make_pre_flop_moves
    ans["make_flop_moves"] = make_flop_moves
    ans["make_turn_moves"] = make_turn_moves
    ans["make_river_moves"] = make_river_moves
    ans["strategy_type"] = "agent_stir"

    return ans


decision_agent_methods = _build_decision_agent_methods_dict()
