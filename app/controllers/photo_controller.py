"""
Alzikrayat - Photo Controller
=============================

Handles:
    - Photo gallery
    - Photo upload form
    - Photo upload
    - Photo details
    - Photo deletion
    - Photo comments
    - Uploaded image serving

The Controller handles request logic.
Database operations are handled by Models.
"""

import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    current_app,
    send_from_directory
)

from werkzeug.utils import secure_filename

from app.models.photo import Photo
from app.models.comment import Comment


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def isLoggedIn():
    """
    Check whether the current user is authenticated.

    Returns:
        bool: True when a user is logged in.
    """

    return "user_id" in session


# ============================================================
# FILE VALIDATION
# ============================================================

def allowedFile(fileName):
    """
    Check whether an uploaded file has an allowed extension.

    Args:
        fileName (str): Uploaded filename.

    Returns:
        bool: True if the extension is allowed.
    """

    if not fileName or "." not in fileName:
        return False

    extension = fileName.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

def getUploadFolder():
    """
    Return the project's uploads directory.

    Creates the directory if it does not already exist.

    Returns:
        str: Absolute path to uploads directory.
    """

    projectRoot = os.path.abspath(
        os.path.join(
            current_app.root_path,
            os.pardir
        )
    )

    uploadFolder = os.path.join(
        projectRoot,
        "uploads"
    )

    os.makedirs(
        uploadFolder,
        exist_ok=True
    )

    return uploadFolder


# ============================================================
# PHOTO GALLERY
# ============================================================

def indexView():
    """
    Display all photos on the homepage.
    """

    try:

        photos = Photo.getAll()

    except Exception as error:

        print(
            "Photo Gallery Error:",
            error
        )

        return render_template(
            "photos/index.html",
            photos=[]
        )

    return render_template(
        "photos/index.html",
        photos=photos
    )


# ============================================================
# UPLOAD PAGE
# ============================================================

def createView():
    """
    Display the photo upload form.

    Only authenticated users may access this page.
    """

    if not isLoggedIn():
        return redirect("/login")

    return render_template(
        "photos/create.html"
    )


# ============================================================
# STORE PHOTO
# ============================================================

