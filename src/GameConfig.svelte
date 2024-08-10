<script lang="ts">
  import {Socket} from "socket.io-client"

  // propsの定義
  export let socket: Socket;
  export let hidden = false;

  let playerList: {name: string, sid: string}[] = [];
  let showWaitingPage = false;

  // プレイヤーの登録
  function join(){
    const playername = (document.getElementById("playername") as HTMLInputElement).value;

    socket.emit("join", playername)
    showWaitingPage = true;
  }

  // ゲームスタート
  function start(){
    socket.emit("start");
  }

  // プレイヤーに変更がある場合は反映
  socket.on("update_player_list", list=>{
    playerList = list;
  });
</script>


<div style="display: {hidden ? "none": ""}" id="main">
  <!-- 新規登録フォーム -->
  <div id="registerPage" style="display: {showWaitingPage ? "none" : ""};"> 
    <h2>プレイヤー名を入力してください</h2>
    <input type="text" name="playername" id="playername">
    <button id="joinButton" on:click={join}>Join</button>
  </div>

  <!-- 待機画面 & 追加の設定 -->
  <div id="waitingPage" style="display: {showWaitingPage ? "" : "none"}">
    <div id="playerList">
      <h2>プレイヤー一覧</h2>
      {#each playerList as player}
      <p>{player.name}</p>
      {/each}
    </div>
    <div id="additionalSettings">
      <h2>追加設定</h2>
    </div>
    <button id="startButton" on:click={start}>START</button>
  </div>
</div>


<style>
  #main{
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.1);
    padding: 1rem;
    border-radius: 1rem;
    min-width: 30rem;
    min-height: 20rem;
  }
</style>