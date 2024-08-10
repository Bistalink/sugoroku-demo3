from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import os
from typing import TypedDict
from random import randrange

# Flaskの初期設定
app = Flask(__name__, template_folder="../dist", static_folder="../dist/assets")
app.config["SECRET_KEY"] = "secretkey"
socketio = SocketIO(app, cors_allowed_origins="*")

# 1人のプレイヤーの情報
class Player(TypedDict):
  name: str
  position: int
  sid: str


class Game:
  game_state = {
    "players": [],
    "turn": 0,
    "currentPlayer": 0,
    "gameover": False
  }

  # コンストラクタ
  def __init__(self, player_list) -> None:
    for player in player_list:
      self.game_state["players"].append({
        "name": player["name"],
        "position": 0,
        "sid": player["sid"]
      })
    self.update_state()

  def move(self, player_idx, pos_diff):
    self.game_state["players"][player_idx]["position"] += pos_diff
    self.game_state["turn"] += 1  # ターン数を増やす

    self.game_state["currentPlayer"] = self.game_state["turn"] % len(self.game_state["players"])  # 現在のプレイヤー番号を計算
    self.update_state()


  # ゲームの内部状態を変更した後に必ず呼ぶ
  def update_state(self):
    emit("update", self.game_state, broadcast=True)
    self.__update_player_state()
  
  def __update_player_state(self):
    for index, player in enumerate(self.game_state["players"]):
      playable = index is self.game_state["currentPlayer"]

      player_state = {
        "playable": playable,
        "name": player["name"]
      }

      emit("update_player_state", player_state, room=player["sid"], broadcast=True)



player_list = []
game = None

@app.route("/")
def home():
  return render_template("index.html")

# プレイヤーの参加リクエストが来たとき
@socketio.on("join")
def on_join(playername):
  player_list.append({"name": playername, "sid": request.sid})
  emit("update_players", player_list, broadcast=True)


# ゲームスタートのリクエストが来たとき
@socketio.on("start")
def on_start():
  global game
  game = Game(player_list)
  emit("started", broadcast=True)


# サイコロを振る
@socketio.on("dice")
def on_dice():
  print("Diced!")
  my_dice = randrange(1, 6)
  game.move(game.game_state["currentPlayer"], my_dice)



# クライアントにメッセージを送信
def alert(text: str, sid=None):
  if sid is not None:
    emit("alert", text, room=sid)
  else:
    emit("alert", text, broadcast=True)

# サーバーの起動
port = int(os.environ.get("PORT", 5555))
socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)