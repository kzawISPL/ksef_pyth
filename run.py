from typing import Callable
from ksef import KSEFSDK
from ksef import KONWDOKUMENT
from tests import test_mix as T
# import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import hashlib
import pyodbc
from typing import Dict, Any, Optional

load_dotenv()

#############################################################################

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=db.intersnack.pl;DATABASE=ross;Trusted_Connection=yes; TrustServerCertificate=yes;timeout=600')
cursor = conn.cursor()

#############################################################################

NIP   = os.getenv('NIP')
TOKEN_TEST   = os.getenv('TOKEN_TEST')
TOKEN_DEMO   = os.getenv('TOKEN_DEMO')


#############################################################################
def KS():
    # K = KSEFSDK.initsdk(KSEFSDK.DEVKSEF, nip=NIP, token=TOKEN_TEST)
    K = KSEFSDK.initsdk(KSEFSDK.PREKSEF, nip=NIP, token=TOKEN_DEMO)
    return K

#############################################################################
def _today():
    return datetime.now().strftime("%Y-%m-%d")

#############################################################################
def gen_numer_faktry():
    nr = "FV"
    data_f = datetime.now().isoformat()
    return nr + data_f

#############################################################################
def test1():
    # PRZYKLAD 1: Otworz sesję i zamknij sesję
    K = KS()
    K.start_session()
    K.close_session()
    K.session_terminate()

#############################################################################
def _send_invoice(path, action: Callable | None = None):
    print(path)
    with open(path, "r") as f:
        invoice = f.read()
    K = KS()
    K.start_session()
    status = K.send_invoice(invoice=invoice)
    print(status)
    if action is not None:
        action(K, status)
    K.close_session()
    K.session_terminate()
    return status

#############################################################################
def test2():
    # PRZYKLAD 2: wyślij niepoprawną fakture do KSEF
    path = T.testdatadir("FA_3_Przykład_9.xml")
    _send_invoice(path)

#############################################################################
def _prepare_invoice():
    inpath = T.testdatadir("FA_3_Przykład_9_pattern.xml")
    outpath = T.workdatadir("faktura.xml")
    zmienne = {
        KONWDOKUMENT.DATA_WYSTAWIENIA: _today(),
        KONWDOKUMENT.NIP: T.NIP,
        KONWDOKUMENT.NIP_NABYWCA: T.NIP_NABYWCA,
        KONWDOKUMENT.NUMER_FAKTURY: gen_numer_faktry()
    }
    KONWDOKUMENT.konwertuj(sou=inpath, dest=outpath, zmienne=zmienne)
    return outpath

#############################################################################
def test3():
    _prepare_invoice()

#############################################################################
def test4():
    # PRZYKŁAD 4: wyślij poprawną fakturę do KSEF
    outpath = _prepare_invoice()
    status = _send_invoice(path=outpath)
    print(status)

#############################################################################
def test5():
    # PRZYKŁAD 5: wyslij poprawną fakturę do KSEF i pobierz UPO
    outpath = _prepare_invoice()

    def wez_upo(K: KSEFSDK, status):
        ok, _, numer_ksef = status
        assert ok
        print("Pobierz UPO dla wysłanej faktury")
        upo = K.pobierz_upo()
        print(upo)

    status = _send_invoice(path=outpath, action=wez_upo)
    print(status)

#############################################################################
def test6():
    # PRZYKLAD 6: Pobierz istniejącą fakturę
    K = KS()
    faktura_ksef = "7497725064-20251207-0100A07C1B9B-7C"
    print(f"Pobierz fakturę o numerze: {faktura_ksef}")
    faktura = K.get_invoice(ksef_number=faktura_ksef)
    print(faktura)
    K.session_terminate()

#############################################################################
def test7():
    K = KS_NABYWCA()
    outpath = _prepare_invoice(patt=T.PRZYKLAD_ZAKUP_8)
    status = _send_invoice_K(K, path=outpath)
    print(status)
    ok, errmess, numer_ksef = status

#############################################################################
def test8():
    K = KS()
    res = K.get_invoices_zakupowe_metadata(
        date_from="2025-11-01", date_to="2025-12-31")
    print(res)
    K.session_terminate()

#############################################################################
def test9():
    K = KS()
    b = b'111111111'
    K.send_batch_session_bytes(payload=[b])
    K.session_terminate()

#############################################################################
def test10():
    K = T.KS_CERT()
    res = K.get_invoices_zakupowe_metadata(
        date_from="2025-12-21", date_to="2025-12-31")
    print(res)
    K.session_terminate()

