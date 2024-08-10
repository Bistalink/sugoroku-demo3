<script lang="ts">
  import type { Socket } from "socket.io-client";
  import type { GameState, Player} from "./util";
  import "animate.css"
  

  export let socket: Socket
  export let started: boolean = false;

  let gameover: boolean;              // ゲームが終了したかどうか
  let gameState: GameState;           // ゲームの内部状態
  let playerState: Player;       // このセッションのプレイヤーの内部状態

  let diceRequested: boolean = false; // サイコロを振るリクエスト中

  let position: number;
  let animationRequired = "";

  let railOffset = 0;

  let winner: string = "";            // 勝者

  // イベントボード
  // TODO: 仮
  let board_events = Array.from({length: 30}, ()=> Math.floor(Math.random() * 6));
  console.log("board:", board_events)

  // ゲーム状態が更新されたとき
  socket.on("update_state", (data: GameState)=>{
    gameState = data;
    console.log(data);
  })

  // プレイヤーの状態が更新されたとき
  socket.on("update_player_state", (data: Player)=>{
    playerState = data;
    position = playerState.position;
    console.log(data);
  })

  // ゲームが終了したとき
  socket.on("gameover", (playername: string)=>{
    gameover = true;
    winner = playername;
  })

  // サイコロを振るリクエストが来たとき
  socket.on("request:dice", ()=>{
    console.log("Dice requested by server");
    diceRequested = true;
  })

  socket.on("animate", (sid: string)=>{
    animationRequired = sid;
    setTimeout(() => {
      animationRequired = "";
    }, 700);
  })

  function dice(){
    socket.emit("dice");
    diceRequested = false;
  }

  function nextRail(){
    railOffset++;
  }

  function prevRail(){
    railOffset--;
  }
</script>


{#if started}
<div>
  <!-- サイコロ回すやつ -->
  <div>
    <button on:click={dice} class="" disabled="{!diceRequested}">サイコロを回す</button>
  </div>

  {#if gameState != undefined && playerState != undefined}
  <div>
    <!-- {#each gameState.players as p}
      <h3>プレイヤー名：{p.name} ポジション：{p.position}</h3>
    {/each} -->

    <!-- プレイヤー情報 -->
    <div id="playerName">プレーヤー名: {playerState.name}</div>
    <div id="position">現在：{playerState.position} マス目</div>
    <div id="remaining">残り：{gameState.goal - playerState.position}マス</div>

    <!-- レール -->
    <!-- TODO:ループで回して全員分表示させる -->
    {#each gameState.players as player}
    <div class="lane">
      <img class="{animationRequired && animationRequired == player["sid"] ? "animate__animated animate__wobble" : ""}" src="" alt="">
      <div class="rail-wrapper">
        <div class="rail" style="left: {-player.position * 5 + 5}rem;">
          {#each board_events as one_grid, index}
          <div class="cell">
            <div></div>
            <p>{index}</p>
          </div>
          <!-- TODO: 開発用 -->
          <!-- <p style="width: 1rem; padding: 0; margin: 0">{one_grid}</p> -->
          {/each}
        </div>
      </div>  
    </div>
    {/each}

    <!-- ゲームクリア画面 -->
    <div class="gameover" style="display: {gameover ? "" : "none"};">
      <h1>{winner} がゴールしました！</h1>
    </div>
  </div>
  {/if}
</div>
{/if}

<style lang="scss">
  .lane {
    display: flex;
    position: relative;
    flex-direction: column;
    height: 10rem;

    img {
      position: absolute;
      width: 4rem;
      height: 4rem;
      left: 5rem;
      background-color: red;
    }
  }

  .rail-wrapper {
    position: relative;
    overflow: hidden;
    width:40rem;
    height: 3rem;
    top: 5rem;
  }

  .rail {
    position: absolute;
    display: flex;
    flex-direction: row;
    gap: 1rem;
    transition: all 0.2s;

    div.cell {
      width: 4rem;
      height: 0.4rem;
      margin: 0;
      padding: 0;

      div {
        background-color: white;
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
      }
    }
  }
</style>