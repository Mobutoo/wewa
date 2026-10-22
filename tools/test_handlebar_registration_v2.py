"""Failure cases protecting immutable GLB geometry during a registration edit."""
import copy
import unittest

from derive_handlebar_registration_v2 import NAMES, decode, derive, encode


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.document = {'asset': {'version': '2.0'}, 'scene': 0,
                         'scenes': [{'nodes': list(range(8))}],
                         'nodes': [{'name': n, 'mesh': i,
                                    'translation': [.045 if ' L ' in n else -.045, .1, .2]}
                                   for i, n in enumerate(sorted(NAMES))]}
        self.binary = b'preserve geometry and textures!!'
        assert len(self.binary) % 4 == 0

    def test_only_translations_change_and_binary_is_exact(self):
        output, report = derive(encode(self.document, self.binary), .0065)
        actual, binary = decode(output)
        self.assertEqual(binary, self.binary)
        self.assertEqual(len(report['changes']), 8)
        for before, after in zip(self.document['nodes'], actual['nodes']):
            self.assertAlmostEqual(abs(after['translation'][0]), .0385)
            self.assertEqual(before['translation'][1:], after['translation'][1:])

    def test_rejects_reapplication(self):
        output, _ = derive(encode(self.document, self.binary), .0065)
        with self.assertRaises(ValueError):
            derive(output, .0065)

    def test_rejects_missing_or_duplicated_part(self):
        for replacement in ['Unexpected part', self.document['nodes'][1]['name']]:
            document = copy.deepcopy(self.document)
            document['nodes'][0]['name'] = replacement
            with self.assertRaises(ValueError):
                derive(encode(document, self.binary), .0065)

    def test_rejects_animated_input(self):
        self.document['animations'] = [{'name': 'Motion'}]
        with self.assertRaises(ValueError):
            derive(encode(self.document, self.binary), .0065)

    def test_rejects_truncated_container(self):
        with self.assertRaises(ValueError):
            decode(encode(self.document, self.binary)[:-1])

    def test_checks_full_assembly_parent(self):
        self.document['nodes'].append({'name': 'PARENT [clamps]', 'children': list(range(8))})
        self.document['scenes'][0]['nodes'] = [8]
        output, _ = derive(encode(self.document, self.binary), .0065, True)
        actual, _ = decode(output)
        self.assertEqual(actual['nodes'][8], self.document['nodes'][8])
        self.document['nodes'][8]['rotation'] = [0, 0, 0, 1]
        with self.assertRaises(ValueError):
            derive(encode(self.document, self.binary), .0065, True)


if __name__ == '__main__':
    unittest.main()
