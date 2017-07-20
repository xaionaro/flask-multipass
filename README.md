Flask-Multipass
===============

Flask-Multipass is an extension that provides a user authentication
system for Flask which can use multiple backends (such as local users,
LDAP and OAuth) simultaneously.

Added support of CAS authentication.

Dependencies
============

* [https://github.com/discogs/python-cas-client](https://github.com/discogs/python-cas-client)

```sh
git clone https://github.com/discogs/python-cas-client
pip install python-cas-client/
```

Installation
============

```sh
git clone https://github.com/discogs/python-cas-client
pip install python-cas-client/
git clone https://github.com/xaionaro/flask-multipass-cas
pip install flask-multipass-cas/
```

Example of CAS+LDAP
===================

`~indico/etc/indico.conf`

```
[…]

# Auth

_acdir_ldap_config = {
    'uri': 'ldap://ldap.example.com:389',
    'bind_dn': 'login',
    'bind_password': 'PaSsWoRd',
    'timeout': 30,
    'verify_cert': False,
    'starttls': True,
    'page_size': 1000,

    'uid': 'mailNickname',
    'user_base': 'OU=Users,OU=Department,DC=Example,DC=Com',
    'user_filter': '(objectClass=person)',

    'member_of_attr': '',
    'ad_group_style': False,
}

AuthProviders = {
    'mephi-cas': {
        'type': 'cas',
        'title': 'cas.example.com',
        'cas_url_base': 'https://cas.example.com',
    }
}

IdentityProviders = {
    'mephi-cas': {
        'type': 'cas',
        'mapping': {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email'
        }
    },
    'acdir-ldap': {
        'type': 'ldap',
        'ldap': _acdir_ldap_config,
        'mapping': {
            'first_name': 'givenName',
            'last_name': 'sn',
            'email': 'mail',
            'affiliation': 'department'
        }
    }
}
```
