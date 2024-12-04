import tkinter as tk
from tkinter import messagebox
import numpy as np

# Initialize global variables
user_balance = 10000  # Initial balance
selected_bet = None  # Keeps track of the selected bet button


# Dummy prediction model (replace with your actual model later)
def predict_win_probability(stats):
    teamA_prob = np.random.randint(40, 60)  # Example probabilities
    teamB_prob = 100 - teamA_prob
    return {"teamA": teamA_prob, "teamB": teamB_prob}


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

    win_team = "Team A" if probabilities["teamA"] > probabilities["teamB"] else "Team B"

    # Check if the user's bet is correct
    if win_team == team_selected:
        winnings = bet_amount * 2  # Example: Double the bet amount on win
        user_balance += winnings
        messagebox.showinfo("Result", f"Congrats! {team_selected} won! You earned ${winnings}.")
    else:
        user_balance -= bet_amount
        messagebox.showinfo("Result", f"Sorry, {team_selected} lost. You lost ${bet_amount}.")

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
        text=f"Win Probabilities - Team A: {probabilities['teamA']}%, Team B: {probabilities['teamB']}%"
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

tk.Button(team_frame, text="Bet on Team A", command=lambda: place_bet("Team A")).pack(
    side=tk.LEFT, padx=20
)
tk.Button(team_frame, text="Bet on Team B", command=lambda: place_bet("Team B")).pack(
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
