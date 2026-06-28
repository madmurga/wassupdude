"""
Math Question Generator - Streamlit App
Run with:  streamlit run question_generator_streamlit.py
Install:   pip install streamlit
"""

import random
import math
import os
import streamlit as st

from account_store import (
    POINTS_BY_DIFFICULTY,
    add_points_to_account,
    authenticate,
    ban_account,
    create_account,
    get_admin_account_rows,
    get_account,
    get_leaderboard_entries,
    unban_account,
)

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be the very first st call)
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Math Question Generator",
    page_icon="📐",
    layout="centered",
)

# ─────────────────────────────────────────────
#  CORE MATH HELPERS
# ─────────────────────────────────────────────

def compute_hcf(a: int, b: int) -> int:
    return math.gcd(a, b)


def compute_lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


def prime_factors(n: int) -> list:
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def count_factors(n: int) -> int:
    count = 0
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count


def get_all_factors(n: int) -> list:
    factors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)


# ─────────────────────────────────────────────
#  QUESTION GENERATORS
# ─────────────────────────────────────────────

def generate_hcf_question(difficulty: str = "medium") -> dict:
    if difficulty == "easy":
        nums = [random.randint(2, 30) for _ in range(2)]
    elif difficulty == "hard":
        nums = [random.randint(20, 200) for _ in range(3)]
    else:
        nums = [random.randint(10, 100) for _ in range(2)]

    answer = nums[0]
    for n in nums[1:]:
        answer = math.gcd(answer, n)

    num_str = " and ".join(str(n) for n in nums)
    return {
        "type": "HCF",
        "question": f"Find the HCF (Highest Common Factor) of {num_str}.",
        "answer": answer,
        "hint": "List the prime factors of each number, then multiply the common prime factors together.",
    }


def generate_lcm_question(difficulty: str = "medium") -> dict:
    if difficulty == "easy":
        nums = [random.randint(2, 20) for _ in range(2)]
    elif difficulty == "hard":
        nums = [random.randint(10, 80) for _ in range(3)]
    else:
        nums = [random.randint(10, 50) for _ in range(2)]

    answer = nums[0]
    for n in nums[1:]:
        answer = compute_lcm(answer, n)

    num_str = " and ".join(str(n) for n in nums)
    return {
        "type": "LCM",
        "question": f"Find the LCM (Least Common Multiple) of {num_str}.",
        "answer": answer,
        "hint": "Find the prime factorisation of each number. Take the highest power of every prime, then multiply.",
    }


def generate_missing_number_question(difficulty: str = "medium") -> dict:
    variant = random.choice(["arithmetic", "geometric", "squares"])

    if variant == "arithmetic":
        step = random.randint(2, 5) if difficulty == "easy" else (
            random.randint(3, 15) if difficulty == "medium" else random.randint(7, 30))
        start = random.randint(1, 20)
        length = 5 if difficulty != "hard" else 6
        sequence = [start + i * step for i in range(length)]
        rule_desc = f"arithmetic sequence with a common difference of {step}"

    elif variant == "geometric":
        ratio = random.randint(2, 3) if difficulty != "hard" else random.randint(2, 4)
        start = random.randint(1, 5)
        sequence = [start * (ratio ** i) for i in range(5)]
        rule_desc = f"geometric sequence with a common ratio of {ratio}"

    else:
        offset = random.randint(1, 4) if difficulty != "easy" else 1
        base_start = random.randint(2, 5)
        sequence = [(base_start + i + offset - 1) ** 2 for i in range(5)]
        rule_desc = "sequence of perfect squares"

    hidden_idx = random.randint(1, len(sequence) - 2)
    answer = sequence[hidden_idx]
    displayed = [str(n) if i != hidden_idx else "?" for i, n in enumerate(sequence)]

    return {
        "type": "Missing Number",
        "question": f"Find the missing number in the sequence: {', '.join(displayed)}",
        "answer": answer,
        "hint": f"This is a {rule_desc}.",
    }


