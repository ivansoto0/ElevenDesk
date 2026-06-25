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
			m = re.search(r'"(Developer ID Application[^"]+)"', line)
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


def notarization_credentials(identity):
	profile = os.environ.get("NOTARYTOOL_PROFILE")
	if profile:
		return ["--keychain-profile", profile]
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


def build_macos():
	pyinstaller()
	app = DIST_DIR / (APP_NAME + ".app")
	dmg = DIST_DIR / (APP_NAME + ".dmg")

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
		missing = []
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
