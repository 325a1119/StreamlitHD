import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
import io

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="CASINO POKER", layout="centered")

# =========================
# CSS（カジノ風UI）
# =========================
# 代替案：PILを使わずHTML/CSSでカードを作る
def show_card_css(rank, suit):
    color = "red" if suit in ["♥","♦"] else "black"
    st.markdown(f"""
    <div style="
        width: 80px;
        height: 120px;
        background-color: white;
        border: 2px solid black;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: {color};
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    ">
        <div style="font-size: 20px;">{rank}</div>
        <div style="font-size: 40px;">{suit}</div>
    </div>
    """, unsafe_allow_html=True)

st.title("🎰 CASINO POKER")

# =========================
# 定義
# =========================
SUITS = ["♠","♥","♦","♣"]
RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
RANK_VALUE = {r:i for i,r in enumerate(RANKS, start=2)}

HAND_ORDER = [
    "ハイカード","ワンペア","ツーペア","スリーカード",
    "ストレート","フラッシュ","フルハウス",
    "フォーカード","ストレートフラッシュ","ロイヤルストレートフラッシュ"
]

HAND_MULTIPLIER = {
    "ハイカード":1,"ワンペア":2,"ツーペア":3,"スリーカード":4,
    "ストレート":5,"フラッシュ":6,"フルハウス":8,
    "フォーカード":12,"ストレートフラッシュ":20,"ロイヤルストレートフラッシュ":50
}

HAND_EXAMPLE = {
    "ロイヤルストレートフラッシュ": "A K Q J 10（同一スート）",
    "ストレートフラッシュ": "9 8 7 6 5（同一スート）",
    "フォーカード": "A A A A 3",
    "フルハウス": "K K K 7 7",
    "フラッシュ": "同一スート5枚",
    "ストレート": "連番5枚",
    "スリーカード": "Q Q Q 4 2",
    "ツーペア": "J J 8 8 3",
    "ワンペア": "10 10 A 7 4",
    "ハイカード": "役なし"
}

# =========================
# カード画像生成
# =========================
@st.cache_data
def generate_card_image(rank, suit):
    img = Image.new("RGB", (120, 180), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 48)
        font_small = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    color = "red" if suit in ["♥","♦","♡"] else "black"

    draw.rectangle((0,0,119,179), outline="black", width=3)

    draw.text((8,5), f"{rank}{suit}", fill=color, font=font_small)
    draw.text((40,70), suit, fill=color, font=font_big)

    return img


def show_card(card):
    img = generate_card_image(card[0], card[1])
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=120)

