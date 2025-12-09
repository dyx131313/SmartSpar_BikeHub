import smtplib
from email.mime.text import MIMEText
from email.header import Header

from flask import current_app


def send_verification_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send a plain-text verification email using SMTP settings from app config.

    This is a simple helper and intentionally avoids introducing extra
    dependencies like Flask-Mail.
    """
    app = current_app

    mail_server = app.config.get("MAIL_SERVER")
    mail_port = app.config.get("MAIL_PORT", 587)
    mail_use_tls = app.config.get("MAIL_USE_TLS", True)
    mail_username = app.config.get("MAIL_USERNAME")
    mail_password = app.config.get("MAIL_PASSWORD")
    mail_default_sender = app.config.get("MAIL_DEFAULT_SENDER") or mail_username

    # Simple debug print to help diagnose config issues in development
    try:
        print(
            "[DEBUG] send_verification_email config:",
            f"server={mail_server}, port={mail_port}, use_tls={mail_use_tls}, "
            f"username={mail_username}, default_sender={mail_default_sender}",
            flush=True,
        )
    except Exception:
        # printing should never break email sending
        pass

    if not mail_server or not mail_default_sender:
        app.logger.warning(
            "Mail configuration is incomplete, skip sending email to %s", to_email
        )
        # Also print to console for easier debugging
        print(
            "[DEBUG] Mail configuration incomplete, MAIL_SERVER or MAIL_DEFAULT_SENDER missing",
            flush=True,
        )
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = mail_default_sender
    msg["To"] = to_email

    try:
        if mail_use_tls:
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(mail_server, mail_port)

        if mail_username and mail_password:
            server.login(mail_username, mail_password)

        server.sendmail(mail_default_sender, [to_email], msg.as_string())
        server.quit()
        app.logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as exc:  # pragma: no cover - best-effort logging
        app.logger.error("Failed to send email to %s: %s", to_email, exc)
        # Print detailed error to console so it can be seen in dev server output
        try:
            print(f"[DEBUG] Failed to send email to {to_email}: {exc!r}", flush=True)
        except Exception:
            pass
        return False


