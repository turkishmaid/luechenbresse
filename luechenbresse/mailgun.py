#!/usr/bin/env python
# coding: utf-8

"""
Convenience API to Mailgun

Created: 11.05.20
"""

import requests
import logging

from luechenbresse import ini


# courtesy https://gist.github.com/lalzada/3938daf1470a3b7ed7d167976a329638
class Mailgun(object):

    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            mailgun = "mailgun"
            cls.instance.url = ini.get(mailgun, "url")
            cls.instance.auth_key = ini.get(mailgun, "auth-key")
            cls.instance.mail_from = ini.get(mailgun, "from")
            cls.instance.mail_to = ini.get(mailgun, "to")
            cls.instance.active = cls.instance.url and cls.instance.auth_key and cls.instance.mail_from and cls.instance.mail_to
        return cls.instance

    def shoot(self, subject, body):
        if not self.active:
            logging.info("no mailgun account configured")
        else:
            logging.info(f"sending mail: {subject}")
            try:
                r = requests.post(
                    self.url,
                    auth=("api", self.auth_key),
                    data={
                        "from": self.mail_from,
                        "to": self.mail_to,
                        "subject": subject,
                        "text": body
                    })
                logging.info(f"HTTP {r.status_code}")
            except Exception as ex:
                logging.exception(f"{ex.__class__.__name__}: {str(ex)}")

if __name__ == "__main__":
    pass