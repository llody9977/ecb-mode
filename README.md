# AES-ECB mode is unsafe

![CI](https://github.com/llody9977/ecb-mode/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/llody9977/ecb-mode/actions/workflows/codeql.yml/badge.svg)
![Secret scan](https://github.com/llody9977/ecb-mode/actions/workflows/gitleaks.yml/badge.svg)
![License](https://img.shields.io/github/license/llody9977/ecb-mode)

Electronic Codebook (ECB) encrypts every block independently under the same key, with no randomization and no dependency between blocks. That determinism alone breaks confidentiality outright: ECB fails the standard IND-CPA definition with adversary advantage 1, regardless of key size. A second property — no authentication — means nothing detects a ciphertext that has been altered or reassembled, which is what turns the same determinism into forgery.

**[▶ Open the interactive site →](https://llody9977.github.io/ecb-mode/)** — every attack below runs live in your browser against real AES.

## Run the attacks yourself, in the browser

The site turns each weakness into a demonstration you can drive. The crypto is **real AES** via the Web Crypto API, executed locally — no server. (Web Crypto omits ECB on purpose, so ECB is reconstructed as AES-CBC with a zero IV, one block at a time; this is verified against the NIST SP 800-38A test vectors in the test suite.)

- **Pattern & structure leakage** — encrypt an image under ECB/CBC/GCM and watch the shape survive ECB; a block-repetition playground highlights identical ciphertext blocks.
- **Equality inference** — cluster users by identical ciphertext with no decryption (the Adobe 2013 pattern).
- **Byte-at-a-time recovery** — step a chosen-plaintext oracle and watch a hidden secret fall one byte at a time.
- **Cut-and-paste** — forge a `role=admin` token from a `role=user` service using only its public interface.
- **The fix** — the *same* `forgeAdminToken()` run against a GCM-backed service: the splice that produced `role=admin` fails tag verification and returns nothing, with the mode as the only variable. A single-bit flip is shown alongside it as the finer-grained case.

![AES-ECB has two root causes — determinism (one key maps a plaintext block to the same ciphertext block at any position, in any message) and no authentication (tampering is not detected). Determinism alone drives Vector 1 pattern leakage, Vector 2 equality inference and Vector 3 byte-at-a-time recovery; Vector 4 cut-and-paste needs determinism and the missing authentication together. There is no third root cause.](docs/diagrams/taxonomy.svg)

## Structure

- [`docs/`](docs/) — the GitHub Pages site and the write-up itself: [`index.html`](docs/index.html), [`styles.css`](docs/styles.css), and the theme-aware SVG [`diagrams/`](docs/diagrams/).
- [`docs/js/`](docs/js/) — the demo logic: [`crypto.mjs`](docs/js/crypto.mjs) (AES-ECB/CBC/GCM) and [`attacks.mjs`](docs/js/attacks.mjs) (the four vectors), plus [`ui.mjs`](docs/js/ui.mjs) which only wires them to the page.
- [`test/`](test/) — a Node test suite that exercises the same modules against real AES, including the NIST SP 800-38A AES-ECB vectors.

## Develop

```bash
npm ci            # install eslint (tests need no dependencies)
npm test          # node --test — verifies every vector against real AES
npm run lint      # eslint

# preview the site locally
python3 -m http.server -d docs 8000   # then open http://localhost:8000
```

Diagrams are regenerated with `python3 docs/diagrams/generate_diagrams.py`.

## Security

Found a vulnerability? Report it privately — see [`SECURITY.md`](SECURITY.md). Do not open a public issue for security reports.

## Disclaimer

For **educational and defensive** security research. Every demonstration runs entirely in your browser against a self-contained, in-page oracle — no network, no third-party system. Use these techniques only against systems you own or are explicitly authorized to test. See [`DISCLAIMER.md`](DISCLAIMER.md).

## License

Licensed under **Apache-2.0** — see [`LICENSE`](LICENSE). Covers the whole repository: code, documentation, and diagrams.
