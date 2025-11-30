## Opis
Zaimplementowany jest tutaj prosty moduł w Python 3 umożliwiający wysyłkę faktur do KSeF 2.0 w trybie interaktywnym. Autentykacja za pomocą tokena. Moduł może być wykorzystany jako pomocnicza biblioteka do komunikacji z systemem KSeF 2.0. 

Zaimplementowane są następujące funkcjonalności:
* Inicjalizacja, autentykacja za pomocą token i rozpoczęcie sesji uwierzytelnienia
* Rozpoczącie 
* Otworzenie sesji interaktywnej
* Wysłanie faktury
* Pobranie UPO
* Zamknięcie sesji interaktywnej
* Zamknięcie sesji uwierzytelniania

## Linki

https://github.com/m32/ksef

https://ksef-test.mf.gov.pl/docs/v2/index.html


# Testowanie

W module to testowania jest zawarty fikcyjny NIP oraz testowy token. Można wykorzystać ten token lub utworzyć własny. W wersji testowej nie ma gwarancji bezpieczeństwa danych, powinny być używane wyłącznie dane fikcyjne lub zanonimowane.

# Utworzenie testowego tokena

https://web2te-ksef.mf.gov.pl/web/

Należy zalogować się do aplikacji testowy za pomocą fikcyjnego NIP i w zakładce "Tokeny" utworzyć token ze wszystkimi uprawnieniami.

# Struktura kodu

* ksef/konwdocs Pomocniczy moduł umożliwiający wstawienie do wzorca XML aktualnych danych. Wykorzystywany do testowania.
* ksef/sdk
  * encrypt.py Pomocniczy moduł do szyfrowania i deszyfrowania danych. Wykorzystywany wewnętrznie przez ksefsdk.py
  * konwdokument.py Pomocniczy moduł do testowania
  * ksefsdk.py Główny moduł zawierający klasę KSEFSDK z funkcjonalnymi metodami

# Zaimplementowane funkcjonalności

| Funkcjonalność | API link | Endpoint | Metoda w klasie KSEFSDK
| -- | -- | -- | -- |
| Inicjalizacja uwierzytelnienia | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1challenge/post) | /api/v2/auth/challenge | Konstruktor KSEFSDK
| Pobranie certyfikatów | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Certyfikaty-klucza-publicznego/paths/~1api~1v2~1security~1public-key-certificates/get) | api/v2/security/public-key-certificates | Konstruktor
| Uwierzytelnienie z wykorzystaniem tokena KSeF | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1ksef-token/post) | /api/v2/auth/ksef-token | Konstruktor 
