import os
import random
import pandas as pd
import streamlit as st

st.markdown("""
<style>
/* Visas puslapio fonas */
[data-testid="stAppViewContainer"] {
    background-image: url("https://raw.githubusercontent.com/JURGITELE1/sviesos-kelias/main/images/fonas.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Nuimame papildomus fonus */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stToolbar"] {
    right: 1rem;
}

/* Pagrindinis turinio blokas - štai čia svarbiausia */
.main .block-container {
    background: rgba(200, 240, 210, 0.92);
    border-radius: 28px;
    padding: 2rem 2rem 3rem 2rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 12px 32px rgba(0,0,0,0.18);
}

/* Tekstas */
h1, h2, h3 {
    color: #153015 !important;
    text-align: center;
    text-shadow: 0 1px1px
    rgba(255,255,255,0.5);
}

p, label, span, div {
    color: #1b2a1b ! important;
    font-weight: 500;
}

/* Mygtukai */
.stButton > button {
    width: 100%;
    border: none;
    border-radius: 16px;
    background: linear-gradient(90deg, #c7f464, #fde68a);
    color: #243424 !important;
    font-weight: 700;
    padding: 0.75rem 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #b6ea4e, #f8d95a);
}

/* Įvesties laukai */
.stTextInput input,
.stTextArea textarea {
    background: #ffffff !important;
    color: #243424 !important;
    border: 1px solid #d6dfb4 !important;
    border-radius: 14px !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #243424 !important;
    border-radius: 14px !important;
}

/* Radio pasirinkimai */
.stRadio > div {
    background: rgba(255,255,255,0.92);
    border-radius: 16px;
    padding: 0.5rem 0.8rem;
}

/* Info blokai */
div[data-testid="stAlert"] {
    border-radius: 16px;
}

/* Paveikslai */
img {
    border-radius: 18px;
}

/* Linija */
hr {
    border: none;
    height: 1px;
    background: rgba(46,125,50,0.18);
    margin: 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Šviesos kelias", page_icon="✨")

CSV_FILE = "steps.csv"
IMAGE_FOLDER = "images"

STEP_JUMP_MAP = {
    1: 7,
    2: 11,
    3: 6,
    4: 10,
    5: 3,
    6: 9,
    7: 10,
    8: 7,
    9: 5,
    10: 7,
    11: 8,
    12: 10,
}

st.markdown("<h1>🌱 Šviesos kelias</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:1.1rem; color:#486248; margin-top:-8px; margin-bottom:24px;'>Tavo vidinės krypties žaidimas ✨</p>",
    unsafe_allow_html=True
)

# -------------------------
# Patikrinimai
# -------------------------
if not os.path.exists(IMAGE_FOLDER):
    st.error("Nerastas aplankas 'images'.")
    st.stop()

all_images = [
    f for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
and f.lower() not in ["fonas.jpg"]
]

if not all_images:
    st.error("Aplanke 'images' nėra paveikslėlių.")
    st.stop()

if not os.path.exists(CSV_FILE):
    st.error("Nerastas failas 'steps.csv'.")
    st.stop()

try:
    df_steps = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
except Exception as e:
    st.error(f"Nepavyko nuskaityti steps.csv: {e}")
    st.stop()

required_columns = [
    "step_number",
    "step_name",
    "question_1",
    "question_2",
    "question_3",
    "question_4",
]

missing_columns = [c for c in required_columns if c not in df_steps.columns]
if missing_columns:
    st.error(f"CSV faile trūksta stulpelių: {missing_columns}")
    st.stop()

steps_data = []
for _, row in df_steps.iterrows():
    steps_data.append(
        {
            "step_number": int(row["step_number"]),
            "step_name": str(row["step_name"]),
            "questions": [
                str(row["question_1"]),
                str(row["question_2"]),
                str(row["question_3"]),
                str(row["question_4"]),
            ],
        }
    )

# -------------------------
# Pagalbinės funkcijos
# -------------------------
def get_step(step_number: int):
    for step in steps_data:
        if step["step_number"] == step_number:
            return step
    return None


def create_player_state():
    return {
        "user_input": "",
        "query_saved": False,
        "dice_result": None,
        "start_card": None,
        "start_answer": "",
        "start_saved": False,
        "goal_card": None,
        "goal_answer": "",
        "goal_saved": False,
        "current_step": 1,
        "current_card": None,
        "question_data": None,
        "visit_history": [],
        "visit_counter": 0,
        "position": 0,
        "group_finished": False,
        "final_answer": "",
        "final_saved": False,
    }


def get_used_cards(player: dict):
    used = []
    if player["start_card"]:
        used.append(player["start_card"])
    if player["goal_card"]:
        used.append(player["goal_card"])
    if player["current_card"]:
        used.append(player["current_card"])
    for item in player["visit_history"]:
        if item.get("card"):
            used.append(item["card"])
    return used


def get_random_card(player=None, extra_exclude=None):
    exclude = list(extra_exclude or [])
    if player is not None:
        exclude.extend(get_used_cards(player))

    possible = [img for img in all_images if img not in exclude]

    if not possible:
        possible = all_images[:]

    return random.choice(possible)


def show_cards_grid(cards, title):
    st.markdown("---")
    st.subheader(title)
    cols = st.columns(4)
    for i, (label, card) in enumerate(cards):
        with cols[i % 4]:
            st.caption(label)
            st.image(os.path.join(IMAGE_FOLDER, card), width="stretch")


# -------------------------
# Session state
# -------------------------
if "players" not in st.session_state:
    st.session_state.players = {
        "Žaidėjas 1": create_player_state(),
        "Žaidėjas 2": create_player_state(),
        "Žaidėjas 3": create_player_state(),
        "Žaidėjas 4": create_player_state(),
        "Žaidėjas 5": create_player_state(),
        "Žaidėjas 6": create_player_state(),
        "Žaidėjas 7": create_player_state(),
    }

# -------------------------
# Viršutiniai pasirinkimai
# -------------------------
mode = st.radio(
    "Pasirink režimą",
    ["Pilna versija", "Grupinė versija"],
    horizontal=True,
)

player_name = st.selectbox(
    "Pasirink žaidėją",
    list(st.session_state.players.keys())
)

player = st.session_state.players[player_name]

st.markdown(f"## {player_name}")

# -------------------------
# Vedlio panelė
# -------------------------
st.markdown("""
<div style="
    background: linear-gradient(90deg, rgba(199,244,100,0.35), rgba(255,255,255,0.72));
    border-radius: 22px;
    padding: 18px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
">
    <div style="font-size:1.2rem; font-weight:700; color:#2e7d32; margin-bottom:12px; text-align:center;">
        🧭 Vedlio panelė
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.72); padding:14px; border-radius:18px;">
        <div><strong>👤 Žaidėjas:</strong> {player_name}</div>
        <div style="margin-top:6px;"><strong>🎮 Režimas:</strong> {mode}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if mode == "Pilna versija":
        position_text = f"Dabartinis žingsnis: {player['current_step']}"
    else:
        position_text = f"Pozicija: {player['position']} / 12"

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.72); padding:14px; border-radius:18px;">
        <div><strong>📍 {position_text}</strong></div>
        <div style="margin-top:6px;"><strong>🔢 Atsakymų kiekis:</strong> {len(player['visit_history'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if not player["goal_saved"]:
        status_text = "pradžia"
    elif player["goal_saved"] and len(player["visit_history"]) == 0:
        status_text = "pasiruošęs kelionei"
    elif player["group_finished"] or player["final_saved"]:
        status_text = "kelias baigtas"
    else:
        status_text = "procese"

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.72); padding:14px; border-radius:18px;">
        <div><strong>🗺️ Būsena:</strong> {status_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
# -------------------------
# Bendra pradžia abiem režimams
# -------------------------
st.subheader("1 etapas – Užklausa")
player["user_input"] = st.text_input(
    "Įrašyk savo klausimą",
    value=player["user_input"],
    key=f"user_input_{player_name}",
)

if st.button("Išsaugoti užklausą", key=f"save_query_{player_name}"):
    if player["user_input"].strip():
        player["query_saved"] = True
        st.success("Užklausa įrašyta.")
    else:
        st.warning("Pirmiausia įrašyk užklausą.")

if player["query_saved"]:
    st.subheader("2 etapas – Kauliukas (tikslas – 6)")
    if st.button("Mesti kauliuką", key=f"dice6_{player_name}"):
        player["dice_result"] = random.randint(1, 6)

    if player["dice_result"] is not None:
        st.write(f"Iškrito: {player['dice_result']}")
        if player["dice_result"] == 6:
            st.success("Gali judėti toliau.")
        else:
            st.warning("Bandyk dar kartą.")

if player["dice_result"] == 6:
    st.subheader("3 etapas – Kokiame taške esi?")

    if player["start_card"] is None:
        player["start_card"] = get_random_card(player)

    st.image(os.path.join(IMAGE_FOLDER, player["start_card"]), width="stretch")

    player["start_answer"] = st.text_area(
        "Ką tau sako ši kortelė?",
        value=player["start_answer"],
        key=f"start_answer_{player_name}",
    )

    if st.button("Išsaugoti atsakymą (3 etapas)", key=f"save_start_{player_name}"):
        if player["start_answer"].strip():
            player["start_saved"] = True
            st.success("Atsakymas įrašytas.")
        else:
            st.warning("Pirmiausia įrašyk atsakymą.")

if player["start_saved"]:
    st.subheader("4 etapas – Kur nori nueiti?")

    if player["goal_card"] is None:
        player["goal_card"] = get_random_card(player, [player["start_card"]])

    st.image(os.path.join(IMAGE_FOLDER, player["goal_card"]), width="stretch")

    player["goal_answer"] = st.text_area(
        "Ką tau sako ši kortelė?",
        value=player["goal_answer"],
        key=f"goal_answer_{player_name}",
    )

    if st.button("Išsaugoti atsakymą (4 etapas)", key=f"save_goal_{player_name}"):
        if player["goal_answer"].strip():
            player["goal_saved"] = True
            st.success("Atsakymas įrašytas.")
        else:
            st.warning("Pirmiausia įrašyk atsakymą.")

# -------------------------
# Pilna versija
# -------------------------
if mode == "Pilna versija" and player["goal_saved"]:
    step = get_step(player["current_step"])
    if step is None:
        st.error("Nepavyko rasti žingsnio.")
        st.stop()

    st.subheader(f"{step['step_number']} žingsnis – {step['step_name']}")

    if player["current_card"] is None:
        player["current_card"] = get_random_card(player)

    st.image(os.path.join(IMAGE_FOLDER, player["current_card"]), width="stretch")

    if st.button("Traukti klausimą", key=f"draw_q_full_{player_name}"):
        idx = random.randint(0, 3)
        player["question_data"] = {
            "text": step["questions"][idx],
            "index": idx + 1,
        }

    if player["question_data"]:
        st.info(player["question_data"]["text"])

        answer = st.text_area(
            "Tavo atsakymas",
            key=f"full_answer_{player_name}_{player['visit_counter']}_{player['current_step']}",
        )

        if st.button("Išsaugoti atsakymą", key=f"save_full_answer_{player_name}"):
            if answer.strip():
                player["visit_counter"] += 1
                player["visit_history"].append(
                    {
                        "visit_no": player["visit_counter"],
                        "step_number": player["current_step"],
                        "step_name": step["step_name"],
                        "question_index": player["question_data"]["index"],
                        "question_text": player["question_data"]["text"],
                        "answer": answer,
                        "card": player["current_card"],
                    }
                )
                st.success("Atsakymas įrašytas.")
            else:
                st.warning("Įrašyk atsakymą.")

        if player["question_data"]["index"] == 4:
            if st.button("Pereiti į nukreiptą žingsnį", key=f"jump_full_{player_name}"):
                next_step = STEP_JUMP_MAP.get(player["current_step"])
                if next_step:
                    player["current_step"] = next_step
                    player["current_card"] = None
                    player["question_data"] = None
                    st.rerun()
                else:
                    st.warning("Šiam žingsniui nėra nurodyto perėjimo.")
        else:
            if st.button("Kitas žingsnis", key=f"next_full_{player_name}"):
                next_step = player["current_step"] + 1
                if next_step <= len(steps_data):
                    player["current_step"] = next_step
                    player["current_card"] = None
                    player["question_data"] = None
                    st.rerun()
                else:
                    st.success("Pasiektas kelio galas.")

# -------------------------
# Grupinė versija
# -------------------------
if mode == "Grupinė versija" and player["goal_saved"]:
    st.subheader("Grupinis režimas – judėjimas per laukelius (D3)")
    st.write(f"*Dabartinė pozicija:* {player['position']}")

    if not player["group_finished"]:
        if st.button("Mesti D3", key=f"roll_d3_{player_name}"):
            roll = random.randint(1, 3)
            player["dice_result"] = roll
            player["position"] += roll

            if player["position"] > 12:
                player["position"] = 12

            player["current_step"] = player["position"]
            player["current_card"] = None
            player["question_data"] = None

        if player["dice_result"] is not None:
            st.write(f"🎲 Iškrito: {player['dice_result']}")
            st.write(f"➡️ Nauja pozicija: {player['position']}")

        if player["position"] > 0:
            step = get_step(player["current_step"])
            if step:
                st.subheader(f"Žingsnis {step['step_number']} – {step['step_name']}")

                if player["current_card"] is None:
                    player["current_card"] = get_random_card(player)

                st.image(os.path.join(IMAGE_FOLDER, player["current_card"]), width="stretch")

                if st.button("Traukti klausimą", key=f"draw_q_group_{player_name}"):
                    idx = random.randint(0, 3)
                    player["question_data"] = {
                        "text": step["questions"][idx],
                        "index": idx + 1,
                    }

                if player["question_data"]:
                    st.info(player["question_data"]["text"])

                    answer = st.text_area(
                        "Tavo atsakymas",
                        key=f"group_answer_{player_name}_{player['visit_counter']}_{player['current_step']}",
                    )

                    if st.button("Išsaugoti atsakymą", key=f"save_group_answer_{player_name}"):
                        if answer.strip():
                            player["visit_counter"] += 1
                            player["visit_history"].append(
                                {
                                    "visit_no": player["visit_counter"],
                                    "step_number": player["current_step"],
                                    "step_name": step["step_name"],
                                    "question_index": player["question_data"]["index"],
                                    "question_text": player["question_data"]["text"],
                                    "answer": answer,
                                    "card": player["current_card"],
                                    "roll": player["dice_result"],
                                    "position": player["position"],
                                }
                            )
                            st.success("Atsakymas įrašytas.")
                        else:
                            st.warning("Įrašyk atsakymą.")

                    if player["question_data"]["index"] == 4:
                        next_step = STEP_JUMP_MAP.get(player["current_step"])

                        if next_step:
                            st.info(f"Šis 4 klausimas nukreipia į {next_step} žingsnį.")

                            if st.button("Pereiti į nukreiptą žingsnį", key=f"group_jump_{player_name}"):
                                player["current_step"] = next_step
                                player["position"] = next_step
                                player["current_card"] = None
                                player["question_data"] = None

                                if next_step < 12:
                                    player["group_finished"] = False

                                st.rerun()
                        else:
                            st.warning("Šiam žingsniui nėra nurodyto nukreipimo.")

                    if player["question_data"]["index"] != 4:
                        if player["position"] == 12:
                            if st.button("Užbaigti kelią", key=f"finish_group_{player_name}"):
                                player["group_finished"] = True
                                player["question_data"] = None
                                st.rerun()

    if player["group_finished"]:
        st.success("🎉 Žaidėjas pasiekė 12 laukelį. Kelias baigtas.")
        player["final_answer"] = st.text_area(
            "Ką supratai pasiekęs šio kelio pabaigą?",
            value=player["final_answer"],
            key=f"group_final_{player_name}",
        )
        if st.button("Išsaugoti paskutinį klausimą", key=f"save_group_final_{player_name}"):
            if player["final_answer"].strip():
                player["final_saved"] = True
                st.success("Paskutinis atsakymas išsaugotas 🌿")
            else:
                st.warning("Įrašyk paskutinį atsakymą.")

# -------------------------
# Bendra santrauka
# -------------------------
if player["visit_history"]:
    st.markdown("---")
    st.subheader("Šio žaidėjo kelio istorija")
    for item in player["visit_history"]:
        st.write(f"*Apsilankymas #{item['visit_no']}*")
        st.write(f"Žingsnis: {item['step_number']} – {item['step_name']}")
        st.write(f"Klausimas #{item['question_index']}: {item['question_text']}")
        st.write(f"Atsakymas: {item['answer']}")
        if "roll" in item:
            st.write(f"Iškrito: {item['roll']}")
            st.write(f"Pozicija: {item['position']}")
        st.write("")

if player["visit_history"]:
    cards = []
    if player["start_card"]:
        cards.append(("3 etapas", player["start_card"]))
    if player["goal_card"]:
        cards.append(("4 etapas", player["goal_card"]))
    for item in player["visit_history"]:
        cards.append(
            (
                f"Apsilankymas #{item['visit_no']} | {item['step_number']} žingsnis",
                item["card"],
            )
        )

    show_cards_grid(cards, "Šio žaidėjo visos kortelės")

if player["visit_history"]:
    st.markdown("---")
    st.subheader("Apibendrinimas")

    player["final_answer"] = st.text_area(
        "Žvelgdamas į visą savo kelią ir korteles, ką dabar supranti apie savo kryptį ir veiksmą?",
        value=player["final_answer"],
        key=f"summary_{player_name}",
    )

    if st.button("Išsaugoti apibendrinimą", key=f"save_summary_{player_name}"):
        if player["final_answer"].strip():
            player["final_saved"] = True
            st.success("Apibendrinimas išsaugotas 🌿")
        else:
            st.warning("Įrašyk apibendrinimą.")

# -------------------------
# Vedlio slaptos įžvalgos
# -------------------------
st.markdown("---")
st.markdown("### 🔒 Vedlio įžvalgos (nematoma žaidėjui)")

if player["visit_history"]:
    all_answers = " ".join([item["answer"] for item in player["visit_history"]])
    all_answers_lower = all_answers.lower()

    keywords = []

    if "poils" in all_answers_lower:
        keywords.append("poilsio poreikis")
    if "baim" in all_answers_lower:
        keywords.append("baimės tema")
    if "kontrol" in all_answers_lower:
        keywords.append("kontrolės tema")
    if "nežin" in all_answers_lower:
        keywords.append("neaiškumo būsena")
    if "pavarg" in all_answers_lower:
        keywords.append("nuovargis")
    if "nor" in all_answers_lower:
        keywords.append("stiprus noras keistis")

    if keywords:
        st.info(f"🔍 Pastebimos temos: {', '.join(keywords)}")
    else:
        st.info("🔍 Aiški pasikartojanti tema neišryškėjo.")

    visited_steps = [item["step_number"] for item in player["visit_history"]]

    if len(set(visited_steps)) < len(visited_steps):
        st.warning("🔁 Žaidėjas grįžta į tuos pačius etapus – svarbi pasikartojimo tema.")
    else:
        st.success("➡️ Judėjimas per skirtingus etapus – progresas vyksta nuosekliai.")

    st.markdown("**Vedliui:**")
    st.write("Klausk: kas kartojasi? Kur yra įtampa? Ko žmogus dar nemato?")
else:
    st.info("Kol kas nėra duomenų įžvalgoms.")
