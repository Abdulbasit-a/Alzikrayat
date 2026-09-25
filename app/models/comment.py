"""
Alzikrayat - Comment Model
==========================

This module handles database operations related to photo comments.

The Model layer is responsible only for data access and SQL.
Business logic and request handling remain in the Controller.

Database table:
    comments
"""

import pymysql

from app import config


class Comment:
    """
    Data model for photo comments.

    Handles creating, retrieving, and deleting comments
    using parameterized SQL queries.
    """

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    @staticmethod
    def getDb():
        """
        Create a connection to the MySQL database.
        """

        return pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )

    # ========================================================
    # GET COMMENTS FOR PHOTO
    # ========================================================

    @staticmethod
    def getByPhotoId(photoId):
        """
        Retrieve all comments belonging to a photo.
        """

        db = Comment.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    comments.id,
                    comments.photo_id,
                    comments.user_id,
                    comments.comment,
                    comments.date_time,
                    users.first_name,
                    users.last_name
                FROM comments
                INNER JOIN users
                    ON comments.user_id = users.id
                WHERE comments.photo_id = %s
                ORDER BY comments.id ASC
            """

            cursor.execute(
                query,
                (photoId,)
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # FIND COMMENT
    # ========================================================

    @staticmethod
    def findById(commentId):
        """
        Retrieve one comment by ID.
        """

        db = Comment.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    comments.id,
                    comments.photo_id,
                    comments.user_id,
                    comments.comment,
                    comments.date_time,
                    users.first_name,
                    users.last_name
                FROM comments
                INNER JOIN users
                    ON comments.user_id = users.id
                WHERE comments.id = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (commentId,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # CREATE COMMENT
    # ========================================================

    @staticmethod
    def create(photoId, userId, commentText):
        """
        Insert a new comment.
        """

        db = Comment.getDb()
        cursor = db.cursor()

        try:

            query = """
                INSERT INTO comments
                (
                    photo_id,
                    user_id,
                    comment
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    photoId,
                    userId,
                    commentText
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
    # DELETE COMMENT
    # ========================================================

    @staticmethod
    def delete(commentId, userId):
        """
        Delete a comment only when it belongs
        to the given user.
        """

        db = Comment.getDb()
        cursor = db.cursor()

        try:

            query = """
                DELETE FROM comments
                WHERE id = %s
                AND user_id = %s
            """

            cursor.execute(
                query,
                (
                    commentId,
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
    # CHECK COMMENT OWNERSHIP
    # ========================================================

    @staticmethod
    def belongsToUser(commentId, userId):
        """
        Check whether a comment belongs
        to a specific user.
        """

        db = Comment.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT id
                FROM comments
                WHERE id = %s
                AND user_id = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (
                    commentId,
                    userId
                )
            )

            return cursor.fetchone() is not None

        finally:

            cursor.close()
            db.close()