# خطة اشتراكات يوتيوب المحلية (Implementation Plan)

> للوكيل المنفِّذ: تُنفَّذ المهام بالترتيب، وكل مهمة تنتهي بفحص مستقل. الخطوات بصيغة `- [ ]`.

**الغاية:** يستمع كمال إلى أحدث مقاطع القنوات التي يتابعها وإلى قوائم تشغيله المحفوظة، بلا تسجيل دخول إلى Google.

**البنية:** الاشتراكات تُحفظ محلياً في `subscriptions.json` بجانب ملف الإعدادات. أحدث المقاطع تُجلب من خلاصة RSS ليوتيوب (`feeds/videos.xml`) بمكتبة بايثون القياسية، ثم تُعرض في نافذة النتائج القائمة (`youtube/results.py`) فيُعاد استعمال التشغيل والجلب المسبق والتنقل كما هي. القائمة المحفوظة تُفتح بالمسار القائم `open_yt_link(ctx, link, forced_kind="playlist")`.

**الأدوات:** Python، wxPython، `urllib` و`xml.etree` من المكتبة القياسية، و`favorites/fileio.py` للقراءة والكتابة الذرية.

**المواصفة:** قرارات كمال في جلسة 2026-11-13 (أدناه).

## قرارات كمال (المواصفة)

1. المصدر: خلاصة RSS، `https://www.youtube.com/feeds/videos.xml?channel_id=<UC...>` (آخر 15 مقطعاً للقناة). تُسقط مقاطع Shorts، ويُعرف المقطع منها بأن رابطه يحوي `/shorts/`.
2. الإضافة: برابط (قناة أو قائمة، يُعرف نوعه آلياً)، ومن نافذة نتائج البحث بأمر «الاشتراك في قناة هذا المقطع». لا استيراد CSV.
3. القوائم المحفوظة تكون داخل الاشتراكات، ولا تدخل في الخلاصة المجمّعة؛ فتحها يعرض القائمة كاملة كما يفعل فتح رابط قائمة اليوم.
4. أمران في قائمة «ملف»: «أحدث مقاطع الاشتراكات» `Ctrl+U`، و«الاشتراكات...» `Ctrl+Shift+U`.
5. الخلاصة المجمّعة: أحدث 50 مقطعاً من كل القنوات، من الأحدث إلى الأقدم. خلاصة قناة واحدة: كل ما تعطيه (بعد إسقاط Shorts).
6. سطر المقطع: «العنوان - القناة - العمر»، ويُحذف اسم القناة في خلاصة قناة واحدة.
7. حوار الاشتراكات: قائمة، ثم أزرار «فتح» و«إضافة برابط...» و«حذف...» و«إغلاق»؛ `Enter` يفتح و`Delete` يحذف بعد تأكيد. كالحوار القائم للمفضلة.
8. ترتيب القائمة بترتيب الإضافة، الأحدث إضافةً أولاً. السطر: «الاسم - قناة» أو «الاسم - قائمة تشغيل».
9. استيراد `subscriptions.csv` من Google Takeout: أسقطه كمال باختياره.

## قيود عامة

- لا حزم جديدة: `urllib.request` و`xml.etree.ElementTree` و`concurrent.futures`.
- كل نص ظاهر يُلفّ بـ `_()`، ثم `python player/scripts/update_pot.py`، وتُكتب العربية في `player/locale/ar/LC_MESSAGES/SimpleAudioPlayer.po`، ثم يُعاد تشغيل السكربت للبناء.
- لا `ngettext` (القالب يُبنى بـ `--keyword=_` وحده، وملف العربية بلا `Plural-Forms`)؛ فالعمر: «اليوم»، «أمس»، `_("{n} days ago")` حتى 30 يوماً، ثم `_("{n} months ago")`، ثم `_("{n} years ago")`.
- كل عنصر واجهة له اسم مقروء، والتسلسل بـ Tab: القائمة ثم الأزرار بترتيبها.
- الشبكة: كل طلب بمهلة 15 ثانية؛ فشل قناة لا يُفشل الخلاصة، بل يُعلن عدد القنوات التي فشلت.
- PEP 8، ثم `ruff check --fix` و`black` و`flake8 --max-line-length 88` على الملفات المعدَّلة.
- يُعامل `feed` و`channel` معاملة نتائج البحث في الانتقال التلقائي (لا انتقال عند نهاية المقطع)، باختيار كمال، فلا يُمسّ `_should_auto_advance_session`. والتالي اليدوي يعمل كما في نتائج البحث.

