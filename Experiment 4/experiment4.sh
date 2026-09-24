===== X.509 CERTIFICATE EXPERIMENT =====

[1] GENERATING RSA PRIVATE KEY
...+.....+......+....+..+.+........+............+...+......+.+.........+++++++++++++++++++++++++++++++++++++++*......+.......+........+................+......+...+.........+......+..+....+++++++++++++++++++++++++++++++++++++++*..+.........+........+...+.......+............+............+.....+....+..+.........+...+............+.............+...+.........+...+..+......+..........+.....+...+.+......+..+.+...........+...+......+.+.....+...+.............+..............+...+.+..+....+...+......+..+...+....+............+.....................+...+..+...+....+..+.+........+..........+.........+........+............+.+......+........+.+............++++++
..+......+....+++++++++++++++++++++++++++++++++++++++*........+.+......+..+...+....+...+++++++++++++++++++++++++++++++++++++++*.....+......+......+.++++++
Private key created.

[2] CREATING SELF-SIGNED CERTIFICATE
Certificate created.

[3] INSPECTING CERTIFICATE
subject=C=IN, ST=Jammu, L=Jammu, O=MIET, OU=CSE, CN=localhost
issuer=C=IN, ST=Jammu, L=Jammu, O=MIET, OU=CSE, CN=localhost
notBefore=Sep 24 16:04:21 2026 GMT
notAfter=Sep 24 16:04:21 2027 GMT
serial=702F22CF0C42D13577F5E1F5DA633C74A0A0F26A

Certificate Extensions:
X509v3 Subject Alternative Name: 
    DNS:localhost, IP Address:127.0.0.1
X509v3 Basic Constraints: critical
    CA:FALSE
X509v3 Key Usage: critical
    Digital Signature, Key Encipherment
X509v3 Extended Key Usage: 
    TLS Web Server Authentication

[4] VERIFYING WITHOUT TRUST
C=IN, ST=Jammu, L=Jammu, O=MIET, OU=CSE, CN=localhost
error 18 at 0 depth lookup: self-signed certificate
error certificate.crt: verification failed

[5] VERIFYING WITH TRUST
certificate.crt: OK

[6] COMPARING PUBLIC KEYS
Private key public-key hash:
SHA2-256(stdin)= fc1d4bf0eb83434ced34ae1d4a09a02ff97774672721edd90961e67

Certificate public-key hash:
SHA2-256(stdin)= fc1d4bf0eb83434ced34ae1d4a09a02ff97774672721edd90961e67c7d075918
PUBLIC KEY CHECK: PASSED

[7] HTTPS SERVER TEST
Starting local HTTPS server...

Testing HTTPS connection...
HTTPS CONNECTION: SUCCESSFUL

Testing with certificate as trusted CA...
TRUSTED HTTPS TEST: PASSED

===== EXPERIMENT COMPLETED =====
