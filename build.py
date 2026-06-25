#!/usr/bin/env python3
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

APP_NAME = "ElevenDesk"
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
_ENTRY = Path("_entry.py")
_CONFIG = Path("build.config")


def _load_config():
	if not _CONFIG.exists():
		return
	for line in _CONFIG.read_text().splitlines():
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		key, _, value = line.partition("=")
		os.environ.setdefault(key.strip(), value.strip())


_load_config()


def run(args, **kwargs):
	subprocess.run(args, check=True, **kwargs)


def capture(args):
	result = subprocess.run(args, capture_output=True, text=True)
	return result.stdout + result.stderr


def clean():
	shutil.rmtree(DIST_DIR, ignore_errors=True)
	shutil.rmtree(BUILD_DIR, ignore_errors=True)
	for spec in Path(".").glob("*.spec"):
		spec.unlink()


def pyinstaller(*args):
	_ENTRY.write_text("from elevendesk.__main__ import run\nrun()\n")
	try:
		run(["uv", "run", "pyinstaller", "--name", APP_NAME, "--windowed",
			 "--clean", "--noconfirm", "--collect-all", APP_NAME.lower()]
			+ list(args) + [str(_ENTRY)])
	finally:
		_ENTRY.unlink(missing_ok=True)


def zip_dir(src, dst):
	with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
		for f in Path(src).rglob("*"):
			if f.is_file():
				zf.write(f, f.relative_to(src.parent))


def find_signing_identity():
	out = capture(["security", "find-identity", "-v", "-p", "codesigning"])
	for line in out.splitlines():
		if "Developer ID Application" in line:
			# Return the SHA1 hash to avoid ambiguity when multiple certs share the same name.
			m = re.search(r'([0-9A-F]{40})', line)
			if m:
				return m.group(1)
	return None


def team_id_from_identity(identity):
	m = re.search(r'\(([A-Z0-9]+)\)$', identity)
	return m.group(1) if m else None


def find_apple_id():
	aid = os.environ.get("APPLE_ID")
	if aid:
		return aid
	out = capture(["security", "find-internet-password", "-s", "idmsa.apple.com", "-g"])
	m = re.search(r'"acct"<blob>="([^"]+)"', out)
	return m.group(1) if m else None


def find_p8_key():
	keys = list(Path(".").glob("AuthKey_*.p8"))
	if not keys:
		return None, None
	key_path = keys[0]
	m = re.search(r'AuthKey_([A-Z0-9]+)\.p8', key_path.name)
	key_id = m.group(1) if m else None
	return key_path, key_id


def notarization_credentials(identity):
	profile = os.environ.get("NOTARYTOOL_PROFILE")
	if profile:
		return ["--keychain-profile", profile]

	key_path, key_id = find_p8_key()
	issuer = os.environ.get("APPLE_ISSUER_ID")
	if key_path and key_id and issuer:
		return ["--key", str(key_path), "--key-id", key_id, "--issuer", issuer]

	aid = find_apple_id()
	tid = os.environ.get("APPLE_TEAM_ID") or team_id_from_identity(identity)
	pw = os.environ.get("APPLE_APP_PASSWORD")
	if aid and tid and pw:
		return ["--apple-id", aid, "--team-id", tid, "--password", pw]
	return None


def sign(path, identity, deep=False):
	args = ["codesign", "--force", "--verify", "--sign", identity, "--options", "runtime"]
	if deep:
		args.append("--deep")
	run(args + [str(path)])


def create_dmg(app, dst):
	staging = BUILD_DIR / "dmg_staging"
	staging.mkdir(parents=True, exist_ok=True)
	dest = staging / app.name
	if dest.exists():
		shutil.rmtree(dest)
	shutil.copytree(app, dest, symlinks=True)
	link = staging / "Applications"
	if not link.exists():
		link.symlink_to("/Applications")
	run(["hdiutil", "create", "-volname", APP_NAME, "-srcfolder", str(staging),
		 "-ov", "-format", "UDZO", str(dst)])
	shutil.rmtree(staging)


def notarize(path, credentials):
	run(["xcrun", "notarytool", "submit", str(path)] + credentials + ["--wait"])
	run(["xcrun", "stapler", "staple", str(path)])


