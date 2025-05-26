import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import asyncio
from datetime import datetime

# إعداد نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معرفات القنوات المطلوب الاشتراك فيها
REQUIRED_CHANNELS = [
    {"id": "@Survival_thefrost", "name": "قناة تلجرام", "link": "https://t.me/Survival_thefrost"},
    {"id": "@whiteoutsurvivel", "name": "قناة يوتيوب", "link": "https://www.youtube.com/@whiteoutsurvivel"}
]

# قاعدة بيانات الفيديوهات والأسئلة الشائعة - محدثة بالكامل
YOUTUBE_VIDEOS = {
    "التمائم والحيوان": {
        "keywords": ["تمائم", "حيوان", "مهارة", "قوي", "اقوى", "مقارنة"],
        "video": "https://youtu.be/dC3SfhT6dd4?si=4Y_gT7Jdb5o9JqhA",
        "description": "ماهو الأقوى في لعبة النجاة في الصقيع التمائم أو مهارة الحيوان"
    },
    "عجلة الحظ": {
        "keywords": ["عجلة", "حظ", "تهكير", "حيل"],
        "video": "https://youtu.be/J5gJakTD94Y?si=bNqf6EUN0IuARjoo",
        "description": "تهكير عجلة الحظ whiteout survival"
    },
    "مسبك الأسلحة": {
        "keywords": ["مسبك", "اسلحة", "أسلحة", "صناعة"],
        "video": "https://youtu.be/9xGzuOhInj8?si=kRttVkOmZ0Rci1G4",
        "description": "مسبك الأسلحة لعبة النجاة"
    },
    "جمع الكريستال": {
        "keywords": ["كريستال", "جمع", "مجانا", "مجاني"],
        "video": "https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO",
        "description": "جمع الكريستال مجاناً"
    },
    "صائد الكنوز": {
        "keywords": ["صائد", "كنوز", "خريطة"],
        "video": "https://youtu.be/9Y7RAP4w0wU?si=leQL6QXlnRQYH9t-",
        "description": "صائد الكنوز لعبة النجاة في الصقيع"
    },
    "الأبطال القوية": {
        "keywords": ["أبطال", "قوية", "جيل", "اختيار", "انتبه"],
        "video": "https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ",
        "description": "انتبه أبطال قوية لازم تاخدها من كل جيل"
    },
    "مقارنة القوة": {
        "keywords": ["قارن", "قوة", "خصم", "خطة", "فوز"],
        "video": "https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ",
        "description": "قارن قوتك مع خصمك واختر خطة الفوز"
    },
    "تطوير البداية": {
        "keywords": ["تطوير", "بداية", "ترقية", "احتراق", "حجرة"],
        "video": "https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared",
        "description": "تطوير من البداية وترقية حجرة الاحتراق"
    },
    "تعبئة التحالف": {
        "keywords": ["تعبئة", "تحالف", "نقاط"],
        "video": "https://youtu.be/YtjHkbf18WE?si=XVZV237cyPwnvrpK",
        "description": "تعبئة التحالف"
    },
    "تعبئة سريعة": {
        "keywords": ["5000", "نقطة", "5", "دقائق", "سريع"],
        "video": "https://youtu.be/AKWYbag0gjM",
        "description": "تعبئة التحالف 5000 نقطة في 5 دقائق"
    },
    "رفع القوة": {
        "keywords": ["رفع", "قوة", "15", "مليون", "دقائق", "رفعت"],
        "video": "https://youtu.be/U42r_SfteG4",
        "description": "رفعت قوة 15 مليون في دقائق"
    },
    "رفع العتاد": {
        "keywords": ["رفع", "عتاد", "مجانا", "مجاني"],
        "video": "https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb",
        "description": "رفع العتاد مجاناً"
    },
    "كوخ الحظ": {
        "keywords": ["كوخ", "حظ", "ميا", "لميا"],
        "video": "https://youtu.be/DvaTHiEFP1A?si=PfRtj9duuQ-mPvrK",
        "description": "كوخ الحظ لميا"
    },
    "ترقية أسبوعية": {
        "keywords": ["ارفع", "عتاد", "أسبوع", "اسبوعي", "كل"],
        "video": "https://youtu.be/Lo7LPRW5ync",
        "description": "ارفع عتادك كل أسبوع"
    },
    "المتاهة": {
        "keywords": ["متاهة", "لعبة"],
        "video": "https://youtu.be/3PLBvj0voNg",
        "description": "المتاهة"
    },
    "ثقرة البلية": {
        "keywords": ["ثقرة", "بلية", "ثقب"],
        "video": "https://youtu.be/3F3ZH6iHFDc",
        "description": "ثقرة البلية - النجاة في الصقيع"
    },
    "سرعة البناء": {
        "keywords": ["سرعة", "بناء", "70%", "70"],
        "video": "https://youtu.be/9RKHMDharRs?si=3tjnl7xv55rXFrl5",
        "description": "سرعة البناء 70%"
    },
    "مهارات الحيوان": {
        "keywords": ["تطوير", "مهارات", "حيوان"],
        "video": "https://youtu.be/yMdMuZE5YwI",
        "description": "تطوير مهارات الحيوان"
    }
}

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من الاشتراك في القنوات المطلوبة"""
    user_id = update.effective_user.id

    try:
        # التحقق من قناة التلجرام فقط (قناة يوتيوب لا يمكن التحقق منها برمجياً)
        member = await context.bot.get_chat_member(chat_id="@Survival_thefrost", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"خطأ في التحقق من الاشتراك: {e}")
        # في حالة الخطأ، نعتبر المستخدم غير مشترك
        return False

def find_youtube_video(message_text):
    """البحث عن فيديو يوتيوب مناسب بناءً على النص"""
    message_lower = message_text.lower()

    for topic, data in YOUTUBE_VIDEOS.items():
        for keyword in data["keywords"]:
            if keyword in message_lower:
                return data
    return None

async def send_subscription_message(update: Update):
    """إرسال رسالة طلب الاشتراك الإجباري"""
    keyboard = []

    # إضافة أزرار الاشتراك
    for channel in REQUIRED_CHANNELS:
        keyboard.append([InlineKeyboardButton(
            f"🔗 اشترك في {channel['name']}", 
            url=channel['link']
        )])

    # زر التحقق من الاشتراك
    keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    subscription_text = (
        "🚫 **اشتراك إجباري مطلوب!**\n\n"
        "🔒 **لا يمكن استخدام البوت بدون الاشتراك في القناتين**\n\n"
        "📺 **قناة يوتيوب:** شروحات ودروس حصرية للعبة\n"
        "💬 **قناة تلجرام:** التحديثات والأخبار الجديدة\n\n"
        "⚠️ **يجب الاشتراك في القناتين معاً:**\n"
        "1️⃣ اشترك في قناة يوتيوب أولاً\n"
        "2️⃣ اشترك في قناة تلجرام ثانياً\n"
        "3️⃣ اضغط 'تحقق من الاشتراك'\n\n"
        "👆 **اضغط على الأزرار أعلاه للاشتراك:**"
    )

    await update.message.reply_text(
        subscription_text, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        is_subscribed = await check_subscription(update, context)

        if is_subscribed:
            # أزرار البداية بعد التحقق من الاشتراك
            keyboard = [
                [InlineKeyboardButton("🚀 ابدأ الآن - Start Now", callback_data="start_bot")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ **مرحباً بك! - Welcome!**\n\n"
                "🎉 تم التحقق من اشتراكك بنجاح!\n"
                "🎉 Subscription verified successfully!\n"
                "🔓 يمكنك الآن استخدام جميع ميزات البوت\n"
                "🔓 You can now use all bot features\n\n"
                "📺 **تأكد من الاشتراك في قناة يوتيوب أيضاً**\n"
                "📺 **Make sure to subscribe to YouTube channel too**\n\n"
                "👇 اضغط الزر أدناه للبدء - Click button below to start:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📺 قناة يوتيوب - YouTube", url="https://youtube.com/@whiteoutsurvivel?si=uYvtRgnm1UAZgnyk")],
                [InlineKeyboardButton("💬 قناة تلجرام - Telegram", url="https://t.me/Survival_thefrost")],
                [InlineKeyboardButton("🔄 إعادة المحاولة - Try Again", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "❌ **لم يتم الاشتراك بعد - Not subscribed yet**\n\n"
                "🚫 **يجب الاشتراك في القناتين معاً:**\n"
                "🚫 **Must subscribe to both channels:**\n"
                "📺 قناة يوتيوب للشروحات - YouTube for tutorials\n"
                "💬 قناة تلجرام للتحديثات - Telegram for updates\n\n"
                "⚠️ **تأكد من الاشتراك في كلا القناتين**\n"
                "⚠️ **Make sure to subscribe to both channels**\n\n"
                "🔄 استخدم /start للعودة للبداية - Use /start to restart",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

    elif query.data == "start_bot":
        # عرض القائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton("⚔️ مقارنة القوات - Power Comparison", callback_data="compare")],
            [InlineKeyboardButton("📚 شرح اللعبة - Game Guide", callback_data="help")],
            [InlineKeyboardButton("ℹ️ معلومات البوت - Bot Info", callback_data="info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = (
            "🎮 **مرحباً بك في بوت النجاة في الصقيع!**\n"
            "🎮 **Welcome to Whiteout Survival Bot!**\n\n"
            "🔥 **الأوامر المتاحة - Available Commands:**\n"
            "⚔️ `/compare` - مقارنة القوات - Power Comparison\n"
            "📚 `/help` - شرح مفصل للعبة - Detailed Game Guide\n"
            "ℹ️ `/info` - معلومات البوت - Bot Information\n\n"
            "💡 **يمكنك أيضاً - You can also:**\n"
            "• إرسال أي سؤال وسأجد الفيديو المناسب\n"
            "• Send any question and I'll find the right video\n"
            "• استخدام الأزرار أدناه للوصول السريع\n"
            "• Use buttons below for quick access"
        )

        await query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif query.data == "compare":
        # معالج زر مقارنة القوات
        keyboard = [
            [InlineKeyboardButton("🌐 موقع المقارنة - Comparison Site", url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("🎥 فيديو المقارنة - Comparison Video", url="https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ")],
            [InlineKeyboardButton("📺 قناة يوتيوب - YouTube", url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 قناة تلجرام - Telegram", url="https://t.me/Survival_thefrost")],
            [InlineKeyboardButton("🔙 العودة للقائمة - Back to Menu", callback_data="start_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response = (
            "⚔️ **مقارنة القوات - النجاة في الصقيع**\n"
            "⚔️ **Power Comparison - Whiteout Survival**\n\n"
            "🎯 **موقع المقارنة التفصيلية - Detailed Comparison Site:**\n"
            "🔗 https://abukhat.github.io/whiteout/\n\n"
            "📊 **مقارنة شاملة تشمل - Complete comparison includes:**\n"
            "• 🏹 قوة الأبطال والمهارات - Heroes power & skills\n"
            "• 🛡️ العتاد والتمائم - Gear & amulets\n"
            "• 🏰 المباني والدفاعات - Buildings & defenses\n"
            "• 🐺 مهارات الحيوانات - Animal skills\n\n"
            "💡 **نصيحة - Tip:** استخدم الموقع لمقارنة قوتك\n"
            "💡 **Tip:** Use the site to compare your power\n"
            "🎬 **شاهد فيديو المقارنة - Watch comparison video**"
        )
        await query.edit_message_text(
            response, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif query.data == "help":
        # معالج زر شرح اللعبة - محسن لعرض جميع الفيديوهات (18 فيديو)
        keyboard = [
            [InlineKeyboardButton("🏠 تطوير من البداية", url="https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared"),
             InlineKeyboardButton("⚔️ الأبطال القوية", url="https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ")],
            [InlineKeyboardButton("💎 جمع الكريستال", url="https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO"),
             InlineKeyboardButton("🛡️ رفع العتاد", url="https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb")],
            [InlineKeyboardButton("🎰 عجلة الحظ", url="https://youtu.be/J5gJakTD94Y?si=bNqf6EUN0IuARjoo"),
             InlineKeyboardButton("⚒️ مسبك الأسلحة", url="https://youtu.be/9xGzuOhInj8?si=kRttVkOmZ0Rci1G4")],
            [InlineKeyboardButton("🗺️ صائد الكنوز", url="https://youtu.be/9Y7RAP4w0wU?si=leQL6QXlnRQYH9t-"),
             InlineKeyboardButton("🐺 التمائم والحيوان", url="https://youtu.be/dC3SfhT6dd4?si=4Y_gT7Jdb5o9JqhA")],
            [InlineKeyboardButton("🤝 تعبئة التحالف", url="https://youtu.be/YtjHkbf18WE?si=XVZV237cyPwnvrpK"),
             InlineKeyboardButton("⚡ تعبئة سريعة 5000", url="https://youtu.be/AKWYbag0gjM")],
            [InlineKeyboardButton("💪 رفع القوة 15م", url="https://youtu.be/U42r_SfteG4"),
             InlineKeyboardButton("🎲 كوخ الحظ", url="https://youtu.be/DvaTHiEFP1A?si=PfRtj9duuQ-mPvrK")],
            [InlineKeyboardButton("📅 ترقية أسبوعية", url="https://youtu.be/Lo7LPRW5ync"),
             InlineKeyboardButton("🌀 المتاهة", url="https://youtu.be/3PLBvj0voNg")],
            [InlineKeyboardButton("🔫 ثقرة البلية", url="https://youtu.be/3F3ZH6iHFDc"),
             InlineKeyboardButton("🏗️ سرعة البناء 70%", url="https://youtu.be/9RKHMDharRs?si=3tjnl7xv55rXFrl5")],
            [InlineKeyboardButton("🐺 مهارات الحيوان", url="https://youtu.be/yMdMuZE5YwI"),
             InlineKeyboardButton("⚔️ استراتيجية المقارنة", url="https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ")],
            [InlineKeyboardButton("📺 القناة كاملة - Full Channel", url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("🔙 العودة للقائمة - Back to Menu", callback_data="start_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        help_text = (
            "📚 **الدليل الشامل - Complete Guide**\n"
            "🌟 **النجاة في الصقيع - Whiteout Survival**\n\n"
            "🔥 **أساسيات اللعبة - Game Basics:**\n"
            "• 🏠 البناء وتطوير القاعدة - Base Building & Development\n"
            "• ⚔️ تدريب الأبطال والجيوش - Heroes & Army Training\n"
            "• 🛡️ الدفاع ضد الأعداء - Defense Against Enemies\n"
            "• 🤝 الانضمام للتحالفات - Alliance Systems\n\n"
            "💡 **نصائح متقدمة - Advanced Tips:**\n"
            "• 💎 جمع الكريستال مجاناً - Free Crystal Collection\n"
            "• 🔧 ترقية العتاد بذكاء - Smart Gear Upgrades\n"
            "• 🎯 اختيار الأبطال الأقوى - Selecting Best Heroes\n"
            "• 🏹 استراتيجيات القتال المتقدمة - Advanced Battle Strategies\n\n"
            "🎬 **جميع الشروحات متاحة (18 فيديو):**\n"
            "🎬 **All Tutorials Available (18 Videos):**\n"
            "استخدم الأزرار أدناه للوصول لكل شرح بالتفصيل\n"
            "Use buttons below to access each detailed tutorial\n\n"
            "❓ **اسأل عن أي موضوع - Ask about anything!**"
        )
        await query.edit_message_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif query.data == "info":
        # معالج زر معلومات البوت
        keyboard = [
            [InlineKeyboardButton("🌐 الموقع الرسمي - Official Site", url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("📺 قناة يوتيوب - YouTube Channel", url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 قناة تلجرام - Telegram Channel", url="https://t.me/Survival_thefrost")],
            [InlineKeyboardButton("🔙 العودة للقائمة - Back to Menu", callback_data="start_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_id = query.from_user.id
        user_name = query.from_user.first_name

        info_text = (
            "ℹ️ **معلومات البوت - Bot Information**\n\n"
            "🤖 **الاسم - Name:** بوت النجاة في الصقيع الشامل\n"
            "🤖 **Name:** Complete Whiteout Survival Bot\n"
            "📅 **الإصدار - Version:** 4.0 المطور - Advanced\n"
            "🔧 **المطور - Developer:** @fulldesigne\n"
            "🌍 **اللغات - Languages:** العربية + English\n\n"
            "⚡ **الميزات - Features:**\n"
            "• 🔒 اشتراك إجباري محمي - Protected Subscription System\n"
            "• 🎥 قاعدة فيديوهات ضخمة (18 فيديو) - Huge Video Database\n"
            "• 🤖 ردود ذكية تلقائية - Smart Auto Responses\n"
            "• ⚔️ مقارنة القوات المتقدمة - Advanced Power Comparison\n"
            "• 📚 شروحات شاملة - Complete Tutorials\n"
            "• 🌐 دعم متعدد اللغات - Multi-language Support\n\n"
            "📊 **إحصائياتك - Your Stats:**\n"
            f"• 🆔 معرف المستخدم - User ID: `{user_id}`\n"
            f"• 👤 الاسم - Name: {user_name}\n"
            f"• ✅ حالة الاشتراك - Subscription: مؤكد Confirmed\n\n"
            "🔄 **البوت يعمل 24/7 - Bot works 24/7**\n"
            "🔄 **Updates continuously - يتم تحديثه باستمرار**"
        )
        await query.edit_message_text(
            info_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start - يبدأ بالاشتراك الإجباري"""
    try:
        # التحقق من الاشتراك أولاً دائماً
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update)
            return

        # إذا كان مشترك، عرض القائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton("⚔️ مقارنة القوات - Power Comparison", callback_data="compare")],
            [InlineKeyboardButton("📚 شرح اللعبة - Game Guide", callback_data="help")],
            [InlineKeyboardButton("ℹ️ معلومات البوت - Bot Info", callback_data="info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = (
            "🎮 **أهلاً بك في بوت النجاة في الصقيع!**\n"
            "🎮 **Welcome to Whiteout Survival Bot!**\n\n"
            "🔥 **الميزات المتاحة - Available Features:**\n"
            "⚔️ **مقارنة القوات - Power Comparison** - قارن قوتك مع الأعداء\n"
            "📚 **شرح اللعبة - Game Guide** - نصائح وحيل احترافية\n"
            "🎯 **ردود ذكية** - اسأل عن أي موضوع في اللعبة\n"
            "🎯 **Smart Responses** - Ask about any topic in the game\n\n"
            "👇 **اختر من القائمة أو أرسل سؤالك مباشرة:**"
        )

        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"المستخدم {update.effective_user.first_name} بدأ المحادثة")
    except Exception as e:
        logger.error(f"خطأ في أمر start: {e}")

