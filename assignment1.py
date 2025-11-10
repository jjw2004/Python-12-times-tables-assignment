from tkinter import *
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import datetime
import os
import threading
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


QUIZ_RESULTS = []
PLAYER_NAME = "Pupil"
FACT_SHOWN = False

# Function to get maths fact (API as mentioned in the assignment on moodle has not been added yet)
def compute_answer(a, op, b):
    """Compute answer using NumPy if available, else pure Python.
    Supports '+', '-', '*', '/' returning float for division rounded to 2dp.
    """
    if HAS_NUMPY:
        if op == '+':
            return int(np.add(a, b))
        if op == '-':
            return int(np.subtract(a, b))
        if op == '*':
            return int(np.multiply(a, b))
        if op == '/':
            return round(float(np.divide(a, b)), 2)
    # fallback
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return round(a / b, 2)
    raise ValueError(f"Unsupported op: {op}")

def generate_table_lines(num, op):
    """Return list of strings for num op i for i=1..12 using vectorised operations if NumPy present."""
    lines = []
    if HAS_NUMPY and op in ['+', '-', '*', '/']:
        i_vals = np.arange(1, 13)
        if op == '+':
            ans = num + i_vals
        elif op == '-':
            ans = num - i_vals
        elif op == '*':
            ans = num * i_vals
        else:  # division
            ans = np.round(num / i_vals.astype(float), 2)
        for i, a in zip(i_vals, ans):
            lines.append(f"{num} {op} {int(i)} = {a}")
        return lines
    # fallback python
    for i in range(1, 13):
        lines.append(f"{num} {op} {i} = {compute_answer(num, op, i)}")
    return lines

def numpy_status_text():
    return "NumPy: ENABLED" if HAS_NUMPY else "NumPy: NOT INSTALLED (using Python math)"
def get_maths_fact(number):
    fallback_facts = [
        "Did you know? 0 is the only number that can't be represented in Roman numerals.",
        "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.",
        "Multiplication is repeated addition.",
        "Division is the inverse of multiplication.",
        f"The number {number} has interesting properties in arithmetic!",
    ]
    try:
        return random.choice(fallback_facts)
    except Exception:
        return "Maths facts are temporarily offline."

# Main Menu
def main_menu():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text=f"Welcome to 12 Times Tables, {PLAYER_NAME}!", font=("Arial", 20)).pack(pady=20)
    tk.Button(root, text="Learn Tables", command=learn_tables, width=20).pack(pady=10)
    tk.Button(root, text="Take Quiz", command=take_quiz, width=20).pack(pady=10)
    tk.Button(root, text="Quit", command=root.quit, width=20).pack(pady=10)