def generate_square_number_question(difficulty: str = "medium") -> dict:
    variant = random.choice(["is_square", "sqrt", "sequence"])

    if variant == "is_square":
        if random.choice([True, False]):
            base = random.randint(2, 10) if difficulty == "easy" else random.randint(5, 20)
            num = base * base
            answer = 1
            hint = f"{num} = {base} × {base}"
        else:
            num = random.randint(10, 500)
            while int(num ** 0.5) ** 2 == num:
                num = random.randint(10, 500)
            answer = 0
            hint = "The square root of this number is not a whole number."
        return {
            "type": "Square Numbers",
            "question": f"Is {num} a perfect square? (Answer 1 for Yes, 0 for No)",
            "answer": answer,
            "hint": hint,
        }

    elif variant == "sqrt":
        base = (random.randint(2, 12) if difficulty == "easy" else
                random.randint(5, 25) if difficulty == "medium" else
                random.randint(10, 50))
        num = base * base
        return {
            "type": "Square Numbers",
            "question": f"What is the square root of {num}?",
            "answer": base,
            "hint": f"Find a number that, when multiplied by itself, gives {num}.",
        }

    else:
        base = (random.randint(2, 8) if difficulty == "easy" else
                random.randint(5, 15) if difficulty == "medium" else
                random.randint(10, 30))
        if random.choice([True, False]):
            return {
                "type": "Square Numbers",
                "question": f"What is the next perfect square after {base * base}?",
                "answer": (base + 1) ** 2,
                "hint": f"The next perfect square after {base}² is {base + 1}².",
            }
        else:
            return {
                "type": "Square Numbers",
                "question": f"What is the perfect square before {base * base}?",
                "answer": (base - 1) ** 2,
                "hint": f"The perfect square before {base}² is {base - 1}².",
            }


def generate_prime_number_question(difficulty: str = "medium") -> dict:
    def next_prime(n):
        c = n + 1
        while not is_prime(c):
            c += 1
        return c

    variant = random.choice(["is_prime", "count_primes", "next_prev"])

    if variant == "is_prime":
        num = (random.randint(2, 30) if difficulty == "easy" else
               random.randint(20, 100) if difficulty == "medium" else
               random.randint(100, 200))
        return {
            "type": "Prime Numbers",
            "question": f"Is {num} a prime number? (Answer 1 for Yes, 0 for No)",
            "answer": 1 if is_prime(num) else 0,
            "hint": "A prime number is only divisible by 1 and itself.",
        }

    elif variant == "count_primes":
        if difficulty == "easy":
            start, end = random.randint(2, 10), random.randint(11, 30)
        elif difficulty == "medium":
            start, end = random.randint(10, 30), random.randint(31, 60)
        else:
            start, end = random.randint(50, 80), random.randint(81, 120)
        primes = [n for n in range(start, end + 1) if is_prime(n)]
        return {
            "type": "Prime Numbers",
            "question": f"How many prime numbers are there between {start} and {end} (inclusive)?",
            "answer": len(primes),
            "hint": "Count numbers that are only divisible by 1 and themselves.",
        }

    else:
        if difficulty == "easy":
            base = random.choice([2, 3, 5, 7, 11, 13, 17, 19])
        elif difficulty == "medium":
            base = random.choice([23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73])
        else:
            base = random.choice([101, 103, 107, 109, 113, 127, 131, 137, 139, 149])

        if random.choice([True, False]):
            return {
                "type": "Prime Numbers",
                "question": f"What is the next prime number after {base}?",
                "answer": next_prime(base),
                "hint": "Find the next number that is only divisible by 1 and itself.",
            }
        else:
            prev = base - 1
            while not is_prime(prev):
                prev -= 1
            return {
                "type": "Prime Numbers",
                "question": f"What is the prime number just before {base}?",
                "answer": prev,
                "hint": "Work backwards to find a number divisible only by 1 and itself.",
            }


