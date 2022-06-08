from user.message_sender import Message

MIN_PASSWORD_LENGTH = 8

token_expire_hours = {
    "login": 24,
    "activate": 1,
    "password": 1,
}


class ErrorMessages:
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

    USER_FIELD_EXISTS = "user with this {field} already exists."
    WEAK_PASSWORD = "Ensure this field has at least {min_length} characters."
    INVALID_TOKEN = "Invalid token"


class EmailTemplates:
    _ACTIVATE_ACCOUNT = Message(
        subject="Please activate your account",
        body="Activation URL: {activation_url}",
    )

    def get_activation_message(self, user):
        message = self._ACTIVATE_ACCOUNT
        message.body = message.body.format(activation_url=user.activation_url)
        return message


email_templates = EmailTemplates()
