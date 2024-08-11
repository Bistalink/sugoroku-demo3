from typing import TypedDict
from random import randrange, choices, shuffle, randint
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from utils import mask_string
import os

# 環境設定
GOAL = 30
WEIGHT_FACTOR = 1


# Flaskの初期設定
app = Flask(__name__, template_folder="../dist", static_folder="../dist/assets")
app.config["SECRET_KEY"] = "secretkey"
socketio = SocketIO(app, cors_allowed_origins="*")

class Player(TypedDict):
  name: str
  position: int
  sid: str


class Game:
  num_members = 0

  game_state = {
    "players": [],
    "turn": 0,
    "current_player": 0,
    "goal": GOAL,  # TODO: 仮
    "event_list": [],
    "log": []
  }

  question = [
    [["beautiful"], ["美しい"]], 
    [["dog"], ["犬"]], 
    [["cat"], ["ねこ"]]
  ]

  # 与えられたプレイヤーのリストでゲームを初期化
  def __init__(self, player_list):
    # プレイヤーを作成、リストに追加
    for p in player_list:
      self.game_state["players"].append({
        "name": p["name"],
        "sid": p["sid"],
        "position": 0,
        "level": 0,
        "skip": False
      })
    self.num_members = len(player_list)

    # イベントマスを作成
    size = self.game_state["goal"]
    count_5 = int(size * 0.05)
    count_4 = int(size * 0.05)
    count_3 = int(size * 0.1)
    count_2 = int(size * 0.1)
    count_1 = int(size * 0.1)
    count_0 = size - (count_5 + count_4 + count_3 + count_2 + count_1)

        # 出現数に基づいてリストを作成
    elements = ([5] * count_5 +
                [4] * count_4 +
                [3] * count_3 +
                [2] * count_2 +
                [1] * count_1 +
                [0] * count_0)
    
    shuffle(elements)

    result = []
    prev_non_zero = None

    for elem in elements:
      if elem != 0:
        # 0以外の数字が連続しないように配置
        if prev_non_zero is not None and prev_non_zero != 0:
          result.append(0)
        result.append(elem)
        prev_non_zero = elem
      else:
        result.append(elem)
        prev_non_zero = 0
        # 要素数が指定したサイズになるように調整
    while len(result) < size:
      result.append(0)

    if len(result) > size:
      result = result[:size]
    
    self.game_state["event_list"] = result

    
  def move(self, diff, player_idx):
    # スキップフラグがついてるときは移動しない
    if self.game_state["players"][player_idx]["skip"]:
      self.game_state["players"][player_idx]["skip"] = False
      return
    
    self.game_state["players"][player_idx]["position"] += diff
    self.animate(player_idx)
    self.update_state()


  def add_turn(self, diff):
    self.game_state["turn"] += diff
    self.game_state["current_player"] = self.game_state["turn"] % self.num_members
    self.update_state()


  def animate(self, player_idx):
    emit("animate", self.game_state["players"][player_idx]["sid"], broadcast=True)


  def update_state(self):
    emit("update_state", self.game_state, broadcast=True)
    self.update_player_state()
  

  def update_player_state(self):
    for player in self.game_state["players"]:
      emit("update_player_state", player, room=player["sid"])


  def update_spectator_state(self):
    spectator = {
        "name": "spectator",
        "position": 0,
        "sid": "spectator",
        "level": 0,
        "skip": "false"
    }
    emit("update_player_state", spectator, broadcast=True)


  def request_dice(self, playeridx):
    emit("request:dice", room=game.get_sid_by_playeridx(playeridx))
  

  def get_playeridx_by_sid(self, sid):
    for index, player in enumerate(self.game_state["players"]):
      if player["sid"] == sid:
        return index
    return None
  

  def get_sid_by_playeridx(self, playeridx):
    return self.game_state["players"][playeridx]["sid"]
  

  def gameover(self, playeridx):
    emit("gameover", self.game_state["players"][playeridx]["name"], broadcast=True)

  # 問題番号をランダムに取得
  def get_question_idx(self, player_idx): # TODO: プレイヤーの難易度に応じて選択
    question_list = self.question
    random_question_idx = randint(0, len(question_list) - 1)
    return random_question_idx
  
  # 正誤判定
  def judgement(self, question_idx, answer: str):
    question_list = self.question
    correct = question_list[question_idx][0][0]
    print(f"答え:{correct}")
    print(f"回答:{answer}")
    return correct == answer
  
  # 問題を送信
  def send_question(self, player_idx, question_idx):
    question_list = self.question
    question = question_list[question_idx]
    payload = {
      "content": [mask_string(question[0][0]), question[1][0]],
      "question_idx": question_idx,
      "sid": self.get_sid_by_playeridx(player_idx)
    }
    emit("request:answer", payload, broadcast=True)
  
  # 指定したプレイヤーの現在マスに応じてイベントを発生させる
  def run_event(self, player_idx: int, correct: bool):
    current_position = self.game_state["players"][player_idx]["position"]
    current_event = self.game_state["event_list"][current_position]
    print(f"Event {current_event} fired!")

    if current_event == 0:  # 正解でプラスいちマス
      if correct:
        self.move(1, player_idx)
      self.add_turn(1)
      self.request_dice(self.game_state["current_player"])
    elif current_event == 1:  # 正解でプラス2マス
      if correct:
        self.move(2, player_idx)
      self.add_turn(1)
      self.request_dice(self.game_state["current_player"])
    elif current_event == 2:  # 不正解でマイナス1マス
      if not correct:
        self.move(-1, player_idx)
      self.add_turn(1)
      self.request_dice(self.game_state["current_player"])
    elif current_event == 3:  # 不正解でマイナス2マス
      if not correct:
        self.move(-2, player_idx)
      self.add_turn(1)
      self.request_dice(self.game_state["current_player"])
    elif current_event == 4:  # 不正解で1回休み
      if not correct:
        self.game_state["players"][player_idx]["skip"] = True;
      self.add_turn(1)
      self.request_dice(self.game_state["current_player"])
    else:                     # もう1ターン
      if correct:
        self.request_dice(player_idx)
      else:
        self.add_turn(1)
        self.request_dice(self.game_state["current_player"])

  # ログを追記
  def write_log(self, text: str):
    self.game_state["log"].append(text)
      


