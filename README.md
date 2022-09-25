# Gcrostore: Crostore with Google system <!-- omit in toc -->

**_Gcrostore_** is a web application of [Crostore] integrated with [Gmail] and [Google Sheets].

- [System requirements](#system-requirements)
- [Installation](#installation)
- [ASGI](#asgi)
- [API endpoints](#api-endpoints)
  - [/cancel/all](#cancelall)
  - [/status/login](#statuslogin)
- [License](#license)

## System requirements

- Google account with [Gmail] and [Google Sheets] available
- Credentials for Google API of the following scopes
  - https://www.googleapis.com/auth/gmail.labels
  - https://www.googleapis.com/auth/gmail.modify
  - https://www.googleapis.com/auth/drive.file
- [Selenium] server

## Installation

```sh
pip install git+https://github.com/ecoreuse/gcrostore
```

## ASGI

The [ASGI] is `gcrostore:app`.

Runnable with [uvicorn].
```sh
uvicorn gcrostore:app
```

## API endpoints

Still under development.

### /cancel/all

Cancels all the sold items according to messages in mailbox of Gmail.

### /status/login

Checks login status of the browser for Selenium.

## License

[MIT License](./LICENSE)

Copyright (c) 2022 Shuhei Nitta

[crostore]: https://github.com/huisint/crostore
[gmail]: https://developers.google.com/gmail/api
[google sheets]: https://developers.google.com/sheets/api
[Selenium]: https://www.selenium.dev/documentation/
[asgi]: https://asgi.readthedocs.io/en/latest/
[uvicorn]: https://www.uvicorn.org/
