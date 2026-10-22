import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from manifest_paths import resolve_manifest_path


class ManifestPathsTest(unittest.TestCase):
    def test_local_readme_does_not_resolve_to_root_readme(self):
        entries = {"README.md", "creative/research/piece/README.md"}
        self.assertEqual(resolve_manifest_path("creative/research/piece/manifest.json", "README.md", entries), "creative/research/piece/README.md")

    def test_repository_qualified_path_stays_rooted(self):
        entries = {"assets-src/piece/README.md", "creative/research/piece/assets-src/piece/README.md"}
        self.assertEqual(resolve_manifest_path("creative/research/piece/manifest.json", "assets-src/piece/README.md", entries), "assets-src/piece/README.md")

    def test_explicit_relative_path_is_normalized(self):
        self.assertEqual(resolve_manifest_path("creative/research/piece/manifest.json", "../other/proof.json", {"creative/research/other/proof.json"}), "creative/research/other/proof.json")

    def test_missing_snapshot_cannot_fall_back_to_mutable_document(self):
        with self.assertRaises(FileNotFoundError):
            resolve_manifest_path("manifest.json", "README.md", {"README.md"}, {"manifest.json::README.md":"frozen/README.md"})

    def test_snapshot_still_has_to_match_original_bytes(self):
        # Run the real Git-index checker; the mapped snapshot must not become an integrity exemption.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for folder in ('tools/motorcycle-lab','frozen','freeze'):(root/folder).mkdir(parents=True,exist_ok=True)
            for name in ('check_motorcycle18_index_v3.py','manifest_paths.py'):
                shutil.copy2(Path(__file__).parent/name,root/'tools'/name)
            (root/'tools/motorcycle-lab/catalog.json').write_text('{"assets":{}}')
            (root/'README.md').write_bytes(b'current')
            snapshot=root/'frozen/README.md';snapshot.write_bytes(b'original')
            manifest=root/'freeze/manifest.json'
            manifest.write_text(json.dumps({'files':[{'path':'README.md','bytes':8,'sha256':hashlib.sha256(b'original').hexdigest()}]}))
            (root/'tools/motorcycle-manifest-paths-v1.json').write_text(json.dumps({'targets':[{'manifest':'freeze/manifest.json','manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'original_path':'README.md','snapshot_path':'frozen/README.md'}]}))
            subprocess.run(['git','init','-q'],cwd=root,check=True)
            subprocess.run(['git','add','.'],cwd=root,check=True)
            command=['python',str(root/'tools/check_motorcycle18_index_v3.py'),'--output',str(root/'result.json')]
            self.assertEqual(subprocess.run(command,cwd=root,capture_output=True).returncode,0)
            snapshot.write_bytes(b'tampered')
            subprocess.run(['git','add','frozen/README.md'],cwd=root,check=True)
            self.assertNotEqual(subprocess.run(command,cwd=root,capture_output=True).returncode,0)
            self.assertTrue(any(error[1]=='hash' for error in json.loads((root/'result.json').read_text())['errors']))

    def test_snapshot_cannot_escape_repository(self):
        with self.assertRaises(ValueError):
            resolve_manifest_path("manifest.json", "README.md", {"../outside"}, {"manifest.json::README.md":"../outside"})


if __name__ == "__main__":
    unittest.main()
