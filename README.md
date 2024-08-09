# 英語スゴロク デモ

お産ハッカソン

チーム：カシオレ

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
