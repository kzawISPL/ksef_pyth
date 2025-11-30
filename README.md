## Opis
Zaimplementowany jest tutaj prosty moduł umożliwiający wysyłkę faktur do KSeF 2.0 w trybie interaktywnym. Autentykacja za pomocą tokena. Moduł może być wykorzystany jako pomocnicza biblioteka do komunikacji z systemem KSeF 2.0. 

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

# Utworzenie testowgo tokena

https://web2te-ksef.mf.gov.pl/web/

Należy zalogować się do aplikacji testowy za pomocą fikcyjnego NIP i w zakładce "Tokeny" utworzyć token ze wszystkimi uprawnieniami.
