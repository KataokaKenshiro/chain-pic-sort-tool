import os

# 画面の無い環境（CI・sandbox）でも Qt を動かす
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
