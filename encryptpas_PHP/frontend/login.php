<?php
// Simple PHP page to render a login form and call the FastAPI backend

function call_api($endpoint, $payload) {
    $url = 'http://127.0.0.1:9099' . $endpoint; // FastAPI server
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload, JSON_UNESCAPED_UNICODE));
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err = curl_error($ch);
    curl_close($ch);

    if ($err) {
        return [
            'http_code' => 500,
            'body' => [ 'error' => 'cURL error: ' . $err ]
        ];
    }

    $decoded = json_decode($response, true);
    if ($decoded === null) {
        return [
            'http_code' => $http_code,
            'body' => [ 'raw' => $response ]
        ];
    }

    return [
        'http_code' => $http_code,
        'body' => $decoded
    ];
}

$result = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    if ($username !== '' && $password !== '') {
        $result = call_api('/api/login', [ 'username' => $username, 'password' => $password ]);
    } else {
        $result = [ 'http_code' => 400, 'body' => [ 'error' => 'Vui lòng nhập đầy đủ username và password' ] ];
    }
}
?>
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Demo Password Manager - Login</title>
  <link rel="stylesheet" href="/frontend/css/styles.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>body{font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}</style>
  <meta name="color-scheme" content="light dark" />
  <meta name="description" content="Login demo for Password Manager" />
  <link rel="icon" href="data:," />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Login</h1>
      <form method="POST" class="form">
        <div class="field">
          <label for="username">Username</label>
          <input type="text" id="username" name="username" placeholder="alice" required />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn">Sign In</button>
      </form>

      <div class="result">
        <?php if ($result !== null): ?>
          <h2>Kết quả API</h2>
          <pre><?php echo htmlspecialchars(json_encode($result['body'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)); ?></pre>
        <?php else: ?>
          <p class="muted">Điền form và nhấn Sign In để xem kết quả.</p>
        <?php endif; ?>
      </div>

      <div class="links">
        <a href="/frontend/signup.php">Chưa có tài khoản? Đăng ký</a>
      </div>
    </div>
  </div>
</body>
</html>