# =========================
# ゲーム関数
# =========================
def create_deck():
    deck = [(r,s) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def evaluate(hand):
    ranks = [r for r,s in hand]
    suits = [s for r,s in hand]
    values = sorted([RANK_VALUE[r] for r in ranks])
    is_flush = len(set(suits)) == 1
    is_straight = values == list(range(values[0], values[0]+5)) or values == [2,3,4,5,14]
    counts = sorted([ranks.count(r) for r in set(ranks)], reverse=True)

    if is_straight and is_flush and max(values)==14:
        return "ロイヤルストレートフラッシュ"
    if is_straight and is_flush:
        return "ストレートフラッシュ"
    if counts==[4,1]:
        return "フォーカード"
    if counts==[3,2]:
        return "フルハウス"
    if is_flush:
        return "フラッシュ"
    if is_straight:
        return "ストレート"
    if counts==[3,1,1]:
        return "スリーカード"
    if counts==[2,2,1]:
        return "ツーペア"
    if counts==[2,1,1,1]:
        return "ワンペア"
    return "ハイカード"

def strength(hand):
    return HAND_ORDER.index(evaluate(hand))

def cpu_change_indexes(hand):
    role = evaluate(hand)
    ranks = [r for r,s in hand]

    if role in ["フルハウス","フォーカード","ストレートフラッシュ","ロイヤルストレートフラッシュ"]:
        return []
    if role in ["フラッシュ","ストレート"]:
        return random.sample(range(5),1)
    if role=="スリーカード":
        main=max(set(ranks), key=ranks.count)
        return [i for i,r in enumerate(ranks) if r!=main]
    if role=="ツーペア":
        pairs=[r for r in set(ranks) if ranks.count(r)==2]
        return [i for i,r in enumerate(ranks) if r not in pairs]
    if role=="ワンペア":
        pair=max(set(ranks), key=ranks.count)
        return [i for i,r in enumerate(ranks) if r!=pair]
    return random.sample(range(5),3)

# =========================
# 初期化
# =========================
if "player_chip" not in st.session_state:
    st.session_state.player_chip = 1_000_000
    st.session_state.cpu_chip = 1_000_000
    st.session_state.phase = "bet"
    st.session_state.game_over = False

st.subheader(
    f"🧑 あなた：{st.session_state.player_chip:,} 💰   "
    f"🤖 CPU：{st.session_state.cpu_chip:,} 💰"
)
st.divider()

# =========================
# YOU WIN / LOSE
# =========================
if st.session_state.game_over:
    if st.session_state.player_chip <= 0:
        st.subheader("💀 YOU LOSE 💀")
    else:
        st.subheader("🎉 YOU WIN 🎉")

    if st.button("最初からやり直す"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# =========================
# ベット
# =========================
elif st.session_state.phase == "bet":
    bet = st.number_input("ベット額",1,st.session_state.player_chip,1)
    if st.button("カードを配る"):
        st.session_state.bet = bet
        st.session_state.deck = create_deck()
        st.session_state.player_hand = [st.session_state.deck.pop() for _ in range(5)]
        st.session_state.cpu_hand = [st.session_state.deck.pop() for _ in range(5)]
        st.session_state.phase = "draw"

# =========================
# ドロー
# =========================
elif st.session_state.phase == "draw":
    col1,col2 = st.columns([3,2])

    with col1:
        st.subheader("🧑 あなたの手札")
        cols = st.columns(5)
        keep=[]
        for i,c in enumerate(st.session_state.player_hand):
            with cols[i]:
                show_card(c)
                keep.append(st.checkbox("KEEP", key=f"k{i}"))

        if st.button("ドロー"):
            for i in range(5):
                if not keep[i]:
                    st.session_state.player_hand[i]=st.session_state.deck.pop()
            for i in cpu_change_indexes(st.session_state.cpu_hand):
                st.session_state.cpu_hand[i]=st.session_state.deck.pop()
            st.session_state.phase="result"
            st.rerun()

        with col2:
            with st.expander("📜 役・例・倍率", expanded=False):
                st.markdown("""
                <div style="
                    background:#ffffff;
                    padding:6px;
                    border-radius:8px;
                    font-size:11px;
                    line-height:1.3;
                ">
                """, unsafe_allow_html=True)

                for h in HAND_ORDER[::-1]:
                    st.markdown(
                        f"**{h}** ×{HAND_MULTIPLIER[h]}<br>"
                        f"<span style='color:gray'>例：{HAND_EXAMPLE[h]}</span><br>",
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 結果
# =========================
elif st.session_state.phase == "result":
    p_role = evaluate(st.session_state.player_hand)
    c_role = evaluate(st.session_state.cpu_hand)

    st.subheader("🧑 あなた")
    cols = st.columns(5)
    for i,c in enumerate(st.session_state.player_hand):
        with cols[i]:
            show_card(c)
    st.success(p_role)

    st.subheader("🤖 CPU")
    cols = st.columns(5)
    for i,c in enumerate(st.session_state.cpu_hand):
        with cols[i]:
            show_card(c)
    st.error(c_role)

    if strength(st.session_state.player_hand) > strength(st.session_state.cpu_hand):
        gain = st.session_state.bet * HAND_MULTIPLIER[p_role]
        st.session_state.player_chip += gain
        st.session_state.cpu_chip -= gain
        st.success(f"+{gain:,} 💰")
    elif strength(st.session_state.player_hand) < strength(st.session_state.cpu_hand):
        loss = st.session_state.bet * HAND_MULTIPLIER[c_role]
        st.session_state.player_chip -= loss
        st.session_state.cpu_chip += loss
        st.error(f"-{loss:,} 💰")
    else:
        st.warning("引き分け")

    if st.session_state.player_chip <= 0 or st.session_state.cpu_chip <= 0:
        st.session_state.game_over = True

    if st.button("次のラウンド"):
        st.session_state.phase="bet"
        for k in list(st.session_state.keys()):
            if k.startswith("k"):
                del st.session_state[k]



