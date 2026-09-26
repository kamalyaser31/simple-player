# المهام (Tasks) - Simple Audio Player

- [x] تشخيص علة انهيار شاشة بحث اليوتيوب عند الدخول المتكرر (`RuntimeError: cannot reuse already awaited coroutine`). <!-- id: 1 -->
- [x] كشف السبب الجذري في دالة `_run` بملف `player/youtube/search.py` الناتج عن محاولة إعادة انتظار كورووتين منقضٍ (`FRAME_COMPLETED`) عند التقاط `RuntimeError`. <!-- id: 2 -->
- [x] معالجة تسرب عميل `httpx.AsyncClient` في مكتبة `py_yt` وضمان إغلاقه صراحةً في بيئة تشغيل ذرية مستقلة. <!-- id: 3 -->
- [x] رتق دالة `_getShelfComponent` ضد خطأ `TypeError: 'NoneType' object is not iterable` عند خلو الرفوف من عناصر القوائم. <!-- id: 4 -->
- [x] تصحيح شرط جلسة نتائج البحث في دالة `_more_done` بملف `player/youtube/results.py`. <!-- id: 5 -->
- [x] التحقق الشامل عبر اختبارات آلية متتالية وضغط بحثي مكثف بنسبة نجاح 100%. <!-- id: 6 -->
- [x] تنظيف الملفات المؤقتة وتوثيق الحالة وسجل التغييرات. <!-- id: 7 -->
