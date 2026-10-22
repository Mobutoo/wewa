"""Resolve immutable manifest paths without mistaking a local README for the repository README."""
import posixpath


def resolve_manifest_path(manifest, reference, entries, redirects=None):
    if reference.startswith("/"):
        raise ValueError("Private absolute references are outside repository validation")
    key = manifest + "::" + reference
    if redirects and key in redirects:
        target = redirects[key]
        if target.startswith("/") or posixpath.normpath(target) != target or target.startswith("../"):
            raise ValueError("Unsafe snapshot path")
        if target not in entries:
            raise FileNotFoundError(target)
        return target
    local = posixpath.normpath(posixpath.join(posixpath.dirname(manifest), reference))
    # Bare filenames and explicit relative paths are relative to their manifest.
    # Repository-qualified paths remain rooted at the repository.
    candidates = [reference, local] if "/" in reference and not reference.startswith(".") else [local, reference]
    for target in candidates:
        if not target.startswith("../") and target in entries:
            return target
    raise FileNotFoundError(reference)
