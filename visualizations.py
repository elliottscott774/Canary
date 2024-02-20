import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Function to extract and parse all JSON objects from the game data file
def extract_json_objects_corrected(content):
    print("Extracting and parsing all JSON objects from the game data file")
    objects = []
    start_pos = 0
    content_length = len(content)
    try:
        while start_pos < content_length:
            obj, end_pos = json.JSONDecoder().raw_decode(content[start_pos:])
            objects.append(obj)
            start_pos += end_pos
            while start_pos < content_length and content[start_pos] in '\n\r\t ':
                start_pos += 1
                print(np.round(start_pos/content_length,5))
    except json.JSONDecodeError:
        pass
    except ValueError:
        pass
    return objects

# Load the file and extract game moves
with open('./game_data.txt', 'r') as file:
    print("Reading file contents")
    new_file_contents = file.read()

game_moves_corrected = extract_json_objects_corrected(new_file_contents)

def count_player_hands():
    # Ensure player_colors is defined in this snippet
    player_colors = {1: "red", 2: "green", 3: "blue", 4: "purple"}

    # Expanded data preparation
    df_players_updated = pd.DataFrame({"Turn Number": range(len(game_moves_corrected))})
    for player in range(1, 5):
        df_players_updated[f"Player {player} Cards in Hand"] = [move["num_cards_in_hands"][player - 1] for move in game_moves_corrected]
        df_players_updated[f"Player {player} Face Up Cards"] = [move.get("num_face_up_cards", [0]*4)[player - 1] for move in game_moves_corrected]
        df_players_updated[f"Player {player} Face Down Cards"] = [move.get("num_face_down_cards", [0]*4)[player - 1] for move in game_moves_corrected]
        df_players_updated[f"Player {player} Total Cards"] = df_players_updated[[f"Player {player} Cards in Hand", f"Player {player} Face Up Cards", f"Player {player} Face Down Cards"]].sum(axis=1)

    # Adjusted visualization
    plt.figure(figsize=(14, 8))
    for player, color in player_colors.items():
        sns.lineplot(data=df_players_updated, x="Turn Number", y=f"Player {player} Total Cards", label=f"Player {player}", marker='o', color=color)
    plt.title('Total Card Distribution for Each Player Over Turns (Including All Card Types)')
    plt.xlabel('Turn Number')
    plt.ylabel('Total Number of Cards')
    plt.legend(title="Player")
    plt.grid(True)
    plt.show()

def count_cards_histogram():
    # Initializing a list to store the counts of cards that were in players' hands just before their hand size increased by more than 2
    card_counts_before_increase = []
    print("Counting cards!")
    # Loop through the game moves to find where a player's hand size increases by more than 2 cards
    for i in range(1, len(game_moves_corrected)):  # Start from the second move to compare with the previous
        for player in range(1, 5):  # Assuming 4 players
            # Calculate the change in hand size for the player
            hand_size_change = game_moves_corrected[i]["num_cards_in_hands"][player - 1] - game_moves_corrected[i-1]["num_cards_in_hands"][player - 1]
            if hand_size_change > 2:  # Checking if the hand size increased by more than 2
                # Add the count of cards in the player's hand just before the increase
                card_counts_before_increase.extend(game_moves_corrected[i-1]["cards_in_hands"][player - 1])

    # Count the occurrences of each card before the increase
    from collections import Counter
    card_counts = Counter(card_counts_before_increase)

    # Prepare data for the histogram
    cards, counts = zip(*card_counts.most_common())  # Unzip the cards and counts into separate lists

    # Plotting the histogram
    plt.figure(figsize=(14, 8))
    sns.barplot(x=list(counts), y=list(cards), palette="viridis")
    plt.title('Card Counts in Players\' Hands Before Hand Size Increased by More Than 2')
    plt.xlabel('Count')
    plt.ylabel('Cards')
    plt.show()

def get_move_at_turn(game_moves, turn_number):
    """
    Function to get the game move at a specified turn number.
    
    :param game_moves: List of all game moves.
    :param turn_number: The turn number to retrieve the move for.
    :return: A dictionary representing the game move at the specified turn, or None if not found.
    """
    for move in game_moves:
        if move["turn_number"] == turn_number:
            return move
    return None

count_cards_histogram()



    