def _find_sound_lib_dylibs():
	result = subprocess.run(
		["uv", "run", "python", "-c", "import sound_lib, pathlib; print(pathlib.Path(sound_lib.__file__).parent)"],
		capture_output=True, text=True,
	)
	path = Path(result.stdout.strip()) / "lib"
	return list(path.rglob("*.dylib")) if path.exists() else []


def strip_ppc_from_sound_lib():
	"""PyInstaller can't handle ppc in fat binaries; strip it from sound_lib dylibs."""
	for dylib in _find_sound_lib_dylibs():
		info = capture(["lipo", "-info", str(dylib)])
		if "ppc" not in info:
			continue
		# Parse architectures, drop ppc variants
		archs = []
		for line in info.splitlines():
			if "are:" in line:
				archs = line.split("are:")[-1].strip().split()
			elif "is architecture:" in line:
				archs = [line.split("is architecture:")[-1].strip()]
		keep = [a for a in archs if not a.startswith("ppc")]
		if not keep:
			print(f"Skipping {dylib.name} — no non-ppc slices remain")
			continue
		tmp = dylib.with_suffix(".tmp.dylib")
		extract_flags = []
		for arch in keep:
			extract_flags += ["-extract", arch]
		run(["lipo", str(dylib)] + extract_flags + ["-output", str(tmp)])
		tmp.replace(dylib)
		print(f"Stripped ppc from {dylib.parent.name}/{dylib.name} → {' '.join(keep)}")


def remove_x86_dylibs_from_app(app):
	"""Remove 32-bit x86 dylibs bundled by PyInstaller.

	These fail notarization (pre-10.9 SDK) and can't run on macOS 10.15+.
	"""
	x86_dir = app / "Contents" / "Frameworks" / "sound_lib" / "lib" / "x86"
	if x86_dir.exists():
		shutil.rmtree(x86_dir)
		print("Removed sound_lib/lib/x86 from bundle (32-bit, pre-10.9 SDK)")


def build_macos():
	strip_ppc_from_sound_lib()
	pyinstaller()
	app = DIST_DIR / (APP_NAME + ".app")
	dmg = DIST_DIR / (APP_NAME + ".dmg")

	remove_x86_dylibs_from_app(app)

	identity = find_signing_identity()
	if not identity:
		print("No Developer ID signing identity found — skipping signing and notarization.")
		create_dmg(app, dmg)
		print("Done: " + str(dmg))
		return

	print("Signing with: " + identity)
	sign(app, identity, deep=True)
	create_dmg(app, dmg)
	sign(dmg, identity)

	creds = notarization_credentials(identity)
	if creds:
		print("Notarizing...")
		notarize(dmg, creds)
	else:
		key_path, key_id = find_p8_key()
		missing = []
		if key_path and key_id:
			if not os.environ.get("APPLE_ISSUER_ID"):
				missing.append("Issuer ID (APPLE_ISSUER_ID env var) — found key " + key_path.name)
		else:
			missing.append("AuthKey_<ID>.p8 file in project root (or NOTARYTOOL_PROFILE keychain profile)")
			if not find_apple_id():
				missing.append("Apple ID (APPLE_ID env var or idmsa.apple.com keychain entry)")
			if not os.environ.get("APPLE_APP_PASSWORD"):
				missing.append("app-specific password (APPLE_APP_PASSWORD env var)")
			if not team_id_from_identity(identity):
				missing.append("Team ID (APPLE_TEAM_ID env var)")
		print("Skipping notarization. Missing:")
		for item in missing:
			print("  - " + item)

	print("Done: " + str(dmg))


def build_windows():
	pyinstaller()
	src = DIST_DIR / APP_NAME
	dst = DIST_DIR / (APP_NAME + "-portable.zip")
	zip_dir(src, dst)
	print("Done: " + str(dst))


def main():
	clean()
	system = platform.system()
	if system == "Darwin":
		build_macos()
	elif system == "Windows":
		build_windows()
	else:
		print("Unsupported platform: " + system, file=sys.stderr)
		sys.exit(1)


if __name__ == "__main__":
	main()
