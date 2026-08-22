# Disclaimer

## Purpose

`ecb-mode` is an educational deep-dive into why AES-ECB block cipher mode is cryptographically unsafe: a formal break, four attack vectors with real-world evidence, a tested demonstration toolkit, ECB detection techniques, and the defensive fix. Its scope is ECB mode and the boundary with correct alternatives (CBC, CTR, GCM) — not a general cryptography course.

## No warranty

This project is provided "as is", without warranty of any kind, express or implied. The authors and contributors accept no liability for any claim, damage, or other consequence arising from its use. You use it at your own risk.

<!-- Include the section below for any security, offensive-security, exploit, or
     otherwise dual-use content. Delete it if the repository has none. -->
## Authorized and educational use only

This repository exists for **educational and defensive security** purposes: understanding how a weakness works so it can be detected, prevented, and fixed.

Any code, proof of concept, or technique here must be used only against systems you **own** or have **explicit written authorization** to test. Do not use it against third-party, production, or shared systems, or against any account, service, or infrastructure that is not yours. Unauthorized access to computer systems is illegal in most jurisdictions, and doing so is solely your responsibility.

Every demonstration here is paired with its mitigation; the intent is to defend, not to enable an attack against anyone else.
