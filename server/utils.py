from random import randint

def mask_string(word: str):
    if len(word) <= 1:
        return word  # 文字数が1以下ならそのまま返す

    # 残す文字のインデックスをランダムに選択
    reveal_index = randint(0, len(word) - 1)

    # "●" に置き換える処理
    masked_word = ''.join([char if i == reveal_index else '●' for i, char in enumerate(word)])

    return masked_word