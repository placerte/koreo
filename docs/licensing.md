# Licensing and dependency audit

Audit date: 2026-10-12

Koreo's original source and documentation are released under the MIT License.
The authoritative terms are in [`LICENSE`](../LICENSE). Third-party work keeps
its own license; MIT licensing does not relicense those components.

## Distribution conclusion

The locked dependency set is compatible with distributing Koreo under MIT.
Most development dependencies are permissively licensed. The runtime GUI
dependency, PySide6 and its Qt libraries, is available under LGPL-3.0-only (or
alternative GPL/commercial terms). Koreo elects the LGPL-3.0-only option for
open-source use.

The current repository and Koreo wheel do not copy PySide6 or Qt binaries:
PySide6 remains a separately installed dependency. Koreo does not modify Qt,
prevent replacement of its shared libraries, or impose terms that override
the LGPL. A future standalone installer that bundles Qt must be audited as a
separate release step and must include the applicable Qt/PySide notices,
license texts, relinking/replacement information, and corresponding-source
offer or access required by the exact modules shipped. Codec and platform
plugins in that bundle must also be inventoried at that time.

## Runtime and bundled assets

| Component | Locked version | License used | Assessment |
| --- | ---: | --- | --- |
| PySide6, Addons, Essentials, Pdf, WebEngine, Shiboken6 | 6.12.0 / 6.12.0.140 | LGPL-3.0-only | Compatible as a separate dynamically linked dependency; LGPL obligations apply to redistribution of its binaries. |
| Lucide icon paths embedded in `icons.py` | Snapshot audited 2026-10-12 | ISC | Permissive; required notice is retained in `THIRD_PARTY_NOTICES.md`. |
| Feather-derived Lucide icons (`square`, `zoom-in`, `zoom-out`) | Snapshot audited 2026-10-12 | MIT | Permissive; required notice is retained in `THIRD_PARTY_NOTICES.md`. |

PySide6's package metadata offers `LGPL-3.0-only OR GPL-2.0-only OR
GPL-3.0-only`. Qt's own documentation notes that only licenses of components
actually used and distributed with an application need to be acknowledged.
That is why the standalone-build audit is a release gate rather than a claim
that every optional Qt component is currently shipped by Koreo.

## Development and build dependencies

These tools are not imported by the distributed application. The audit covers
the packages resolved by `uv.lock` plus the declared Hatchling build backend.

| Packages | License |
| --- | --- |
| Black, mypy, mypy-extensions, ast-serialize, librt, platformdirs, pytokens, pytest, iniconfig, pluggy, pytest-qt, pathspec, Hatchling | MIT |
| Click | BSD-3-Clause |
| Packaging | Apache-2.0 OR BSD-2-Clause |
| Pygments | BSD-2-Clause |
| typing-extensions | PSF-2.0 |

All are permissive licenses compatible with developing and distributing an
MIT-licensed project. Development tools do not become part of Koreo merely by
running them.

## Audit method and maintenance

- Compared every package in `uv tree` with the installed distribution's
  `License-Expression`, `License`, classifier, and included license metadata.
- Compared the bundled icon names and notice against Lucide's upstream license.
- Confirmed the project wheel contains `LICENSE` and does not contain PySide6,
  Qt, test tools, or local media/project files.
- Re-run this audit whenever dependencies change and before publishing a
  standalone executable or installer.

This is an engineering compliance record, not legal advice.