## مواضع الخطر (Review Focus)

1. رابط قناة بصيغة `@handle` أو `/c/` أو `/user/` لا يحوي `channel_id`: يُجلب HTML الصفحة ويُستخرج المعرّف من `<link rel="canonical" href=".../channel/UC...">` أو `"externalId":"UC..."`؛ ويُرسل الطلب بكعكة `CONSENT=YES+1` لئلا تعيده صفحة الموافقة الأوروبية. جُرِّب حياً في 2026-11-13 على `@GoogleDevelopers` فأعاد المعرّف بالطريقين.
2. الإضافة المكررة (القناة نفسها برابطين مختلفين): يُطابَق بالمعرّف لا بالرابط، ويُعلن «القناة مشتركٌ فيها من قبل».
3. لا اتصال بالشبكة: رسالة خطأ واضحة، والحوار يبقى يعمل محلياً (فتح القائمة، الحذف).
4. ملف `subscriptions.json` تالف أو مفقود: يُعامل قائمةً فارغة ولا ينهار التطبيق.
5. فتح الخلاصة المجمّعة بلا اشتراكات: يُعلن «لا اشتراكات بعد» ويُعرض حوار الاشتراكات.

---

### المهمة 1: الخلاصة وتحليل الروابط (`player/subscriptions/feed.py`)

**الملفات:**
- إنشاء: `player/subscriptions/__init__.py` (فارغ)، `player/subscriptions/feed.py`
- تعديل: `player/youtube/resolver.py` (حقل في `YtItem`)
- اختبار: `player/subscriptions/run_tests.py`

**الواجهات:**
- يُنتج:
  - `YtItem.published: float = 0.0` (حقل جديد بعد `description`، طابع زمني UTC).
  - `parse_link(link: str) -> tuple[str, str]`: يعيد `("channel", "UC...")` أو `("playlist", "PL...")` أو `("channel_page", url)` لرابط قناة بلا معرّف، أو `("", "")` لغير ذلك. القائمة تُعرف بالوسيط `list=` أو مسار `/playlist`.
  - `channel_id_from_html(html: str) -> str`: المعرّف من canonical أو externalId، أو `""`.
  - `parse_feed(xml_text: str) -> tuple[str, list[YtItem]]`: عنوان الخلاصة والمقاطع، Shorts مُسقطة. `url` هو `https://www.youtube.com/watch?v=<id>`، و`channel_url` و`channel_name` من `<author>`.
  - `fetch_feed(kind: str, ident: str, timeout=15) -> tuple[str, list[YtItem]]`: يجلب `?channel_id=` أو `?playlist_id=` ويحلله؛ يرمي `OSError` أو `ValueError` عند الفشل.
  - `resolve_link(link: str, timeout=15) -> tuple[str, str, str]`: `(kind, ident, name)`، والاسم من عنوان الخلاصة؛ يرمي `ValueError` لرابط غير صالح.
  - `merge_latest(feeds: list[list[YtItem]], limit=50) -> list[YtItem]`: يدمج ويرتّب بـ `published` تنازلياً ويقصّ إلى `limit`، بلا تكرار رابط.
  - `age_label(published: float, now: float) -> str`: نصوص العمر المذكورة في القيود.

