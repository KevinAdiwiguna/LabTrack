from models import User, Category, Item, Borrower, Loan, LoanRequest, ActivityLog
import database as db
import utils


class AuthController:
    current_user: User = None

    @classmethod
    def login(cls, username, password):
        user = User.authenticate(username, password)
        if user:
            cls.current_user = user
            db.log_activity(user.id, user.username, "LOGIN",
                            f"Login berhasil sebagai {user.role}")
            return True, user
        return False, None

    @classmethod
    def logout(cls):
        if cls.current_user:
            db.log_activity(cls.current_user.id, cls.current_user.username, "LOGOUT", "Logout")
            cls.current_user = None

    @classmethod
    def register(cls, username, password, full_name):
        ok, result = User.register(username, password, full_name)
        if ok:
            db.log_activity(result, username, "REGISTRASI",
                            f"Akun baru terdaftar: {full_name} (viewer)")
        return ok, result

    @classmethod
    def has_permission(cls, min_role):
        roles = ['viewer', 'laboran', 'admin']
        if not cls.current_user:
            return False
        return roles.index(cls.current_user.role) >= roles.index(min_role)

    @classmethod
    def can_edit(cls):
        return cls.has_permission('laboran')

    @classmethod
    def is_admin(cls):
        return cls.has_permission('admin')

    @classmethod
    def is_viewer(cls):
        return cls.current_user and cls.current_user.role == 'viewer'
