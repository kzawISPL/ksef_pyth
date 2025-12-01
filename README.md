## Opis
Zaimplementowany jest tutaj prosty moduł w Python 3 umożliwiający wysyłkę faktur do KSeF 2.0 w trybie interaktywnym. Autentykacja za pomocą tokena. Moduł może być wykorzystany jako pomocnicza biblioteka do komunikacji z systemem KSeF 2.0. 

Zaimplementowane są następujące funkcjonalności:
* Inicjalizacja, autentykacja za pomocą token i rozpoczęcie sesji uwierzytelnienia
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
* tests Testy unitowe

# Zaimplementowane funkcjonalności

| Funkcjonalność | API link | Endpoint | Metoda w klasie KSEFSDK
| -- | -- | -- | -- |
| Inicjalizacja uwierzytelnienia | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1challenge/post) | /api/v2/auth/challenge | Konstruktor KSEFSDK
| Pobranie certyfikatów | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Certyfikaty-klucza-publicznego/paths/~1api~1v2~1security~1public-key-certificates/get) | api/v2/security/public-key-certificates | Konstruktor
| Uwierzytelnienie z wykorzystaniem tokena KSeF | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1ksef-token/post) | /api/v2/auth/ksef-token | Konstruktor 
| Pobranie statusu uwierzytelniania | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1%7BreferenceNumber%7D/get) | /api/v2/auth/{referenceNumber} | Konstruktor
| Pobranie tokenów dostępowych | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Uzyskiwanie-dostepu/paths/~1api~1v2~1auth~1token~1redeem/post) | /api/v2/auth/token/redeem | Konstruktor
| Otwarcie sesji interaktywnej | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Wysylka-interaktywna/paths/~1api~1v2~1sessions~1online/post) | /api/v2/sessions/online | start_session
| Wysłanie faktury | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Wysylka-interaktywna/paths/~1api~1v2~1sessions~1online~1%7BreferenceNumber%7D~1invoices/post) | /api/v2/sessions/online/{referenceNumber}/invoices | send_invoice
| Pobranie statusu faktury z sesji | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Status-wysylki-i-UPO/paths/~1api~1v2~1sessions~1%7BreferenceNumber%7D~1invoices~1%7BinvoiceReferenceNumber%7D/get) | /v2/sessions/{referenceNumber}/invoices/{invoiceReferenceNumber} | send_invoice
| Pobranie UPO faktury z sesji na podstawie numeru referencyjnego faktury | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Status-wysylki-i-UPO/paths/~1api~1v2~1sessions~1%7BreferenceNumber%7D~1invoices~1%7BinvoiceReferenceNumber%7D~1upo/get) | /api/v2/sessions/{referenceNumber}/invoices/{invoiceReferenceNumber}/upo | pobierz_upo
| Zamknięcie sesji interaktywnej | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Wysylka-interaktywna/paths/~1api~1v2~1sessions~1online~1%7BreferenceNumber%7D~1close/post) | /api/v2/auth/sessions/{referenceNumber} | close_session 
| Unieważnienie sesji uwierzytelnienia | [link](https://ksef-test.mf.gov.pl/docs/v2/index.html#tag/Aktywne-sesje/paths/~1api~1v2~1auth~1sessions~1%7BreferenceNumber%7D/delete) | /api/v2/auth/sessions/{referenceNumber} | terminate_session

# Działanie

## Ogólny opis

Jest to moduł napisany w Python 3. Ogólny schemat wykorzystanie
* Utworzenie klasy KSEFSDK
* Rozpoczęcie sesji interaktywnej (metoda open_session)
* Wysłanie jednej lub więcej faktur oraz odczytanie wygenerowanego numeru ksef (send_invoice)
* (Opcjonalnie) Odczytanie UPO (pobierz_upo)
* Zamknięcie sesji interaktywnej (close_session)
* Zamknięcie sesji uwierzytelnienia (terminate_session)

Błedy (także z konstruktora klasy) są wyrzucane jako HTTPError lub ValueError. 


## Inicjalizacja, konstruktor KSEFSDK

*KSEFSDK.init(env: int, nip: str, token: str)*

Parametry:
* env Może przybierać trzy wartości: KSEFSDK.DEVKSEF, KSEFSDK.PREKSEF, KSEFSDK.PRODKSEF. Uwaga: testowane tylko w środowisku KSEFSDK.DEVKSEF
* nip NIP do uwierzytelnienia
* token Token KSeF do uwierzytleniania

Działanie:
* Inicjalizacja uwierzytelnienia
* Pobranie publicznych certyfikatów z kluczem do szyfrowania
* Autentykacja poprzez token KSeF

Zwraca:

Zainicjalizowana klasa KSEFSDK

## Otworzenie sesji interaktywnej

*start_session*

Działanie:

Rozpoczęcie sesji interaktywnej

## Wysłanie faktury

*send_invoice(invoice:str)*

Parametry:
* invoice Faktura do wysłania

Działanie:

Szyfruje i wysyła fakturę do KSeF.

Zwraca:

tuple[ok, error_mess, numer_ksef]
* ok True/False, wysyłka udana lub nieudana
* err_mess Jeśli wysyłka nieudana, to komunikat o przyczynie błędu (np. Niepoprawny format faktury)
* numer_ksef Jeśli wysyłka udana, to numer KSeF wysłanej faktury

## Odczytanie UPO

*pobierz_upo*

Działanie:

Pobiera UPO ostatnio przesłanej faktury jeśli faktura została wysłana z sukcesem. Musi być wywołana bezpośrednio po send_invoice.

Zwraca:

UPO

## Zamknięcie sesji interaktywnej

*close_session*

Działanie:

Zamyka sesję interaktywną rozpoczętą wywołaniem start_session

## Zamknięcie sesji uwierzytelniania

*terminate_session*

Działanie:

Zamyka sesję uwierzytelnienia rozpoczętą w konstruktorze KSIEFSDK

# Przykłady użycia

https://github.com/stanislawbartkowski/ksef_pyth/blob/main/test.py

https://github.com/stanislawbartkowski/ksef_pyth/blob/main/tests/test1.py