async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /compare - مقارنة القوات"""
    try:
        # التحقق من الاشتراك أولاً
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update)
            return

        # أزرار مقارنة القوات
        keyboard = [
            [InlineKeyboardButton("🌐 موقع المقارنة - Comparison Site", url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("🎥 فيديو المقارنة - Comparison Video", url="https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ")],
            [InlineKeyboardButton("📺 قناة يوتيوب - YouTube", url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 قناة تلجرام - Telegram", url="https://t.me/Survival_thefrost")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response = (
            "⚔️ **مقارنة القوات - النجاة في الصقيع**\n"
            "⚔️ **Power Comparison - Whiteout Survival**\n\n"
            "🎯 **موقع المقارنة التفصيلية - Detailed Comparison Site:**\n"
            "🔗 https://abukhat.github.io/whiteout/\n\n"
            "📊 **مقارنة شاملة تشمل - Complete comparison includes:**\n"
            "• 🏹 قوة الأبطال والمهارات - Heroes power & skills\n"
            "• 🛡️ العتاد والتمائم - Gear & amulets\n"
            "• 🏰 المباني والدفاعات - Buildings & defenses\n"
            "• 🐺 مهارات الحيوانات - Animal skills\n\n"
            "💡 **نصيحة - Tip:** استخدم الموقع لمقارنة قوتك\n"
            "💡 **Tip:** Use the site to compare your power\n"
            "🎬 **شاهد فيديو المقارنة - Watch comparison video**\n\n"
            "📞 **للمساعدة - For Help:** /help"
        )
        await update.message.reply_text(
            response, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"المستخدم {update.effective_user.first_name} طلب المقارنة")
    except Exception as e:
        logger.error(f"خطأ في أمر compare: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help - شرح شامل للعبة"""
    try:
        # التحقق من الاشتراك أولاً
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update)
            return

        # أزرار الشرح والمساعدة
        keyboard = [
            [InlineKeyboardButton("🏠 تطوير من البداية", url="https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared")],
            [InlineKeyboardButton("⚔️ الأبطال القوية", url="https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ")],
            [InlineKeyboardButton("💎 جمع الكريستال", url="https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO")],
            [InlineKeyboardButton("🛡️ رفع العتاد", url="https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb")],
            [InlineKeyboardButton("📺 قناة يوتيوب - YouTube", url="https://www.youtube.com/@whiteoutsurvivel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        help_text = (
            "📚 **الدليل الشامل - النجاة في الصقيع**\n"
            "📚 **Complete Guide - Whiteout Survival**\n\n"
            "🔥 **أساسيات اللعبة - Game Basics:**\n"
            "• 🏠 البناء وتطوير القاعدة - Base Building\n"
            "• ⚔️ تدريب الأبطال والجيوش - Heroes Training\n"
            "• 🛡️ الدفاع ضد الأعداء - Defense Strategies\n"
            "• 🤝 الانضمام للتحالفات - Alliance Systems\n\n"
            "💡 **نصائح متقدمة - Advanced Tips:**\n"
            "• 💎 جمع الكريستال مجاناً - Free Crystals\n"
            "• 🔧 ترقية العتاد بذكاء - Smart Gear Upgrade\n"
            "• 🎯 اختيار الأبطال الأقوى - Best Heroes\n"
            "• 🏹 استراتيجيات القتال - Battle Strategies\n\n"
            "🎬 **فيديوهات مفيدة - Useful Videos:**\n"
            "استخدم الأزرار أدناه للوصول للشروحات\n\n"
            "❓ **اسأل عن أي موضوع - Ask anything:** أرسل رسالة وسأجد الفيديو المناسب!"
        )
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"خطأ في أمر help: {e}")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /info - معلومات البوت"""
    try:
        # التحقق من الاشتراك أولاً
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update)
            return

        # أزرار معلومات البوت
        keyboard = [
            [InlineKeyboardButton("🌐 الموقع الرسمي - Official Site", url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("📺 قناة يوتيوب - YouTube Channel", url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 قناة تلجرام - Telegram Channel", url="https://t.me/Survival_thefrost")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        info_text = (
            "ℹ️ **معلومات البوت - Bot Information**\n\n"
            "🤖 **الاسم - Name:** بوت النجاة في الصقيع الشامل\n"
            "🤖 **Name:** Complete Whiteout Survival Bot\n"
            "📅 **الإصدار - Version:** 4.0 المطور - Advanced\n"
            "🔧 **المطور - Developer:** @fulldesigne\n"
            "🌍 **اللغات - Languages:** العربية + English\n\n"
            "⚡ **الميزات - Features:**\n"
            "• 🔒 اشتراك إجباري محمي - Protected Subscription\n"
            "• 🎥 قاعدة فيديوهات ضخمة - Huge Video Database\n"
            "• 🤖 ردود ذكية تلقائية - Smart Auto Responses\n"
            "• ⚔️ مقارنة القوات المتقدمة - Advanced Comparison\n"
            "• 📚 شروحات شاملة - Complete Tutorials\n"
            "• 🌐 دعم متعدد اللغات - Multi-language Support\n\n"
            "📊 **إحصائياتك - Your Stats:**\n"
            f"• 🆔 معرف المستخدم - User ID: `{update.effective_user.id}`\n"
            f"• 👤 الاسم - Name: {update.effective_user.first_name}\n"
            f"• ✅ حالة الاشتراك - Subscription: مؤكد Confirmed\n\n"
            "🔄 **البوت يعمل 24/7 - Bot works 24/7**"
        )
        await update.message.reply_text(
            info_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"خطأ في أمر info: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العادية مع الاشتراك الإجباري"""
    try:
        # التحقق من الاشتراك أولاً دائماً
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update)
            return

        user_message = update.message.text.lower()

        # البحث عن فيديو يوتيوب مناسب
        youtube_result = find_youtube_video(user_message)

        if youtube_result:
            keyboard = [
                [InlineKeyboardButton("🎥 شاهد الفيديو - Watch Video", url=youtube_result["video"])],
                [InlineKeyboardButton("📺 القناة كاملة - Full Channel", url="https://www.youtube.com/@whiteoutsurvivel")],
                [InlineKeyboardButton("💬 قناة تلجرام - Telegram", url="https://t.me/Survival_thefrost")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            response = (
                f"🎯 **وجدت الإجابة! - Found the answer!**\n\n\n"
                f"📹 **{youtube_result['description']}**\n\n"
                f"🎬 شاهد الشرح المفصل في الفيديو المرفق\n"
                f"🎬 Watch the detailed explanation in attached video\n"
                f"👆 اضغط على 'شاهد الفيديو' أعلاه\n"
                f"👆 Click 'Watch Video' above\n\n"
                f"💡 **نصيحة - Tip:** اشترك في القناة ولا تنس الإعجاب!\n"
                f"💡 **Tip:** Subscribe to the channel and like!"
            )
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"تم إرسال فيديو يوتيوب للمستخدم {update.effective_user.first_name}")
            return

        # ردود ذكية محدثة
        if any(word in user_message for word in ['مرحبا', 'السلام', 'هلا', 'أهلا', 'هاي', 'hello', 'hi', 'hey']):
            response = "🌟 أهلاً وسهلاً بك في عالم النجاة في الصقيع! 🧊❄️\nاسأل عن أي شيء في اللعبة وسأساعدك!\n🌟 Welcome to the world of Whiteout Survival! 🧊❄️ Ask me anything about the game!"
        elif any(word in user_message for word in ['شكرا', 'شكراً', 'ممتاز', 'رائع', 'thanks', 'thank', 'excellent', 'amazing']):
            response = "😊 العفو! سعيد جداً لمساعدتك في رحلة النجاة! 🎮❄️\n😊 You're welcome! Glad to help you in your survival journey! 🎮❄️"
        elif any(word in user_message for word in ['مقارنة', 'قارن', 'قوة', 'compare', 'power']):
            response = "⚔️ للحصول على مقارنة القوات الشاملة، استخدم /compare\n⚔️ For a comprehensive power comparison, use /compare"
        elif any(word in user_message for word in ['مساعدة', 'ساعدني', 'شرح', 'help', 'guide']):
            response = "📚 للحصول على الشرح الكامل، استخدم /help\n📚 For a complete guide, use /help"
        elif any(word in user_message for word in ['معلومات', 'تفاصيل', 'بوت', 'info', 'details', 'bot']):
            response = "ℹ️ لمعرفة تفاصيل البوت، استخدم /info\nℹ️ For bot details, use /info"
        else:
            keyboard = [
                [InlineKeyboardButton("⚔️ مقارنة القوات - Power Comparison", callback_data="compare")],
                [InlineKeyboardButton("📚 شرح اللعبة - Game Guide", callback_data="help")],
                [InlineKeyboardButton("🎥 فيديوهات يوتيوب - YouTube Videos", url="https://www.youtube.com/@whiteoutsurvivel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            response = (
                "💬 شكراً لرسالتك! ❄️\n"
                "💬 Thanks for your message! ❄️\n\n"
                "🔍 **جرب أن تسأل عن - Try asking about:**\n"
                "• التمائم والحيوانات - Amulets & Animals 🐺\n"
                "• عجلة الحظ وتهكيرها - Lucky Wheel & Hacks 🎰\n"
                "• مسبك الأسلحة - Weapons Foundry ⚔️\n"
                "• جمع الكريستال - Crystal Collection 💎\n"
                "• رفع العتاد - Gear Upgrade 🛡️\n"
                "• تعبئة التحالف - Alliance Filling 🤝\n"
                "• سرعة البناء - Building Speed 🏗️\n\n"
                "👇 **أو استخدم الأزرار - Or use the buttons:**"
            )
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return

        await update.message.reply_text(response)
        logger.info(f"رد على رسالة من {update.effective_user.first_name}")

    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيب للأعضاء الجدد مع الاشتراك الإجباري"""
    try:
        for new_member in update.message.new_chat_members:
            # التحقق من الاشتراك أولاً
            is_subscribed = await check_subscription(update, context)

            if not is_subscribed:
                await send_subscription_message(update)
                return

            keyboard = [
                [InlineKeyboardButton("🚀 ابدأ مع البوت - Start with Bot", callback_data="start_bot")],
                [InlineKeyboardButton("📺 قناة يوتيوب - YouTube Channel", url="https://www.youtube.com/@whiteoutsurvivel")],
                [InlineKeyboardButton("🌐 الموقع الرسمي - Official Site", url="https://abukhat.github.io/whiteout/")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            welcome_text = (
                f"🎉 **مرحباً {new_member.first_name}!**\n"
                f"🎉 **Welcome {new_member.first_name}!**\n\n"
                f"❄️ أهلاً بك في **قناة النجاة في الصقيع**\n"
                f"❄️ Welcome to **Whiteout Survival Channel**\n\n"
                f"📋 **قواعد القناة - Channel Rules:**\n"
                f"• احترم جميع الأعضاء - Respect all members 🤝\n"
                f"• لا تنشر روابط مشبوهة - No suspicious links 🚫\n"
                f"• استخدم البوت للحصول على المساعدة - Use the bot for help 🤖\n"
                f"• شارك خبراتك مع الآخرين - Share your experience 📢\n\n"
                f"🎮 **أرسل أي سؤال للبوت - Ask bot any question:**\n"
                f"💡 مثال - Example: التمائم, العتاد, الكريستال\n"
                f"💡 Example: Amulets, Gear, Crystals\n\n"
                f"📺 **لا تنس الاشتراك في يوتيوب للشروحات الحصرية!**\n"
                f"📺 **Don't forget to subscribe to YouTube for exclusive tutorials!**"
            )

            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"رحب بالعضو الجديد: {new_member.first_name}")
    except Exception as e:
        logger.error(f"خطأ في رسالة الترحيب: {e}")

async def keep_alive():
    """وظيفة للحفاظ على البوت نشط"""
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"🔄 Keep Alive: البوت نشط - {current_time}")
            await asyncio.sleep(300)  # كل 5 دقائق
        except Exception as e:
            logger.error(f"خطأ في Keep Alive: {e}")
            await asyncio.sleep(60)  # إعادة المحاولة بعد دقيقة

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    error_msg = str(context.error)

    # تجاهل أخطاء التضارب المؤقتة
    if "Conflict" in error_msg and "getUpdates" in error_msg:
        logger.warning("تضارب مؤقت في getUpdates - سيتم المتابعة تلقائياً")
        return

    logger.error(f"حدث خطأ: {context.error}")

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت. يرجى المحاولة مرة أخرى.\n"
                "⚠️ A temporary error occurred. Please try again.\n"
                "🔄 إذا استمر الخطأ، استخدم /start للإعادة التشغيل.\n"
                "🔄 If the error persists, use /start to restart."
            )
        except:
            pass

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # الحصول على التوكن من متغيرات البيئة
    TOKEN = os.environ.get("TOKEN")

    if not TOKEN:
        logger.error("لم يتم العثور على TOKEN في متغيرات البيئة!")
        print("❌ خطأ: يرجى إضافة TOKEN في Secrets")
        print("💡 اذهب إلى Tools > Secrets وأضف:")
        print("   Key: TOKEN")
        print("   Value: توكن البوت الخاص بك")
        return

    try:
        # إنشاء التطبيق
        application = Application.builder().token(TOKEN).build()

        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("compare", compare))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", info_command))

        # معالج الأعضاء الجدد
        from telegram.ext import MessageHandler
        application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, 
            welcome_new_member
        ))

        # إضافة معالج الأزرار التفاعلية
        from telegram.ext import CallbackQueryHandler
        application.add_handler(CallbackQueryHandler(handle_callback))

        # إضافة معالج الرسائل العادية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)

        logger.info("🚀 تم بدء تشغيل البوت بنجاح...")
        logger.info("🚀 Bot started successfully...")
        print("✅ البوت المحدث يعمل الآن!")
        print("✅ Updated bot is now running!")
        print("🔒 الاشتراك الإجباري مفعل كأولوية")
        print("🔒 Mandatory subscription is active as a priority")
        print("📺 قاعدة فيديوهات يوتيوب محدثة بالكامل")
        print("📺 YouTube videos database fully updated")
        print("⚔️ أوامر محسنة: /start /compare /help /info")
        print("⚔️ Improved commands: /start /compare /help /info")
        print("🎯 ردود ذكية متطورة")
        print("🎯 Advanced smart responses")
        print("🔄 البوت جاهز لاستقبال المستخدمين 24/7")
        print("🔄 Bot is ready to receive users 24/7")
        print("💚 نظام Keep Alive مفعل - Keep Alive system enabled")

        # بدء مهمة Keep Alive (للنشر فقط)
        # سيعمل Autoscale تلقائياً بدون الحاجة لـ Keep Alive

        # تشغيل البوت مع معالجة التضارب
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )

    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()