def store():
    """
    Validate and store a new photo.

    The physical image is saved inside uploads/.
    Its metadata is saved through the Photo Model.
    """

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not isLoggedIn():
        return redirect("/login")

    userId = session["user_id"]

    # --------------------------------------------------------
    # Form data
    # --------------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    oldData = {
        "title": title,
        "description": description
    }

    # --------------------------------------------------------
    # Validate title
    # --------------------------------------------------------

    if not title:

        return render_template(
            "photos/create.html",
            errors=[
                "عنوان الصورة مطلوب."
            ],
            old=oldData
        )

    if len(title) > 200:

        return render_template(
            "photos/create.html",
            errors=[
                "عنوان الصورة يجب ألا يتجاوز 200 حرف."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Validate description
    # --------------------------------------------------------

    if len(description) > 1000:

        return render_template(
            "photos/create.html",
            errors=[
                "وصف الصورة يجب ألا يتجاوز 1000 حرف."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Get uploaded file
    #
    # The HTML form uses:
    #
    # name="photo"
    #
    # --------------------------------------------------------

    uploadedFile = request.files.get(
        "photo"
    )

    if uploadedFile is None:

        return render_template(
            "photos/create.html",
            errors=[
                "يرجى اختيار صورة."
            ],
            old=oldData
        )

    if not uploadedFile.filename:

        return render_template(
            "photos/create.html",
            errors=[
                "يرجى اختيار صورة."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Check file size
    # --------------------------------------------------------

    try:

        uploadedFile.stream.seek(0, os.SEEK_END)

        fileSize = uploadedFile.stream.tell()

        uploadedFile.stream.seek(0)

    except (OSError, ValueError):

        return render_template(
            "photos/create.html",
            errors=[
                "تعذر قراءة حجم الملف."
            ],
            old=oldData
        )

    if fileSize > MAX_FILE_SIZE:

        return render_template(
            "photos/create.html",
            errors=[
                "حجم الصورة يجب ألا يتجاوز 10 ميغابايت."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Secure original filename
    # --------------------------------------------------------

    originalFileName = secure_filename(
        uploadedFile.filename
    )

    if not originalFileName:

        return render_template(
            "photos/create.html",
            errors=[
                "اسم الملف غير صالح."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    if not allowedFile(
        originalFileName
    ):

        return render_template(
            "photos/create.html",
            errors=[
                "نوع الملف غير مسموح. "
                "يسمح فقط بـ JPG و JPEG و PNG و GIF و WEBP."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    extension = originalFileName.rsplit(
        ".",
        1
    )[1].lower()

    fileName = (
        "photo_"
        + uuid.uuid4().hex
        + "."
        + extension
    )

    # --------------------------------------------------------
    # Upload folder
    # --------------------------------------------------------

    uploadFolder = getUploadFolder()

    filePath = os.path.join(
        uploadFolder,
        fileName
    )

    # --------------------------------------------------------
    # Save physical image
    # --------------------------------------------------------

    try:

        uploadedFile.save(
            filePath
        )

    except OSError as error:

        print(
            "Upload Error:",
            error
        )

        return render_template(
            "photos/create.html",
            errors=[
                "حدث خطأ أثناء حفظ الصورة."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Save database record
    # --------------------------------------------------------

    try:

        photoId = Photo.create(
            userId,
            fileName,
            title,
            description if description else None
        )

    except Exception as error:

        print(
            "Photo Database Error:",
            error
        )

        # Remove physical file if database insertion fails.

        if os.path.exists(filePath):

            try:

                os.remove(
                    filePath
                )

            except OSError:

                pass

        return render_template(
            "photos/create.html",
            errors=[
                "حدث خطأ أثناء حفظ بيانات الصورة."
            ],
            old=oldData
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return redirect(
        f"/photo/{photoId}"
    )


# ============================================================
# SHOW PHOTO
# ============================================================

def show(photoId):
    """
    Display one photo with metadata and comments.
    """

    if not isinstance(
        photoId,
        int
    ) or photoId <= 0:

        return "Photo Not Found", 404

    # --------------------------------------------------------
    # Find photo
    # --------------------------------------------------------

    photo = Photo.findById(
        photoId
    )

    if photo is None:
        return "Photo Not Found", 404

    # --------------------------------------------------------
    # Get comments
    # --------------------------------------------------------

    comments = Comment.getByPhotoId(
        photoId
    )

    # --------------------------------------------------------
    # Render page
    # --------------------------------------------------------

    return render_template(
        "photos/show.html",
        photo=photo,
        comments=comments
    )


# ============================================================
# DELETE PHOTO
# ============================================================

def delete(photoId):
    """
    Delete a photo owned by the authenticated user.
    """

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not isLoggedIn():
        return redirect("/login")

    if not isinstance(
        photoId,
        int
    ) or photoId <= 0:

        return "Photo Not Found", 404

    userId = session["user_id"]

    # --------------------------------------------------------
    # Retrieve photo
    # --------------------------------------------------------

    photo = Photo.findById(
        photoId
    )

    if photo is None:
        return "Photo Not Found", 404

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if not Photo.belongsToUser(
        photoId,
        userId
    ):

        return "Forbidden", 403

    # --------------------------------------------------------
    # Save filename before deleting DB record
    # --------------------------------------------------------

    fileName = photo.get(
        "file_name"
    )

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    deleted = Photo.delete(
        photoId,
        userId
    )

    if not deleted:
        return "Forbidden", 403

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    if fileName:

        uploadFolder = getUploadFolder()

        safeFileName = os.path.basename(
            fileName
        )

        filePath = os.path.join(
            uploadFolder,
            safeFileName
        )

        if os.path.exists(
            filePath
        ):

            try:

                os.remove(
                    filePath
                )

            except OSError as error:

                print(
                    "File Delete Warning:",
                    error
                )

    # --------------------------------------------------------
    # Return home
    # --------------------------------------------------------

    return redirect("/")


# ============================================================
# STORE COMMENT
# ============================================================

def commentStore():
    """
    Add a comment to a photo.

    Only authenticated users may comment.
    """

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not isLoggedIn():
        return redirect("/login")

    userId = session["user_id"]

    # --------------------------------------------------------
    # Receive data
    # --------------------------------------------------------

    photoIdValue = request.form.get(
        "photo_id",
        ""
    ).strip()

    commentText = request.form.get(
        "comment",
        ""
    ).strip()

    # --------------------------------------------------------
    # Validate photo ID
    # --------------------------------------------------------

    try:

        photoId = int(
            photoIdValue
        )

    except (
        TypeError,
        ValueError
    ):

        return "Invalid Photo ID", 400

    if photoId <= 0:
        return "Invalid Photo ID", 400

    # --------------------------------------------------------
    # Validate comment
    # --------------------------------------------------------

    if not commentText:

        return redirect(
            f"/photo/{photoId}"
        )

    if len(commentText) > 1000:

        return redirect(
            f"/photo/{photoId}"
        )

    # --------------------------------------------------------
    # Check photo existence
    # --------------------------------------------------------

    photo = Photo.findById(
        photoId
    )

    if photo is None:
        return "Photo Not Found", 404

    # --------------------------------------------------------
    # Store comment
    # --------------------------------------------------------

    try:

        Comment.create(
            photoId,
            userId,
            commentText
        )

    except Exception as error:

        print(
            "Comment Database Error:",
            error
        )

        return redirect(
            f"/photo/{photoId}"
        )

    # --------------------------------------------------------
    # Return to photo
    # --------------------------------------------------------

    return redirect(
        f"/photo/{photoId}"
    )


# ============================================================
# SERVE UPLOADED FILE
# ============================================================

def uploadedFile(fileName):
    """
    Serve an uploaded image from the uploads directory.

    This function is called by:
        GET /uploads/<filename>

    The basename check prevents directory traversal.
    """

    if not fileName:

        return "File Not Found", 404

    safeFileName = os.path.basename(
        fileName
    )

    if safeFileName != fileName:

        return "File Not Found", 404

    uploadFolder = getUploadFolder()

    filePath = os.path.join(
        uploadFolder,
        safeFileName
    )

    if not os.path.isfile(
        filePath
    ):

        return "File Not Found", 404

    return send_from_directory(
        uploadFolder,
        safeFileName
    )

# ============================================================
# DELETE COMMENT
# ============================================================

def commentDelete(commentId):
    """
    Delete a comment owned by the authenticated user.
    """

    if not isLoggedIn():
        return redirect("/login")

    if not isinstance(
        commentId,
        int
    ) or commentId <= 0:

        return "Comment Not Found", 404

    userId = session["user_id"]

    # --------------------------------------------------------
    # Find comment
    # --------------------------------------------------------

    comment = Comment.findById(
        commentId
    )

    if comment is None:
        return "Comment Not Found", 404

    # --------------------------------------------------------
    # Get photo ID before deletion
    # --------------------------------------------------------

    photoId = comment.get(
        "photo_id"
    )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if not Comment.belongsToUser(
        commentId,
        userId
    ):

        return "Forbidden", 403

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    deleted = Comment.delete(
        commentId,
        userId
    )

    if not deleted:
        return "Forbidden", 403

    # --------------------------------------------------------
    # Return to photo
    # --------------------------------------------------------

    return redirect(
        f"/photo/{photoId}"
    )