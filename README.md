# 🤲 Daily Joshan Kabir

ربات تلگرام برای انتشار روزانه‌ی **یک فراز از دعای جوشن کبیر** به ترتیب از فراز ۱ تا ۱۰۰.

## رفتار ربات

هر روز یک پست در کانال زیر منتشر می‌شود:

`@Daily_JoshanKabir`

فرمت پست:

🕊️ **فراز X از دعای جوشن کبیر**

متن عربی فراز

🌱 **معنی:**
ترجمه فارسی

🆔 @Daily_JoshanKabir | دعای جوشن کبیر

فراز بعدی فقط بعد از ارسال موفق فراز فعلی انتخاب می‌شود؛ بنابراین اگر Telegram خطا بدهد، شماره جلو نمی‌رود.

پس از انتشار فراز ۱۰۰، ربات متوقف می‌شود.

## منبع متن و ترجمه

داده‌ها در زمان اجرای workflow از صفحه‌ی دعای جوشن کبیر در سایت مؤسسه قرآنی ولی‌عصر (عج) دریافت و در `data/joshan_kabir.json` ذخیره می‌شوند.

منبع:
https://www.maood.ir/دعاها-و-زیارات/دعاهای-ماه-مبارک-رمضان/446-دعای-جوشن-کبیر.html

صفحه منبع شامل ۱۰۰ بند دعای جوشن کبیر و ترجمه فارسی آن‌هاست.

## راه‌اندازی

### 1. ساخت Bot

در Telegram به `@BotFather` برو و یک Bot بساز.

توکن Bot را نگه دار.

### 2. اضافه کردن Bot به کانال

Bot را به عنوان **Administrator** در `@Daily_JoshanKabir` اضافه کن و اجازه‌ی ارسال پیام بده.

### 3. ساخت Repository

این فایل‌ها را در یک GitHub Repository قرار بده:

```text
Daily_JoshanKabir/
├── main.py
├── sync_data.py
├── requirements.txt
├── state.json
├── data/
│   └── joshan_kabir.json
└── .github/
    └── workflows/
        └── daily.yml
```

`data/joshan_kabir.json` را می‌توانی بعد از اولین اجرای `sync_data.py` ایجاد کنی؛ خود workflow هم آن را می‌سازد.

### 4. GitHub Secret

در Repository برو به:

`Settings → Secrets and variables → Actions → New repository secret`

یک Secret بساز:

```text
Name:
TELEGRAM_BOT_TOKEN

Value:
توکن BotFather
```

### 5. اجرای تست

از GitHub:

`Actions → Daily Joshan Kabir → Run workflow`

در اولین اجرا باید **فراز ۱** ارسال شود.

بعد از آن:

```text
روز ۱  → فراز ۱
روز ۲  → فراز ۲
روز ۳  → فراز ۳
...
روز ۱۰۰ → فراز ۱۰۰
```

## ساعت ارسال

Workflow در ساعت:

**08:00 به وقت ایران**

اجرا می‌شود.

Cron:

```text
30 4 * * *
```

که معادل 04:30 UTC است.

اگر می‌خواهی ساعت را تغییر بدهی، فقط مقدار `cron` در `.github/workflows/daily.yml` را تغییر بده.

## تست روی Mac

```bash
cd Daily_JoshanKabir
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="TOKEN_HERE"

python sync_data.py
python main.py
```

## شروع دوباره از فراز ۱

فایل `state.json` را به این حالت برگردان:

```json
{
  "current_section": 1,
  "completed": false
}
```

بعد commit و push کن.

## نکته مهم

`state.json` عمداً در Repository نگهداری می‌شود تا GitHub Actions بداند فردا باید کدام فراز را ارسال کند.

Workflow بعد از ارسال موفق، state را commit و push می‌کند.