#############################################################################
def print_dict(d, prefix="")-> None:
    if isinstance(d, dict):
        for key, value in d.items():
            print_dict(value, prefix + str(key) + ".")
    elif isinstance(d, list):
        for i, item in enumerate(d):
            print_dict(item, prefix + f"[{i}].")
    else:
        print(f"{prefix[:-1]} = {d}")

#############################################################################

# def zapisz_response_do_pliku(response, filename_prefix="ksef_response")-> None:
#     output_dir = Path("ksef_responses")
#     output_dir.mkdir(exist_ok=True)

#     filename = f"ksef_response_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"

#     with open(output_dir / filename, "w", encoding="utf-8") as f:
#         json.dump(response, f, ensure_ascii=False, indent=2)

#############################################################################


#############################################################################

def pobierz_i_zapisz_faktury(subjectType: str, date_from:str, date_to:str, pageSize:int)-> None:

    offset = 0
    # page_size = pageSize

    while True:
        
        response    = K.search_incoming_invoices(subjectType, date_from, date_to, pageSize, offset)
        id          = zapisz_json_do_bazy(subjectType, date_from, date_to, response, pageSize, offset)
        if id != -1:
            zapisz_pola_do_bazy(id)

        if response.get("isTruncated") is True:
            # przerwij i zawęż kryteria zapytania
            raise RuntimeError("Wynik został ucięty – należy zawęzić kryteria")

        if response.get("hasMore") is False:
            break

        offset += 1


    # print(response)
    # for inv in response['invoices']:
    #     # print(f"KsefNumber:{inv['ksefNumber']}, Numer faktury: {inv['invoiceNumber']}, Data wystawienia: {inv['issueDate']}")
    #     print("----------------------------------------------------------------")
    #     print_dict(inv)
    #     print("----------------------------------------------------------------")

    # return response



