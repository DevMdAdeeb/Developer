<?php session_start(); ?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر إلكتروني</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <a href="#">اسم الموقع</a>
            </div>
            <nav>
                <?php if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true): ?>
                    <button id="auth-button">مرحباً، <?php echo htmlspecialchars($_SESSION['user_name']); ?></button>
                    <!-- Here you can add a logout button as well -->
                <?php else: ?>
                    <button id="auth-button">تسجيل الدخول / إنشاء حساب</button>
                <?php endif; ?>
            </nav>
        </div>
    </header>

    <main>
        <div class="container">
            <h1>الأقسام</h1>
            <!-- سيتم عرض الأقسام هنا لاحقًا -->
        </div>
    </main>

    <footer>
        <div class="container">
            <div class="footer-nav">
                <a href="#" class="footer-link">
                    <!-- أيقونة الرئيسية -->
                    <span>الرئيسية</span>
                </a>
                <a href="#" class="footer-link">
                    <!-- أيقونة البحث -->
                    <span>بحث</span>
                </a>
                <a href="#" class="footer-link cart-icon">
                    <!-- أيقونة السلة -->
                    <span class="cart-count">0</span>
                    <span>السلة</span>
                </a>
                <a href="#" class="footer-link">
                    <!-- أيقونة الحساب -->
                    <span>الحساب</span>
                </a>
            </div>
        </div>
    </footer>

    <!-- The Modal -->
    <div id="auth-modal" class="modal">
        <!-- Modal content -->
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <div id="login-form-container">
                <h2>تسجيل الدخول</h2>
                <form id="login-form">
                    <div class="message-container"></div>
                    <input type="email" name="email" placeholder="البريد الإلكتروني" required>
                    <input type="password" name="password" placeholder="كلمة المرور" required>
                    <button type="submit">تسجيل الدخول</button>
                    <p>ليس لديك حساب؟ <a href="#" id="show-signup">إنشاء حساب</a></p>
                </form>
            </div>
            <div id="signup-form-container" style="display: none;">
                <h2>إنشاء حساب جديد</h2>
                <form id="signup-form">
                    <div class="message-container"></div>
                    <input type="text" name="name" placeholder="الاسم الكامل" required>
                    <input type="email" name="email" placeholder="البريد الإلكتروني" required>
                    <input type="password" name="password" placeholder="كلمة المرور" required>
                    <button type="submit">إنشاء الحساب</button>
                    <p>لديك حساب بالفعل؟ <a href="#" id="show-login">تسجيل الدخول</a></p>
                </form>
            </div>
        </div>
    </div>

    <script src="js/main.js"></script>
</body>
</html>
