class ErrorMessagesClass:
    # LoginSerializer
    USER_IS_DEACTIVATED = "This user has been deactivated."
    USER_WRONG_CREDENTIALS = "A user with this email and password was not found."

    # UserManager
    USER_MUST_HAVE_USERNAME = "Users must have a username."
    USER_MUST_HAVE_EMAIL = "Users must have an email address."
    SUPERUSER_MUST_HAVE_PASSWORD = "Superusers must have a password."

    NOT_AUTHENTICATED = "Authentication credentials were not provided."
    NOT_FOUND = "Not found."
    NOT_ALLOWED = "Not allowed"
    FIELD_IS_REQUIRED = "This field is required."
    NOT_VALID_EMAIL = "Enter a valid email address."
    NO_PERMISSION = "You do not have permission to perform this action."

    MIN_PASSWORD_LENGTH = 8
    _USER_FIELD_EXISTS = "user with this {field} already exists."
    _WEAK_PASSWORD = "Ensure this field has at least {min_length} characters."

    def get_user_exists_message(self, field: str):
        return self._USER_FIELD_EXISTS.format(field=field)

    def get_week_password_message(self):
        return self._WEAK_PASSWORD.format(min_length=self.MIN_PASSWORD_LENGTH)


ErrorMessages = ErrorMessagesClass()
