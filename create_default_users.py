from app import app, db
from models import User, Role

def create_default_users():
    # قائمة المستخدمين الافتراضيين
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@eelu.edu.eg',
            'password': 'admin123',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': Role.ADMIN
        },
        {
            'username': 'ehosny',
            'email': 'ehosny@eelu.edu.eg',
            'password': 'prof123',
            'first_name': 'Ehab',
            'last_name': 'Hosny',
            'role': Role.PROFESSOR
        },
        {
            'username': 'mkamal',
            'email': 'mkamal@eelu.edu.eg',
            'password': 'prof123',
            'first_name': 'Mohamed',
            'last_name': 'Kamal',
            'role': Role.PROFESSOR
        },
        {
            'username': 'amr21-00499',
            'email': 'amr21-00499@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Amr',
            'last_name': 'Student',
            'role': Role.STUDENT
        },
        {
            'username': 'ahmed21-00355',
            'email': 'ahmed21-00355@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Ahmed',
            'last_name': 'Student',
            'role': Role.STUDENT
        },
        {
            'username': 'youssef21-01741',
            'email': 'youssef21-01741@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Youssef',
            'last_name': 'Student',
            'role': Role.STUDENT
        },
        {
            'username': 'ashraf21-00521',
            'email': 'ashraf21-00521@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Ashraf',
            'last_name': 'Student',
            'role': Role.STUDENT
        },
        {
            'username': 'mariam21-02081',
            'email': 'mariam21-02081@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Mariam',
            'last_name': 'Student',
            'role': Role.STUDENT
        },
        {
            'username': 'yomna21-01703',
            'email': 'yomna21-01703@student.eelu.edu.eg',
            'password': 'user123',
            'first_name': 'Yomna',
            'last_name': 'Student',
            'role': Role.STUDENT
        }
    ]

    with app.app_context():
        # إنشاء الحسابات
        for user_data in default_users:
            # التحقق من عدم وجود المستخدم مسبقاً
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role']
                )
                db.session.add(user)
        
        try:
            db.session.commit()
            print("✅ تم إنشاء الحسابات الافتراضية بنجاح")
        except Exception as e:
            db.session.rollback()
            print("❌ حدث خطأ أثناء إنشاء الحسابات:", str(e))

if __name__ == '__main__':
    create_default_users() 