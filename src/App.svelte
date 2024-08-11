<script lang="ts">
  import {connect} from "socket.io-client"

  // Svelteコンポーネントのインポート
  import GameConfig from "./GameConfig.svelte";
  import Sugoroku from "./Sugoroku.svelte";

  import bb_footer from "./assets/bb_footer.png"

  let isGameStarted = false;  // ゲームが始まっているかどうか
  const socket = connect(location.href);

  // 一般メッセージを受信した場合
  socket.on("alert", text=>{
    alert(text)
  });

  // ゲームがスタートしたら画面を切り替える
  socket.on("started", ()=>{
    isGameStarted = true;
  })

  socket.on("dev:restart", ()=>{
    socket.emit("restart_confirmed")

    setTimeout(() => {
      location.reload();
    }, 100);
  })
</script>


<main>
  <button on:click={()=>{socket.emit("restart")}} style="position: absolute; top: 0; left: 0;">（開発用）緊急リセットボタン</button>
  <GameConfig socket={socket} hidden={isGameStarted}/>
  <Sugoroku socket={socket} started={isGameStarted}/>
</main>


<style>
</style>
