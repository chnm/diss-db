"""
Custom SMTP email backend that sends a proper FQDN in the EHLO/HELO greeting.
Django's default backend uses socket.getfqdn() which inside Docker containers
returns the short container ID rather than a fully-qualified hostname,
causing some SMTP servers to reject the connection.
"""

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    def open(self):
        """Override open() to inject a proper local_hostname into the SMTP connection."""
        if self.connection:
            return False

        local_hostname = getattr(settings, "EMAIL_LOCAL_HOSTNAME", None)

        connection_params = {}
        if local_hostname:
            connection_params["local_hostname"] = local_hostname
        else:
            from django.core.mail.utils import DNS_NAME

            connection_params["local_hostname"] = DNS_NAME.get_fqdn()

        if self.timeout is not None:
            connection_params["timeout"] = self.timeout
        if self.use_ssl:
            connection_params["context"] = self.ssl_context

        try:
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )
            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=self.ssl_context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
