<?php
// Include the database connection file
require_once 'db_connect.php';

// Set header to return JSON response
header('Content-Type: application/json');

// Get the posted data
$name = isset($_POST['name']) ? trim($_POST['name']) : '';
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$password = isset($_POST['password']) ? trim($_POST['password']) : '';

// --- Data Validation ---

// Check for empty fields
if (empty($name) || empty($email) || empty($password)) {
    echo json_encode(['success' => false, 'message' => 'الرجاء ملء جميع الحقول.']);
    exit;
}

// Validate email format
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'البريد الإلكتروني غير صالح.']);
    exit;
}

// --- Check if user already exists ---

$sql = "SELECT id FROM users WHERE email = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $email);
$stmt->execute();
$stmt->store_result();

if ($stmt->num_rows > 0) {
    echo json_encode(['success' => false, 'message' => 'هذا البريد الإلكتروني مسجل بالفعل.']);
    $stmt->close();
    $conn->close();
    exit;
}
$stmt->close();

// --- Insert new user ---

// Hash the password for security
$hashed_password = password_hash($password, PASSWORD_DEFAULT);

$sql = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("sss", $name, $email, $hashed_password);

if ($stmt->execute()) {
    // On successful registration
    // We can also start a session here if needed
    echo json_encode(['success' => true, 'message' => 'تم إنشاء الحساب بنجاح!']);
} else {
    // On failure
    echo json_encode(['success' => false, 'message' => 'حدث خطأ ما. الرجاء المحاولة مرة أخرى.']);
}

$stmt->close();
$conn->close();

?>