- [ ] **الخطوة 1: الاختبارات أولاً** في `run_tests.py` (سكربت بسيط بـ `assert` ودوال `test_*` تُستدعى من `main`، يطبع النجاح والفشل، بلا pytest). عيّنة RSS نصية داخل الملف بثلاثة مقاطع: عادي قديم، وShort، وعادي حديث.
  ```python
  def test_parse_feed_drops_shorts():
      title, items = parse_feed(SAMPLE)
      assert title == "Sample Channel"
      assert [i.url for i in items] == [WATCH_NEW, WATCH_OLD]  # مرتبة كما في الخلاصة، بلا Short
      assert items[0].channel_name == "Sample Channel"
      assert items[0].published > items[1].published

  def test_parse_link():
      assert parse_link("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw") == ("channel", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
      assert parse_link("https://youtube.com/playlist?list=PLabc123") == ("playlist", "PLabc123")
      assert parse_link("https://www.youtube.com/watch?v=x&list=PLabc123") == ("playlist", "PLabc123")
      assert parse_link("https://www.youtube.com/@SomeName")[0] == "channel_page"
      assert parse_link("https://example.com/x") == ("", "")

  def test_channel_id_from_html():
      html = '<link rel="canonical" href="https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv">'
      assert channel_id_from_html(html) == "UCabcdefghijklmnopqrstuv"
      assert channel_id_from_html('"externalId":"UCabcdefghijklmnopqrstuv"') == "UCabcdefghijklmnopqrstuv"
      assert channel_id_from_html("<html></html>") == ""

  def test_merge_latest_sorts_and_limits():
      # ستون مقطعاً من ثلاث قنوات بتواريخ متداخلة
      out = merge_latest(feeds, limit=50)
      assert len(out) == 50
      assert all(a.published >= b.published for a, b in zip(out, out[1:]))

  def test_age_label():
      assert age_label(now - 3600, now) == _("today")
      assert age_label(now - 86400 * 1.5, now) == _("yesterday")
      assert age_label(now - 86400 * 5, now) == _("{n} days ago").format(n=5)
      assert age_label(now - 86400 * 70, now) == _("{n} months ago").format(n=2)
  ```
- [ ] **الخطوة 2:** `python subscriptions/run_tests.py` من `player/` يفشل (الوحدة غير موجودة).
- [ ] **الخطوة 3:** كتابة `feed.py` بالتواقيع أعلاه. أسماء النطاقات: Atom `http://www.w3.org/2005/Atom`، و`yt` `http://www.youtube.com/xml/schemas/2015`. التاريخ من `<published>` بـ `datetime.fromisoformat`. الطلبات بـ `urllib.request.Request` مع `User-Agent` متصفح عام وكعكة `CONSENT=YES+1`.
- [ ] **الخطوة 4:** إضافة خيار `--live` إلى `run_tests.py` يجلب خلاصة `UC_x5XG1OV2P6uZZ5FSM9Ttw` ويحل `https://www.youtube.com/@GoogleDevelopers` ويطبع العدد والمعرّف. يُشغَّل مرة واحدة، ولا يدخل في التشغيل المبدئي.
- [ ] **الخطوة 5:** الاختبارات تنجح (`python subscriptions/run_tests.py` ثم `--live`).

### المهمة 2: المخزن (`player/subscriptions/store.py`)

**الملفات:** إنشاء `player/subscriptions/store.py`؛ اختبارات في `run_tests.py`.

**الواجهات:**
- يستهلك: `favorites.fileio.read_json` و`write_json`.
- يُنتج:
  - `@dataclass Sub(id: str, kind: str, name: str, url: str, added: float)`؛ `kind` في `("channel", "playlist")`، و`url` رابط القناة `https://www.youtube.com/channel/<id>` أو القائمة `https://www.youtube.com/playlist?list=<id>`.
  - `SubStore(settings_path: str, filename="subscriptions.json")` بالدوال: `list_all() -> list[Sub]` (الأحدث إضافةً أولاً)، `channels() -> list[Sub]`، `has(kind, ident) -> bool`، `add(kind, ident, name) -> Sub | None` (`None` إن وُجد)، `delete(sub_id) -> bool`.
  - شكل الملف: `{"version": 1, "items": [{"id", "kind", "name", "url", "added"}]}`. العنصر الناقص أو ذو النوع المجهول يُتجاهل.

- [ ] **الخطوة 1: الاختبارات** في مجلد مؤقت (`tempfile.TemporaryDirectory`):
  ```python
  def test_store_add_dedupe_order_delete():
      st = SubStore(os.path.join(tmp, "settings.json"))
      assert st.list_all() == []
      a = st.add("channel", "UCaaa", "A"); b = st.add("playlist", "PLbbb", "B")
      assert st.add("channel", "UCaaa", "A again") is None
      assert [s.id for s in SubStore(path).list_all()] == ["PLbbb", "UCaaa"]  # الأحدث أولاً، ويبقى بعد إعادة الفتح
      assert [s.id for s in st.channels()] == ["UCaaa"]
      assert st.delete("UCaaa") and not st.has("channel", "UCaaa")

  def test_store_corrupt_file():
      write "{not json" to subscriptions.json
      assert SubStore(path).list_all() == []
  ```
- [ ] **الخطوة 2:** تفشل، ثم كتابة `store.py` على نمط `favorites/store.py`، ثم تنجح.

