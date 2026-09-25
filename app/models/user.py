"""
Alzikrayat - User Model
=======================

This module represents the User data model.

Responsibilities:
    - Connect to the MySQL database.
    - Insert new users.
    - Find users by email or ID.
    - Validate user input.
    - Execute parameterized SQL queries.

Architecture:
    Model / Data Tier

Security:
    - SQL queries use parameterized placeholders.
    - Passwords are expected to be stored as Bcrypt hashes.
    - Raw passwords must never be stored in the database.
"""

import re

import pymysql

from app import config


class User:
    """
    User Model responsible for database operations related
    to registered users.
    """

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    @staticmethod
    def getDb():
        """
        Create and return a MySQL database connection.
        """

        return pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate(firstName, lastName, email, password):
        """
        Validate registration data.

        Returns:
            tuple:
                (True, {}) when validation succeeds.
                (False, errors) when validation fails.
        """

        errors = {}

        # ----------------------------------------------------
        # TYPE VALIDATION
        # ----------------------------------------------------

        if not isinstance(firstName, str):
            errors["first_name"] = "First name must be text."

        if not isinstance(lastName, str):
            errors["last_name"] = "Last name must be text."

        if not isinstance(email, str):
            errors["email"] = "Email must be text."

        if not isinstance(password, str):
            errors["password"] = "Password must be text."

        if errors:
            return False, errors

        # ----------------------------------------------------
        # CLEAN INPUT
        # ----------------------------------------------------

        firstName = firstName.strip()
        lastName = lastName.strip()
        email = email.strip().lower()

        # ----------------------------------------------------
        # FIRST NAME
        # ----------------------------------------------------

        if not firstName:

            errors["first_name"] = (
                "First name is required."
            )

        elif len(firstName) > 50:

            errors["first_name"] = (
                "First name must not exceed 50 characters."
            )

        elif not re.fullmatch(
            r"[A-Za-z\u0600-\u06FF]+",
            firstName
        ):

            errors["first_name"] = (
                "First name must contain letters only."
            )

        # ----------------------------------------------------
        # LAST NAME
        # ----------------------------------------------------

        if not lastName:

            errors["last_name"] = (
                "Last name is required."
            )

        elif len(lastName) > 50:

            errors["last_name"] = (
                "Last name must not exceed 50 characters."
            )

        elif not re.fullmatch(
            r"[A-Za-z\u0600-\u06FF]+",
            lastName
        ):

            errors["last_name"] = (
                "Last name must contain letters only."
            )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        emailPattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        if not email:

            errors["email"] = (
                "Email is required."
            )

        elif len(email) > 100:

            errors["email"] = (
                "Email must not exceed 100 characters."
            )

        elif not re.fullmatch(
            emailPattern,
            email
        ):

            errors["email"] = (
                "Please enter a valid email address."
            )

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        if not password:

            errors["password"] = (
                "Password is required."
            )

        elif len(password) < 8:

            errors["password"] = (
                "Password must contain at least 8 characters."
            )

        elif len(password) > 72:

            errors["password"] = (
                "Password must not exceed 72 characters."
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if errors:
            return False, errors

        return True, {}

    # ========================================================
    # CREATE USER
    # ========================================================

    @staticmethod
    def create(
        firstName,
        lastName,
        email,
        password,
        location=None,
        description=None,
        occupation=None
    ):
        """
        Create a new user in the database.

        Password must already be a Bcrypt hash.
        """

        db = User.getDb()
        cursor = db.cursor()

        try:

            query = """
                INSERT INTO users
                (
                    first_name,
                    last_name,
                    email,
                    password,
                    location,
                    description,
                    occupation
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    firstName,
                    lastName,
                    email,
                    password,
                    location,
                    description,
                    occupation
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
    # FIND BY EMAIL
    # ========================================================

    @staticmethod
    def findByEmail(email):
        """
        Find a user by email.

        Returns:
            dict or None
        """

        db = User.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    password,
                    location,
                    description,
                    occupation
                FROM users
                WHERE email = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (email,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # FIND BY ID
    # ========================================================

    @staticmethod
    def findById(userId):
        """
        Find a user by numeric ID.

        Returns:
            dict or None
        """

        if not isinstance(userId, int) or userId <= 0:
            raise ValueError(
                "User ID must be a positive integer."
            )

        db = User.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    password,
                    location,
                    description,
                    occupation
                FROM users
                WHERE id = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (userId,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # CHECK EMAIL
    # ========================================================

    @staticmethod
    def emailExists(email):
        """
        Check whether an email already exists.
        """

        db = User.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT id
                FROM users
                WHERE email = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (email,)
            )

            return cursor.fetchone() is not None

        finally:

            cursor.close()
            db.close()

    # ========================================================
    # GET ALL USERS
    # ========================================================

    @staticmethod
    def getAll():
        """
        Retrieve all registered users.

        Passwords are intentionally excluded.
        """

        db = User.getDb()
        cursor = db.cursor()

        try:

            query = """
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    location,
                    description,
                    occupation
                FROM users
                ORDER BY id DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            db.close()