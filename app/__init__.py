"""
Alzikrayat Application
----------------------
Application initialization and configuration.

Project: Alzikrayat - Photo Sharing Application
Architecture: MVC + 3-Tier
Backend: Python + Flask
"""

import os

from flask import Flask, send_from_directory


def create_app():
    """
    إنشاء وتهيئة تطبيق Flask.

    Returns:
        Flask:
            تطبيق Flask مهيأ بالكامل.
    """

    # ========================================================
    # APPLICATION PATHS
    # ========================================================

    appDirectory = os.path.dirname(os.path.abspath(__file__))

    projectDirectory = os.path.abspath(
        os.path.join(
            appDirectory,
            ".."
        )
    )

    templateDirectory = os.path.join(
        appDirectory,
        "views",
        "templates"
    )

    uploadDirectory = os.path.join(
        projectDirectory,
        "uploads"
    )

    staticDirectory = os.path.join(
        appDirectory,
        "static"
    )


    # ========================================================
    # CREATE FLASK APPLICATION
    # ========================================================

    app = Flask(
        __name__,
        template_folder=templateDirectory,
        static_folder=staticDirectory
    )


    # ========================================================
    # SECRET KEY
    # ========================================================

    app.config["SECRET_KEY"] = "alzikrayat-secret-key"


    # ========================================================
    # UPLOAD DIRECTORY
    # ========================================================

    app.config["UPLOAD_FOLDER"] = uploadDirectory

    os.makedirs(
        uploadDirectory,
        exist_ok=True
    )


    # ========================================================
    # SERVE UPLOADED IMAGES
    # ========================================================

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        """
        عرض ملف من مجلد uploads.

        Args:
            filename:
                اسم الملف المطلوب.

        Returns:
            Response:
                الملف المطلوب من مجلد uploads.
        """

        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )


    # ========================================================
    # REGISTER MANUAL ROUTER
    # ========================================================

    from app.routes import register_routes

    register_routes(app)


    # ========================================================
    # RETURN APPLICATION
    # ========================================================

    return app