### المهمة 3: حوار الاشتراكات (`player/ui/subs_dlg.py`)

**الملفات:** إنشاء `player/ui/subs_dlg.py`.

**الواجهات:**
- يُنتج: `SubsDlg(parent, subs: list[Sub])`، يعيد من `ShowModal()` أحد: `ID_SUB_OPEN`، `ID_SUB_ADD`، `ID_SUB_REMOVE`، `wx.ID_CANCEL`؛ و`selected_id() -> str`، و`set_items(subs, selected_id="")`.
- عنوان الحوار `_("YouTube subscriptions")`؛ تسمية القائمة `_("Subscriptions")` بـ `wx.StaticText` قبلها مباشرة؛ السطر `_("{name} - channel")` أو `_("{name} - playlist")`.
- الأزرار بترتيبها: `_("Open")` (افتراضي)، `_("Add by link...")`، `_("Remove...")`، `_("Close")`. «فتح» و«حذف» معطَّلان إن خلت القائمة. `Enter` على القائمة يفتح، و`Delete` يحذف، و`Escape` يغلق.

- [ ] **الخطوة 1:** كتابته على نمط `FavManageDlg` في `ui/favorite_dlg.py`.
- [ ] **الخطوة 2:** فحص يدوي بسكربت صغير مؤقت في `.tmp\` يفتح الحوار بعنصرين، ثم يُحذف السكربت: التسلسل بـ Tab (القائمة، فتح، إضافة، حذف، إغلاق) والأسماء المقروءة.

### المهمة 4: أوامر الاشتراكات (`player/app_actions/subscription_actions.py`)

**الملفات:**
- إنشاء: `player/app_actions/subscription_actions.py`
- تعديل: `player/core/action_context.py` (وسيط `subs=None`)، `player/core/controller.py` (إنشاء `SubStore(self._settings.config_path)` وربط الأمرين)، `player/actions.py`، `player/ui/mainwin/menu.py`، `player/ui/mainwin/state.py`، `player/youtube/ui_utils.py` (`res_label`)، `player/youtube/results.py` (`_set_res`)، `player/subscriptions/feed.py` (`feed_row`).

**الواجهات:**
- يستهلك: `fetch_feed`، `resolve_link`، `merge_latest`، `age_label` (المهمة 1)؛ `SubStore` (2)؛ `SubsDlg` (3)؛ `run_task` من `youtube/task_ui.py` للعمل في الخلفية بنافذة انتظار قابلة للإلغاء؛ `mk_ses`، `show_res`، `open_yt_link`، و`_prefetch_range`، `_play_item`، `_PREP_POOL`، `_opts` من `youtube/flow.py` (تُصدَّر دالة واحدة `show_videos(ctx, kind, title, items)` في `flow.py` تجمع `mk_ses` و`_opts` و`show_res` كما في `search_yt`، فلا تُستورد الأسماء الخاصة).
- يُنتج:
  - ثابتان في `actions.py`: `OPEN_SUBS_FEED = "open_subs_feed"` بـ `Shortcut("u", frozenset({"ctrl"}))` واسم `"Latest Subscription Videos"`، و`OPEN_SUBSCRIPTIONS = "open_subscriptions"` بـ `Shortcut("u", frozenset({"ctrl", "shift"}))` واسم `"YouTube Subscriptions"`.
  - في قائمة «ملف» بعد «المقاطع المفضلة...»: `_("Latest subscription videos")` و`_("YouTube subscriptions...")`.
  - `open_latest(ctx)`: بلا قنوات يعلن `_("No subscriptions yet.")` ويفتح `manage_subs`. وإلا يجلب خلاصات القنوات متوازية (8 خيوط) داخل `run_task`، ثم `merge_latest(..., 50)`، ثم `show_videos(ctx, "feed", _("Latest subscription videos"), items)`. إن فشلت قنوات يُنطق `_("{n} channels could not be loaded.")`.
  - `manage_subs(ctx)`: حلقة الحوار. «فتح» قناةً: يجلب خلاصتها ثم `show_videos(ctx, "channel", name, items)`. «فتح» قائمةً: `open_yt_link(ctx, sub.url, forced_kind="playlist")`. «إضافة»: `wx.TextEntryDialog` بعنوان `_("Add subscription")` ونص `_("Channel or playlist link:")`، ثم `resolve_link` في `run_task`، ثم `add`، وينطق `_("Subscribed to {name}.")` أو `_("Already subscribed to {name}.")`. «حذف»: تأكيد `_("Remove {name} from subscriptions?")`.
  - `subscribe_channel(ctx, channel_url: str, channel_name: str) -> bool`: يحل الرابط ويضيف، بالرسائل نفسها.
  - سطر النتيجة: `_set_res` يستعمل `feed_row(item, kind: str, now: float) -> str` من `subscriptions/feed.py`: لنوع `feed` «العنوان - القناة - العمر»، ولنوع `channel` «العنوان - العمر»، ولغيرهما العنوان كما اليوم. و`res_label` يعيد `_("Latest videos")` لـ `feed` و`_("Channel videos")` لـ `channel`.

- [ ] **الخطوة 1: اختبار السطر** في `run_tests.py`: `feed_row` لنوعي `feed` و`channel` و`search` يعيد الصيغ الثلاث.
- [ ] **الخطوة 2:** يفشل، ثم الكتابة، ثم ينجح.
- [ ] **الخطوة 3:** التأكد بـ grep من أن كل موضع يسرد الأوامر (`ui/mainwin/state.py`، `core/controller.py`، وإعدادات الاختصارات إن كان فيها جدول) يحوي الثابتين.

### المهمة 5: الاشتراك من نافذة النتائج

**الملفات:** تعديل `player/ui/yt_dialogs.py` (`ResultsDlg`)، `player/youtube/results.py`.

**الواجهات:**
- يستهلك: `subscribe_channel` (المهمة 4)، يُستورد داخل الدالة في `results.py` تجنباً للدوران (`app_actions` يستورد `youtube.actions`).
- يُنتج: `ResultsDlg.id_subscribe`، وعنصر قائمة منبثقة `_("Subscribe to channel\tCtrl+S")` بعد «الانتقال إلى القناة»، واختصار `Ctrl+S` في `_build_accels`.

- [ ] **الخطوة 1:** إضافة العنصر والاختصار وربطهما في `show_res` بدالة `do_subscribe` تأخذ `channel_url` و`channel_name` من العنصر المحدد؛ إن خلا الرابط ينطق `_("Channel link is not available.")` (نص موجود).
- [ ] **الخطوة 2:** فحص حي: بحث، ثم `Ctrl+S` على نتيجة، ثم `Ctrl+Shift+U` يُظهر القناة.

### المهمة 6: الترجمة والفحص والتوثيق والإيداع

- [ ] `python player/scripts/update_pot.py`، ثم ترجمة النصوص الجديدة في ملف العربية، ثم إعادة تشغيله للبناء.
- [ ] `ruff check --fix` و`black` و`flake8 --max-line-length 88` على الملفات المعدَّلة والجديدة، و`python -m py_compile` عليها.
- [ ] `python subscriptions/run_tests.py` و`--live` ينجحان، و`python player/scripts/validate_project_consistency.py` ينجح.
- [ ] قبل الإيداع: `git diff --stat -- CHANGELOG.md project_state.md task.md README.md` للتأكد من خلوّها من تعديلات جلسة أخرى، ويُودَع ما يخص هذه الميزة وحده.
- [ ] تشغيل التطبيق من المصدر وتجربة: إضافة قناة برابط `@`، وإضافة قائمة، و`Ctrl+U`، وفتح قناة، وفتح قائمة، وتشغيل مقطع والانتقال للتالي يدوياً، والاشتراك من نتائج البحث، والحذف.
- [ ] مراجعة الفرق بمهارة `code-review`.
- [ ] تحديث `CHANGELOG.md` و`project_state.md` و`task.md`، وقسم الميزات والاختصارات في `README.md` بعد تحميل `readme-writer`.
- [ ] إيداع محلي على master بملفات هذه الميزة وحدها: `feat: add local YouTube subscriptions`. بلا push.

## ما يُختبر حياً بيد كمال بعد التسليم

- قراءة NVDA لأسطر الحوار والخلاصة، وتسلسل Tab في حوار الاشتراكات.
- `Ctrl+U` و`Ctrl+Shift+U` من النافذة الرئيسية، و`Ctrl+S` في نافذة النتائج.
- إضافة قنواته الفعلية بروابطها، وزمن تحميل الخلاصة المجمّعة.
