import ast
import random
import re
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import joblib
# Initialize global variables
user_balance = 10000  # Initial balance
selected_bet = None  # Keeps track of the selected bet button

data = pd.read_csv('final_data.csv')
model = xgb.Booster()
model.load_model('model.json')
ppi_data = pd.read_csv('Player_PPI.csv')


# Using Model
def predict_win_probability(stats):
    stats_fixed = re.sub(r'(\b[a-zA-ZÀ-ÿ\s-]+\b)', r"'\1'", stats)
    stats_list = ast.literal_eval(stats_fixed)

    prediction_data = pd.DataFrame(
        [stats_list],
        columns=[
            'SCOREMARGIN', 'TIME_REMAINING', 'PERIOD', 'TEAM_1', 'TEAM_2',
            'PLAYER_1.1', 'PLAYER_1.2', 'PLAYER_1.3', 'PLAYER_1.4', 'PLAYER_1.5',
            'PLAYER_2.1', 'PLAYER_2.2', 'PLAYER_2.3', 'PLAYER_2.4', 'PLAYER_2.5',
            'SCORE_1', 'SCORE_2'
        ]
    )
    player_rating_map = dict(zip(ppi_data['Player'], ppi_data['PPI']))
    player_columns = [col for col in prediction_data.columns if 'PLAYER' in col]

    # Replace player names with ratings
    for col in player_columns:
        prediction_data[col] = prediction_data[col].map(player_rating_map)

    # Replace player names with ratings
    for col in player_columns:
        prediction_data[col] = prediction_data[col].map(player_rating_map)

    # Preprocessing
    numerical_cols = [
        'SCOREMARGIN', 'TIME_REMAINING', 'PERIOD', 'PLAYER_1.1', 'PLAYER_1.2',
        'PLAYER_1.3', 'PLAYER_1.4', 'PLAYER_1.5', 'PLAYER_2.1', 'PLAYER_2.2',
        'PLAYER_2.3', 'PLAYER_2.4', 'PLAYER_2.5'  # Numerical feature names
    ]
    categorical_cols = ["TEAM_1", "TEAM_2"]
    # Scale numerical features
    scaler = joblib.load('scaler.pkl')
    prediction_data[numerical_cols] = scaler.fit_transform(prediction_data[numerical_cols])
    # Encode categorical features
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        prediction_data[col] = le.fit_transform(prediction_data[col])
        label_encoders[col] = le
    demo = xgb.DMatrix(prediction_data)
    pred = model.predict(demo)
    # pred
    # prediction_data
    team_1_prob = pred[0]
    team_2_prob = 1 - team_1_prob
    return {"team 1": round(team_1_prob, 2), "team 2": round(team_2_prob, 2)}


# Function to handle bet selection
def select_bet(amount, button):
    global selected_bet
    # Reset previously selected bet button color
    if selected_bet is not None:
        selected_bet.config(bg="SystemButtonFace")  # Default button color
    # Highlight the newly selected button
    button.config(bg="darkgray")
    selected_bet = button  # Update the currently selected bet


# Function to process bets
def place_bet(team_selected):
    global user_balance

    # Check if a bet amount is selected
    if selected_bet is None:
        messagebox.showwarning("Error", "Please select a bet amount first!")
        return

    # Get the selected bet amount
    bet_amount = int(selected_bet["text"].strip("$"))

    # Check if the user has enough balance
    if user_balance < bet_amount:
        messagebox.showerror("Error", "Insufficient balance!")
        return

    # Get prediction probabilities
    probabilities = get_probabilities()
    if probabilities is None:
        return
    ran = random.uniform(0, 1)
    max_prob = max(probabilities['team 1'], probabilities['team 2'])
    win_team = ""
    if ran < max_prob:
        if probabilities['team 1'] == max_prob:
            win_team = "team 1"
        else:
            win_team = "team 2"

    # Check if the user's bet is correct
    if win_team == team_selected:
        winnings = bet_amount * 0.9/probabilities[win_team]  # Example: Double the bet amount on win
        winnings = round(winnings, 2)
        user_balance += winnings
        messagebox.showinfo("Result", f"Congrats! {team_selected} won! You earned ${winnings}.")
    else:
        user_balance -= bet_amount
        messagebox.showinfo("Result", f"Sorry, {team_selected} lost. You lost ${bet_amount}.")
    user_balance = round(user_balance, 2)
    # Update UI elements
    balance_label.config(text=f"Balance: ${user_balance}")


# Function to get probabilities and update UI
def get_probabilities():
    stats = stats_entry.get("1.0", tk.END).strip()
    if not stats:
        messagebox.showwarning("Input Error", "Please enter basketball game stats!")
        return None

    # Get prediction probabilities
    probabilities = predict_win_probability(stats)
    result_label.config(
        text=f"Win Probabilities - Team 1: {round(probabilities['team 1']*100, 2)}%, Team 2: {round(probabilities['team 2']*100, 2)}%"
    )
    return probabilities


# Function to reset balance
def reset_balance():
    global user_balance
    global selected_bet
    user_balance = 10000
    selected_bet = None  # Reset selected bet button
    balance_label.config(text=f"Balance: ${user_balance}")
    result_label.config(text="Win Probabilities will appear here.")
    for button in bet_buttons:
        button.config(bg="SystemButtonFace")  # Reset all buttons to default color


# Create Tkinter window
root = tk.Tk()
root.title("Basketball Prediction App")
root.geometry("700x500")

# Title
tk.Label(root, text="Basketball Prediction", font=("Arial", 16, "bold")).pack(pady=10)

# Input box for game stats
tk.Label(root, text="Enter game stats (e.g., scores, assists, rebounds):").pack()

input_frame = tk.Frame(root)
input_frame.pack(pady=5)

stats_entry = tk.Text(input_frame, height=5, width=50)
stats_entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(input_frame, text="Send", command=get_probabilities)
send_button.pack(side=tk.LEFT)

# Buttons to select bet amount
tk.Label(root, text="Select your bet amount:").pack(pady=10)
bet_frame = tk.Frame(root)
bet_frame.pack()

bet_buttons = []  # To store bet amount buttons
for amount in [100, 500, 1000, 5000]:
    btn = tk.Button(
        bet_frame,
        text=f"${amount}",
    )
    btn.config(command=lambda a=amount, b=btn: select_bet(a, b))  # Define the command separately
    btn.pack(side=tk.LEFT, padx=10)
    bet_buttons.append(btn)

# Buttons to bet on specific teams
tk.Label(root, text="Choose a team to bet on:").pack(pady=10)
team_frame = tk.Frame(root)
team_frame.pack()

tk.Button(team_frame, text="Bet on team 1", command=lambda: place_bet("team 1")).pack(
    side=tk.LEFT, padx=20
)
tk.Button(team_frame, text="Bet on team 2", command=lambda: place_bet("team 2")).pack(
    side=tk.LEFT, padx=20
)

# Result display
result_label = tk.Label(root, text="Win Probabilities will appear here.", font=("Arial", 12))
result_label.pack(pady=10)

# Balance display
balance_label = tk.Label(root, text=f"Balance: ${user_balance}", font=("Arial", 12, "bold"))
balance_label.pack(pady=10)

# Reset balance button
tk.Button(root, text="Reset Balance", command=reset_balance).pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