def generate_factors_question(difficulty: str = "medium") -> dict:
    variant = random.choice(["count", "list", "is_factor"])

    if variant == "count":
        num = (random.randint(10, 30) if difficulty == "easy" else
               random.randint(20, 100) if difficulty == "medium" else
               random.randint(50, 200))
        return {
            "type": "Factors",
            "question": f"How many factors does {num} have?",
            "answer": count_factors(num),
            "hint": "A factor divides evenly into the number. Count pairs from 1 up to √n.",
        }

    elif variant == "list":
        num = (random.randint(12, 36) if difficulty == "easy" else
               random.randint(30, 100) if difficulty == "medium" else
               random.randint(60, 200))
        factors = get_all_factors(num)
        return {
            "type": "Factors",
            "question": f"How many factors does {num} have? (List: {', '.join(map(str, factors))})",
            "answer": len(factors),
            "hint": f"The factors of {num} are: {', '.join(map(str, factors))}",
        }

    else:
        num = random.randint(20, 100)
        factors = get_all_factors(num)
        if random.choice([True, False]):
            factor = random.choice(factors)
            return {
                "type": "Factors",
                "question": f"Is {factor} a factor of {num}? (Answer 1 for Yes, 0 for No)",
                "answer": 1,
                "hint": f"{num} ÷ {factor} = {num // factor} with no remainder.",
            }
        else:
            non_factor = random.randint(1, num)
            while non_factor in factors:
                non_factor = random.randint(1, num)
            return {
                "type": "Factors",
                "question": f"Is {non_factor} a factor of {num}? (Answer 1 for Yes, 0 for No)",
                "answer": 0,
                "hint": f"{num} ÷ {non_factor} does not divide evenly.",
            }


def generate_prime_factorization_question(difficulty: str = "medium") -> dict:
    from collections import Counter
    variant = random.choice(["factorize", "product", "verify"])

    if difficulty == "easy":
        num = random.choice([12, 18, 20, 24, 30, 36, 40, 42, 48, 50])
    elif difficulty == "medium":
        num = random.randint(30, 150)
    else:
        num = random.randint(100, 300)

    factors = prime_factors(num)

    if variant == "factorize":
        factor_counts = Counter(factors)
        factor_expr = " × ".join(
            [f"{p}^{c}" if c > 1 else str(p) for p, c in sorted(factor_counts.items())]
        )
        return {
            "type": "Prime Factorization",
            "question": f"How many prime factors does {num} have (counting repeats)?",
            "answer": len(factors),
            "hint": f"The prime factorization of {num} is: {factor_expr}",
        }

    elif variant == "product":
        return {
            "type": "Prime Factorization",
            "question": f"What number has the prime factors: {' × '.join(map(str, factors))}?",
            "answer": num,
            "hint": f"Multiply them together: {' × '.join(map(str, factors))} = {num}",
        }

    else:
        correct_factors = prime_factors(num)
        if random.choice([True, False]):
            test_factors = correct_factors.copy()
            return {
                "type": "Prime Factorization",
                "question": f"Is {' × '.join(map(str, test_factors))} = {num}? (Answer 1 for Yes, 0 for No)",
                "answer": 1,
                "hint": f"Multiply it out: {' × '.join(map(str, test_factors))} = {num}",
            }
        else:
            test_factors = correct_factors.copy()
            if len(test_factors) > 1:
                test_factors[random.randint(0, len(test_factors) - 1)] = random.randint(2, 11)
            return {
                "type": "Prime Factorization",
                "question": f"Is {' × '.join(map(str, test_factors))} the prime factorization of {num}? (Answer 1 for Yes, 0 for No)",
                "answer": 0,
                "hint": f"The correct prime factorization of {num} is {' × '.join(map(str, correct_factors))}",
            }


# ─────────────────────────────────────────────
#  UNIFIED GENERATOR
# ─────────────────────────────────────────────

QUESTION_TYPES = {
    "Random":                   "random",
    "HCF (Highest Common Factor)": "hcf",
    "LCM (Least Common Multiple)": "lcm",
    "Missing Number":           "missing",
    "Square Numbers":           "square",
    "Prime Numbers":            "prime",
    "Factors":                  "factors",
    "Prime Factorization":      "factorization",
}

GENERATORS = {
    "hcf":           generate_hcf_question,
    "lcm":           generate_lcm_question,
    "missing":       generate_missing_number_question,
    "square":        generate_square_number_question,
    "prime":         generate_prime_number_question,
    "factors":       generate_factors_question,
    "factorization": generate_prime_factorization_question,
}

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]


def generate_question(q_type: str = "random", difficulty: str = "medium") -> dict:
    if q_type == "random":
        q_type = random.choice(list(GENERATORS.keys()))
    question = GENERATORS[q_type](difficulty)
    question["difficulty"] = difficulty
    question["points"] = POINTS_BY_DIFFICULTY.get(difficulty, 10)
    return question


