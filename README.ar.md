[English](README.md)

# Simple Audio Player

Simple Audio Player مشغل صوت يسهل الوصول إليه على Windows، مبني بـ Python وwxPython وlibmpv.
صُنع لمن يستعمل قارئ شاشة مثل NVDA: لكل أمر اختصار في لوحة المفاتيح، وينطق التطبيق رسائل حالته بنفسه.
يشغّل الملفات المحلية والمجلدات وبث الويب وYouTube.

## الميزات

- تحكم بلوحة المفاتيح في كل شيء، باختصارات يمكن تغييرها، واختصارات عامة تعمل من أي برنامج.
- مستوى تفصيل منطوق: مبتدئ ومتقدم.
- تشغيل الملفات الصوتية والمجلدات وروابط البث؛ والتحكم في السرعة ومستوى الصوت (حتى 1000%)؛ وتكرار A-B؛ والإشارات المرجعية؛ ونسخ الملفات المحددة ونقلها وحذفها.
- مرشحات صوت: تسوية علو الصوت مع محدِّد، والتشغيل أحادي القناة، وإزالة الصمت.
- بحث YouTube وروابطه وقوائم تشغيله ومفضلته، وتنزيل الصوت بصيغة M4A.
- اشتراكات YouTube دون حساب Google: تابع القنوات وقوائم التشغيل، واضغط Ctrl+U لأحدث مقاطع قنواتك (حتى 50، دون Shorts).
- التسجيل من جهاز الإدخال الافتراضي إلى WAV أو MP3.
- مفاتيح الوسائط في Windows، والتكامل مع المستكشف ("Play with Simple Audio Player")، والفحص التلقائي للتحديثات.

## التثبيت

نزّل ملفًا من [صفحة الإصدارات](https://github.com/kamalyaser31/simple-player/releases):

- `SimpleAudioPlayer-v<version>.exe` هو المثبّت. يثبّت التطبيق لمستخدم Windows الحالي دون صلاحيات المسؤول، وافتراضيًا في `%LOCALAPPDATA%\Programs\Simple Audio Player`.
- `SimpleAudioPlayer-v<version>.zip` هو النسخة المحمولة. فُكَّ ضغطها وشغّل `SimpleAudioPlayer.exe`.

مكونا YouTube `yt-dlp.exe` و`deno.exe` ليسا في ملفات الإصدار. يعرض التطبيق تنزيلهما عند أول تشغيل.

## دليل المستخدم

الدليل الكامل في [player/docs/ar/userguide.html](player/docs/ar/userguide.html). وفي التطبيق اضغط F1. وقائمة التغييرات في [CHANGELOG.md](CHANGELOG.md).

## البناء والتشغيل من المصدر

تحتاج إلى Windows وPython 3.11 (يستعمل سير الإصدار 3.11). وInno Setup 6 لازم للمثبّت وحده.

ثبّت المتطلبات من جذر المستودع:

```powershell
pip install -r player/requirements.txt
```

شغّل التطبيق من مجلد `player`:

```powershell
cd player; python SimpleAudioPlayer.py
```

ابنِ المجلد المستقل بـ PyInstaller، من مجلد `player` (ثبّته أولًا بـ `pip install pyinstaller`):

```powershell
python -m PyInstaller --noconfirm SimpleAudioPlayer.spec
```

ابنِ المثبّت بـ Inno Setup، من جذر المستودع، بعد أن يوجد المجلد أعلاه:

```powershell
iscc player/simple_audio_player.iss
```

شغّل بناء الإصدار المحلي كاملًا، وهو يبني أيضًا `Updater.exe` وينزّل `mpv.dll`:

```powershell
.\build_test.ps1
```

## المساهمة

المساهمات مرحَّب بها. افتح قضية (issue) أولًا للاتفاق على التغيير.
وقبل طلب الدمج (pull request) تحقق من اتفاق الإصدار وأنواع الملفات والترجمات وملفات التحزيم:

```powershell
python scripts/validate_project_consistency.py
```

شغّله من مجلد `player`. وأبلغ عن المشكلات في [GitHub Issues](https://github.com/kamalyaser31/simple-player/issues).

## بيانات المطور (Developer Details)

- **المطور:** كمال ياسر (Kamal Yaser)
- **البريد الإلكتروني:** [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- **تيليجرام:** [@kamalyaser31](https://t.me/kamalyaser31)

---

## رخصة الاستخدام (License)

يخضع هذا المشروع لشروط رخصة MIT License مفتوحة المصدر.
