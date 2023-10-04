"""
Pot designing:
In our design, we will distribute the pot in the conclude_round.
Before this, we will use 
    players_last_move_list
    
    in game:
        current_gameboard['pots_amount_list'] = []
        current_gameboard['pots_attendee_list'] = []
    
    in each round
        player_pot(dict): key = player_name, value = spent amount


check_betting_over:
    if there is NONE in the players_last_move_list, then False. (meaning some player haven't actioned yet)


Once a player bet, raise_bet -> initialize players_last_move_list to NONE (remain ALLIN, FOLD and LOSE) execpt the aggressor


How to distribute the pot in concluded_round?
1.


cur_side_pot_amount_list = []
cur_side_pot_attendee_list = []

if have ALL-IN: 
    # get all ALL-IN players, and sort by the betting amount 
    all_in_players_list = [] # each element: (player_name, all_in_amount)
    for p_idx, p in enumerate(current_gameboard['players']):
        if players_last_move_list[p_idx] == 'AII-IN'
            all_in_players_list.append((p.player_name, player_pot[p.player_name]))
    all_in_players_list.sort(key = lambda x: x[1], reverse = True) # sort all_in_amount in decending order

    while(all_in_players_list):
        side_attendee = set()
        all_in_player, all_in_amount = all_in_players.pop()
        for p_idx, p in enumerate(current_gameboard['players']):
            if player_pot[player_name] > all_in_amount: 
                player_pot[player_name] -= all_in_amount
                side_attendee.add(player_name)

        cur_side_pot_amount_list.append(all_in_amount*len(side_attendee))
        cur_side_pot_attendee_list.append(side_attendee)


# main pot if there is no ALL-IN, or rightmost side pot(only these people are active)
cur_main_pot_amount = 0
cur_main_pot_attendee = set()
fold_count = 0
for p_idx, p in enumerate(current_gameboard['players']):
    if p in player_pot:
        # might be fold, bet and call
        cur_main_pot_amount += player_pot[p.player_name]
        if current_gameboard['players_last_move_list'] != 'FOLD':
            cur_main_pot_attendee.add(p.player_name)
        else:
            fold_count += 1






assert fold_count + len(cur_main_pot_attendee) == len(current_gameboard['pots_attendee_list'][-1])

# These might inlcude player who is fold, should recheck again in find_winner(conclude_game)

current_gameboard['pots_amount_list'][-1] += cur_main_pot_amount 

if cur_side_pot_amount_list:
    current_gameboard['pots_amount_list'] += cur_side_pot_amount_list
    current_gameboard['pots_attendee_list'] += cur_side_pot_attendee_list









deprecated:


Condition: A player has no enough money to call, it can choose all-in.
Once a player call all-in, the pot will be devided into main pot and side pot.

main pot: not all-in players
side pot: specific all-in player

Case1: everybody in the main pot
Case2: one player call all-in
Case3: two player call all-in in the same round
    ex1: 4 3 2 4
        step1: 4
            amount_in_pot = [[4 n n n]]
            highest_bet = [4]
            player_in_pot = [{p1}]
            pot = [0]
            players_last_move_list = [B N N N]
        step2: 4 3 (p2 call all-in)
            amount_in_pot = [[3 3 n n], [1 0 n n]]
            highest_bet = [3 1]
            player_in_pot = [{p1, p2} {p1}]
            pot = [0, 0]
            players_last_move_list = [B A N N]
        step3: 4 3 2 (p3 call all-in)
            amount_in_pot = [[2 2 2 n], [1 1 0 n] [1 0 0 n]]
            highest_bet = [2 1 1]
            player_in_pot = [{p1 p2 p3} {p1 p2} {p1}]
            pot = [0, 0, 0]
            players_last_move_list = [B A A N]
        step4: 4 3 2 4
            amount_in_pot = [[2 2 2 2], [1 1 0 1] [1 0 0 1]]
            player_in_pot = [{p1 p2 p3 p4} {p1 p2 p4} {p1 p4}]
            highest_bet = [2 1 1]
            pot = [0, 0, 0, 0]
            players_last_move_list = [B A A C]

    ex2: 4 2 3 4
        step1: 4
            amount_in_pot = [[4 n n n]]
            player_in_pot = [{p1}]
            pot = [0]
            players_last_move_list = [B N N N]
        step2: 4 2 (p2 call all-in)
            amount_in_pot = [[2 2 n n], [2 0 n n]]
            player_in_pot = [{p1, p2} {p1}]
            pot = [0, 0]
            players_last_move_list = [B A N N]
        step3: 4 2 3 (p3 call all-in)
            amount_in_pot = [[2 2 2 n], [1 0 1 n] [1 0 0 n]]
            player_in_pot = [{p1 p2 p3} {p1 p3} {p1}]
            pot = [0, 0, 0]
            players_last_move_list = [B A A N]
        step4: 4 2 3 4
            amount_in_pot = [[2 2 2 2], [1 0 1 1] [1 0 0 1]]
            player_in_pot = [{p1 p2 p3 p4} {p1 p3 p4} {p1 p4}]
            pot = [0, 0, 0, 0]
            players_last_move_list = [B A A C]

    ex3: 4 3 2 8



Case4: two player call all-in in the different rounds


declare:
    amount_in_pot = [[0] * total_number_of_players] # how many does player put in put in that round
    player_in_pot = [set(player)]
    highest_bet = [[]]
    pot = []
    players_last_move_list = []


len(amount_in_pot) == len(player_in_pot) == len(pot)
main pot = pot[0]
side pot = pot[1], pot[2] ...

Once bet or raise_bet, we will initialize amount_in_pot
    


"""