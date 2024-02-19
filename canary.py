import itertools
import random

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        # Determine if the card is special
        self.is_special = value in [2, 10, 'Joker']
        self.is_seven = value in [7]

    def __repr__(self):
        return f"{self.value} of {self.suit}" if self.suit else f"{self.value}"


class CardGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.deck = self.create_deck()
        self.players_hands = [[] for _ in range(num_players)]
        self.face_down_cards = [[] for _ in range(num_players)]
        self.face_up_cards = [[] for _ in range(num_players)]
        self.draw_pile = []
        self.play_pile = []
        self.game_over = False
        self.play_direction = 1 # 1 for clockwise, -1 for counterclockwise
        self.current_player_index = -1
        self.setup_game()
        
    def create_deck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = [2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        deck = [Card(value, suit) for suit in suits for value in values]

        # Include Jokers without a suit
        deck.extend([Card('Joker', None) for _ in range(2)])  # Adding two Jokers

        # Use 2 decks for 5-8 players
        if self.num_players >= 5:
            deck = deck * 2

        return deck
    
    def setup_game(self):
        # Shuffle the deck
        random.shuffle(self.deck) 

        # Deal 3 face-down and 6 to choose face-up cards to each player
        for i in range(self.num_players):
            # Deal 3 face-down cards
            self.face_down_cards[i] = [self.deck.pop() for _ in range(3)]

            # Deal 6 cards for choosing 3 to be face-up
            face_up_candidates = [self.deck.pop() for _ in range(6)]

            # Players choose 3 of these to be face-up, for simplicity, randomly select here
            self.face_up_cards[i] = random.sample(face_up_candidates, 3)

            # The remaining 3 cards from the 6 initially dealt for choosing go into the player's hand
            self.players_hands[i] = [card for card in face_up_candidates if card not in self.face_up_cards[i]]

        # The rest of the cards form the draw pile
        self.draw_pile = self.deck
    
    def find_starting_player(self):
        # Define the order for determining the starting player
        card_value_order = [3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 'Joker', 10, 2]

        # Initialize counts for each card value for each player
        player_card_counts = [{value: 0 for value in card_value_order} for _ in range(self.num_players)]

        # Count the number of each card value in each player's hand
        for player_index, hand in enumerate(self.players_hands):
            for card in hand:
                if card.value in card_value_order:
                    player_card_counts[player_index][card.value] += 1

        # Determine who starts based on the cards
        for value in card_value_order:
            # Find players with the current card value
            players_with_card = [(index, count[value]) for index, count in enumerate(player_card_counts) if count[value] > 0]

            if not players_with_card:  # If no player has the card, continue to the next value
                continue

            # If only one player has the card, they start
            if len(players_with_card) == 1:
                return players_with_card[0][0]

            # If multiple players have the same card, compare counts
            max_count = max(players_with_card, key=lambda x: x[1])[1]
            players_with_max = [player for player, count in players_with_card if count == max_count]

            if len(players_with_max) == 1:
                return players_with_max[0]
            # If still tied, continue to the next card value

        # If somehow no one can start, return a random player as fallback
        return random.randint(0, self.num_players - 1)

    def start_game(self):
        
        starting_player_index = self.find_starting_player()
        self.current_player_index = starting_player_index
        
        while not self.game_over:
            # Player takes their turn.
            self.play_turn()        
            self.game_over = self.check_game_over()
            
            if len(self.play_pile) >= 4:
                #print("thats a big pile")
                for i in range(len(self.play_pile) -3):
                    if self.play_pile[i] == self.play_pile[i+1] == self.play_pile[i+2] == self.play_pile[i+3]:
                        print("4 in a row!")    
                        self.play_pile.clear()
                
            
            # Move to the next player
            self.current_player_index = (self.current_player_index + self.play_direction) % self.num_players
            
        print("Game Over")

    def play_turn(self):
        print(f"Player {self.current_player_index + 1}'s turn:")
        

        # Try playing from hand, face-up, then face-down in order.
        if not self.attempt_play_from_hand():
            if not self.attempt_play_from_face_up():
                if not self.attempt_play_from_face_down():
                    print("No more cards to play.")
         
    def attempt_play_from_hand(self):
        print("Player Hand: ", self.players_hands[self.current_player_index])
        return self.attempt_play(card_source = self.players_hands[self.current_player_index])

    def attempt_play_from_face_up(self):
        print("Players Face-Up Hand: ", self.face_up_cards[self.current_player_index])
        return self.attempt_play(card_source = self.face_up_cards[self.current_player_index], is_face_up = True)

    def attempt_play_from_face_down(self, is_face_down = True):
        # Face-down play is a bit different as it involves random choice and immediate play without checking
        if self.face_down_cards[self.current_player_index]:
            chosen_card = random.choice(self.face_down_cards[self.current_player_index])
            #print("Players Face-Down Hand:: ", chosen_card)
            return self.attempt_play(card_source = chosen_card, is_face_down = True)
        else:
            return False
    
    def attempt_play(self, card_source, is_face_up = False, is_face_down = False):

        if is_face_up:
            if not card_source:
                #Face up cards is empty, move to facedown
                return False
            
            playable_cards = [card for card in card_source if self.can_play_card(card)]
            print("Playable Cards: ", playable_cards)
            if not playable_cards:
                    print("No playable cards in face up pile")
                    self.pick_up_pile()
                    return True
            chosen_card = random.choice(playable_cards)
            self.play_card(chosen_card, is_face_up = True)
            return True
        
        if is_face_down:
            if not card_source:
                return False
            
            print("Card Selected: ", card_source)
            
            if self.can_play_card(card_source):
                self.play_pile.append(card_source)
                self.face_down_cards[self.current_player_index].remove(card_source)
                return True
            else:
                self.play_pile.append(card_source)
                self.face_down_cards[self.current_player_index].remove(card_source)
                self.pick_up_pile()
                return True

        
        if not card_source:
            print("No Cards in Hand!")
            return False
        
        playable_cards = [card for card in card_source if self.can_play_card(card)]
        print("Playable Cards: ", playable_cards)
        if not playable_cards:
            self.pick_up_pile()   
            return True

        chosen_card = random.choice(playable_cards)
        self.play_card(chosen_card)
        return True
    
    def can_play_card(self, card):
        """Check if the card can be played on top of the play pile."""
        if not self.play_pile:
            return True  # Any card can be played if the play pile is empty
        
        top_card = self.play_pile[-1]
        
        # Allow any card to be played if the top card is a special card or the played card is special
        if top_card.is_special:
            return True
        
        if card.is_special:
            return True
        
        if top_card.is_seven:
            #print(card.value, " <= ", top_card.value,"?", card.value <= top_card.value)
            return card.value <= 7
        
        #print(card.value, " >= ", top_card.value,"?", card.value >= top_card.value)
        return card.value >= top_card.value

    def play_card(self, chosen_card, is_face_up=False, is_face_down=False):
        # Check for special cards (Joker, 2, 10, and handling of 7 if needed)
        if chosen_card.is_special:
            if chosen_card.value == 'Joker':
                self.play_pile.append(chosen_card)
                print(f"Played {chosen_card}.")
                self.play_direction *= -1
                if not is_face_down:
                    if is_face_up:
                        self.face_up_cards[self.current_player_index].remove(chosen_card)
                    else:
                        self.players_hands[self.current_player_index].remove(chosen_card)
                        
                self.post_play_card_actions()
                return
            elif chosen_card.value == 2:
                # Logic for 2 allowing the player to play again
                self.play_pile.append(chosen_card)
                print(f"Played {chosen_card}.")
                if not is_face_down:
                    if is_face_up:
                        self.face_up_cards[self.current_player_index].remove(chosen_card)
                    else:
                        self.players_hands[self.current_player_index].remove(chosen_card)
                self.allow_play_again()
                return
            elif chosen_card.value == 10:
                # Maybe a special logic for 10, like clearing the play pile
                self.play_pile.append(chosen_card)
                print(f"Played {chosen_card}.")
                self.clear_play_pile()
                # Remove the card from its current location unless it's face-down
                if not is_face_down:
                    if is_face_up:
                        self.face_up_cards[self.current_player_index].remove(chosen_card)
                    else:
                        self.players_hands[self.current_player_index].remove(chosen_card)
                        
                self.post_play_card_actions()
                return
            # Additional logic for any special actions based on card
        elif chosen_card.is_seven:
            # Handle seven's special rule if applicable
            self.play_pile.append(chosen_card)
            print(f"Played {chosen_card}.")
            # Remove the card from its current location unless it's face-down
            if not is_face_down:
                if is_face_up:
                    self.face_up_cards[self.current_player_index].remove(chosen_card)
                else:
                    self.players_hands[self.current_player_index].remove(chosen_card)
            self.post_play_card_actions()
            return

        if not is_face_down:
            if is_face_up:
                self.face_up_cards[self.current_player_index].remove(chosen_card)
            else:
                self.players_hands[self.current_player_index].remove(chosen_card)

        self.play_pile.append(chosen_card)
        print(f"Played {chosen_card}.")
        self.post_play_card_actions()
        
    def post_play_card_actions(self):
        # Ensures the player has at least 3 cards in their hand if the draw pile isn't empty
        while len(self.players_hands[self.current_player_index]) < 3 and self.draw_pile:
            self.draw_card()
            #print(f"Player {self.current_player_index + 1} draws a card. Hand now: {self.players_hands[self.current_player_index]}")

    def reverse_play_order(self):
        """Reverses the current order of play."""
        # This is a simplified representation. You might store the current direction of play
        # (e.g., as a class attribute) and reverse it here. For example:
        self.play_direction *= -1
        print("Reversing Direction!")
        return
    
    def draw_card(self):
        """Player draws a card from the draw pile."""
        if self.draw_pile:
            card_drawn = self.draw_pile.pop()
            self.players_hands[self.current_player_index].append(card_drawn)
        else:
            print("The draw pile is empty. No card drawn.")
    
    def pick_up_pile(self):
        """Player picks up the play pile."""
        self.players_hands[self.current_player_index].extend(self.play_pile)
        self.play_pile.clear()
        print("Pile picked up!")
        
    def check_game_over(self):
        # Implement logic to determine if the game has ended.
        # This could involve checking if any player has successfully played all their cards (hand, face-up, and face-down).
        for player_index in range(self.num_players):
            if (not self.players_hands[player_index] and 
                not self.face_up_cards[player_index] and 
                not self.face_down_cards[player_index]):
                print(f"Player {player_index + 1} wins and is declared the Canary!")
                return True  # A winner is found
        return False  # The game continues
    
    def allow_play_again(self):
        print("Play again:")
        self.current_player_index = (self.current_player_index - self.play_direction)
        #print(self.current_player_index)
        # Implement logic to allow the current player to play again. This might mean not advancing
        # the current_player_index or setting a flag that allows another turn for the current player.
    
    def clear_play_pile(self):
        print("Clearing play pile")
        self.play_pile.clear()
        # Implement logic to clear the play pile if a 10 is played, for example.

    def handle_seven_action(self):
        print("Seven or below!")
        
    # Implement any special rule for playing a seven, if applicable.

        
game = CardGame(4)  
game.start_game()