"""
Alzikrayat - Authentication Controller
======================================

مسؤول عن:
- عرض صفحة التسجيل وتسجيل الدخول.
- إنشاء حسابات المستخدمين.
- التحقق من بيانات التسجيل.
- تشفير كلمات المرور باستخدام bcrypt.
- تسجيل دخول المستخدم باستخدام Session.
- حفظ آخر وقت تسجيل دخول في Cookie لمدة 7 أيام.
- تسجيل خروج المستخدم.
- التعامل مع أخطاء قاعدة البيانات.

Architecture:
    Route
      ↓
    Authentication Controller
      ↓
    User Model
      ↓
    MySQL Database
"""

from datetime import datetime

import bcrypt
import pymysql

from flask import (
    request,
    redirect,
    render_template,
    session,
    make_response
)

from app.models.user import User


# ============================================================================
# Registration
# ============================================================================

def register_view():
    """
    عرض صفحة إنشاء حساب جديد.

    Returns:
        HTML صفحة التسجيل.
    """

    return render_template("auth/register.html")


def register_store():
    """
    معالجة طلب إنشاء حساب جديد.

    الخطوات:
    1. قراءة بيانات النموذج.
    2. تنظيف البيانات النصية.
    3. التحقق من صحة البيانات.
    4. التأكد من عدم استخدام البريد الإلكتروني مسبقًا.
    5. تشفير كلمة المرور.
    6. إنشاء المستخدم في قاعدة البيانات.
    7. إعادة توجيه المستخدم إلى صفحة تسجيل الدخول.

    Returns:
        Response
    """

    # ------------------------------------------------------------------------
    # قراءة البيانات من النموذج
    # ------------------------------------------------------------------------

    firstName = request.form.get("first_name", "").strip()
    lastName = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    oldData = {
        "first_name": firstName,
        "last_name": lastName,
        "email": email
    }

    # ------------------------------------------------------------------------
    # التحقق من صحة البيانات
    # ------------------------------------------------------------------------

    isValid, errors = User.validate(
        firstName,
        lastName,
        email,
        password
    )

    if not isValid:
        return render_template(
            "auth/register.html",
            errors=errors,
            old=oldData
        )

    # ------------------------------------------------------------------------
    # التعامل مع قاعدة البيانات
    # ------------------------------------------------------------------------

    try:

        # التأكد من أن البريد الإلكتروني غير مستخدم
        if User.emailExists(email):

            errors = {
                "email": "البريد الإلكتروني مستخدم بالفعل."
            }

            return render_template(
                "auth/register.html",
                errors=errors,
                old=oldData
            )

        # --------------------------------------------------------------------
        # تشفير كلمة المرور
        #
        # bcrypt يقوم بإنشاء Salt عشوائي مع كل عملية تشفير.
        # لذلك لا يتم تخزين كلمة المرور الأصلية في قاعدة البيانات.
        # --------------------------------------------------------------------

        hashedPassword = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # --------------------------------------------------------------------
        # إنشاء المستخدم
        # --------------------------------------------------------------------

        User.create(
            firstName,
            lastName,
            email,
            hashedPassword
        )

    except pymysql.MySQLError as error:

        # تسجيل الخطأ في Console أثناء التطوير
        print("Database Error:", error)

        return render_template(
            "auth/register.html",
            errors={
                "general": "حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى."
            },
            old=oldData
        )

    except Exception as error:

        # التعامل مع أي خطأ غير متوقع
        print("Registration Error:", error)

        return render_template(
            "auth/register.html",
            errors={
                "general": "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
            },
            old=oldData
        )

    # ------------------------------------------------------------------------
    # بعد نجاح التسجيل
    # ------------------------------------------------------------------------

    return redirect("/login")


# ============================================================================
# Login
# ============================================================================

def login_view():
    """
    عرض صفحة تسجيل الدخول.

    Returns:
        HTML صفحة تسجيل الدخول.
    """

    return render_template("auth/login.html")


