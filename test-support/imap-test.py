
import imaplib

with imaplib.IMAP4_SSL("127.0.0.1") as M:
    M.login("jj","pass")
    # M.create("test")
    # M.append("test","","",b'From:TestMessage\n\r')
    M.select("INBOX")
    typ, data = M.search(None, 'ALL')
    print(len(data[0].split()))
    print(typ, data)
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        print('Message %s\n%s\n' % (num, data[0][1]))
    M.close()
    M.logout()