# Learn Tables
def learn_tables():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Learn Your Tables", font=("Arial", 18)).pack(pady=10)
    # Choices via buttons for younger users
    tk.Label(root, text="Choose an operation:", font=("Arial", 12)).pack(pady=5)
    op_var = tk.StringVar(value='+')
    ops_frame = tk.Frame(root)
    ops_frame.pack()
    for symbol in ['+', '-', '*', '/']:
        tk.Radiobutton(ops_frame, text=symbol, variable=op_var, value=symbol, font=("Arial", 14)).pack(side='left', padx=6)

    tk.Label(root, text="Choose a number (0-12):", font=("Arial", 12)).pack(pady=5)
    num_var = tk.IntVar(value=12)
    num_spin = tk.Spinbox(root, from_=0, to=12, textvariable=num_var, width=5, font=("Arial", 12))
    num_spin.pack()

    # area for interactive question display
    q_frame = tk.Frame(root)
    q_frame.pack(pady=10)

    # Show the full table immediately (for learners who just want to view it)
    def show_table():
        op = op_var.get()
        try:
            num = int(num_var.get())
            if num < 0 or num > 12:
                messagebox.showerror("Error", "Number must be 0-12.")
                return
        except:
            messagebox.showerror("Error", "Invalid number.")
            return

        lines = generate_table_lines(num, op)
        table_text = "\n".join(lines)

        # show table in a simple popup
        messagebox.showinfo("Table Result", table_text)

        # Note: Maths fact popups are shown only once at startup now.

    def start_learning():
        op = op_var.get()
        num = num_var.get()
        try:
            num = int(num)
        except:
            messagebox.showerror("Error", "Invalid number selection.")
            return

        # sequence over 1..12
        index = {'i': 1}

        for widget in q_frame.winfo_children():
            widget.destroy()

        question_label = tk.Label(q_frame, text="", font=("Arial", 16))
        question_label.pack(pady=6)
        answer_entry = tk.Entry(q_frame, font=("Arial", 14))
        answer_entry.pack()

        hint_label = tk.Label(q_frame, text="", font=("Arial", 12), fg='blue')
        hint_label.pack(pady=4)

        # create a persistent submit button so it's always visible for pupils
        submit_btn = tk.Button(q_frame, text="Submit")
        submit_btn.pack(pady=6)

        def ask_next():
            i = index['i']
            if i > 12:
                messagebox.showinfo("Well done!", f"Great work, {PLAYER_NAME}! You completed the table for {num} {op}.")
                main_menu()
                return

            # compute correct answer depending on op
            correct = compute_answer(num, op, i)

            question_label.config(text=f"{num} {op} {i} = ?")
            answer_entry.delete(0, 'end')
            hint_label.config(text=f"Question {i} of 12")

            def submit():
                val = answer_entry.get().strip()
                if not val:
                    messagebox.showerror("Error", "Please enter an answer.")
                    return
                try:
                    user_val = float(val) if '.' in val else int(val)
                except:
                    messagebox.showerror("Error", "Please enter a number.")
                    return

                # comparison with tolerance for division
                if isinstance(correct, float):
                    if HAS_NUMPY:
                        is_correct = bool(np.isclose(float(user_val), correct, atol=0.01))
                    else:
                        is_correct = abs(float(user_val) - correct) < 0.01
                else:
                    is_correct = int(user_val) == correct

                if is_correct:
                    messagebox.showinfo("Correct!", f"Good job, {PLAYER_NAME}! That's right.")
                    index['i'] += 1
                    ask_next()
                else:
                    # give higher/lower hint
                    try:
                        numeric = float(user_val)
                        if numeric < correct:
                            hint = "Try a bit higher!"
                        else:
                            hint = "Try a bit lower!"
                    except:
                        hint = "That's not quite right."
                    hint_label.config(text=hint)

            # wire the persistent submit button to this question's submit handler
            submit_btn.config(command=submit)

        ask_next()

    tk.Button(root, text="Show Table", command=show_table, bg='#87cefa', font=("Arial", 12)).pack(pady=6)
    # Show NumPy status
    tk.Label(root, text=numpy_status_text(), font=("Arial", 10), fg='gray').pack(pady=2)
    
    tk.Button(root, text="Start Learning", command=start_learning, bg='#8fbc8f', font=("Arial", 12)).pack(pady=6)
    tk.Button(root, text="Back to Menu", command=main_menu).pack(pady=5)

# Quiz
def take_quiz():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Take the Tables Quiz", font=("Arial", 18)).pack(pady=10)
    # show the stored player name (captured at program start)
    tk.Label(root, text=f"Player: {PLAYER_NAME}").pack(pady=5)

    # configuration: allow pupil to choose a maximum operand (1..20)
    tk.Label(root, text="Choose maximum number for operands (0-12):").pack()
    max_var = tk.IntVar(value=12)
    tk.Spinbox(root, from_=0, to=12, textvariable=max_var, width=5).pack(pady=4)

    # store pupil name and quiz state
    pupil_name = [PLAYER_NAME]
    lives = [3]
    consecutive_wrong = [0]
    question_num = [0]

    QUIZ_RESULTS.clear()
    QUIZ_RESULTS.extend([[0, 0, 0, None, None, None] for _ in range(20)])  # Pre-allocate 20 rows

    def start_quiz():
        # begin with first question
        question_num[0] = 0
        lives[0] = 3
        consecutive_wrong[0] = 0
        for i in range(20):
            QUIZ_RESULTS[i] = [0, 0, 0, None, None, None]
        next_question()

    def next_question():
        if question_num[0] >= 20:
            show_results(pupil_name[0])
            return
        if lives[0] <= 0:
            show_results(pupil_name[0])
            return

        # Allow range 0..12; if user picks 0, only 0-based questions produced
        raw_max = int(max_var.get())
        if raw_max < 0:
            raw_max = 0
        if raw_max > 12:
            raw_max = 12
        max_n = raw_max

        # pick an operator and operands
        op = random.choice(['+', '-', '*', '/'])
        if op == '/':
            # ensure denominator is never zero; allow numerator to be zero
            b = random.randint(1, max_n if max_n >= 1 else 1)
            q = random.randint(0, max_n)
            a = b * q  # guarantees exact division result
        else:
            a = random.randint(0, max_n)
            b = random.randint(0, max_n)

        # encode operator as required (1=+,2=-,3=*,4=/)
        op_code = {'+':1, '-':2, '*':3, '/':4}[op]

        # calculate correct answer
        correct_ans = compute_answer(a, op, b)

        # store in results
        QUIZ_RESULTS[question_num[0]][0] = a
        QUIZ_RESULTS[question_num[0]][1] = op_code
        QUIZ_RESULTS[question_num[0]][2] = b
        QUIZ_RESULTS[question_num[0]][4] = correct_ans

        # render question UI
        for widget in root.winfo_children():
            widget.destroy()
        tk.Label(root, text=f"Question {question_num[0]+1} of 20", font=("Arial", 14)).pack(pady=6)
        tk.Label(root, text=f"{a} {op} {b} = ?", font=("Arial", 18)).pack(pady=4)
        answer_entry = tk.Entry(root, font=("Arial", 14))
        answer_entry.pack()

        info_label = tk.Label(root, text=f"Lives: {lives[0]}    Player: {PLAYER_NAME}", fg='blue')
        info_label.pack(pady=6)

        def submit_answer():
            val = answer_entry.get().strip()
            if val == '999':
                show_results(pupil_name[0])
                return
            try:
                user_ans = float(val) if '.' in val else int(val)
            except:
                messagebox.showerror("Error", "Please enter a number or 999 to quit.")
                return

            QUIZ_RESULTS[question_num[0]][3] = user_ans

            # check correctness (allow small tolerance for division)
            if isinstance(correct_ans, float):
                if HAS_NUMPY:
                    correct = bool(np.isclose(float(user_ans), correct_ans, atol=0.01))
                else:
                    correct = abs(float(user_ans) - correct_ans) < 0.01
            else:
                try:
                    correct = int(user_ans) == correct_ans
                except:
                    correct = False

            if correct:
                QUIZ_RESULTS[question_num[0]][5] = 1
                consecutive_wrong[0] = 0
                messagebox.showinfo("Correct!", f"Well done, {PLAYER_NAME}!")
            else:
                QUIZ_RESULTS[question_num[0]][5] = 0
                consecutive_wrong[0] += 1
                if consecutive_wrong[0] >= 2:
                    lives[0] = max(0, lives[0] - 1)
                    consecutive_wrong[0] = 0
                    messagebox.showinfo("Life Lost", f"You lost a life, {PLAYER_NAME}. Lives remaining: {lives[0]}")
                else:
                    messagebox.showinfo("Try Again", f"Not quite, {PLAYER_NAME}. One more wrong answer will lose a life.")

            question_num[0] += 1
            next_question()

        tk.Button(root, text="Submit", command=submit_answer).pack(pady=6)
        tk.Button(root, text="Quit Quiz", command=lambda: show_results(pupil_name[0])).pack(pady=6)

    tk.Button(root, text="Start Quiz", command=start_quiz, width=20, bg='#f4a460').pack(pady=8)
    tk.Button(root, text="Back to Menu", command=main_menu, width=20).pack(pady=6)


