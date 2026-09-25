"""
Alzikrayat - Photo Model
========================

This module handles database operations related to photos.

Responsibilities:
    - Connect to the MySQL database.
    - Retrieve photos.
    - Retrieve a single photo with its owner.
    - Create photo metadata.
    - Delete photo metadata.
    - Check photo ownership.

Architecture:
    Controller -> Model -> MySQL

Security:
    - All SQL queries use parameterized placeholders.
    - No raw SQL values are concatenated into queries.
    - Ownership checks are performed at the database level.
    - Passwords and unrelated sensitive user data are never returned.

Database table:
    photos
"""


import pymysql

from app import config


class Photo:
    """
    Data model for photos.

    The Photo model is responsible only for database access
    and SQL operations. Request handling, file management,
    authentication, and business logic remain in the Controller.
    """

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    @staticmethod
    def getDb():
        """
        Create and return a MySQL database connection.

        Returns:
            pymysql.connections.Connection:
                Active MySQL database connection.

        Raises:
            pymysql.MySQLError:
                If the database connection fails.
        """

        return pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )

    # ========================================================
    # GET ALL PHOTOS
    # ========================================================

    @staticmethod
    def getAll():
        """
        Retrieve all photos from the database.

        Each photo is returned together with the first and last
        name of its owner.

        The newest photos are returned first.

        Returns:
            list:
                List of photo dictionaries.

        Raises:
            pymysql.MySQLError:
                If the database query fails.
        """

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    photos.id,
                    photos.user_id,
                    photos.file_name,
                    photos.title,
                    photos.description,
                    photos.date_time,
                    users.first_name,
                    users.last_name
                FROM photos

                INNER JOIN users
                    ON photos.user_id = users.id

                ORDER BY photos.id DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # FIND PHOTO BY ID
    # ========================================================

    @staticmethod
    def findById(photoId):
        """
        Retrieve one photo by its ID.

        The result also contains the first and last name
        of the user who owns the photo.

        Args:
            photoId (int):
                ID of the requested photo.

        Returns:
            dict or None:
                Photo record when found, otherwise None.

        Raises:
            ValueError:
                If photoId is not a positive integer.

            pymysql.MySQLError:
                If the database query fails.
        """

        if not isinstance(photoId, int) or photoId <= 0:

            raise ValueError(
                "Photo ID must be a positive integer."
            )

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    photos.id,
                    photos.user_id,
                    photos.file_name,
                    photos.title,
                    photos.description,
                    photos.date_time,
                    users.first_name,
                    users.last_name
                FROM photos

                INNER JOIN users
                    ON photos.user_id = users.id

                WHERE photos.id = %s

                LIMIT 1
            """

            cursor.execute(
                query,
                (photoId,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # CREATE PHOTO
    # ========================================================

    @staticmethod
    def create(
        userId,
        fileName,
        title,
        description=None
    ):
        """
        Create a new photo metadata record.

        The physical image file is handled by the Controller.
        This method stores only the metadata in the database.

        The date_time field is intentionally omitted because
        MySQL generates it automatically using CURRENT_TIMESTAMP.

        Args:
            userId (int):
                ID of the user who uploaded the photo.

            fileName (str):
                Physical filename stored in uploads/.

            title (str):
                Photo title.

            description (str, optional):
                Photo description.

        Returns:
            int:
                ID of the newly created photo.

        Raises:
            ValueError:
                If required values are invalid.

            pymysql.MySQLError:
                If the INSERT operation fails.
        """

        if not isinstance(userId, int) or userId <= 0:

            raise ValueError(
                "User ID must be a positive integer."
            )

        if not isinstance(fileName, str) or not fileName.strip():

            raise ValueError(
                "File name is required."
            )

        if not isinstance(title, str) or not title.strip():

            raise ValueError(
                "Photo title is required."
            )

        if description is not None and not isinstance(
            description,
            str
        ):

            raise ValueError(
                "Photo description must be text."
            )

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                INSERT INTO photos
                (
                    user_id,
                    file_name,
                    title,
                    description
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    userId,
                    fileName,
                    title.strip(),
                    description
                )
            )

            db.commit()

            return cursor.lastrowid

        except pymysql.MySQLError:

            db.rollback()

            raise

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # DELETE PHOTO
    # ========================================================

    @staticmethod
    def delete(photoId, userId):
        """
        Delete a photo database record.

        The deletion is allowed only when the photo belongs
        to the specified user.

        The physical image file is NOT deleted here.
        Physical file deletion is handled by PhotoController.

        Args:
            photoId (int):
                ID of the photo to delete.

            userId (int):
                ID of the authenticated user.

        Returns:
            bool:
                True if the photo was deleted.
                False if the photo does not exist or does not
                belong to the specified user.

        Raises:
            ValueError:
                If either ID is invalid.

            pymysql.MySQLError:
                If the DELETE operation fails.
        """

        if not isinstance(photoId, int) or photoId <= 0:

            raise ValueError(
                "Photo ID must be a positive integer."
            )

        if not isinstance(userId, int) or userId <= 0:

            raise ValueError(
                "User ID must be a positive integer."
            )

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                DELETE FROM photos

                WHERE id = %s
                AND user_id = %s
            """

            cursor.execute(
                query,
                (
                    photoId,
                    userId
                )
            )

            db.commit()

            return cursor.rowcount > 0

        except pymysql.MySQLError:

            db.rollback()

            raise

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # CHECK PHOTO OWNERSHIP
    # ========================================================

    @staticmethod
    def belongsToUser(photoId, userId):
        """
        Check whether a photo belongs to a specific user.

        Args:
            photoId (int):
                ID of the photo.

            userId (int):
                ID of the user.

        Returns:
            bool:
                True when the photo belongs to the user.
                False otherwise.

        Raises:
            ValueError:
                If either ID is invalid.

            pymysql.MySQLError:
                If the database query fails.
        """

        if not isinstance(photoId, int) or photoId <= 0:

            raise ValueError(
                "Photo ID must be a positive integer."
            )

        if not isinstance(userId, int) or userId <= 0:

            raise ValueError(
                "User ID must be a positive integer."
            )

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    id

                FROM photos

                WHERE id = %s
                AND user_id = %s

                LIMIT 1
            """

            cursor.execute(
                query,
                (
                    photoId,
                    userId
                )
            )

            return cursor.fetchone() is not None

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # GET PHOTOS BY USER
    # ========================================================

    @staticmethod
    def getByUserId(userId):
        """
        Retrieve all photos belonging to a specific user.

        Args:
            userId (int):
                ID of the user.

        Returns:
            list:
                List of the user's photos ordered from newest
                to oldest.

        Raises:
            ValueError:
                If userId is not a positive integer.

            pymysql.MySQLError:
                If the database query fails.
        """

        if not isinstance(userId, int) or userId <= 0:

            raise ValueError(
                "User ID must be a positive integer."
            )

        db = Photo.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    id,
                    user_id,
                    file_name,
                    title,
                    description,
                    date_time

                FROM photos

                WHERE user_id = %s

                ORDER BY id DESC
            """

            cursor.execute(
                query,
                (userId,)
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            db.close()