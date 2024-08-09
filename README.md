# 英語スゴロク　デモ

お産ハッカソン　チーム：カシオレ

# 開発環境のインストール方法
1. リポジトリのクローン

（クライアントの開発環境）

2. Node.jsをあらかじめPCにインストールしておき、`npm install`コマンドをルートディレクトリで実行
3. `npm run dev`で開発サーバーの開始、ターミナルに表示されたアドレスをブラウザで開く

（ゲームサーバーの開発環境）

4. PC内にAnaconda等で仮想環境を構築し、`pip install flask flask-socketio`を実行、パッケージをインストールする（`conda`環境において`pip`コマンドが使えない場合には`conda install pip`で先に`pip`をインストールしておく）
5. ターミナルで`server`フォルダ内に移動し、**4.で作成した仮想環境において**`python main.py`でサーバーを起動

## クライアントの本番用ビルド
1. ルートディレクトリにおいて、`npm run build`コマンドの実行
2. `dist`フォルダに成果物が出力される

# 採用した技術に関して

## なぜクライアント/サーバー方式なのか？
- 将来的に大規模なマルチプレイやオンライン対戦を見据えた際、拡張性に優れているため
- 複数人が同時にプレイするというゲーム性から、この仕組みの方が処理がわかりやすく合理的

## サーバーサイドにPython（Flask）を採用するメリット
- 言語そのものの習得が容易であるので、効率的・スピーディーに開発が可能
- Flaskによる簡潔なAPI定義
- Pythonコミュニティがもつ多彩なライブラリをゲームに応用できる（拡張性）

## クライアントサイドにWeb技術（Svelte）を採用するメリット
- Webベースで実装することで様々な端末で実行できる
- UIを実装する際、HTMLとCSSによる柔軟性の高いデザインが可能（アニメーションも容易）
- Svelteを使用することで、プレーンなHTML/CSS/Javascriptを組み合わせたページよりも簡潔なコードが書け、それにより開発スピードが速くなり、保守性も高くなる

## 通信にWebSocketを採用するメリット
- 双方向通信であり、リアルタイム性が高いため、オンラインゲームに適している
- ライブラリが充実している　今回はFlask-socketio（サーバー側）、Socket.IO Client（クライアント側）を採用
- 標準的なHTTP通信よりもオーバーヘッドが少ない