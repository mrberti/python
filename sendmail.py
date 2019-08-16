#!/usr/bin/env python
import sys
import smtplib
import getpass
import readline

if __name__ == "__main__":
	argv = sys.argv

	from_mail = "simon.bertling@gmail.com";
	to_mail = "berti.x@gmx.de";
	subject = "sendmail.py";
	
	server_url = "smtp.gmail.com";
	port = 587;
	username = "simon.bertling@gmail.com";

	for i in range(len(argv)):
		arg = argv[i]
		if arg == "--to" or arg == "-t":
			try:
				to_mail = argv[i+1]
			except:
				print("Usage: -t, --to <mail_to_address>")
				sys.exit(0)
		elif arg == "--subject" or arg == "-s":
			try:
				subject = argv[i+1]
			except:
				print("Usage: -s, --subject <subject>")
				sys.exit(0)

	msg =  ""
	for line  in sys.stdin.readlines():
		msg = msg + line
	
	header = "To: " + to_mail + "\n"
	header = header + "From: " + from_mail + "\n"
	header = header + "Subject: " + subject + "\n";
	content = header + msg
	
	print( header + "\n" )

	pw = getpass.getpass("Password for %s: " % username);

	server = smtplib.SMTP(server_url, port);
	server.ehlo();
	server.starttls();
	server.login(username, pw);
	server.ehlo();

	server.sendmail(from_mail, to_mail, content);

	server.quit();