# Show results and save to file
def show_results(name):
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text=f"{name}'s Quiz Results", font=("Arial", 18)).pack(pady=10)
    
    score = sum([1 for row in QUIZ_RESULTS if row[5]==1])
    tk.Label(root, text=f"Score: {score}/{len(QUIZ_RESULTS)}").pack(pady=5)
    
    op_map_rev = {1: '+', 2: '-', 3: '*', 4: '/'}
    for i, row in enumerate(QUIZ_RESULTS):
        op_sym = op_map_rev.get(row[1], '?')
        tk.Label(root, text=f"{row[0]} {op_sym} {row[2]} = {row[4]} | Your Answer: {row[3]} | {'Correct' if row[5]==1 else 'Incorrect'}").pack()
    
    # Save to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    rnd = random.randint(1, 999)
    filename = f"{name}-{timestamp}-{rnd}.txt"
    with open(filename, 'w') as f:
        f.write(f"Quiz Results for {name}\n\n")
        for i, row in enumerate(QUIZ_RESULTS):
            f.write(f"Q{i+1}: {row[0]} {row[1]} {row[2]} = {row[4]} | Your Answer: {row[3]} | {'Correct' if row[5]==1 else 'Incorrect'}\n")
        f.write(f"\nFinal Score: {score}/{len(QUIZ_RESULTS)}\n")
    
    tk.Button(root, text="Back to Menu", command=main_menu).pack(pady=10)

# Main
root = tk.Tk()
root.title("12 Times Tables Learning")
root.geometry("500x600")
def ask_player_name():
    global PLAYER_NAME
    try:
        name = simpledialog.askstring("Player Name", "What's your name?", parent=root)
        if name and name.strip():
            PLAYER_NAME = name.strip()
    except Exception:
        # If dialogs aren't available for some reason, keep default name
        PLAYER_NAME = PLAYER_NAME

def show_startup_fact_once():
    global FACT_SHOWN
    if FACT_SHOWN:
        return
    try:
        # pick a number between 0 and 12 for a relevant fact
        n = random.randint(0, 12)
        messagebox.showinfo("Maths Fact", get_maths_fact(n))
    finally:
        FACT_SHOWN = True

ask_player_name()
# Show a single maths fact after the name is provided
show_startup_fact_once()
main_menu()
root.mainloop()