def zapisz_json_do_bazy(Subject_type: str, date_from: str, date_to: str, response_json: Dict[str, Any], page_size, offset) -> int:

    """
    Zapisuje pojedynczy JSON do bazy SQL Server
    """
    json_str = json.dumps(response_json, ensure_ascii=False)
    hash_bytes = hashlib.sha256(json_str.encode("utf-8")).digest()
    has_more = response_json.get("hasMore", False)
    is_truncated = response_json.get("isTruncated", False)
    continuation = response_json.get("continuationToken")
    ile_faktur= len(response_json.get("invoices", []))
    pageSize= page_size
    offset= offset


    mapping = {
                "Subject1": "OUT",
                "Subject2": "IN"
               }
    InOut = mapping.get(Subject_type, 0)

    data_od=date_from
    data_do=date_to
    check_date = data_do[:10]

    try:
        cursor.execute("""
            INSERT INTO KSEF.KSeF_Response (
                InOut,                data_od,                data_do,                check_date,           received_at,            has_more,
                is_truncated,         continuation,           ile_faktur,                pageSize,             offset,                 response_json,
                response_hash
            ) VALUES (?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            InOut,              data_od,            data_do,            check_date,         datetime.now(),     has_more,
            is_truncated,       continuation,       ile_faktur,            pageSize,           offset,            json_str,
            hash_bytes
            )
        )
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        row_id = cursor.fetchone()[0]
        # print(row_id)

        return int(row_id)
    
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
        return -1
    
#############################################################################

def zapisz_pola_do_bazy(row_id: int) -> int:
    """
    Zapisuje wybrane pola faktury do bazy SQL Server
    """

    def to_sqlserver_datetime(dt_str: str) -> str:
        """
        Konwertuje:        2026-01-13T12:13:17.866827+00:00        -> 2026-01-13 12:13:17
        """
        if not dt_str:
            return None

        return dt_str.replace("T", " ")[:19]

    try:
        # 1. Pobranie response_json
        cursor.execute(""" SELECT response_json    FROM KSEF.KSeF_Response  WHERE id = ?""",row_id)
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Brak rekordu KSeF_Response o id={row_id}")

        response_json = json.loads(row.response_json)

        # 2. Lista faktur (zmień klucz jeśli inny)
        invoices = response_json.get("invoices", [])

        if not invoices:
            return 0

        insert_sql = """
            INSERT INTO KSEF.KSeF_Invoice_Metadata (
                request_id,                ksef_number,                invoice_number,                invoice_hash,
                issue_date,                invoicing_date,             acquisition_date,              permanent_storage_date,
                seller_nip,                seller_name,                buyer_identifier_type,         buyer_identifier_value,
                buyer_name,                net_amount,                 vat_amount,                    gross_amount,
                currency,                  invoicing_mode,             invoice_type,                  form_code_system,
                form_code_schema_version,  form_code_value,            is_self_invoicing,             has_attachment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        inserted = 0

        for inv in invoices:
            cursor.execute(insert_sql, (
                row_id,
                inv["ksefNumber"],
                inv["invoiceNumber"],
                inv["invoiceHash"],

                # daty
                inv["issueDate"],                       # DATE jako 'YYYY-MM-DD'
                to_sqlserver_datetime(inv["invoicingDate"]),
                to_sqlserver_datetime(inv["acquisitionDate"]),
                to_sqlserver_datetime(inv["permanentStorageDate"]),

                # sprzedawca
                inv["seller"]["nip"],
                inv.get("seller", {}).get("name", "BRAK"),

                # nabywca
                inv["buyer"]["identifier"]["type"],
                inv["buyer"]["identifier"]["value"],
                inv.get("buyer", {}).get("name", "BRAK"),

                # kwoty
                float(inv["netAmount"]),
                float(inv["vatAmount"]),
                float(inv["grossAmount"]),
                inv["currency"],

                # typy
                inv["invoicingMode"],
                inv["invoiceType"],

                # formCode
                inv["formCode"]["systemCode"],
                inv["formCode"]["schemaVersion"],
                inv["formCode"]["value"],

                # flagi
                int(inv["isSelfInvoicing"]),   # BIT
                int(inv["hasAttachment"])      # BIT
            ))
            inserted += 1

        conn.commit()
        return inserted
    
    except Exception as e:
        print(f"Error saving invoice to database: {e}")
        conn.rollback()        


#############################################################################

def pobierz_brakujace_dni() -> list[tuple[str, str]]:
    """
    Wyczytuje maksymalna date z pola check_date dla IN i OUT i zwraca liste brakujacych dni do dzisiaj
    """

    cursor.execute("""
                    with maks as
                    (
                    select max(a.[check_date]) as maks_data,a.[InOut]
                    FROM [Ross].[KSEF].[KSeF_Response] as a
                    group by a.[InOut]
                    ),
                    crooss as
                    (
                    select 'Subject1'  as [Subject],'OUT' as INOUT 
                    union 
                    select 'Subject2','IN' as INOUT
                    )
                    SELECT
                    isnull(maks.maks_data,'2025-12-01') as czd_data,crooss.[Subject],crooss.INOUT 
                    from crooss
                    left join maks on crooss.INOUT=maks.InOut
                    """)
    
    return [(row.czd_data, row.Subject) for row in cursor.fetchall()]

#############################################################################

def przetworz_dzien(subject_type: str, day: str, pageSize:int)-> None:

    new_day_from = datetime.strptime(str(day), "%Y-%m-%d").date()
    new_day_from1 = new_day_from + timedelta(days=1)
    day_from    = new_day_from1.strftime("%Y-%m-%d")   

    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")  
    
    date_from = f"{day_from}T00:00:00.000000+00:00"
    date_to   = f"{yesterday_str}T23:59:59.999999+00:00"
    # print(f"Pobieranie faktur dla {subject_type} od {date_from} do {date_to}")


    pobierz_i_zapisz_faktury(subject_type, date_from, date_to, pageSize)

#############################################################################

def uzupelnij_brakujace_dni(pageSize:int=250)-> None:
    missing_days = pobierz_brakujace_dni()

    if not missing_days:
        print("Brak luk – baza kompletna")
        return

    print(f"Znaleziono {len(missing_days)} brakujących dni")

    for day,subject in missing_days:
        print(f"Dogrywanie dnia: {day},{subject}\n")

        przetworz_dzien(subject, day,pageSize=pageSize)


#############################################################################



if __name__ == "__main__":

    K = KS()
    K.start_session()

    uzupelnij_brakujace_dni()
    
    K.close_session()
    K.session_terminate()

    cursor.close()
    conn.close()



    # cursor.execute(""" SELECT response_json    FROM KSEF.KSeF_Response  WHERE id = 1""")
    # row = cursor.fetchone()
    # if not row:
    #     raise ValueError(f"Brak rekordu KSeF_Response o id=1")
    # response_json = json.loads(row.response_json)

    # for invoice in response_json.get("invoices", []):
    # #     # print(f"KsefNumber:{inv['ksefNumber']}, Numer faktury: {inv['invoiceNumber']}, Data wystawienia: {inv['issueDate']}")
    #     print("----------------------------------------------------------------")
    #     # print_dict(invoice)
    #     print(   invoice.get("seller", {}).get("name", "BRAK")       )
    #     print("----------------------------------------------------------------")

    # cursor.close()
    # conn.close()


