<?php
// Start the session
session_start();

// Include the database connection file
require_once 'db_connect.php';

// Set header to return JSON response
header('Content-Type: application/json');

// Get the posted data
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$password = isset($_POST['password']) ? trim($_POST['password']) : '';

// --- Data Validation ---
if (empty($email) || empty($password)) {
    echo json_encode(['success' => false, 'message' => 'الرجاء إدخال البريد الإلكتروني وكلمة المرور.']);
    exit;
}

// --- Find user and verify password ---
$sql = "SELECT id, name, password FROM users WHERE email = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 1) {
    $user = $result->fetch_assoc();

    // Verify the password
    if (password_verify($password, $user['password'])) {
        // Password is correct, start the session
        $_SESSION['loggedin'] = true;
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_name'] = $user['name'];

        echo json_encode([
            'success' => true,
            'message' => 'تم تسجيل الدخول بنجاح.',
            'user' => ['name' => $user['name']]
        ]);
    } else {
        // Incorrect password
        echo json_encode(['success' => false, 'message' => 'كلمة المرور غير صحيحة.']);
    }
} else {
    // User not found
    echo json_encode(['success' => false, 'message' => 'لم يتم العثور على حساب بهذا البريد الإلكتروني.']);
}

$stmt->close();
$conn->close();

?>
