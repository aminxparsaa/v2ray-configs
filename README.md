# V2Ray Configs 📁

مخزن کانفیگ‌های V2Ray برای فروشگاه

## ساختار

```
configs/
├── us-vip.json        # کانفیگ VIP آمریکا
├── de-standard.json   # کانفیگ استاندارد آلمان
└── nl-premium.json    # کانفیگ ویژه هلند
```

## فرمت فایل‌ها

هر فایل JSON شامل اطلاعات زیر است:

```json
{
    "name": "نام کانفیگ",
    "description": "توضیحات",
    "config": { ... },           // کانفیگ V2Ray
    "price": 50000,              // قیمت (تومان)
    "duration_days": 30,         // مدت زمان (روز)
    "server_location": "آمریکا",  // موقعیت سرور
    "stock": 10                  // موجودی
}
```

## نحوه اتصال به سایت

1. GitHub Token با دسترسی `repo` ایجاد کنید
2. در فایل `.env` سایت تنظیم کنید:
   ```
   GITHUB_TOKEN=your_token
   GITHUB_REPO=aminxparsaa/v2ray-configs
   GITHUB_CONFIGS_PATH=configs/
   ```
3. از پنل مدیریت دکمه "همگام‌سازی با GitHub" را بزنید

## اضافه کردن کانفیگ جدید

1. فایل JSON جدیدی در پوشه `configs/` ایجاد کنید
2. فرمت بالا را رعایت کنید
3. Commit و Push کنید
4. در سایت همگام‌سازی کنید
