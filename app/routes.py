"""
Alzikrayat - Application Routes
================================

Manual URL Router.

المسؤول عن:
    - استقبال HTTP Requests.
    - تحديد المسار المطلوب.
    - توجيه الطلب إلى Controller المناسب.
    - التعامل مع المسارات الديناميكية باستخدام Regex.

Controllers:
    auth_controller.py
    photo_controller.py
"""

import re

from flask import request

from app.controllers import auth_controller
from app.controllers import photo_controller


# ============================================================
# REGISTER ROUTES
# ============================================================

def register_routes(app):
    """
    تسجيل Router واحد مع Flask.

    لا نضع منطق التطبيق هنا.
    وظيفة هذا الملف فقط هي معرفة المسار
    وتوجيه الطلب إلى الـ Controller المناسب.
    """

    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    app.add_url_rule(
        "/",
        endpoint="router_root",
        view_func=dispatch_request,
        methods=["GET"]
    )

    # --------------------------------------------------------
    # ALL OTHER PATHS
    # --------------------------------------------------------

    app.add_url_rule(
        "/<path:path>",
        endpoint="router_path",
        view_func=dispatch_request,
        methods=["GET", "POST"]
    )


# ============================================================
# MAIN DISPATCHER
# ============================================================

def dispatch_request(path=None):
    """
    Manual URL Dispatcher.

    يقرأ:
        request.path
        request.method

    ثم يوجه الطلب إلى Controller المناسب.
    """

    current_path = request.path
    method = request.method

    # ========================================================
    # HOME
    # ========================================================

    if method == "GET" and current_path == "/":
        return photo_controller.indexView()

    # ========================================================
    # REGISTER
    # ========================================================

    if current_path == "/register":

        if method == "GET":
            return auth_controller.register_view()

        if method == "POST":
            return auth_controller.register_store()

    # ========================================================
    # LOGIN
    # ========================================================

    if current_path == "/login":

        if method == "GET":
            return auth_controller.login_view()

        if method == "POST":
            return auth_controller.login_store()

    # ========================================================
    # LOGOUT
    # ========================================================

    if method == "GET" and current_path == "/logout":
        return auth_controller.logout()

    # ========================================================
    # PHOTO UPLOAD PAGE
    #
    # GET /photo/upload
    # ========================================================

    if method == "GET" and current_path == "/photo/upload":
        return photo_controller.createView()

    # ========================================================
    # STORE PHOTO
    #
    # POST /photo/store
    # ========================================================

    if method == "POST" and current_path == "/photo/store":
        return photo_controller.store()

    # ========================================================
    # SHOW PHOTO
    #
    # GET /photo/15
    # ========================================================

    photo_match = re.fullmatch(
        r"/photo/(\d+)",
        current_path
    )

    if method == "GET" and photo_match:

        photoId = int(
            photo_match.group(1)
        )

        return photo_controller.show(photoId)

    # ========================================================
    # DELETE PHOTO
    #
    # POST /photo/15/delete
    # ========================================================

    delete_match = re.fullmatch(
        r"/photo/(\d+)/delete",
        current_path
    )

    if method == "POST" and delete_match:

        photoId = int(
            delete_match.group(1)
        )

        return photo_controller.delete(photoId)

    # ========================================================
    # STORE COMMENT
    #
    # POST /comment/store
    # ========================================================

    if method == "POST" and current_path == "/comment/store":
        return photo_controller.commentStore()

    # ========================================================
    # SERVE UPLOADED IMAGE
    #
    # GET /uploads/photo_xxxxx.jpg
    #
    # هذا المسار مسؤول عن عرض الصور المخزنة
    # داخل مجلد uploads.
    # ========================================================

    upload_match = re.fullmatch(
        r"/uploads/(.+)",
        current_path
    )

    if method == "GET" and upload_match:

        fileName = upload_match.group(1)

        return photo_controller.uploadedFile(
            fileName
        )

    # ========================================================
    # DELETE COMMENT
    #
    # POST /comment/15/delete
    # ========================================================

    comment_delete_match = re.fullmatch(
        r"/comment/(\d+)/delete",
        current_path
    )

    if method == "POST" and comment_delete_match:

        commentId = int(
            comment_delete_match.group(1)
        )

        return photo_controller.commentDelete(
            commentId
        )

    # ========================================================
    # 404
    # ========================================================

    return "404 - Page Not Found", 404