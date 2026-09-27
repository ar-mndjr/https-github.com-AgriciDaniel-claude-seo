import type { APIRoute } from 'astro';
import settings from '../content/settings.json';

// Built to /contact.php. Runs on your cPanel hosting (PHP) and emails form
// submissions to the "Form recipient" address set in the CMS settings.
const quote = (s: string) => `'${s.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`;

const php = `<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function reply(bool $ok, string $error = '', int $code = 200): void {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'error' => $error]);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') reply(false, 'Method not allowed', 405);

// Spam trap: people never fill this hidden field, bots usually do.
if (!empty($_POST['company_website'])) reply(true);

$to = ${quote(settings.form_recipient)};
$kind = preg_replace('/[^a-z_]/', '', (string)($_POST['_kind'] ?? 'contact'));
$subjects = [
    'contact'    => 'New project enquiry',
    'audit'      => 'Free SEO audit request',
    'newsletter' => 'New newsletter signup',
];
$subject = ($subjects[$kind] ?? 'Website enquiry') . ' — RankStruct website';

$email = trim((string)($_POST['email'] ?? ''));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) reply(false, 'Please enter a valid email address.', 422);

$lines = [];
foreach ($_POST as $key => $value) {
    if (in_array($key, ['company_website', '_kind'], true)) continue;
    if (is_array($value)) $value = implode(', ', array_map('strval', $value));
    $value = mb_substr(trim((string)$value), 0, 5000);
    if ($value === '') continue;
    $label = ucfirst(str_replace('_', ' ', (string)$key));
    $lines[] = $label . ":\\n" . $value;
}
$body = implode("\\n\\n", $lines) . "\\n\\n--\\nSent from " . ($_SERVER['HTTP_REFERER'] ?? 'the website');

$host = preg_replace('/^www\\./', '', preg_replace('/[^a-z0-9.-]/i', '', (string)($_SERVER['HTTP_HOST'] ?? 'localhost')));
$headers = implode("\\r\\n", [
    'From: RankStruct Website <no-reply@' . $host . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
]);

$sent = mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);
$sent ? reply(true) : reply(false, 'Mail could not be sent.', 500);
`;

export const GET: APIRoute = () => new Response(php);