def generate_quiz(n: int, q_type: str, difficulty: str) -> list:
    return [generate_question(q_type, difficulty) for _ in range(n)]


# ─────────────────────────────────────────────
#  SESSION STATE INITIALISATION
#  Streamlit reruns the whole script on every
#  interaction, so all state lives here.
# ─────────────────────────────────────────────

def init_state():
    defaults = {
        "mode":            "single",   # "single" | "quiz"
        "question":        None,       # current question dict
        "quiz_questions":  [],
        "quiz_index":      0,
        "score":           0,
        "show_hint":       False,
        "show_answer":     False,
        "answer_checked":  False,
        "answer_correct":  None,       # True / False / None
        "quiz_finished":   False,
        "user_answer":     "",
        "user_key":         None,
        "app_view":         "Practice",
        "admin_authenticated": False,
        "question_awarded": False,
        "last_points_awarded": 0,
        "session_points_earned": 0,
        "quiz_points_earned": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()


def get_admin_password() -> str:
    try:
        admin_password = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        admin_password = ""
    return admin_password or os.environ.get("ADMIN_PASSWORD", "")


def award_points_for_correct_answer(question: dict) -> int:
    if st.session_state.question_awarded:
        st.session_state.last_points_awarded = 0
        return 0

    st.session_state.question_awarded = True
    points = int(question.get("points", 0))
    updated_account = add_points_to_account(st.session_state.user_key, points)

    if updated_account is None:
        st.session_state.last_points_awarded = 0
        return 0

    st.session_state.last_points_awarded = points
    st.session_state.session_points_earned += points

    if st.session_state.mode == "quiz":
        st.session_state.quiz_points_earned += points

    return points


def render_correct_feedback() -> None:
    if st.session_state.user_key and st.session_state.last_points_awarded:
        st.markdown(
            f'<div class="correct-box">✅ Correct! +{st.session_state.last_points_awarded} points</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.user_key:
        st.markdown('<div class="correct-box">✅ Correct! Points already saved.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="correct-box">✅ Correct! Sign in before answering to earn points.</div>',
            unsafe_allow_html=True,
        )


def render_leaderboard() -> None:
    st.subheader("🏆 Leaderboard")
    st.caption("Rankings are based on points earned from correct answers.")

    entries = get_leaderboard_entries()
    if not entries:
        st.info("No points have been earned yet.")
        return

    leader = entries[0]
    st.metric("Current leader", leader["User"], f'{leader["Points"]} points')
    st.dataframe(entries, hide_index=True, use_container_width=True)


def render_admin_panel() -> None:
    st.subheader("Admin Account Manager")

    admin_password = get_admin_password()
    if not admin_password:
        st.warning("Set ADMIN_PASSWORD in Streamlit secrets before using admin tools.")
        st.code('ADMIN_PASSWORD = "choose-a-private-admin-password"', language="toml")
        return

    if not st.session_state.admin_authenticated:
        with st.form("admin_login_form"):
            entered_password = st.text_input("Admin password", type="password")
            submitted = st.form_submit_button("Unlock admin tools", type="primary")

        if submitted:
            if entered_password == admin_password:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.warning("Incorrect admin password.")
        return

    if st.button("Lock admin tools"):
        st.session_state.admin_authenticated = False
        st.rerun()

    rows = get_admin_account_rows()
    if not rows:
        st.info("No accounts have been created yet.")
        return

    st.dataframe(rows, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Ban or Unban")
    usernames = [row["Username"] for row in rows]
    selected_username = st.selectbox("Account", usernames)
    selected_row = next(row for row in rows if row["Username"] == selected_username)

    if selected_row["Banned"]:
        st.warning(f"{selected_username} is currently banned.")
        if st.button("Unban account", type="primary"):
            ok, message = unban_account(selected_username)
            st.success(message) if ok else st.warning(message)
            st.rerun()
    else:
        ban_reason = st.text_input("Ban reason", placeholder="Optional")
        if st.button("Ban account", type="primary"):
            ok, message = ban_account(selected_username, ban_reason)
            st.success(message) if ok else st.warning(message)
            if selected_username.lower() == str(st.session_state.user_key).lower():
                st.session_state.user_key = None
            st.rerun()

# ─────────────────────────────────────────────
#  STYLING
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .question-box {
        background: #f8f9fa;
        border-left: 4px solid #4c8bf5;
        border-radius: 6px;
        padding: 20px 24px;
        font-size: 1.15rem;
        margin-bottom: 16px;
        color: #000000 !important;
    }
    .hint-box {
        background: #fff8e1;
        border-left: 4px solid #ffc107;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.95rem;
        margin-bottom: 12px;
        color: #000000 !important;
    }
    .correct-box {
        background: #e8f5e9;
        border-left: 4px solid #28a745;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 1rem;
        font-weight: bold;
        color: #1b5e20;
    }
    .wrong-box {
        background: #ffebee;
        border-left: 4px solid #dc3545;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 1rem;
        font-weight: bold;
        color: #b71c1c;
    }
    .answer-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 1rem;
        font-weight: bold;
        color: #e65100;
    }
    .score-box {
        background: #e3f2fd;
        border-radius: 8px;
        padding: 12px 20px;
        font-size: 1.1rem;
        font-weight: bold;
        color: #0d47a1;
        text-align: center;
    }
    .type-badge {
        display: inline-block;
        background: #4c8bf5;
        color: white;
        border-radius: 12px;
        padding: 2px 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────

st.title("📐 Math Question Generator")
st.caption("HCF · LCM · Missing Number · Squares · Primes · Factors · Prime Factorization")
st.divider()

# ─────────────────────────────────────────────
#  SIDEBAR  –  Settings
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("Account")
    account = get_account(st.session_state.user_key)

    if st.session_state.user_key and account is None:
        st.session_state.user_key = None
    elif account and account.get("banned"):
        st.warning("This account has been banned.")
        st.session_state.user_key = None
        account = None

    if account:
        st.success(f"Signed in as {account.get('username', st.session_state.user_key)}")
        st.metric("Points", int(account.get("points", 0)))
        st.caption(f"Correct answers: {int(account.get('solved', 0))}")

        if st.button("Log out", use_container_width=True):
            st.session_state.user_key = None
            st.rerun()
    else:
        st.caption("Sign in before answering to save points.")
        account_action = st.radio("Account action", ["Log in", "Create account"])

        if account_action == "Log in":
            with st.form("login_form"):
                login_username = st.text_input("Username")
                login_password = st.text_input("Password", type="password")
                login_submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

            if login_submitted:
                ok, message, user_key = authenticate(login_username, login_password)
                if ok:
                    st.session_state.user_key = user_key
                    st.success(message)
                    st.rerun()
                else:
                    st.warning(message)
        else:
            with st.form("signup_form"):
                signup_username = st.text_input("Choose a username")
                signup_password = st.text_input("Choose a password", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                signup_submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

            if signup_submitted:
                if signup_password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    ok, message, user_key = create_account(signup_username, signup_password)
                    if ok:
                        st.session_state.user_key = user_key
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)

    st.divider()
    st.header("Navigation")
    view_options = ["Practice", "Leaderboard", "Admin"]
    st.session_state.app_view = st.radio(
        "View",
        view_options,
        index=view_options.index(st.session_state.app_view)
        if st.session_state.app_view in view_options
        else 0,
    )

    st.divider()
    st.header("⚙️ Settings")

    mode = st.radio(
        "Mode",
        ["Single Question", "Quiz"],
        index=0 if st.session_state.mode == "single" else 1,
        key="mode_radio",
    )
    st.session_state.mode = "single" if mode == "Single Question" else "quiz"

    st.divider()

    selected_type_label = st.selectbox(
        "Question Type",
        options=list(QUESTION_TYPES.keys()),
        index=0,
    )
    selected_type = QUESTION_TYPES[selected_type_label]

    selected_difficulty = st.selectbox(
        "Difficulty",
        options=DIFFICULTY_LEVELS,
        index=1,
        format_func=str.capitalize,
    )

    if st.session_state.mode == "quiz":
        st.divider()
        quiz_n = st.slider("Number of Questions", min_value=1, max_value=20, value=5)

    st.divider()

    if st.session_state.mode == "single":
        if st.button("🎯 Generate Question", use_container_width=True, type="primary"):
            st.session_state.question       = generate_question(selected_type, selected_difficulty)
            st.session_state.show_hint      = False
            st.session_state.show_answer    = False
            st.session_state.answer_checked = False
            st.session_state.answer_correct = None
            st.session_state.user_answer    = ""
            st.session_state.question_awarded = False
            st.session_state.last_points_awarded = 0
    else:
        if st.button("🎪 Start Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_questions  = generate_quiz(quiz_n, selected_type, selected_difficulty)
            st.session_state.quiz_index      = 0
            st.session_state.score           = 0
            st.session_state.show_hint       = False
            st.session_state.show_answer     = False
            st.session_state.answer_checked  = False
            st.session_state.answer_correct  = None
            st.session_state.user_answer     = ""
            st.session_state.quiz_finished   = False
            st.session_state.question        = st.session_state.quiz_questions[0]
            st.session_state.question_awarded = False
            st.session_state.last_points_awarded = 0
            st.session_state.quiz_points_earned = 0

    if st.button("🔄 Reset", use_container_width=True):
        user_key = st.session_state.get("user_key")
        session_points_earned = st.session_state.get("session_points_earned", 0)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.session_state.user_key = user_key
        st.session_state.session_points_earned = session_points_earned
        st.rerun()


# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────

# ── SINGLE QUESTION MODE ──────────────────────
if st.session_state.app_view == "Leaderboard":
    render_leaderboard()
    st.stop()

if st.session_state.app_view == "Admin":
    render_admin_panel()
    st.stop()

if st.session_state.mode == "single":

    if st.session_state.question is None:
        st.info("👈 Choose a question type and difficulty in the sidebar, then click **Generate Question**.")

    else:
        q = st.session_state.question

        # Type badge + question
        st.markdown(f'<span class="type-badge">{q["type"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-box">{q["question"]}</div>', unsafe_allow_html=True)

        # Hint toggle
        col_hint, col_reveal = st.columns([1, 1])

        with col_hint:
            if st.button("💡 Show Hint" if not st.session_state.show_hint else "💡 Hide Hint"):
                st.session_state.show_hint = not st.session_state.show_hint

        with col_reveal:
            if st.button("👁️ Reveal Answer"):
                st.session_state.show_answer    = True
                st.session_state.answer_checked = False
                st.session_state.answer_correct = None

        if st.session_state.show_hint:
            st.markdown(f'<div class="hint-box">💡 {q["hint"]}</div>', unsafe_allow_html=True)

        st.divider()

        # Answer input
        if not st.session_state.show_answer:
            with st.form("answer_form", clear_on_submit=False):
                user_input = st.text_input(
                    "Your Answer",
                    placeholder="Enter a whole number...",
                    value=st.session_state.user_answer,
                )
                submitted = st.form_submit_button("✓ Check Answer", type="primary")

            if submitted:
                try:
                    user_ans = int(user_input.strip())
                    st.session_state.user_answer    = user_input
                    st.session_state.answer_checked = True
                    st.session_state.answer_correct = (user_ans == q["answer"])
                    st.session_state.last_points_awarded = 0
                    if st.session_state.answer_correct:
                        award_points_for_correct_answer(q)
                except ValueError:
                    st.warning("Please enter a whole number.")

        # Feedback
        if st.session_state.answer_checked:
            if st.session_state.answer_correct:
                render_correct_feedback()
            else:
                st.markdown(
                    f'<div class="wrong-box">❌ Wrong. The correct answer is <b>{q["answer"]}</b>.</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.show_answer:
            st.markdown(
                f'<div class="answer-box">📌 Answer: <b>{q["answer"]}</b></div>',
                unsafe_allow_html=True,
            )


# ── QUIZ MODE ────────────────────────────────
else:
    if not st.session_state.quiz_questions:
        st.info("👈 Set up your quiz in the sidebar and click **Start Quiz**.")

    elif st.session_state.quiz_finished:
        # Results screen
        total      = len(st.session_state.quiz_questions)
        score      = st.session_state.score
        percentage = score / total * 100

        st.subheader("🏆 Quiz Complete!")
        st.markdown(f'<div class="score-box">Score: {score} / {total} &nbsp;|&nbsp; {percentage:.1f}%</div>',
                    unsafe_allow_html=True)
        if st.session_state.user_key:
            st.success(f"You earned {st.session_state.quiz_points_earned} points in this quiz.")
        else:
            st.info("Sign in before starting a quiz to save points to the leaderboard.")
        st.divider()

        # Show all questions and correct answers
        st.subheader("Review")
        for i, q in enumerate(st.session_state.quiz_questions, 1):
            with st.expander(f"Q{i}: {q['type']} — {q['question'][:60]}..."):
                st.write(f"**Question:** {q['question']}")
                st.write(f"**Answer:** {q['answer']}")
                st.write(f"*{q['hint']}*")

        if st.button("🔄 Start a New Quiz", type="primary"):
            user_key = st.session_state.get("user_key")
            session_points_earned = st.session_state.get("session_points_earned", 0)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.session_state.user_key = user_key
            st.session_state.session_points_earned = session_points_earned
            st.rerun()

    else:
        # Active quiz
        idx   = st.session_state.quiz_index
        total = len(st.session_state.quiz_questions)
        q     = st.session_state.quiz_questions[idx]

        # Progress bar + score
        st.markdown(
            f'<div class="score-box">Question {idx + 1} of {total} &nbsp;|&nbsp; Score: {st.session_state.score}</div>',
            unsafe_allow_html=True,
        )
        st.progress((idx) / total)
        st.divider()

        # Question
        st.markdown(f'<span class="type-badge">{q["type"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-box">{q["question"]}</div>', unsafe_allow_html=True)

        # Hint
        col_hint, _ = st.columns([1, 3])
        with col_hint:
            if st.button("💡 Show Hint" if not st.session_state.show_hint else "💡 Hide Hint",
                         key="quiz_hint_btn"):
                st.session_state.show_hint = not st.session_state.show_hint

        if st.session_state.show_hint:
            st.markdown(f'<div class="hint-box">💡 {q["hint"]}</div>', unsafe_allow_html=True)

        st.divider()

        # Answer input (only shown if not yet answered)
        if not st.session_state.answer_checked:
            with st.form("quiz_answer_form", clear_on_submit=True):
                user_input = st.text_input("Your Answer", placeholder="Enter a whole number...")
                col_sub, col_skip = st.columns([2, 1])
                with col_sub:
                    submitted = st.form_submit_button("✓ Submit Answer", type="primary", use_container_width=True)
                with col_skip:
                    skipped = st.form_submit_button("⏭ Skip", use_container_width=True)

            if submitted:
                try:
                    user_ans = int(user_input.strip())
                    correct  = (user_ans == q["answer"])
                    st.session_state.answer_checked  = True
                    st.session_state.answer_correct  = correct
                    st.session_state.last_points_awarded = 0
                    if correct:
                        st.session_state.score += 1
                        award_points_for_correct_answer(q)
                    st.rerun()
                except ValueError:
                    st.warning("Please enter a whole number.")

            if skipped:
                st.session_state.answer_checked  = True
                st.session_state.answer_correct  = None   # skipped: no mark
                st.session_state.last_points_awarded = 0
                st.rerun()

        # Feedback + Next button (shown after answering)
        else:
            if st.session_state.answer_correct is True:
                render_correct_feedback()
            elif st.session_state.answer_correct is False:
                st.markdown(
                    f'<div class="wrong-box">❌ Wrong. The correct answer was <b>{q["answer"]}</b>.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="answer-box">⏭ Skipped. The answer was <b>{q["answer"]}</b>.</div>',
                    unsafe_allow_html=True,
                )

            # Next / Finish button
            is_last = (idx + 1 >= total)
            btn_label = "🏁 See Results" if is_last else "▶ Next Question"

            if st.button(btn_label, type="primary"):
                st.session_state.quiz_index     += 1
                st.session_state.show_hint       = False
                st.session_state.show_answer     = False
                st.session_state.answer_checked  = False
                st.session_state.answer_correct  = None
                st.session_state.user_answer     = ""
                st.session_state.question_awarded = False
                st.session_state.last_points_awarded = 0

                if is_last:
                    st.session_state.quiz_finished = True

                st.rerun()
