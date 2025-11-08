# 🗣️ 5min Talk – Language Practice App (Prototype)
**Minimal Language Speaking Platform / 言語練習のためのミニマルな会話プラットフォーム**

---

## 🌱 Overview / 概要

**5min Talk** is a prototype of a simple and safe platform where students can practice speaking a language for just **5 minutes** with teachers.  
No social clutter, no endless chatting — just focused, structured micro-sessions.  

**5min Talk** は、生徒が先生と **たった5分間だけ** 言語練習できるシンプルで安全なプラットフォームのプロトタイプです。  
SNS的な雑談や出会い要素を一切排除し、「短く・集中して・安心して話せる」ことを目的にしています。  

---

## 🎯 Features / 主な特徴

| Feature / 機能 | Description / 説明 |
|----------------|-------------------|
| 🕔 **5-Minute Talk Room / 5分トークルーム** | A timer-controlled 5-minute session that ends automatically. / タイマー付きで自動終了する5分間の練習部屋。 |
| 👩‍🏫 **Teacher & Student Modes / 先生・生徒モード** | Different dashboards depending on your role. / ロール選択でUIが変化。 |
| 🌍 **Language Selection / 言語選択** | Japanese, English, Spanish, French (multi-select for teachers). / 日本語・英語・スペイン語・フランス語に対応。 |
| 💬 **Clean Bootstrap UI / クリーンなUI** | Simple, mobile-friendly interface using Bootstrap 5. / Bootstrap 5で構築したシンプルなUI。 |
| 💻 **Run Locally / 即起動可能** | Runs instantly with FastAPI and SQLite. / FastAPI + SQLiteで動作、追加設定不要。 |

---

## 👨‍🎓 For Students / 生徒の利点

- 🎯 Practice anytime for **just 5 minutes**  
- 💸 Low cost or free (prototype phase)  
- 😌 100% safe — no DMs or “social” elements  
- 🌍 Talk to real speakers, globally  
- 🔁 Rate “Bad” to never match with someone again  

> **短く・安心して・何度でも練習できる。**

---

## 👩‍🏫 For Teachers / 先生の利点

- 💰 Teach for 5 minutes — perfect for side income or experience  
- 🕒 Go online/offline anytime  
- 💬 Meet motivated learners only  
- 🎓 Great for student teachers or native speakers who want to help others  

> **"Teach in 5 minutes" — a new micro-teaching style.**

---

## 💡 Why It’s Different / 他との違い

| 項目 | 一般的な言語学習サービス | 5min Talk |
|------|---------------------------|------------|
| セッション時間 | 30分〜60分 | **5分だけ** |
| 料金体系 | 月額・サブスク | **1回ごと（チケット制予定）** |
| 雰囲気 | SNS寄り・雑談多め | **完全学習特化・出会い要素ゼロ** |
| 先生登録 | 審査制・面倒 | **即登録OK・自由** |
| 継続性 | 長期前提 | **短時間×高頻度スタイル** |

---

## 🚀 Setup / セットアップ方法

### 🔧 Requirements / 必要条件
- Python 3.9+
- FastAPI
- Uvicorn

### ⚙️ Installation / インストール
```bash
git clone https://github.com/YOUR_USERNAME/5min-talk.git
cd 5min-talk
pip install fastapi uvicorn
uvicorn main:app --reload
