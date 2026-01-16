import streamlit as st
import random

# ページ設定

st.set_page_config(page_title="CASINO POKER", layout="centered")

# CSS

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #0b3d2e 0%, #05231a 80%);
}
/* カードの基本スタイル */
.playing-card {
    width: 100px;
    height: 145px;
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 5px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.5);
    user-select: none;
    margin: 0 auto;
}
.card-rank {
    font-size: 18px;
    font-weight: bold;
    width: 100%;
    text-align: left;
    margin-left: 10px;
}
.card-suit {
    font-size: 48px;
}
.card-rank-reverse {
    font-size: 18px;
    font-weight: bold;
    width: 100%;
    text-align: right;
    margin-right: 10px;
    transform: rotate(180deg);
}
</style>
""", unsafe_allow_html=True)

st.title("🎰 ポーカー🎰")

# 定義

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

# カード表示関数（HTML/CSS）

def show_card(card):
    rank, suit = card
    color = "#d63031" if suit in ["♥","♦"] else "#2d3436"
    
    card_html = f"""
    <div class="playing-card" style="color: {color};">
        <div class="card-rank">{rank}</div>
        <div class="card-suit">{suit}</div>
        <div class="card-rank-reverse">{rank}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ゲームロジック

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

# 初期化

if "player_chip" not in st.session_state:
    st.session_state.player_chip = 1_000_000
    st.session_state.cpu_chip = 1_000_000
    st.session_state.phase = "bet"
    st.session_state.game_over = False

st.subheader(
    f"🧑 あなた：{st.session_state.player_chip:,} 💰    "
    f"🤖 CPU：{st.session_state.cpu_chip:,} 💰"
)
st.divider()

# ゲームオーバー画面

if st.session_state.game_over:
    if st.session_state.player_chip <= 0:
        st.error("💀 YOU LOSE... チップがなくなりました 💀")
    else:
        st.success("🎉 YOU WIN! CPUを破産させました 🎉")

    if st.button("最初からやり直す"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# フェーズ：ベット

elif st.session_state.phase == "bet":
    bet = st.number_input("ベット額を選択してください", 100, st.session_state.player_chip, 1000)
    if st.button("勝負を開始する"):
        st.session_state.bet = bet
        st.session_state.deck = create_deck()
        st.session_state.player_hand = [st.session_state.deck.pop() for _ in range(5)]
        st.session_state.cpu_hand = [st.session_state.deck.pop() for _ in range(5)]
        st.session_state.phase = "draw"
        st.rerun()

# フェーズ：ドロー（カード交換）

elif st.session_state.phase == "draw":
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("🧑 あなたの手札")
        cols = st.columns(5)
        keep = []
        for i, c in enumerate(st.session_state.player_hand):
            with cols[i]:
                show_card(c)
                # チェックボックスをカードの下に配置
                keep.append(st.checkbox("KEEP", key=f"k{i}", value=True))
        
        st.write("交換したいカードの「KEEP」を外してください。")
        
        if st.button("カードを交換して結果を見る"):
            # プレイヤーの交換
            for i in range(5):
                if not keep[i]:
                    st.session_state.player_hand[i] = st.session_state.deck.pop()
            # CPUの交換
            for i in cpu_change_indexes(st.session_state.cpu_hand):
                st.session_state.cpu_hand[i] = st.session_state.deck.pop()
            st.session_state.phase = "result"
            st.rerun()

    with col2:
        with st.expander("📜 役一覧と倍率", expanded=True):
            for h in HAND_ORDER[::-1]:
                st.markdown(f"**{h}** (x{HAND_MULTIPLIER[h]})")

# フェーズ：結果発表

elif st.session_state.phase == "result":
    p_role = evaluate(st.session_state.player_hand)
    c_role = evaluate(st.session_state.cpu_hand)

    st.subheader("🧑 あなたの手札")
    cols = st.columns(5)
    for i, c in enumerate(st.session_state.player_hand):
        with cols[i]:
            show_card(c)
    st.info(f"あなたの役: **{p_role}**")

    st.divider()

    st.subheader("🤖 CPUの手札")
    cols = st.columns(5)
    for i, c in enumerate(st.session_state.cpu_hand):
        with cols[i]:
            show_card(c)
    st.info(f"CPUの役: **{c_role}**")

    # 勝敗判定
    p_strength = strength(st.session_state.player_hand)
    c_strength = strength(st.session_state.cpu_hand)

    if p_strength > c_strength:
        gain = st.session_state.bet * HAND_MULTIPLIER[p_role]
        st.session_state.player_chip += gain
        st.session_state.cpu_chip -= gain
        st.balloons()
        st.success(f"勝利！ {gain:,} 💰 を獲得しました！")
    elif p_strength < c_strength:
        loss = st.session_state.bet * HAND_MULTIPLIER[c_role]
        st.session_state.player_chip -= loss
        st.session_state.cpu_chip += loss
        st.error(f"敗北... {loss:,} 💰 を失いました。")
    else:
        st.warning("引き分け！ チップの移動はありません。")

    if st.session_state.player_chip <= 0 or st.session_state.cpu_chip <= 0:
        st.session_state.game_over = True

    if st.button("次のラウンドへ"):
        st.session_state.phase = "bet"
        # KEEP状態をクリア
        for k in list(st.session_state.keys()):
            if k.startswith("k"):
                del st.session_state[k]
        st.rerun()