player_list = []
game = None



@app.route("/")
def index():
  return render_template("index.html")

@socketio.on("dice")
def on_roll_dice():
  idx = game.get_playeridx_by_sid(request.sid)

  # サイコロを振る
  diced = randrange(1, 6)
  game.write_log(f"プレイヤー {game.game_state["players"][idx]["name"]} がサイコロを振りました！")
  game.write_log(f"サイコロの目は {diced} でした")

  # プレイヤーを動かす
  game.move(diced, idx)
  if game.game_state["players"][idx]["position"] >= game.game_state["goal"]:
    game.gameover(idx)
    return
  
  game.send_question(idx, game.get_question_idx(idx))
  # # 次の人に回す
  # game.add_turn(1)
  # # 新しい人にサイコロを振らせる
  # game.request_dice(game.game_state["current_player"])


@socketio.on("join")
def on_join(playername):
  # すでにゲームが始まっている場合は観戦モードになる
  if game is not None:
    emit("started", room=request.sid)
    game.update_state()
    return

  global player_list
  player_list.append({"name": playername, "sid": request.sid})
  emit("update_player_list", player_list, broadcast=True)
  print(f"Player {playername} joined!")


@socketio.on("start")
def on_start():
  global game
  idx = 0
  game = Game(player_list)
  emit("request:dice", room=game.game_state["players"][idx]["sid"])
  emit("started", broadcast=True)
  game.update_state()
  print("Game start requested and START!")
  print(f"Dice requested to player {idx}!")


@socketio.on("answer")
def on_answer(answer):
  user_input = answer["answer"]
  q_idx = answer["question_idx"]
  p_idx = game.get_playeridx_by_sid(request.sid)
  print(f"User Answered question {q_idx}: {user_input}")
  game.write_log(f"プレイヤー {game.game_state["players"][p_idx]["name"]} が問題に答えました！ 回答：{user_input}")
  judge = game.judgement(q_idx, user_input)
  game.write_log("正解です！" if judge else f"不正解です... 正解は {game.question[q_idx][0][0]}でした")
  game.write_log("解説：...（今後追加予定）...")

  game.run_event(p_idx, judge)
  pass


port = int(os.environ.get("PORT", 5555))
socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)