def login_store():
    """
    معالجة عملية تسجيل الدخول.

    الخطوات:
    1. قراءة البريد الإلكتروني وكلمة المرور.
    2. التحقق من عدم ترك الحقول فارغة.
    3. البحث عن المستخدم بواسطة البريد.
    4. مقارنة كلمة المرور مع Hash الموجود في قاعدة البيانات.
    5. إنشاء Session للمستخدم.
    6. قراءة آخر تسجيل دخول من Cookie.
    7. تحديث Cookie بوقت تسجيل الدخول الحالي.
    8. إعادة المستخدم إلى الصفحة الرئيسية.

    Returns:
        Response
    """

    # ------------------------------------------------------------------------
    # قراءة بيانات تسجيل الدخول
    # ------------------------------------------------------------------------

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # ------------------------------------------------------------------------
    # التحقق الأساسي
    # ------------------------------------------------------------------------

    if not email or not password:

        return render_template(
            "auth/login.html",
            errors={
                "general": "يرجى إدخال البريد الإلكتروني وكلمة المرور."
            },
            old={
                "email": email
            }
        )

    # ------------------------------------------------------------------------
    # البحث عن المستخدم
    # ------------------------------------------------------------------------

    try:

        user = User.findByEmail(email)

    except pymysql.MySQLError as error:

        print("Database Error:", error)

        return render_template(
            "auth/login.html",
            errors={
                "general": "حدث خطأ أثناء الاتصال بقاعدة البيانات."
            },
            old={
                "email": email
            }
        )

    except Exception as error:

        print("Login Error:", error)

        return render_template(
            "auth/login.html",
            errors={
                "general": "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
            },
            old={
                "email": email
            }
        )

    # ------------------------------------------------------------------------
    # إذا لم يتم العثور على المستخدم
    #
    # نستخدم رسالة عامة حتى لا نكشف للمهاجم ما إذا كان البريد الإلكتروني
    # موجودًا فعلًا في قاعدة البيانات أم لا.
    # ------------------------------------------------------------------------

    if not user:

        return render_template(
            "auth/login.html",
            errors={
                "general": "البريد الإلكتروني أو كلمة المرور غير صحيحة."
            },
            old={
                "email": email
            }
        )

    # ------------------------------------------------------------------------
    # الحصول على كلمة المرور المشفرة
    # ------------------------------------------------------------------------

    storedPassword = user.get("password")

    if not storedPassword:

        return render_template(
            "auth/login.html",
            errors={
                "general": "البريد الإلكتروني أو كلمة المرور غير صحيحة."
            },
            old={
                "email": email
            }
        )

    # ------------------------------------------------------------------------
    # PyMySQL قد يعيد الحقل كنص أو bytes حسب إعدادات الاتصال.
    # bcrypt.checkpw يحتاج إلى bytes.
    # ------------------------------------------------------------------------

    if isinstance(storedPassword, str):
        storedPassword = storedPassword.encode("utf-8")

    try:

        passwordIsValid = bcrypt.checkpw(
            password.encode("utf-8"),
            storedPassword
        )

    except (ValueError, TypeError):

        passwordIsValid = False

    # ------------------------------------------------------------------------
    # كلمة المرور غير صحيحة
    # ------------------------------------------------------------------------

    if not passwordIsValid:

        return render_template(
            "auth/login.html",
            errors={
                "general": "البريد الإلكتروني أو كلمة المرور غير صحيحة."
            },
            old={
                "email": email
            }
        )

    # ------------------------------------------------------------------------
    # حفظ آخر تسجيل دخول قبل تحديثه
    #
    # Cookie السابقة تمثل آخر عملية دخول ناجحة.
    # ------------------------------------------------------------------------

    previousLastLogin = request.cookies.get("last_login")

    # ------------------------------------------------------------------------
    # إنشاء Session جديدة
    #
    # session.clear() تمنع بقاء بيانات جلسة قديمة عند الانتقال بين الحسابات.
    # ------------------------------------------------------------------------

    session.clear()

    session["user_id"] = user["id"]
    session["first_name"] = user["first_name"]
    session["last_name"] = user["last_name"]
    session["email"] = user["email"]

    # ------------------------------------------------------------------------
    # حفظ آخر تسجيل دخول سابق في Session
    #
    # إذا كان المستخدم قد سجل دخوله من قبل، يمكن للواجهة عرضه.
    # ------------------------------------------------------------------------

    if previousLastLogin:

        session["last_login"] = previousLastLogin

    # ------------------------------------------------------------------------
    # إنشاء Response
    # ------------------------------------------------------------------------

    response = make_response(
        redirect("/")
    )

    # ------------------------------------------------------------------------
    # وقت تسجيل الدخول الحالي
    # ------------------------------------------------------------------------

    currentLogin = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ------------------------------------------------------------------------
    # Cookie:
    #
    # max_age = 604800 ثانية = 7 أيام
    #
    # httponly=True:
    # يمنع JavaScript من الوصول إلى Cookie.
    #
    # samesite="Lax":
    # يقلل مخاطر CSRF في الاستخدامات المعتادة.
    # ------------------------------------------------------------------------

    response.set_cookie(
        "last_login",
        currentLogin,
        max_age=604800,
        httponly=True,
        samesite="Lax"
    )

    return response


# ============================================================================
# Logout
# ============================================================================

def logout():
    """
    تسجيل خروج المستخدم.

    يتم حذف بيانات Session الخاصة بالمستخدم.

    ملاحظة:
    لا نحذف Cookie الخاصة بـ last_login لأنها تمثل آخر تسجيل دخول
    ويمكن استخدامها عند تسجيل الدخول التالي.

    Returns:
        Response
    """

    session.clear()

    return make_response(
        redirect("/")
    )